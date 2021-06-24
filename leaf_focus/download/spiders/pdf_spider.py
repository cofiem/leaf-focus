from pathlib import Path
from string import Template

from scrapy import Spider, Request, linkextractors
from scrapy.exceptions import IgnoreRequest
from scrapy.linkextractors import LinkExtractor

from leaf_focus.download.items.pdf_item import PdfItem


class PdfSpider(Spider):
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
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Register46thparl",
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
    link_deny_extensions = sorted(set(linkextractors.IGNORED_EXTENSIONS) - {"pdf"})
    link_extractor = LinkExtractor(
        allow_domains=["aph.gov.au"], deny_extensions=link_deny_extensions
    )
    _custom_seen_links = {}

    def start_requests(self):
        for url in self.custom_start_urls["members"]:
            yield Request(url=url, callback=self.parse)
        for url in self.custom_start_urls["sentors"]:
            yield Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        links = self.link_extractor.extract_links(response)
        for link in links:
            url_lower = link.url.lower()
            if "pdf" in url_lower:
                if url_lower not in self._custom_seen_links:
                    link_info = self._extract_info(response, link)
                    self._custom_seen_links[url_lower] = link_info
                yield Request(link.url, self._parse_pdf)

    def _parse_pdf(self, response):
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

    def _extract_info(self, response, link):
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
                Template('//a[contains(@href, "${url}")]/parent::li/em/text()'),
            ],
            "name": [
                Template(
                    '//a[contains(@href, "${url}")]/parent::td/parent::tr/td[not(@class)]/text()'
                ),
                Template('//a[contains(@href, "${url}")]/text()'),
            ],
            "location": [
                Template(
                    '//a[contains(@href, "${url}")]/parent::li/text()[normalize-space()]'
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
            raise IgnoreRequest("Cannot be both MP and Senator.")
        if is_member:
            category = "member"
        elif is_senator:
            category = "senator"
        else:
            raise IgnoreRequest(f"Unknown category.")

        found_info = {
            "link": link,
            "category": category,
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
                    if len(found) == 1:
                        found_info[key] = found[0].get().strip()

        return found_info
