from dataclasses import dataclass

from typing import Optional


@dataclass
class ReportItem:
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

    # text dates are parsed from the pdf text
    date_created_text: Optional[str] = None
    date_updated_text: Optional[str] = None

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
