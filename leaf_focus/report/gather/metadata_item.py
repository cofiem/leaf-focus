from dataclasses import dataclass
from pathlib import Path

from typing import Optional
from urllib.parse import urlparse


@dataclass
class MetadataItem:
    """A report covers the information for one person for one parliment."""

    # house of reps or senate
    category: str

    # the parliament as a number - e.g. 45(th), 46(th)
    parliament_number: str

    # parsed info about person from website or pdf metadata or pdf text
    person_full: str
    person_last: str
    person_first: str
    person_electorate: str
    person_state: str
    person_title: str

    # web dates are parsed from the web page containing the link to the pdf
    date_created_web: Optional[str] = None
    date_updated_web: Optional[str] = None

    # doc dates are obtained from the pdf metadata
    date_created_doc: Optional[str] = None
    date_updated_doc: Optional[str] = None

    # pdf metadata
    pdf_is_tagged: Optional[str] = None
    pdf_form: Optional[str] = None
    pdf_page_count: Optional[str] = None
    pdf_is_encrypted: Optional[str] = None
    pdf_pagesize: Optional[str] = None
    pdf_width: Optional[str] = None
    pdf_height: Optional[str] = None
    pdf_measure: Optional[str] = None
    pdf_format: Optional[str] = None
    pdf_rotation: Optional[str] = None
    pdf_filesize: Optional[str] = None
    pdf_size_amount: Optional[str] = None
    pdf_size_suffix: Optional[str] = None
    pdf_is_optimized: Optional[str] = None
    pdf_version: Optional[str] = None

    # url for pdf
    page_url: Optional[str] = None

    # url for page pdf is linked from
    referrer_url: Optional[str] = None

    def __str__(self) -> str:
        result = []

        display_full = self.display_full
        if display_full:
            result.append(display_full)

        display_url = self.display_url
        if display_url:
            result.append(display_url)

        if not result:
            result.append(self.person_full or self.page_url or "(unknown)")

        return " - ".join(result)

    @property
    def display_full(self):
        display_full = self.person_full.strip("()[] \r\n\f")
        if len(display_full) > 0:
            return self.person_full
        return None

    @property
    def display_url(self):
        if self.page_url:
            pdf_url = urlparse(self.page_url)
            if len(pdf_url.path) > 0:
                return Path(pdf_url.path).name
        return None
