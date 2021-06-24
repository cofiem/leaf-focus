from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ResultItem:
    """One row in the report."""

    # These results need to account for a few different data structures:
    # - member or senator
    # - first names
    # - last name
    # - self / spouse / children
    # - entries regarding interestsm need to know:
    #   - which document,
    #   - who is it for,
    #   - what is the content (which can be multiple lines)

    # TODO

    url: str

    entry_name: str
    entry_value: str

    last_updated_web: Optional[datetime] = None
    last_updated_doc: Optional[datetime] = None

    last_name: Optional[str] = None
    first_name1: Optional[str] = None
    first_name2: Optional[str] = None
    first_name3: Optional[str] = None

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
