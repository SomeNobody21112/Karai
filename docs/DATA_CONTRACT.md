# DATA CONTRACT — MPLADS / eSAKSHI raw stage-wise exports

**Status:** Phase 0, measured 2026-08-25 from `Dataset/raw/`.
**Every number in this document was produced by `scripts/profile_data.py` and the Phase 0
analysis run against the actual files.** Nothing here is copied from the pitch deck, the
FRD, or the previous team's `Dataset/README.md`. Where our measurements disagree with
those documents, the disagreement is recorded explicitly in §11.

Regenerate the underlying profile with:

```bash
python scripts/profile_data.py
```

---

## 1. What our pipeline reads

Three files, and only these three:

| File | Rows | Cols | House |
|---|---:|---:|---|
| `Dataset/raw/esakshi_stagewise_works_ls17_raw.csv` | 242,358 | 31 | 17th Lok Sabha |
| `Dataset/raw/esakshi_stagewise_works_ls18_raw.csv` | 179,415 | 31 | 18th Lok Sabha |
| `Dataset/raw/esakshi_stagewise_works_rs_raw.csv` | 58,995 | 29 | Rajya Sabha |
| **Total raw rows** | **480,768** | | |

All three are comma-delimited, UTF-8, one row per **work-stage** — not per work.

**Not read by the pipeline:**

- `Dataset/raw/vonter_mplads_recommendations_raw.csv` (60,359 × 15, semicolon-delimited).
  Recommendation stage only — no sanction or completion rows — so it cannot support the
  lifecycle join. **However**, it is the only source in the package carrying
  `VILLAGE` (29,881 distinct), `BLOCK` (5,965), `CITY` and `WARD`. See §12.
- `Dataset/raw/original_archives/` — the as-downloaded `.tar.gz` files plus three
  `._works_*.csv` macOS AppleDouble stubs (163–319 bytes, no data).
- Everything under `Dataset/processed/`, `Dataset/features/`, `Dataset/models/`,
  `Dataset/outputs/` — a previous pipeline's derived output. **Reference and
  cross-check only. Never an input.** See §11.

## 2. Grain and the join key

`tile_label` splits every file into three stages:

| `tile_label` | Rows | Distinct works | Duplicate rows per key |
|---|---:|---:|---:|
| `Works Recommended` | 211,784 | 210,298 | 156 |
| `Works Sanctioned` | 181,846 | 180,363 | 154 |
| `Works Completed` | 87,138 | 85,773 | 37 |
| **Total** | **480,768** | | |

### The join key is `(WORK_RECOMMENDATION_DTL_ID, mp_id)` — composite, not `WORK_ID`

Two columns look like a work identifier. Neither works alone:

- **`WORK_ID` is unusable.** It is 100% null on `Works Recommended` and
  `Works Sanctioned` rows and 1.52% null even on `Works Completed` rows — 82.151% null
  overall. It identifies nothing for the 125,220 works that have not completed. Keep it
  for traceability; never join on it.
- **`WORK_RECOMMENDATION_DTL_ID` alone is not unique.** 210,266 distinct values across
  480,768 rows, but 210,993 distinct works. The serial restarts per MP.
- **`(WORK_RECOMMENDATION_DTL_ID, mp_id)` is the key.** Exactly one key value appears in
  more than one house file, so the pair is effectively unique nationally. Our canonical
  `work_ref` is `"MP" + mp_id + "-W" + WORK_RECOMMENDATION_DTL_ID`.

### Row reconciliation — no silent drops

```
480,768   raw stage rows
 -3,987   rows with a null WORK_RECOMMENDATION_DTL_ID  (§3 — these are NOT work rows)
--------
476,781   work-stage rows with a usable key
210,993   distinct works (union of keys across all three stages)
```

### Orphans — stated, as the FRD requires

| Orphan class | Count |
|---|---:|
| Works with **no `Works Recommended` row** at all | **695** |
| `Works Sanctioned` keys with no recommendation row | 687 |
| `Works Completed` keys with no recommendation row | 242 |
| `Works Completed` keys with **no sanction record** | **70** |

Those 695 works have no recommendation date, no recommended amount, no description and
no state — they exist only as a sanction and/or completion record. They are the entire
explanation for the 0.329% null rate on `RECOMMENDED_AMOUNT` at work level. They must be
**carried and flagged**, never silently dropped: an unexplained completion with no
recommendation is itself a lifecycle-conformance lead.

The 70 completed-but-never-sanctioned works are a genuine lifecycle inconsistency and a
conformance signal, not a bug to repair.

## 3. The 3,987 rows with a null join key are MP-level summary rows

The previous team dropped these as rows that "cannot be attached to any work". That is
true but incomplete, and the reason matters.

Measured facts about those 3,987 rows:

- `WORK_RECOMMENDATION_DTL_ID` is null on all 3,987; `mp_id` is present on all 3,987.
- **`Total_Amt` is non-null on all 3,987 — and null on all 476,781 work rows.** The two
  are perfectly complementary.
