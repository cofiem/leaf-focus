from pathlib import Path

import scrapy
from scrapy.linkextractors import LinkExtractor

from leaf_focus.download.items import LeafFocusItem


class PdfSpider(scrapy.Spider):
    name = "pdf"

    custom_start_urls = {
        "members": [
            # current 46th
            "https://www.aph.gov.au/Senators_and_Members/Members/Register",
            # previous by parliment
            "https://www.aph.gov.au/Senators_and_Members/Members/Register/Previous_Parliaments/45P_Members_Interest_Statements",
            "https://www.aph.gov.au/Senators_and_Members/Members/Register/Previous_Parliaments/44P_Members_Interest_Statements",
            "http://www.aph.gov.au/Parliamentary_Business/Committees/House_of_Representatives_Committees?url=pmi/declarations.htm",
        ],
        "sentors": [
            # current 46th
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests",
            # previous by parliment
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Register45thparl",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Register44thparl",
            # previous by year range
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Volumes_Tabled",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Volumes_Tabled/2008-10",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Volumes_Tabled/2004-07",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Volumes_Tabled/2004-07",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Volumes_Tabled/2002-04",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Volumes_Tabled/1998-02",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Volumes_Tabled/1996-98",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Volumes_Tabled/pre1996",
        ],
    }
    link_deny_extensions = sorted(
        set(scrapy.linkextractors.IGNORED_EXTENSIONS) - {"pdf"}
    )
    link_extractor = LinkExtractor(
        allow_domains=["aph.gov.au"], deny_extensions=link_deny_extensions
    )
    _custom_seen_links = {}

    def start_requests(self):
        for url in self.custom_start_urls["members"]:
            yield scrapy.Request(url=url, callback=self.parse)
        for url in self.custom_start_urls["sentors"]:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        links = self.link_extractor.extract_links(response)
        for link in links:
            url_lower = link.url.lower()
            if "pdf" in url_lower:
                if url_lower not in self._custom_seen_links:
                    self._custom_seen_links[url_lower] = link
                yield scrapy.Request(link.url, self._parse_pdf)

    def _parse_pdf(self, response):
        if "pdf" not in response.url:
            return

        name = ""  # TODO
        category = ""  # TODO
        cache_file = self._get_response_cache_file(response)
        link = self._custom_seen_links.get(response.url.lower())
        referrer = response.request.headers.get("referer", b"").decode("utf-8")
        last_updated = ""  # TODO
        item = LeafFocusItem(
            name=name,
            category=category,
            path=cache_file,
            url=link.url,
            referrer=referrer,
            last_updated=last_updated,
        )
        return item

    def _get_response_cache_file(self, response):
        downloader_mw = self.crawler.engine.downloader.middleware.middlewares
        mw_name = "httpcache.HttpCacheMiddleware"
        http_cache_mw = next(
            (mw for mw in downloader_mw if mw_name in str(type(mw))), None
        )
        storage = http_cache_mw.storage
        cache_dir = storage._get_request_path(self, response.request)
        cache_file = Path(cache_dir, "response_body")
        return cache_file
