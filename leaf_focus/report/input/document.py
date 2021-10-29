from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional, Iterable

from leaf_focus.download.crawl.item import Item as CrawlItem
from leaf_focus.pdf.identify.item import Item as PdfIdentifyItem
from leaf_focus.pdf.info.item import Item as PdfInfoItem
from leaf_focus.report.output.item import Item as ReportItem
from leaf_focus.report.input.dates import Dates
from leaf_focus.report.input.page import Page
from leaf_focus.report.input.text import Text


@dataclass
class Document:
    pdf_path: Path
    pdf_hash_type: str
    pdf_hash_value: str

    pdf_created_date: Optional[date]
    pdf_modified_date: Optional[date]
    pdf_downloaded_date: date
    website_modified_date: Optional[date]

    pdf_url: str
    referrer_url: Optional[str]

    pages: list[Page] = field(default_factory=list)
    """The pages in this document."""

    def parse(self) -> Iterable[ReportItem]:
        # TODO: parse documents into report items
        doc = ReportItem(
            pdf_path=self.pdf_path,
            pdf_hash_type=self.pdf_hash_type,
            pdf_hash_value=self.pdf_hash_value,
            pdf_created_date=self.pdf_created_date,
            pdf_modified_date=self.pdf_modified_date,
            pdf_downloaded_date=self.pdf_downloaded_date,
            website_modified_date=self.website_modified_date,
            pdf_url=self.pdf_url,
            referrer_url=self.referrer_url,
            pdf_source=None,
            processed_date=None,
            signed_date=None,
            assembly=None,
            last_name=None,
            first_name=None,
            state_or_territory=None,
            electorate=None,
            register_section=None,
            change_type=None,
            form_who=None,
        )
        yield doc

    @classmethod
    def load(cls, processing_dir: Path, feed_dir: Path) -> Iterable["Document"]:
        """Load documents from a directory."""

        dates = Dates()
        text = Text()

        items = {}

        for csv_path in feed_dir.rglob("*.csv"):
            for pdf_feed in CrawlItem.load(csv_path):
                # feed
                pdf_fee_path = pdf_feed.path
                if pdf_fee_path not in items:
                    items[pdf_fee_path] = {}
                items[pdf_fee_path]["feed"] = pdf_feed

        for json_path in processing_dir.rglob("pdf-identify.json"):
            # identify
            pdf_identify = PdfIdentifyItem.read(json_path)
            pdf_identify_path = str(pdf_identify.pdf_file)
            if pdf_identify_path not in items:
                items[pdf_identify_path] = {}
            items[pdf_identify_path]["identify"] = pdf_identify
            items[pdf_identify_path]["processing"] = json_path.parent

            # info
            info_path = json_path.with_name("pdf-info.json")
            if not info_path.exists():
                continue
            pdf_info = PdfInfoItem.load_json(info_path)
            pdf_info_path = str(pdf_info.pdf_path)
            if pdf_info_path not in items:
                items[pdf_info_path] = {}
            items[pdf_info_path]["info"] = pdf_info

        for pdf_file, item in items.items():
            pdf_path = Path(pdf_file)
            pdf_feed = item.get("feed")  # type: CrawlItem
            pdf_identify = item.get("identify")  # type: PdfIdentifyItem
            pdf_info = item.get("info")  # type: PdfInfoItem
            pdf_processing = item.get("processing")  # type: Path

            if pdf_info and pdf_info.entries:
                pdf_created_date = text.norm_text(pdf_info.entries.get("CreationDate"))
                pdf_modified_date = text.norm_text(pdf_info.entries.get("ModDate"))
            else:
                pdf_created_date = None
                pdf_modified_date = None

            if pdf_feed:
                website_modified_date = text.norm_text(pdf_feed.last_updated)
                pdf_url = pdf_feed.url
                referrer_url = pdf_feed.referrer
            else:
                website_modified_date = None
                pdf_url = None
                referrer_url = None

            doc = Document(
                pdf_path=pdf_path,
                pdf_hash_type=pdf_identify.hash_type,
                pdf_hash_value=pdf_identify.file_hash,
                pdf_created_date=dates.parse(pdf_created_date),
                pdf_modified_date=dates.parse(pdf_modified_date),
                pdf_downloaded_date=dates.downloaded(pdf_path),
                website_modified_date=dates.parse(website_modified_date),
                pdf_url=pdf_url,
                referrer_url=referrer_url,
            )
            pages = Page.load(pdf_processing, doc)
            doc.pages = pages
            yield doc