- They appear as roughly **one row per (MP, stage)**: 557/557/557 in LS17, 552/554/553 in
  LS18, 219/219/219 in RS, across 1,253 distinct MP names.
- Every work-level column (`ACTIVITY_NAME`, `WORK_DESCRIPTION`, amounts, dates, `IDA_NAME`,
  `Sno`, `FLAG`) is null on every one of them.

Example — MP 3018937 (Kuldeep Rai Sharma, Andaman & Nicobar):

| `tile_label` | `Total_Amt` |
|---|---:|
| Works Recommended | 90,108,089 |
| Works Sanctioned | 90,108,089 |
| Works Completed | 9,689,273 |

**These are per-MP, per-stage portfolio totals** — the "MP Allocation & Sanction Limits"
box in the architecture diagram. They are not corrupt.

**How we use them:** as a free, independent **reconciliation oracle**. The sum of our
work-level `RECOMMENDED_AMOUNT` per MP should equal that MP's `Total_Amt` on the
`Works Recommended` row. Any MP where it does not is either a data-quality lead or a bug
in our ingestion. This check costs nothing and is worth more than the rows themselves.

They are **excluded from the work table** (they have no work grain) and **retained in a
separate `mp_totals` table**. `Total_Amt` never enters a work-level feature.

## 4. Column dictionary — one table per file

Every column of every raw file. `dtype` is the **inferred** dtype: the narrowest type
every non-null value actually satisfies, which is what ingestion should cast to — not
what pandas happens to guess. Files are read as `str` so nothing is coerced on the way
in. `null %` and `n_unique` are measured **per file**, so they differ from the pooled
figures quoted elsewhere in this document.

**Trustworthy** = safe to use in a calculation after the stated transformation.

### 4.1 `esakshi_stagewise_works_ls17_raw.csv` - 17th Lok Sabha

242,358 rows x 31 columns.

| Column | dtype | null % | n_unique | Meaning | Trustworthy |
|---|---|---:|---:|---|---|
| `tenure_label` | str | 0.000% | 1 | House and tenure this export was pulled for | yes |
| `tenure_id` | int | 0.000% | 1 | Internal tenure id (5 = LS17, 7 = LS18). Absent from the RS file | yes |
| `house` | str | 0.000% | 1 | `Lok Sabha` / `Rajya Sabha` | yes |
| `state_id` | int | 0.000% | 36 | Portal state id. Range 1-130, not contiguous | yes |
| `state_name` | str | 0.000% | 36 | State/UT. Identical to `STATE_NAME` on 100% of work rows; prefer this one | yes |
| `constituency_id` | int | 0.000% | 541 | Constituency id. Absent from the RS file | yes |
| `constituency_name` | str | 0.000% | 541 | Constituency. Identical to `CONSTITUENCY` where both present. Absent from RS | yes |
| `mp_id` | int | 0.000% | 557 | **MP id - half of the join key** | yes |
| `mp_name` | str | 0.000% | 554 | MP name, clean. Prefer over `MP_NAME` | yes |
| `tile_label` | str | 0.000% | 3 | **The lifecycle stage.** Recommended / Sanctioned / Completed | yes |
| `ACTIVITY_NAME` | str | 0.689% | 91,488 | **Composite, not a name:** `WS/MP<code>/<FY>/<serial>-<official category>`. See §5 | yes, **after parsing** |
| `ACTUAL_AMOUNT` | int | 77.541% | 22,048 | **NOT expenditure** - a completion confirmation echoing the recommended amount. See §6 | **no, for any money question** |
| `ACTUAL_END_DATE` | date | 77.541% | 1,157 | Completion date. **0 unparseable**. 9 values fall after the anchor (to 2044) | yes, after the out-of-window filter |
| `ATTACH_ID` | int | 44.772% | 47,953 | Attachment id. Proves a document exists; **the file itself is login-gated and absent** | only as a boolean `has_attachment` |
| `AVERAGE_RATING` | int | 77.541% | 2 | Only three values exist nationally (0, 1, 5) and the scale differs by file | **no** |
| `CONSTITUENCY` | str | 0.689% | 536 | Constituency. **All RS rows read `Sitting`/`Nominated Rajya Sabha`** - real, but not a place | yes, with the RS caveat |
| `CONSTITUENCY_ID` | int | 0.689% | 536 | Constituency id (545/546 are the two RS pseudo-constituencies) | yes |
| `FILE_STATUS` | bool | 44.772% | 1 | Literally one value, `True`, wherever populated. Zero bits | **no** |
| `FLAG` | int | 0.689% | 3 | Stage code: 1 = live, 3 = completed, 2 = 957 recommendations that never progress. See §7 | yes for 1/3; **UNVERIFIED** for 2 |
| `IDA_NAME` | str | 0.689% | 734 | **Implementing District Authority**, format `District(ROLE_IDA)`. 778 distinct, 775 after stripping the role | yes, normalise the bracket first |
| `LETTER_NO` | str | 0.689% | 37,959 | Recommendation letter ref `LN/MP<code>/<FY>/<n>`. A natural batch grouping | yes |
| `MP_NAME` | str | 0.689% | 538 | MP name **with a tenure suffix on some RS members**. Agrees with `mp_name` on only 87.76% of rows | **no - use `mp_name`/`mp_id`** |
| `RECOMMENDATION_DATE` | date | 23.148% | 640 | Date the MP recommended the work. Format `%d-%b-%Y`, **0 unparseable**. On `Works Sanctioned` rows this is a **verbatim copy**, not a sanction date | yes on Recommended rows; **no** on Sanctioned rows |
| `RECOMMENDED_AMOUNT` | float | 23.148% | 24,922 | **Rupees, the amount the MP recommended.** The only usable money column. Median Rs 315,000 | yes |
| `STATE_NAME` | str | 0.689% | 35 | State/UT. Duplicate of `state_name` | yes (prefer `state_name`) |
| `Sno` | int | 0.689% | 1,478 | Row serial within the portal page; resets per MP | **no - presentation artifact** |
| `Total_Amt` | float | 99.311% | 1,305 | **Per-MP, per-stage portfolio total.** Non-null *only* on the 3,987 MP summary rows | yes at MP grain; **no** at work grain |
| `WORK_CATEGORY` | str | 0.748% | 4 | Four coarse values. Too broad to form a peer group alone | yes, low information |
| `WORK_DESCRIPTION` | str | 0.928% | 83,190 | Free-text description written by the MP's office. Mean 92 chars, max 500. Mixed English/Hindi/Gujarati | yes, as text |
| `WORK_ID` | int | 77.541% | 54,431 | Portal work id, issued **only at completion** | **no - never join on this** |
| `WORK_RECOMMENDATION_DTL_ID` | int | 0.689% | 94,897 | **Per-MP work serial - other half of the join key.** Not unique alone | yes, only as part of the composite key |

