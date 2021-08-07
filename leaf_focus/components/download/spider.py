from pathlib import Path
from string import Template

from scrapy import Request, linkextractors, Spider as ScrapySpider
from scrapy.exceptions import IgnoreRequest
from scrapy.http import Response
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor
from scrapy.settings import Settings

from leaf_focus.download.items.pdf_item import PdfItem


class Spider(ScrapySpider):
    name = "pdf"

    _link_extractor = None
    _custom_seen_links = {}
    _custom_start_urls = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        s = super(Spider, cls).from_crawler(crawler, *args, **kwargs)  # type: Spider
        settings = s.settings  # type:Settings
        s._custom_start_urls = settings.get("CUSTOM_START_URLS")
        s._link_extractor = LinkExtractor(
            allow_domains=settings.get("CUSTOM_ALLOW_DOMAINS"),
            deny_extensions=sorted(set(linkextractors.IGNORED_EXTENSIONS) - {"pdf"}),
        )
        return s

    def start_requests(self):
        for item in self._custom_start_urls:
            url = item["url"]
            category = item["category"]
            comment = item["comment"]
            yield Request(
                url=url,
                callback=self.parse,
                meta={"custom_pdf_category": category, "custom_pdf_comment": comment},
            )

    def parse(self, response: Response, **kwargs):
        links = self._link_extractor.extract_links(response)
        for link in links:
            url_lower = link.url.lower()
            if "pdf" in url_lower:
                if url_lower not in self._custom_seen_links:
                    link_info = self._extract_info(response, link)
                    self._custom_seen_links[url_lower] = link_info
                yield Request(link.url, self._parse_pdf)

    def _parse_pdf(self, response: Response):
        if "pdf" not in response.url.lower():
            return

        link_info = self._custom_seen_links.get(response.url.lower())

        name = (link_info.get("name", "") + " " + link_info.get("location", "")).strip()
        category = link_info.get("category", "")
        cache_file = self._get_response_cache_file(response)
        link = link_info.get("link")
        referrer = response.request.headers.get("referer", b"").decode("utf-8")
        last_updated = link_info.get("last_updated", "")
        item = PdfItem(
            name=name,
            category=category,
            path=cache_file,
            url=link.url,
            referrer=referrer,
            last_updated=last_updated,
        )
        return item

    def _get_response_cache_file(self, response: Response):
        downloader_mw = self.crawler.engine.downloader.middleware.middlewares
        mw_name = "httpcache.HttpCacheMiddleware"
        http_cache_mw = next(
            (mw for mw in downloader_mw if mw_name in str(type(mw))), None
        )
        storage = http_cache_mw.storage
        cache_dir = storage._get_request_path(self, response.request)
        cache_file = Path(cache_dir, "response_body")
        return cache_file

    def _extract_info(self, response: Response, link: Link):
        urls = [
            link.url,
            "/" + "/".join(link.url.split("/")[3:]),
            ("?" + link.url.split("?")[1]) if "?" in link.url else None,
        ]
        templates = {
            "last_updated": [
                Template(
                    '//a[contains(@href, "${url}")]/parent::td/parent::tr/td[@class="date"]/text()'
                ),
                Template('//a[contains(@href, "${url}")]/parent::li/em//text()'),
                Template(
                    '//a[contains(@href, "${url}")]/parent::td/parent::tr/td[1]/text()'
                ),
            ],
            "name": [
                Template(
                    '//a[contains(@href, "${url}")]/parent::td/parent::tr/td[not(@class)]/text()'
                ),
                Template('//a[contains(@href, "${url}")]/text()'),
            ],
            "location": [
                Template(
                    '//a[contains(@href, "${url}")]/parent::*/text()[normalize-space()]'
                ),
            ],
        }

        url_lower = link.url.lower()
        # is_member = "member" in url_lower or "representat" in url_lower
        # is_senator = "senator" in url_lower or "senator" in url_lower
        is_member = (
            len(response.xpath(f'//text()[contains(.,"Members\' Interests")]')) > 0
        )
        is_senator = (
            len(response.xpath(f'//text()[contains(.,"Senators\' Interests")]')) > 0
        )

        if is_member and is_senator:
            raise IgnoreRequest(f"Cannot be both MP and Senator for '{url_lower}'.")

        if is_member:
            category = "member"
        elif is_senator:
            category = "senator"
        else:
            raise IgnoreRequest(f"Unknown category for '{url_lower}'.")

        found_info = {
            "link": link,
            "category": category,
            "config_category": response.meta["custom_pdf_category"],
            "config_comment": response.meta["custom_pdf_comment"],
        }

        # extract information from the webpage
        for url in urls:
            if url is None:
                continue
            for key, value in templates.items():
                if key in found_info:
                    continue
                if key == "name" and "volumes_tabled" in url_lower:
                    # don't extract the person's name from the 'volumes tabled' files
                    continue
                for template in value:
                    query = template.substitute(url=url)
                    found = response.xpath(query)
                    if len(found) > 0:
                        found_value = " ".join(found.getall()).strip()
                        if key == "last_updated":
                            found_value = found_value.replace("Last updated", "")
                            found_value = found_value.replace("lodged between", "")
                            found_value = found_value.replace("lodged by", "")
                        found_info[key] = found_value.strip()

        return found_info