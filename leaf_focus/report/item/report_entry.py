import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional, Iterable


@dataclass
class ReportEntry:
    """An entry in a report."""

    pdf_path: Path
    """The path on disk to the pdf file."""

    pdf_hash_type: str
    """The hash algorithm used to generate the pdf file hash value."""

    pdf_hash_value: str
    """The pdf file hash digest."""

    pdf_page: str
    """The page number in the pdf file."""

    pdf_line: str
    """The line number in the pdf page."""

    pdf_created_date: Optional[date]
    """The created date from the pdf file metadata."""

    pdf_modified_date: Optional[date]
    """The modified date from the pdf file metadata."""

    pdf_downloaded_date: date
    """The date the pdf file was downloaded."""

    pdf_url: str
    """The absolute url for the pdf file."""

    referrer_url: Optional[str]
    """The referrer url that lead to the pdf url."""

    website_modified_date: Optional[date]
    """The last updated date parsed from the website."""

    processed_date: Optional[date]
    """The processed date from the pdf file."""

    signed_date: Optional[date]
    """The signed date from the pdf file."""

    assembly: str
    """
    The involvement the person has:
    'member' (house of reps) or 'senator' (senate).
    """

    last_name: str
    """The person's last name."""

    first_name: str
    """The person's first name."""

    state_or_territory: str
    """The Australian state or territory the person is representing."""

    electorate: Optional[str]
    """Name of person's electorate for house of representatives."""

    register_section: str
    """The title of the section in the register of member's interests form."""

    change_type: str
    """The type of change to the register: addition or deletion."""

    # --- form table headings ---

    form_who: str
    """
    The person or people relevant to the entry for all sections:
    'self', 'partner', 'dependent'.
    """

    form_name: Optional[str] = None
    """
    Name of the thing.
    Name for section
    1. Shareholdings - company;
    2. i. trust beneficial interest - trust/nominee;
    2. ii. trustee and beneficial interest - trust/nominee;
    4. Directorships of companies - company;
    5. Partnerships - partnership;
    6. Liabilities - creditor;
    7. bonds and other investments - body in which investment is held;
    8. Saving or investment accounts - name of bank/institution;
    13. Organisation membership - name of organisation;
    """

    form_activity: Optional[str] = None
    """
    What does the thing do.
    Nature / activities of trust / company for section
    2. i. trust beneficial interest - trust operation;
    2. ii. trustee and beneficial interest - trust operation;
    4. Directorships of companies - company;
    5. Partnerships - partnership;
    """

    form_participation: Optional[str] = None
    """
    What is your interest / participation / involvement in the thing.
    Beneficial interest / nature of participation for section
    2. i. trust beneficial interest - Beneficial interest;
    2. ii. trustee and beneficial interest - Beneficial interest;
    3. Real estate - Purpose for which owned;
    5. Partnerships - nature of interest;
    6. Liabilities - nature of liability;
    7. bonds and other investments - type of investment;
    8. Saving or investment accounts - nature of account;
    9. other assets - nature of any other assets;
    10. Other income - nature of income;
    11. Gifts - details of gifts;
    12. travel and hospitality - details of travel/hospitality;
    14. Other interests - nature of interest;
    """

    form_location: Optional[str] = None
    """
    Where is the thing physically located.
    Real estate location for section
    3. Real estate;
    """

    @property
    def is_valid(self):
        return all(
            [
                self.pdf_url,
                self.assembly,
                self.last_name,
                self.state_or_territory,
                self.register_section,
                self.change_type,
                any(
                    [
                        self.form_location,
                        self.form_who,
                        self.form_name,
                        self.form_activity,
                        self.form_participation,
                    ]
                ),
            ]
        )

    @property
    def short_hash(self):
        return self.pdf_hash_value[0:15]

    @classmethod
    def save(cls, path: Path, items: Iterable["ReportEntry"]):
        """Save items to a csv file."""
        fields = [
            "assembly",
            "state_or_territory",
            "electorate",
            "last_name",
            "first_name",
            "register_section",
            "change_type",
            "form_who",
            "form_name",
            "form_activity",
            "form_participation",
            "form_location",
            "pdf_created_date",
            "pdf_modified_date",
            "pdf_downloaded_date",
            "website_modified_date",
            "processed_date",
            "signed_date",
            "pdf_page",
            "pdf_line",
            "pdf_url",
            "referrer_url",
            "pdf_hash_type",
            "pdf_hash_value",
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wt", newline="", encoding="utf8") as f:
            writer = csv.DictWriter(f, fields, dialect="excel")
            writer.writeheader()
            for i in items:
                writer.writerow(
                    {
                        "pdf_hash_type": i.pdf_hash_type,
                        "pdf_hash_value": i.pdf_hash_value,
                        "pdf_page": i.pdf_page,
                        "pdf_line": i.pdf_line,
                        "pdf_created_date": cls.fmt_date(i.pdf_created_date),
                        "pdf_modified_date": cls.fmt_date(i.pdf_modified_date),
                        "pdf_downloaded_date": cls.fmt_date(i.pdf_downloaded_date),
                        "pdf_url": i.pdf_url,
                        "referrer_url": i.referrer_url,
                        "website_modified_date": cls.fmt_date(i.website_modified_date),
                        "processed_date": cls.fmt_date(i.processed_date),
                        "signed_date": cls.fmt_date(i.signed_date),
                        "assembly": i.assembly,
                        "last_name": i.last_name,
                        "first_name": i.first_name,
                        "state_or_territory": i.state_or_territory,
                        "electorate": i.electorate,
                        "register_section": i.register_section,
                        "change_type": i.change_type,
                        "form_who": i.form_who,
                        "form_name": i.form_name,
                        "form_activity": i.form_activity,
                        "form_participation": i.form_participation,
                        "form_location": i.form_location,
                    }
                )

    @classmethod
    def fmt_date(cls, value: date) -> str:
        if not value:
            return ""
        return value.isoformat()

    def __str__(self):
        items = [
            ("doc", self.short_hash),
            ("page", self.pdf_page),
            ("line", self.pdf_line),
            ("person", self.last_name),
            ("group", self.register_section),
            ("location", self.form_location),
            ("who", self.form_who),
            ("name", self.form_name),
            ("activity", self.form_activity),
            ("participation", self.form_participation),
        ]
        return "; ".join(f"{k}={v}" for k, v in items if v)