### 4.2 `esakshi_stagewise_works_ls18_raw.csv` - 18th Lok Sabha

179,415 rows x 31 columns.

| Column | dtype | null % | n_unique | Meaning | Trustworthy |
|---|---|---:|---:|---|---|
| `tenure_label` | str | 0.000% | 1 | House and tenure this export was pulled for | yes |
| `tenure_id` | int | 0.000% | 1 | Internal tenure id (5 = LS17, 7 = LS18). Absent from the RS file | yes |
| `house` | str | 0.000% | 1 | `Lok Sabha` / `Rajya Sabha` | yes |
| `state_id` | int | 0.000% | 36 | Portal state id. Range 1-130, not contiguous | yes |
| `state_name` | str | 0.000% | 36 | State/UT. Identical to `STATE_NAME` on 100% of work rows; prefer this one | yes |
| `constituency_id` | int | 0.000% | 542 | Constituency id. Absent from the RS file | yes |
| `constituency_name` | str | 0.000% | 542 | Constituency. Identical to `CONSTITUENCY` where both present. Absent from RS | yes |
| `mp_id` | int | 0.000% | 553 | **MP id - half of the join key** | yes |
| `mp_name` | str | 0.000% | 552 | MP name, clean. Prefer over `MP_NAME` | yes |
| `tile_label` | str | 0.000% | 3 | **The lifecycle stage.** Recommended / Sanctioned / Completed | yes |
| `ACTIVITY_NAME` | str | 0.925% | 67,437 | **Composite, not a name:** `WS/MP<code>/<FY>/<serial>-<official category>`. See §5 | yes, **after parsing** |
| `ACTUAL_AMOUNT` | int | 87.853% | 7,798 | **NOT expenditure** - a completion confirmation echoing the recommended amount. See §6 | **no, for any money question** |
| `ACTUAL_END_DATE` | date | 87.853% | 517 | Completion date. **0 unparseable**. 9 values fall after the anchor (to 2044) | yes, after the out-of-window filter |
| `ATTACH_ID` | int | 69.348% | 20,149 | Attachment id. Proves a document exists; **the file itself is login-gated and absent** | only as a boolean `has_attachment` |
| `AVERAGE_RATING` | int | 87.853% | 2 | Only three values exist nationally (0, 1, 5) and the scale differs by file | **no** |
| `CONSTITUENCY` | str | 0.925% | 538 | Constituency. **All RS rows read `Sitting`/`Nominated Rajya Sabha`** - real, but not a place | yes, with the RS caveat |
| `CONSTITUENCY_ID` | int | 0.925% | 538 | Constituency id (545/546 are the two RS pseudo-constituencies) | yes |
| `FILE_STATUS` | bool | 69.348% | 1 | Literally one value, `True`, wherever populated. Zero bits | **no** |
| `FLAG` | int | 0.925% | 3 | Stage code: 1 = live, 3 = completed, 2 = 957 recommendations that never progress. See §7 | yes for 1/3; **UNVERIFIED** for 2 |
| `IDA_NAME` | str | 0.925% | 758 | **Implementing District Authority**, format `District(ROLE_IDA)`. 778 distinct, 775 after stripping the role | yes, normalise the bracket first |
| `LETTER_NO` | str | 0.925% | 39,136 | Recommendation letter ref `LN/MP<code>/<FY>/<n>`. A natural batch grouping | yes |
| `MP_NAME` | str | 0.925% | 538 | MP name **with a tenure suffix on some RS members**. Agrees with `mp_name` on only 87.76% of rows | **no - use `mp_name`/`mp_id`** |
| `RECOMMENDATION_DATE` | date | 13.071% | 672 | Date the MP recommended the work. Format `%d-%b-%Y`, **0 unparseable**. On `Works Sanctioned` rows this is a **verbatim copy**, not a sanction date | yes on Recommended rows; **no** on Sanctioned rows |
| `RECOMMENDED_AMOUNT` | float | 13.071% | 12,413 | **Rupees, the amount the MP recommended.** The only usable money column. Median Rs 315,000 | yes |
| `STATE_NAME` | str | 0.925% | 36 | State/UT. Duplicate of `state_name` | yes (prefer `state_name`) |
| `Sno` | int | 0.925% | 1,455 | Row serial within the portal page; resets per MP | **no - presentation artifact** |
| `Total_Amt` | float | 99.075% | 1,455 | **Per-MP, per-stage portfolio total.** Non-null *only* on the 3,987 MP summary rows | yes at MP grain; **no** at work grain |
| `WORK_CATEGORY` | str | 0.925% | 4 | Four coarse values. Too broad to form a peer group alone | yes, low information |
| `WORK_DESCRIPTION` | str | 1.064% | 81,049 | Free-text description written by the MP's office. Mean 92 chars, max 500. Mixed English/Hindi/Gujarati | yes, as text |
| `WORK_ID` | int | 87.853% | 21,756 | Portal work id, issued **only at completion** | **no - never join on this** |
| `WORK_RECOMMENDATION_DTL_ID` | int | 0.925% | 88,855 | **Per-MP work serial - other half of the join key.** Not unique alone | yes, only as part of the composite key |

