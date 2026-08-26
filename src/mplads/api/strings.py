"""The English source of every user-facing interface string.

One flat dictionary, translated as a unit and cached per language. Keys are stable; only
values are ever translated. Numbers and case-file content are translated separately at
request time because they change with the data.
"""

from __future__ import annotations

UI: dict[str, str] = {
    # navigation
    "nav.monitor": "Monitor",
    "nav.intelligence": "Intelligence",
    "nav.trust": "Trust",
    "nav.overview": "Overview",
    "nav.worklist": "Investigation Queue",
    "nav.trends": "Temporal",
    "nav.duplicates": "Near-Duplicates",
    "nav.compliance": "Compliance",
    "nav.archetypes": "Work Archetypes",
    "nav.transparency": "Data Transparency",
    "nav.how": "How it works",
    # shell
    "shell.brandSub": "Forensic Monitoring",
    "shell.stakeholder": "Stakeholder view",
    "shell.roleSim": "Role simulation — no authentication in this prototype",
    "shell.viewingAs": "Viewing as",
    "shell.chain": "Learn, Compare, Predict, Explain, Prioritise",
    "shell.leadsNotVerdicts":
        "Investigation leads, not fraud verdicts. A human decides every action.",
    # overview
    "overview.title": "National Overview",
    "overview.worksMonitored": "Works monitored",
    "overview.totalRecommended": "Total recommended",
    "overview.exposure": "Exposure at risk",
    "overview.exposureFoot": "Completion-risk weighted, not loss, not spend",
    "overview.leads": "Investigation leads",
    "overview.byState": "Exposure by state (top 10, crore)",
    "overview.bands": "Confidence bands",
    "overview.archetypes": "Learned work archetypes",
    "overview.completed": "completed",
    "overview.open": "open",
    # worklist
    "worklist.title": "Investigation Queue",
    "worklist.sub": "Ranked by Audit-ROI = priority x exposure x corroboration",
    "worklist.search": "Search description or implementing agency",
    "worklist.allStates": "All states",
    "worklist.allBands": "All bands",
    "worklist.empty": "No leads match these filters.",
    "worklist.work": "Work",
    "worklist.state": "State",
    "worklist.confidence": "Confidence",
    "worklist.amount": "Amount",
    "worklist.auditRoi": "Audit-ROI",
    "worklist.prev": "Previous",
    "worklist.next": "Next",
    "worklist.page": "Page",
    "worklist.of": "of",
    # case file
    "case.title": "Case File",
    "case.back": "Back to queue",
    "case.evidence": "Evidence — why this was surfaced",
    "case.peerContext": "Peer context",
    "case.nextStep": "Recommended next step",
    "case.recommended": "Recommended",
    "case.completionRisk": "Completion risk",
    "case.corroboration": "Corroboration",
    "case.families": "families",
    "case.earlyWarning": "Early warning",
    "case.compliance": "Compliance findings",
    "case.duplicate": "Near-duplicate candidate",
    "case.aiBrief": "AI briefing",
    "case.archetype": "Work type",
    "case.peerLevel": "Peer level",
    "case.peerSize": "Peer group size",
    "case.amountPercentile": "Amount percentile",
    # shared banners
    "banner.hitl":
        "Investigation leads, not fraud verdicts. Every item is ranked by audit "
        "return-on-investment from transparent, corroborated signals. There are no fraud "
        "labels in this data — a human reviews the evidence and decides what happens.",
    "common.loading": "Loading intelligence",
    "common.works": "works",
    "common.leads": "leads",
    "common.language": "Language",
    "common.generating": "Writing briefing",
}
