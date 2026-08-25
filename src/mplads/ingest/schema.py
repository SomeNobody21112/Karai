"""Canonical schema: raw column names, snake_case renames, and target dtypes.

Every entry here is justified in `docs/DATA_CONTRACT.md` section 4. This module holds no
logic — it is the declarative half of ingestion so that the contract and the code cannot
drift apart silently.
"""

from __future__ import annotations

from typing import Final

#: Raw portal/scraper column -> canonical snake_case name.
#:
#: Three raw columns duplicate a scraper-supplied column (DATA_CONTRACT section 4). They are
#: renamed with a `_portal` suffix rather than dropped, so that ingestion stays lossless and
#: the choice of which to trust is made downstream, visibly.
RAW_TO_CANONICAL: Final[dict[str, str]] = {
    # --- scraper context (0% null; comes from the request, not the payload) ---
    "tenure_label": "tenure_label",
    "tenure_id": "tenure_id",
    "house": "house",
    "state_id": "state_id",
    "state_name": "state_name",
    "constituency_id": "constituency_id",
    "constituency_name": "constituency_name",
    "mp_id": "mp_id",
    "mp_name": "mp_name",
    "mp_tenure": "mp_tenure",
    "tile_label": "stage",
    # --- work identity and description ---
    "WORK_RECOMMENDATION_DTL_ID": "work_recommendation_dtl_id",
    # Deliberately NOT called `work_id`: it is 82% null, issued only at completion, and
    # must never be used as a join key. The name is a guard rail.
    "WORK_ID": "portal_work_id",
    "WORK_DESCRIPTION": "work_description",
    "ACTIVITY_NAME": "activity_name",
    "WORK_CATEGORY": "work_category",
    "LETTER_NO": "letter_no",
    "Sno": "sno",
    # --- location and entity ---
    "STATE_NAME": "state_name_portal",
    "CONSTITUENCY": "constituency",
    "CONSTITUENCY_ID": "constituency_id_portal",
    "IDA_NAME": "implementing_agency",
    "MP_NAME": "mp_name_portal",
    # --- dates ---
    "RECOMMENDATION_DATE": "recommendation_date",
    "ACTUAL_END_DATE": "completion_date",
    # --- money ---
    "RECOMMENDED_AMOUNT": "recommended_amount",
    "ACTUAL_AMOUNT": "actual_amount",
    "Total_Amt": "mp_total_amount",
    # --- low-value / flags ---
    "AVERAGE_RATING": "average_rating",
    "FILE_STATUS": "file_status",
    "ATTACH_ID": "attach_id",
    "FLAG": "flag",
}

#: Canonical name -> pandas dtype. Nullable extension types throughout: every one of these
#: columns has real nulls in at least one file, and silently coercing a null to 0 or to NaN
#: would be exactly the kind of quiet corruption this pipeline forbids.
CANONICAL_DTYPES: Final[dict[str, str]] = {
    "tenure_id": "Int64",
    "state_id": "Int64",
    "constituency_id": "Int64",
    "constituency_id_portal": "Int64",
    "mp_id": "Int64",
    "work_recommendation_dtl_id": "Int64",
    "portal_work_id": "Int64",
    "attach_id": "Int64",
    "flag": "Int64",
    "sno": "Int64",
    "recommended_amount": "Float64",
    "actual_amount": "Float64",
    "mp_total_amount": "Float64",
    "average_rating": "Float64",
    "file_status": "boolean",
}

#: Parsed with an explicit format, never by inference. DATA_CONTRACT section 4 records
#: 0 unparseable values in either column under this format across all three files.
DATE_COLUMNS: Final[tuple[str, ...]] = ("recommendation_date", "completion_date")
DATE_FORMAT: Final[str] = "%d-%b-%Y"

#: `tile_label` -> canonical stage code.
STAGE_LABELS: Final[dict[str, str]] = {
    "Works Recommended": "RECOMMENDED",
    "Works Sanctioned": "SANCTIONED",
    "Works Completed": "COMPLETED",
}

#: Columns carrying a work's descriptive attributes, sourced from its recommendation row.
WORK_ATTRIBUTE_COLUMNS: Final[tuple[str, ...]] = (
    "recommendation_date",
    "recommended_amount",
    "work_description",
    "activity_name",
    "work_category",
    "letter_no",
    "state_name",
    "state_name_portal",
    "state_id",
    "constituency",
    "constituency_name",
    "constituency_id",
    "implementing_agency",
    "mp_name",
    "house",
    "tenure_label",
    "flag",
    "attach_id",
)