### 4.3 `esakshi_stagewise_works_rs_raw.csv` - Rajya Sabha

58,995 rows x 29 columns.

| Column | dtype | null % | n_unique | Meaning | Trustworthy |
|---|---|---:|---:|---|---|
| `tenure_label` | str | 0.000% | 1 | House and tenure this export was pulled for | yes |
| `house` | str | 0.000% | 1 | `Lok Sabha` / `Rajya Sabha` | yes |
| `state_id` | int | 0.000% | 32 | Portal state id. Range 1-130, not contiguous | yes |
| `state_name` | str | 0.000% | 32 | State/UT. Identical to `STATE_NAME` on 100% of work rows; prefer this one | yes |
| `mp_id` | int | 0.000% | 219 | **MP id - half of the join key** | yes |
| `mp_name` | str | 0.000% | 219 | MP name, clean. Prefer over `MP_NAME` | yes |
| `mp_tenure` | str | 0.005% | 13 | RS only. Rajya Sabha term, e.g. `2020-26` | yes |
| `tile_label` | str | 0.000% | 3 | **The lifecycle stage.** Recommended / Sanctioned / Completed | yes |
| `ACTIVITY_NAME` | str | 1.114% | 21,957 | **Composite, not a name:** `WS/MP<code>/<FY>/<serial>-<official category>`. See §5 | yes, **after parsing** |
| `ACTUAL_AMOUNT` | int | 83.751% | 3,735 | **NOT expenditure** - a completion confirmation echoing the recommended amount. See §6 | **no, for any money question** |
| `ACTUAL_END_DATE` | date | 83.751% | 741 | Completion date. **0 unparseable**. 9 values fall after the anchor (to 2044) | yes, after the out-of-window filter |
| `ATTACH_ID` | int | 64.572% | 7,467 | Attachment id. Proves a document exists; **the file itself is login-gated and absent** | only as a boolean `has_attachment` |
| `AVERAGE_RATING` | int | 83.751% | 1 | Only three values exist nationally (0, 1, 5) and the scale differs by file | **no** |
| `CONSTITUENCY` | str | 1.114% | 2 | Constituency. **All RS rows read `Sitting`/`Nominated Rajya Sabha`** - real, but not a place | yes, with the RS caveat |
| `CONSTITUENCY_ID` | int | 1.114% | 2 | Constituency id (545/546 are the two RS pseudo-constituencies) | yes |
| `FILE_STATUS` | bool | 64.572% | 1 | Literally one value, `True`, wherever populated. Zero bits | **no** |
| `FLAG` | int | 1.114% | 3 | Stage code: 1 = live, 3 = completed, 2 = 957 recommendations that never progress. See §7 | yes for 1/3; **UNVERIFIED** for 2 |
| `IDA_NAME` | str | 1.114% | 648 | **Implementing District Authority**, format `District(ROLE_IDA)`. 778 distinct, 775 after stripping the role | yes, normalise the bracket first |
| `LETTER_NO` | str | 1.114% | 14,296 | Recommendation letter ref `LN/MP<code>/<FY>/<n>`. A natural batch grouping | yes |
| `MP_NAME` | str | 1.114% | 198 | MP name **with a tenure suffix on some RS members**. Agrees with `mp_name` on only 87.76% of rows | **no - use `mp_name`/`mp_id`** |
| `RECOMMENDATION_DATE` | date | 17.362% | 915 | Date the MP recommended the work. Format `%d-%b-%Y`, **0 unparseable**. On `Works Sanctioned` rows this is a **verbatim copy**, not a sanction date | yes on Recommended rows; **no** on Sanctioned rows |
| `RECOMMENDED_AMOUNT` | float | 17.362% | 5,251 | **Rupees, the amount the MP recommended.** The only usable money column. Median Rs 315,000 | yes |
| `STATE_NAME` | str | 1.114% | 32 | State/UT. Duplicate of `state_name` | yes (prefer `state_name`) |
| `Sno` | int | 1.114% | 676 | Row serial within the portal page; resets per MP | **no - presentation artifact** |
| `Total_Amt` | float | 98.886% | 544 | **Per-MP, per-stage portfolio total.** Non-null *only* on the 3,987 MP summary rows | yes at MP grain; **no** at work grain |
| `WORK_CATEGORY` | str | 1.144% | 4 | Four coarse values. Too broad to form a peer group alone | yes, low information |
| `WORK_DESCRIPTION` | str | 1.175% | 23,922 | Free-text description written by the MP's office. Mean 92 chars, max 500. Mixed English/Hindi/Gujarati | yes, as text |
| `WORK_ID` | int | 83.751% | 9,586 | Portal work id, issued **only at completion** | **no - never join on this** |
| `WORK_RECOMMENDATION_DTL_ID` | int | 1.114% | 27,044 | **Per-MP work serial - other half of the join key.** Not unique alone | yes, only as part of the composite key |

