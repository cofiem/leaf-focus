import logging
import subprocess
from pathlib import Path

from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.crawler import Crawler

from leaf_focus.download.middleware.base_spider_middleware import BaseSpiderMiddleware

logger = logging.getLogger(__name__)


class PdfInfoSpiderMiddleware(BaseSpiderMiddleware):
    def __init__(self, executable_path: Path):
        self._executable_path = executable_path

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        # This method is used by Scrapy to create your spiders.
        exec_path = cls._get_path(crawler, "PDF_TO_INFO_FILE")
        return cls(Path(exec_path))

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for item in result:

            # don't process Requests, only process items
            if not isinstance(item, Request):
                adapter = ItemAdapter(item)
                item_file = adapter.get("path")

                # can only process if the item has a path property
                if item_file:
                    pdf_file = Path(item_file).resolve()
                    self._extract_pdf_info(pdf_file)

            yield item

    def _extract_pdf_info(self, pdf_file: Path):
        if not pdf_file or not pdf_file.exists():
            logger.error(f"Could not find pdf file '{pdf_file}'.")

        # always create the info file
        info_file = pdf_file.parent / "response_body_info"
        # if not info_file.exists():
        commands = [str(self._executable_path), str(pdf_file)]
        result = subprocess.run(commands, capture_output=True, check=True)
        if result.returncode != 0:
            logger.error(f"Pdf to info command failed: {repr(result)}")
        else:
            info_file.write_text(data=result.stdout.decode("utf8"), encoding="utf8")
