"""Data availability, provenance and confidence — the honesty layer.

Every metric the platform shows declares where it came from, whether it is measured or
derived, and how much confidence it deserves. Fields the public dataset does not contain
are listed explicitly as UNAVAILABLE with the reason, rather than quietly substituted.

The ingestion interfaces for the unavailable fields exist in `FUTURE_FIELDS`: if a MoSPI
data grant supplies them, they slot into the same schema without restructuring.
"""

from __future__ import annotations

import pandas as pd

DIRECT = "Direct measurement"
DERIVED = "Model-derived"
UNAVAILABLE = "Unavailable"

#: metric -> provenance record.
METRICS: list[dict] = [
    {
        "metric": "Works monitored",
        "source": "eSAKSHI stage-wise exports (LS17, LS18, RS)",
        "type": DIRECT,
        "confidence": "High",
        "note": "Counted from the raw records; reconciled against the portal's own per-MP totals.",
    },
    {
        "metric": "Recommended amount",
        "source": "RECOMMENDED_AMOUNT",
        "type": DIRECT,
        "confidence": "High",
        "note": "The only trustworthy money column. It is what was recommended, not what was spent.",
    },
    {
        "metric": "Completion status",
        "source": "Works Completed lifecycle stage",
        "type": DIRECT,
        "confidence": "High",
        "note": "Presence of a completion record, with its date.",
    },
    {
        "metric": "Work archetype",
        "source": "MiniLM embeddings + our MiniBatchKMeans",
        "type": DERIVED,
        "confidence": "Medium",
        "note": "Unsupervised grouping. Cluster separation (silhouette) is ~0.05 — a "
                "separation measure, never accuracy.",
    },
    {
        "metric": "Peer comparison percentile",
        "source": "Hierarchical peer groups (category x state)",
        "type": DERIVED,
        "confidence": "High",
        "note": "Leave-one-out ranking within genuinely comparable works.",
    },
    {
        "metric": "Completion risk",
        "source": "Cox proportional-hazards survival model",
        "type": DERIVED,
        "confidence": "Medium",
        "note": "Held-out concordance 0.676. Ranks which works finish sooner; it is not a "
                "probability of wrongdoing.",
    },
    {
        "metric": "Early-warning level",
        "source": "Survival model + peer stall ratio",
        "type": DERIVED,
        "confidence": "Medium",
        "note": "A risk score with an explanation, not a validated failure prediction.",
    },
    {
        "metric": "Near-duplicate candidates",
        "source": "384-d embedding similarity within state x archetype blocks",
        "type": DERIVED,
        "confidence": "Medium",
        "note": "Repeated descriptions are common and often legitimate in this scheme. A "
                "match is a question for a human, not proof of a duplicate claim.",
    },
    {
        "metric": "₹ exposure at risk",
        "source": "Recommended amount x completion risk",
        "type": DERIVED,
        "confidence": "Medium",
        "note": "Money that could be tied up in works that may not finish. NOT loss, NOT "
                "missing money, NOT spend.",
    },
    {
        "metric": "Verified actual expenditure",
        "source": "ACTUAL_AMOUNT",
        "type": UNAVAILABLE,
        "confidence": "None",
        "note": "98.35% of completed works have it exactly equal to the recommended amount, "
                "and all but one of the rest differ by parts per million. It is a completion "
                "confirmation, not an independent record of money spent.",
    },
    {
        "metric": "Payment tranches / releases",
        "source": "—",
        "type": UNAVAILABLE,
        "confidence": "None",
        "note": "No payment, release or utilisation-certificate field exists in any public "
                "MPLADS source.",
    },
    {
        "metric": "Cost estimate",
        "source": "—",
        "type": UNAVAILABLE,
        "confidence": "None",
        "note": "No estimate column exists, so a true estimate-versus-actual cost overrun "
                "cannot be computed. We report relative recommendation anomalies instead.",
    },
    {
        "metric": "Physical progress %",
        "source": "—",
        "type": UNAVAILABLE,
        "confidence": "None",
        "note": "The portal publishes administrative stages only. We report administrative "
                "lifecycle progress, never physical construction progress.",
    },
    {
        "metric": "Sanction date",
        "source": "—",
        "type": UNAVAILABLE,
        "confidence": "None",
        "note": "Sanction rows carry a verbatim copy of the recommendation date on 100.00% "
                "of 179,676 works. Sanction presence is testable; its timing is unknowable.",
    },
    {
        "metric": "Photographic / geotagged evidence",
        "source": "ATTACH_ID",
        "type": UNAVAILABLE,
        "confidence": "None",
        "note": "Attachment IDs prove documents exist, but the files are login-gated and not "
                "downloadable. No computer-vision verification is claimed.",
    },
    {
        "metric": "District",
        "source": "—",
        "type": UNAVAILABLE,
        "confidence": "None",
        "note": "No district column exists. IDA_NAME is a district administration office and "
                "CONSTITUENCY is a constituency; district-level claims would be invented.",
    },
]

#: Optional ingestion interfaces. Present, typed, and null until a data grant fills them.
FUTURE_FIELDS: list[dict] = [
    {"field": "actual_expenditure", "dtype": "float", "unlocks": "True fund-utilisation analysis"},
    {"field": "payment_tranches", "dtype": "list[record]", "unlocks": "Payment-pattern anomalies"},
    {"field": "cost_estimate", "dtype": "float", "unlocks": "Genuine cost-overrun detection"},
    {"field": "physical_progress_pct", "dtype": "float", "unlocks": "Real progress monitoring"},
    {"field": "sanction_date", "dtype": "date", "unlocks": "Lifecycle timing conformance"},
    {"field": "vendor_id", "dtype": "string", "unlocks": "Repeat-winner / collusion analysis"},
    {"field": "geo_lat, geo_lon", "dtype": "float", "unlocks": "Geospatial hotspots, site clustering"},
    {"field": "evidence_photos", "dtype": "list[uri]", "unlocks": "Perceptual-hash photo reuse checks"},
]


def build(works: pd.DataFrame) -> dict:
    """Provenance registry plus measured completeness for the fields we do have."""
    total = len(works)

    def completeness(column: str) -> float:
        if column not in works.columns:
            return 0.0
        return round(100 * float(works[column].notna().mean()), 2)

    return {
        "metrics": METRICS,
        "future_fields": FUTURE_FIELDS,
        "completeness": [
            {"field": "work_description", "present_pct": completeness("work_description")},
            {"field": "recommendation_date", "present_pct": completeness("recommendation_date")},
            {"field": "recommended_amount", "present_pct": completeness("recommended_amount")},
            {"field": "state_name", "present_pct": completeness("state_name")},
            {"field": "implementing_agency", "present_pct": completeness("implementing_agency")},
            {"field": "archetype_id", "present_pct": completeness("archetype_id")},
            {"field": "activity_category", "present_pct": completeness("activity_category")},
        ],
        "totals": {
            "works": total,
            "available_metrics": sum(1 for m in METRICS if m["type"] == DIRECT),
            "derived_metrics": sum(1 for m in METRICS if m["type"] == DERIVED),
            "unavailable_metrics": sum(1 for m in METRICS if m["type"] == UNAVAILABLE),
        },
        "statement": (
            "This platform does not fabricate government data it does not have. Where a "
            "field is unavailable it is listed as unavailable, with the measurement that "
            "proves it and the analysis we substitute instead."
        ),
    }