### 4.4 `vonter_mplads_recommendations_raw.csv` - NOT read by the pipeline

60,359 rows x 15 columns.

| Column | dtype | null % | n_unique | Meaning | Trustworthy |
|---|---|---:|---:|---|---|
| `MP NAME` | str | 0.000% | 633 | MP name. No id column, so joining to eSAKSHI requires fuzzy name matching | unknown |
| `WORK` | str | 0.000% | 20,735 | Work description, prefixed `NA - ` | unknown |
| `CATEGORY` | str | 0.000% | 4 | Same four coarse values as `WORK_CATEGORY` | yes |
| `STATE` | str | 0.000% | 33 | State/UT (33 present vs 36 in eSAKSHI) | yes |
| `CONSTITUENCY` | str | 0.008% | 456 | Constituency. **All RS rows read `Sitting`/`Nominated Rajya Sabha`** - real, but not a place | yes, with the RS caveat |
| `IDA` | str | 0.000% | 699 | Implementing authority, different string format from `IDA_NAME` | unknown |
| `CITY` | str | 77.718% | 2,140 | **Sub-district location - absent from eSAKSHI entirely** | unknown |
| `WARD` | str | 77.960% | 4,669 | **Ward - absent from eSAKSHI entirely** | unknown |
| `BLOCK` | str | 23.475% | 5,965 | **Block - absent from eSAKSHI entirely** | unknown |
| `VILLAGE` | str | 23.468% | 29,881 | **Village - absent from eSAKSHI entirely**, 29,881 distinct | unknown |
| `RECOMMENDED DATE` | date | 0.000% | 280 | Recommendation date, ISO format. Spans only 2023-04-26 to 2024-03-04 | yes |
| `ALLOCATION AMOUNT` | int | 0.000% | 3,391 | Recommended/allocated amount in rupees | unknown - relationship to `RECOMMENDED_AMOUNT` untested |
| `IDA APPROVAL` | str | 0.000% | 3 | `Action Pending` / `Approved by IDA` / **`Rejected by IDA`** - an explicit rejection state eSAKSHI lacks. Possible lead on Q1 | unknown |
| `STATUS` | str | 1.344% | 4 | `Unsanctioned` / `Ongoing` / `Sanctioned` / `Completed` - explicit lifecycle status eSAKSHI lacks | unknown |
| `HOUSE` | str | 0.000% | 2 | `Lok Sabha` / `Rajya Sabha` | yes |

## 5. `ACTIVITY_NAME` contains the official MPLADS works taxonomy — and it was missed

`ACTIVITY_NAME` has 180,707 distinct values, which is why both the pitch deck and the
previous team's `Dataset/README.md` §14 conclude it "cannot form a peer group" and that
work types must therefore be learned by clustering.

**That conclusion does not survive parsing the field.** The format is:

```
WS/MP519/2023-2024/49391-Installation of multi-gym equipment
WS/MP<code>/<financial-year>/<serial>-<official permissible-works category>
```

