from enum import unique, Enum


@unique
class LineGroupEnum(Enum):
    UNKNOWN = "unknown"
    ACCOUNTS = "accounts"
    ALTERATION = "alteration"
    DIRECTORSHIPS = "directorships"
    GIFTS = "gifts"
    INVESTMENTS = "investments"
    LIABILITIES = "liabilities"
    METADATA = "metadata"
    METADATA_DATE = "metadata-date"
    METADATA_DATE_RANGE = "metadata-date-range"
    METADATA_ELECTORATE = "metadata-electorate"
    METADATA_FORM = "metadata-form"
    METADATA_NAME = "metadata-name"
    METADATA_NEW_MEMBERS = "metadata-new-members"
    METADATA_NOTES = "metadata-notes"
    METADATA_PAGE = "metadata-page"
    METADATA_PARLIAMENT = "metadata-parliament"
    METADATA_PROCESSED = "metadata-processed"
    METADATA_RETURNING_MEMBERS = "metadata-returning-members"
    METADATA_TITLE = "metadata-title"
    ORGANISATIONS = "organisations"
    OTHER_ASSETS = "other-assets"
    OTHER_INCOME = "other-income"
    OTHER_INTERESTS = "other-interests"
    PARTNERSHIPS = "partnerships"
    REAL_ESTATE = "real-estate"
    SHAREHOLDINGS = "shareholdings"
    TRAVEL_HOSPITALITY = "travel-hospitality"
    TRUSTS_INTERESTS = "trusts-interests"
    TRUSTS_BENEFICIARY = "trusts-beneficiary"
    TRUSTS_TRUSTEE = "trusts-trustee"

    @classmethod
    def get_by_value(cls, value: str):
        for i in cls:
            if i.value == value:
                return i
        raise ValueError(value)
