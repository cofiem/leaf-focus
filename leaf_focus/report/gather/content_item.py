import dataclasses
from dataclasses import dataclass
from typing import Optional


@dataclass
class ContentItem:
    """One row in the report."""

    page_number: int
    doc_url: str

    # These results need to account for a few different data structures:
    # - member or senator
    # - first names
    # - last name
    # - self / spouse / children
    # - entries regarding interests, need to know:
    #   - which document,
    #   - who is it for,
    #   - what is the content (which can be multiple lines)

    # text dates are parsed from the pdf text
    date_created_text: Optional[str] = None
    date_updated_text: Optional[str] = None
    date_processed_text: Optional[str] = None

    last_names: Optional[str] = None
    first_names: Optional[str] = None

    electorate: Optional[str] = None
    state: Optional[str] = None

    shareholdings_self: Optional[str] = None
    shareholdings_spouse: Optional[str] = None
    shareholdings_children: Optional[str] = None

    trust_beneficial_self: Optional[str] = None
    trust_beneficial_spouse: Optional[str] = None
    trust_beneficial_children: Optional[str] = None

    trust_trustee_self: Optional[str] = None
    trust_trustee_spouse: Optional[str] = None
    trust_trustee_children: Optional[str] = None

    def has_content(self):
        as_dict = dataclasses.asdict(self)
        as_dict["page_number"] = None
        as_dict["doc_url"] = None
        fields = as_dict.values()
        return any([f is not None for f in fields])
