import logging
import re
from datetime import datetime
from logging import Logger
from numbers import Number
from typing import Any

from prometheus_client import Gauge, Counter, Info, Enum
from prometheus_client.twisted import MetricsResource
from scrapy import signals, Spider, Request, Item
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured, DropItem
from scrapy.http import Response, Headers
from scrapy.statscollectors import StatsCollector
from scrapy.utils.reactor import listen_tcp
from twisted.internet import task
from twisted.python.failure import Failure
from twisted.web.resource import Resource
from twisted.web.server import Site


class PrometheusExtension:
    """A scrapy extension that provides a prometheus metrics endpoint."""

    # based on
    # https://github.com/rangertaha/scrapy-prometheus-exporter/blob/master/scrapy_prometheus_exporter/prometheus.py
    # https://github.com/sashgorokhov/scrapy_prometheus/blob/master/scrapy_prometheus.py
    # https://docs.scrapy.org/en/latest/topics/extensions.html#sample-extension
    # https://github.com/prometheus/client_python

    _metric_name_re = re.compile(r"[^a-zA-Z0-9_:]+")

    def __init__(
        self,
        name: str,
        stats: StatsCollector,
        logger: Logger,
        host: str = "0.0.0.0",
        port: int = 9080,
        path: str = "metrics",
        interval: int = 10,
        prefix: str = "scrapy",
    ):
        """Create a new Scrapy extension for Prometheus metrics."""

        self.name = name
        self.stats = stats
        self.logger = logger
        self.host = host
        self.port = port
        self.path = path
        self.interval = interval
        self.prefix = prefix

        self._metrics = {}

        self._twisted_root = Resource()
        self._twisted_root.putChild(self.path.encode("utf-8"), MetricsResource())

        self._twisted_site = Site(self._twisted_root)

        self._twisted_endpoint = None

        self._twisted_tasks = []

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        """Entry point for Scrapy extension."""

        # first check if the extension should be enabled and raise
        # NotConfigured otherwise
        if not crawler.settings.getbool("PROM_METRICS_ENABLED"):
            raise NotConfigured

        name = crawler.settings.get("BOT_NAME")
        stats = crawler.stats

        ext_kwargs = {
            "host": crawler.settings.get("PROM_METRICS_HOST"),
            "port": crawler.settings.getint("PROM_METRICS_PORT"),
            "path": crawler.settings.get("PROM_METRICS_PATH"),
            "interval": crawler.settings.getint("PROM_METRICS_INTERVAL"),
            "prefix": crawler.settings.getint("PROM_METRICS_PREFIX"),
        }

        # instantiate the extension object
        ext = cls(
            name=name,
            stats=stats,
            logger=logging.getLogger(cls.__class__.__name__),
            **dict([(k, v) for k, v in ext_kwargs.items() if v]),
        )

        # connect the extension object to signals

        m = [
            # engine
            {"func": ext._engine_started, "signal": signals.engine_started},
            {"func": ext._engine_stopped, "signal": signals.engine_stopped},
            # spider
            {"func": ext._spider_opened, "signal": signals.spider_opened},
            {"func": ext._spider_idle, "signal": signals.spider_idle},
            {"func": ext._spider_closed, "signal": signals.spider_closed},
            {"func": ext._spider_error, "signal": signals.spider_error},
            # request
            {"func": ext._request_scheduled, "signal": signals.request_scheduled},
            {"func": ext._request_dropped, "signal": signals.request_dropped},
            {
                "func": ext._request_reached_downloader,
                "signal": signals.request_reached_downloader,
            },
            {
                "func": ext._request_left_downloader,
                "signal": signals.request_left_downloader,
            },
            {"func": ext._bytes_received, "signal": signals.bytes_received},
            {"func": ext._headers_received, "signal": signals.headers_received},
            # response
            {"func": ext._response_received, "signal": signals.response_received},
            {"func": ext._response_downloaded, "signal": signals.response_downloaded},
            # item
            {"func": ext._item_scraped, "signal": signals.item_scraped},
            {"func": ext._item_dropped, "signal": signals.item_dropped},
            {"func": ext._item_error, "signal": signals.item_error},
        ]

        for entry in m:
            signal_func = entry.get("func")
            signal_name = entry.get("signal")
            crawler.signals.connect(signal_func, signal_name)

        # return the extension object
        return ext

    def update(self):
        # collect stats as metrics
        # scrapy stats are in the format group/name/code
        # where group and code are optional
        sep = "/"
        for stat_name, stat_value in self.stats.get_stats().items():
            # create stat name
            names = stat_name.split(sep)
            if len(names) == 1:
                name1 = "general"
                name2 = names[0]
                name3 = "all"
            elif len(names) == 2:
                name1 = names[0]
                name2 = names[1]
                name3 = "all"
            elif len(names) == 3:
                name1 = names[0]
                name2 = names[1]
                name3 = names[2]
            else:
                raise ValueError(f"Unexpected number of separators in '{stat_name}'.")

            # set code if available
            labels = {"spider": self.name}

            name = "_".join([i for i in ["stat", name1, name2, name3] if i])

            # set stat value
            if isinstance(stat_value, Number):
                self._update_metric(name, labels, "gauge", stat_value)
            elif isinstance(stat_value, datetime):
                self._update_metric(name, labels, "info", str(stat_value))
            elif isinstance(stat_value, str):
                self._update_metric(name, labels, "enum", stat_value)
            else:
                raise ValueError(f"Unrecognised value '{repr(stat_value)}'.")

    def _update_metric(
        self,
        name: str,
        labels: dict,
        metric_type: str = "counter",
        value: Any = None,
    ):
        if not name:
            raise ValueError("Must provide name.")
        if not metric_type:
            raise ValueError("Must provide metric type.")
        if metric_type not in ["counter", "gauge", "info", "enum"]:
            raise ValueError(
                "Metric type must be one of 'counter', 'gauge', 'info', 'enum'."
            )
        if metric_type in ["counter"] and value is not None:
            raise ValueError("Counter cannot have value.")
        if metric_type in ["gauge", "info", "enum"] and value is None:
            raise ValueError("Gauge or info or enum must have value.")
        if metric_type in ["gauge"] and not isinstance(value, Number):
            raise ValueError("Gauge must have a numeric value.")
        if metric_type in ["enum"] and not isinstance(value, str):
            raise ValueError("Enum must have a string value.")

        name = self._metric_name_re.sub("_", name)
        metric_name = f"{self.prefix}_{name}".lower()

        label_keys = list(labels.keys())

        # for debugging
        show_metric_info = False
        if show_metric_info:
            details = {
                "original_name": name,
                "metric_name": metric_name,
                "metric_type": metric_type,
                "labels": labels,
                "label_keys": label_keys,
                "value": value,
            }
            details = ", ".join(
                [
                    f"{k} = {details[k]}"
                    for k in sorted(details.keys())
                    if details[k] is not None
                ]
            )
            self.logger.info(f"Prometheus metric '{details}'.")

        # ensure metric exists
        msg = f"'{metric_name}' with labels '{label_keys}'"
        if metric_name not in self._metrics:
            if metric_type == "counter":
                metric = Counter(metric_name, f"Counter {msg}.", label_keys)
            elif metric_type == "gauge":
                metric = Gauge(metric_name, f"Gauge {msg}.", label_keys)
            elif metric_type == "info":
                metric = Info(metric_name, f"Info {msg}.", label_keys)
            elif metric_type == "enum":
                metric = Enum(metric_name, f"Enum {msg}.", label_keys)
            else:
                raise ValueError(f"Unknown metric type '{metric_type}'.")

            self._metrics[metric_name] = metric

        # update metric
        metric = self._metrics[metric_name]
        if metric_type == "counter":
            metric.labels(**labels).inc()
        elif metric_type == "gauge":
            metric.labels(**labels).set(value)
        elif metric_type == "info":
            metric.labels(**labels).info({"info_value": value})
        elif metric_type == "enum":
            metric.labels(**labels).state(value)
        else:
            raise ValueError(f"Unknown metric '{metric_name}' type '{metric_type}'.")

    def _engine_started(self):
        self._update_metric("signal_engine_started", {"spider": self.name})

        # Start prometheus /metrics endpoint
        self._twisted_endpoint = listen_tcp([self.port], self.host, self._twisted_site)

        # Start task to regularly update the metrics
        self._twisted_tasks.append(task.LoopingCall(self.update))
        for twisted_task in self._twisted_tasks:
            if not twisted_task.running:
                twisted_task.start(self.interval, now=True)

    def _engine_stopped(self):
        self._update_metric("signal_engine_stopped", {"spider": self.name})

        # Stop task to regularly update the metrics
        for twisted_task in self._twisted_tasks:
            if twisted_task.running:
                twisted_task.stop()

        # Stop prometheus /metrics endpoint
        self._twisted_endpoint.stopListening()

    def _spider_opened(self, spider: Spider):
        self._update_metric("signal_spider_opened", {"spider": self.name})

    def _spider_idle(self, spider: Spider):
        self._update_metric("signal_spider_idle", {"spider": self.name})

    def _spider_error(self, failure: Failure, response: Response, spider: Spider):
        self._update_metric("signal_spider_error", {"spider": self.name})

    def _spider_closed(self, spider: Spider, reason: str):
        self._update_metric(
            "signal_spider_closed", {"spider": self.name, "reason": reason}
        )

    def _request_scheduled(self, request: Request, spider: Spider):
        self._update_metric("signal_request_scheduled", {"spider": self.name})

    def _request_dropped(self, request: Request, spider: Spider):
        self._update_metric("signal_request_dropped", {"spider": self.name})

    def _request_reached_downloader(self, request: Request, spider: Spider):
        self._update_metric("signal_request_reached_downloader", {"spider": self.name})

    def _request_left_downloader(self, request: Request, spider: Spider):
        self._update_metric("signal_request_left_downloader", {"spider": self.name})

    def _bytes_received(self, data: bytes, request: Request, spider: Spider):
        self._update_metric("signal_request_bytes_received", {"spider": self.name})

    def _headers_received(self, headers: Headers, request: Request, spider: Spider):
        self._update_metric("signal_request_headers_received", {"spider": self.name})

    def _response_received(self, response: Response, request: Request, spider: Spider):
        self._update_metric("signal_response_received", {"spider": self.name})

    def _response_downloaded(
        self, response: Response, request: Request, spider: Spider
    ):
        self._update_metric("signal_request_downloaded", {"spider": self.name})

    def _item_scraped(self, item: Item, response: Response, spider: Spider):
        self._update_metric("signal_item_scraped", {"spider": self.name})

    def _item_dropped(
        self, item: Item, response: Response, exception: DropItem, spider: Spider
    ):
        self._update_metric("signal_item_dropped", {"spider": self.name})

    def _item_error(
        self, item: Item, response: Response, spider: Spider, failure: Failure
    ):
        self._update_metric("signal_item_error", {"spider": self.name})