It is a composite of an identifier and a category. Split on the first `-` after the serial:

| Measure | Value |
|---|---:|
| Rows matching the pattern | **443,258 of 476,781 (92.97%)** |
| Distinct category suffixes | **118** |
| Suffixes used by ≥100 rows | 84, covering **99.8%** of parsed rows |
| Financial years present | 2023-2024, 2024-2025, 2025-2026, 2026-2027 |

The suffixes are the official MPLADS permissible-works list:

| Category | Rows |
|---|---:|
| Construction of roads, link roads, pathways or any other road with or without drainage system | 110,367 |
| Lighting of public spaces | 66,599 |
| Street lights | 44,666 |
| Construction of community centers and community halls | 36,899 |
| Installing tube-wells and borewells | 12,023 |
| Purchase of mobile water tankers | 11,609 |
| Construction of rooms and halls in school and colleges | 10,357 |
| Installing community drinking water plants | 9,943 |
| … 110 more | |

**Consequences for later phases — these are design decisions, not observations:**

1. **Phase 4 peer grouping gains a real, official, interpretable dimension for free.**
   `activity_category` (118 values, 93% coverage) is a defensible peer axis that needs no
   model and cannot be accused of being a black box.
2. **Phase 3 archetypes are no longer load-bearing, and gain an evaluation.** Learned
   archetypes over `WORK_DESCRIPTION` still add resolution *within* a category and cover
   the 7% that do not parse — but they are now a *secondary* signal, exactly as the FRD's
   risk table hoped. More importantly, agreement between our clusters and the 118 official
   categories is a **real cluster-quality metric** (adjusted Rand / mutual information)
   that is defensible in a way silhouette 0.04 is not.
3. **The FY component gives a recommendation financial year** independent of
   `RECOMMENDATION_DATE`, which is a cross-check on the 695 orphans.

The 7.03% of rows that do not match the pattern must be counted and reported, not
discarded.

## 6. `ACTUAL_AMOUNT` is not expenditure — measured

This is FRD hard constraint #4, and here is the evidence rather than the assertion.

Of 85,525 completed works carrying both amounts:

| | Count | Share |
|---|---:|---:|
| `ACTUAL_AMOUNT` **exactly equal** to `RECOMMENDED_AMOUNT` | 84,112 | **98.35%** |
| Differing at all | 1,413 | 1.65% |
| Differing by more than ±0.01% | **1** | 0.001% |
| Ratio above 1.05 (any overrun) | **0** | 0% |

The 1,413 differing works span a ratio of **0.999992 → 1.000011** — parts per million,
i.e. floating-point representation noise. Exactly **one** work in the entire national
portfolio has a materially different value (ratio 0.6798).

`ACTUAL_AMOUNT` is a **completion confirmation that echoes the recommended amount**, not
an independent record of money spent. Therefore:

- No cost-overrun signal is computable. Do not build one.
- No underspend signal is computable. Do not build one.
- `₹ exposure` must be derived from `RECOMMENDED_AMOUNT` × risk, and must be labelled
  **exposure at risk**, never loss, missing money, or spend.

## 7. `FLAG` — an undocumented stage code

| `FLAG` | Recommended | Sanctioned | Completed |
|---|---:|---:|---:|
| `1` | 209,497 | 180,517 | 0 |
| `2` | **957** | 0 | 0 |
| `3` | 0 | 0 | 85,810 |

`FLAG` is redundant with `tile_label` (1 = live, 3 = completed) **except for 957
recommendation rows carrying `FLAG=2`**. Of those 957, only **1** ever reaches a sanction
row and only **1** ever reaches completion. So `FLAG=2` marks a recommendation that
essentially never progresses — plausibly *returned*, *rejected*, or *withdrawn*.

**Marked UNVERIFIED.** The portal does not publish a legend. See §13 Q1. Until confirmed,
we carry `flag` through to the work table and exclude `FLAG=2` works from the
completion-risk fit (they are not censored — they appear to be terminated), but we make no
public claim about what the code means.

## 8. Description quality

- 1,029 works (0.488%) have **no** description — these are exactly the works the previous
  team could not assign to an archetype.
- 187,869 distinct descriptions across 209,964 non-null works.
- 75 descriptions are shared by ≥50 works each, covering 8,597 works. The largest is
  `SOLAR LIGHT` (1,026 works).
