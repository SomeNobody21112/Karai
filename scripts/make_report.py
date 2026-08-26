"""Generate the plain-English project report as a PDF.

Everything a non-technical reader needs: the problem, the solution, every technical term
explained, and every number traced to a real artifact.

    python scripts/make_report.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fpdf import FPDF

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mplads import config  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "docs" / "MPLADS_Project_Report.pdf"


def load_numbers() -> dict:
    """Read the real artifacts so no figure in the report is typed by hand."""
    art = config.ARTIFACTS
    stats = json.loads((art / "stats.json").read_text(encoding="utf-8"))
    metrics = json.loads((art / "models" / "metrics.json").read_text(encoding="utf-8"))
    temporal = json.loads((art / "temporal.json").read_text(encoding="utf-8"))
    validation = json.loads((art / "validation.json").read_text(encoding="utf-8"))
    n = stats["national"]
    return {
        "works": f"{n['total_works']:,}",
        "completed": f"{n['completed']:,}",
        "open": f"{n['open']:,}",
        "rec_cr": f"{n['total_recommended_rupees'] / 1e7:,.0f}",
        "exp_cr": f"{n['total_exposure_rupees'] / 1e7:,.0f}",
        "leads": f"{n['surfaced_leads']:,}",
        "high": f"{n['bands']['HIGH']:,}",
        "med": f"{n['bands']['MEDIUM']:,}",
        "states": n["states"],
        "consts": n["constituencies"],
        "agencies": f"{n['implementing_agencies']:,}",
        "k": metrics["archetype_clustering"]["k_chosen"],
        "sil": metrics["archetype_clustering"]["silhouette_at_chosen_k"],
        "emb": f"{metrics['archetype_clustering']['n_descriptions_clustered']:,}",
        "cindex": metrics["completion_risk"]["c_index_heldout"],
        "events": f"{metrics['completion_risk']['n_events_total']:,}",
        "censored": f"{metrics['completion_risk']['n_censored_total']:,}",
        "iso": f"{metrics['anomaly_detection']['n_flagged']:,}",
        "dup_total": f"{stats['duplicates']['total_pairs']:,}",
        "dup_conc": f"{stats['duplicates']['concerning_pairs']:,}",
        "dup_ident": f"{stats['duplicates']['identical_text_pairs']:,}",
        "health": stats["health_index"]["score"],
        "ew_med": f"{stats['early_warning']['levels']['MEDIUM']:,}",
        "ew_high": f"{stats['early_warning']['levels']['HIGH']:,}",
        "comp_flag": f"{stats['compliance']['works_with_any_flag']:,}",
        "ag_changed": temporal["counts"]["agencies_changed"],
        "ag_total": temporal["counts"]["agencies_analysed"],
        "val_all": f"{validation['overall']['detected_rate'] * 100:.1f}",
        "val_planted": validation["overall"]["planted_total"],
        "val_stall": f"{validation['per_perturbation']['stalled_lifecycle']['detected_rate'] * 100:.1f}",
        "val_infl": f"{validation['per_perturbation']['inflated_amount']['detected_rate'] * 100:.1f}",
        "val_break": f"{validation['per_perturbation']['lifecycle_break']['detected_rate'] * 100:.1f}",
        "val_clone": f"{validation['per_perturbation']['cloned_description']['detected_rate'] * 100:.1f}",
    }


class Report(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "MPLADS AI Forensic Monitoring - Plain English Report", align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def build(html_sections: list[str]) -> None:
    pdf = Report(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(18, 16, 18)
    pdf.set_title("MPLADS AI Forensic Monitoring - Plain English Report")

    for i, section in enumerate(html_sections):
        pdf.add_page()
        pdf.set_text_color(20, 20, 20)
        pdf.write_html(section, tag_styles={})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"wrote {OUT}  ({OUT.stat().st_size / 1024:.0f} KB, {pdf.page_no()} pages)")


if __name__ == "__main__":
    from report_content import sections  # noqa: E402

    build(sections(load_numbers()))