- Several high-frequency descriptions are administrative boilerplate that describes a
  *process*, not a work (e.g. "From My MP development fund place the solar lights as par
  attached list by Area manager …", 311 works).
- Mixed scripts: English alongside Hindi and Gujarati in Latin transliteration. Any
  embedding will partly cluster on **script and language**, not work type. The previous
  team measured ~4 of their 50 clusters as pure language artifacts.

A specificity filter (length, boilerplate detection, duplicate-description collapse) is
required before embedding.

## 9. Data-quality issues — measured, with counts

| # | Issue | Count | Handling |
|---|---|---:|---|
| 1 | `WORK_ID` unusable as a key | 82.151% null | Carry for traceability; join on `work_ref` |
| 2 | Works with `RECOMMENDED_AMOUNT` = 0 | **6** | Flag and exclude from money features; keep the row |
| 3 | **Back-dated** works (completion before recommendation) | **1,193** | Flag `is_backdated`; null `delay_days` so they cannot corrupt the survival fit; surface as a conformance lead |
| 4 | **Out-of-window** completion dates (after the 2026-05-26 anchor) | **9** | Dates: 2026-06-02, 2026-09-15, 2027-06-28, 2028-11-09, 2034-01-01, 2034-02-24, 2034-07-29, 2044-05-28, 2044-10-20. Flag and exclude from duration maths. **These are why the censoring anchor must be `max(RECOMMENDATION_DATE)`, never `max(all dates)`** — anchoring on 2044 would inflate every open work's duration by ~18 years |
| 5 | Works with **no recommendation row** (orphans) | **695** | Carry, flag, exclude from recommendation-time features |
| 6 | Completed with **no sanction record** | **70** | Carry; conformance signal |
| 7 | `FLAG=2` recommendations that never progress | **957** | Carry; UNVERIFIED meaning (§7, Q1) |
| 8 | Duplicate rows per key within a stage | 156 / 154 / 37 | Deterministic dedup: sort by `RECOMMENDATION_DATE` then key, `keep="first"`. **Must be tie-broken on a stable secondary sort** — see §11.2 |
| 9 | `ACTUAL_AMOUNT` carries no expenditure variance | 98.35% identical | §6 — no overrun/underspend signal exists |
| 10 | No district field | — | Never claim district-level results |
| 11 | RS constituency is `Sitting Rajya Sabha` for 58,995 rows | — | Peer/travel grouping must key on **state + constituency**, never constituency alone |

## 10. Derived quantities established in Phase 0

| Quantity | Value | How |
|---|---|---|
| **Censoring anchor** (`SNAPSHOT_DATE` candidate) | **2026-05-26** | `max(RECOMMENDATION_DATE)` over all parseable values. Confirmed in Phase 2 |
| Distinct works | **210,993** | Union of keys across the three stages |
| Works after dropping ≤0 amounts | **210,987** | 210,993 − 6 |
| Sanctioned works | 180,363 | |
| Completed works | 85,773 | |
| Completed with both dates | 85,531 | |
| Open (not completed) works | 125,220 | 210,993 − 85,773 |
| Naive median delay, completed works | **401 days** | Completed, both dates, excluding back-dated and out-of-window (n = 84,329). Mean 440, p90 808, max 2,236. **This describes survivors only — it is the survivorship bias the project exists to correct** |
| Distinct MPs | 1,076 | on recommendation rows |
| States/UTs | 36 | |
| Constituencies | 545 | includes the 2 RS pseudo-constituencies |
| Implementing authorities | 778 | 775 after normalising the bracketed role |

## 11. Where we disagree with the supplied documents

`Dataset/` ships a previous pipeline's outputs and a detailed `README.md`, but **not its
source code**. We therefore treat it as an independent oracle to check our numbers
against, not as a source to copy. Most numbers agree exactly, which is strong mutual
validation. These do not.

### 11.1 The works count — the FRD flagged this, and both figures are right

| Source | Claim |
|---|---|
| Pitch deck slide 2 | 210,993 works |
| `Dataset/README.md` | 210,987 works |
| FRD | "208k" |

**Resolved.** 210,993 is the number of distinct works in the raw data. 210,987 is that
number after dropping the 6 works with `RECOMMENDED_AMOUNT ≤ 0`. They differ by exactly 6
and both are defensible with a stated definition. **The FRD's "208k" matches nothing and
should be corrected.** Likewise the deck's "85,531 full lifecycles" is the count of
completed works with both dates; 85,525 is the count with both amounts; 85,773 is the
count with a completion row. Every published figure must state which.

### 11.2 `ACTUAL_AMOUNT` ratio range — their phrasing overstates the spread

`Dataset/README.md` §11.5 says the differing works "span a ratio of 0.6798 → 1.00001".
Literally true, but it reads as a distribution when it is **one outlier plus rounding
noise**: 1,413 of the 1,414 differing works fall in 0.999992–1.000011. We state it as
§6 instead. Their conclusion (no usable expenditure signal) is correct and, framed this
way, stronger.

### 11.3 Their "0.329% of recommendation dates fail to parse" is a mislabel

**0 of 390,971** present `RECOMMENDATION_DATE` values fail to parse under `%d-%b-%Y`. The
0.329% is the share of *works* with no recommendation row at all — the 695 orphans of §2.
Absence, not malformation. The distinction matters: a parse failure is a bug to fix, an
orphan is a signal to surface.

### 11.4 Our dedup differs from theirs by one work

We measure 84,112 equal / 1,413 differing; they report 84,111 / 1,414. The gap is a single
work whose duplicate recommendation rows tie on `RECOMMENDATION_DATE`, so `keep="first"`
resolves differently under a different input row order. **Our dedup must therefore sort on
`(RECOMMENDATION_DATE, work_ref, source_file, raw_row_index)`** so the result is
independent of file concatenation order. Recorded as an ingestion requirement for Phase 1.

### 11.5 Their back-dated count

They report 1,191; we measure **1,193** on the raw data before dropping the 6 non-positive
amount works. Consistent given the different population.

## 12. Deliberately unused, and why

| Asset | Why not used in the MVP |
|---|---|
| `Dataset/raw/vonter_mplads_recommendations_raw.csv` | Recommendation stage only; cannot support the lifecycle join. **Worth revisiting**: it is the only source with `VILLAGE` (29,881), `BLOCK` (5,965), `CITY`, `WARD` — sub-district location the eSAKSHI export lacks entirely. A name-and-amount match against our works could recover approximate location for a subset. Out of MVP scope; record as a future module |
| `Dataset/models/archetype/desc_embeddings.npz` | 187,865 × 384 MiniLM vectors, ~45 min of CPU to regenerate. **Phase 3 may reuse this as a cache** if and only if the description set it was built from matches ours exactly (verified by hash). Otherwise recompute. It is a cache, never a result |
| `Dataset/outputs/*` | A previous pipeline's conclusions. We cannot regenerate them (no source code shipped), so publishing them would violate Definition of Done #2 and #7. Used only to sanity-check our own |
| `Dataset/synthetic/` | 406 synthetic works + ground truth + 40 generated photos. **Not real data.** May inform the Phase 10 synthetic-injection harness; must never mix with the real portfolio |

## 13. UNVERIFIED — questions we need answered

These are the marks that must be removed before the contract is final. Everything else in
this document is measured.

**Q1. What does `FLAG = 2` mean?** 957 recommendation rows carry it and effectively none
progress to sanction or completion. If it means *rejected/returned/withdrawn*, those works
are **terminated, not censored**, and including them in the survival fit as censored
observations would bias completion risk downward. Currently excluded from the fit and
carried with no public interpretation. *(Needs: portal documentation, or an MoSPI answer.)*

> **Lead, found while profiling.** The unused Vonter file carries an `IDA APPROVAL` column
> with values `Action Pending` / `Approved by IDA` / **`Rejected by IDA`**, and a `STATUS`
> column with `Unsanctioned` / `Ongoing` / `Sanctioned` / `Completed`. eSAKSHI exposes
> neither. If Vonter rows can be matched to our works — it covers only 2023-04-26 to
> 2024-03-04 and has no `mp_id`, so matching is fuzzy — the overlap between
> `Rejected by IDA` and `FLAG = 2` would answer Q1 empirically without waiting on MoSPI.
> Worth one Phase 1 experiment; not a blocker.

**Q2. Is `RECOMMENDED_AMOUNT` in rupees, and is it the amount recommended or the amount
sanctioned?** Median ₹315,000 and max ₹75.7M are consistent with rupees under the ₹5 crore
per-MP annual entitlement. We assume **rupees, as recommended by the MP**. Every ₹ figure
we publish depends on this. *(Needs: confirmation against a published MPLADS statement.)*

**Q3. Does `Total_Amt` on the MP summary rows mean cumulative allocation, or the sum of
that MP's works at that stage?** Our reconciliation check in §3 will answer this
empirically — if it matches the per-MP sum of `RECOMMENDED_AMOUNT`, it is the latter.
Phase 1 must run that check and record the result here.

**Q4. Are the 9 out-of-window completion dates typos or genuine future targets?** We treat
them as data errors and exclude them from duration maths, which is the conservative
choice. *(Needs: no action if the count stays at 9; revisit if a refreshed extract grows it.)*

**Q5. `AVERAGE_RATING` takes only the values {0, 1, 5} and differs by file.** We assume it
is an abandoned or partially-rolled-out feature and place it on the DO-NOT-USE list. *(Needs:
confirmation, or it stays unused — low stakes either way.)*

## 14. DO NOT USE list

Enforced by `tests/test_data_contract.py`. Using any of these in a calculation is a bug.

| Column | Reason |
|---|---|
| `ACTUAL_AMOUNT` | Not expenditure (§6). No money question may read it |
| `WORK_ID` | 82% null; never a join key (§2) |
| `AVERAGE_RATING` | Three values nationally, inconsistent between files (§4) |
| `FILE_STATUS` | Single-valued (§4) |
| `Sno` | Page row number (§4) |
| `MP_NAME` | Tenure suffix contamination; use `mp_name` / `mp_id` (§4) |
| `Total_Amt` at work grain | MP-level only; null on every work row (§3) |
| Sanction **timing** | Does not exist in any source (§4) |
| `RECOMMENDATION_DATE` on `Works Sanctioned` rows | A copy of the recommendation date, not a sanction date (§4) |
