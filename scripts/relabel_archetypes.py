"""Regenerate archetype labels from the saved cluster assignment.

Re-runs only the c-TF-IDF labelling step, so it costs seconds rather than re-clustering.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mplads import config
from mplads.intelligence.labels import build_label

MODELS = config.ARTIFACTS / "models"
assign = pd.read_parquet(MODELS / "archetype_assignment.parquet")

docs = assign.groupby("archetype_id")["work_description"].apply(
    lambda s: " ".join(s.astype(str).head(2000))
)
vec = TfidfVectorizer(max_features=6000, stop_words="english", ngram_range=(1, 2), min_df=3)
matrix = vec.fit_transform(docs.values)
terms = np.array(vec.get_feature_names_out())

rows = []
sizes = assign["archetype_id"].value_counts()
for i, aid in enumerate(docs.index):
    ranked = terms[matrix[i].toarray().ravel().argsort()[::-1][:12]].tolist()
    label, interpretable, note = build_label(ranked)
    rows.append({
        "archetype_id": int(aid),
        "label": label,
        "interpretable": bool(interpretable),
        "note": note,
        "top_terms": ", ".join(ranked[:8]),
        "n_descriptions": int(sizes.get(aid, 0)),
    })

catalog = pd.DataFrame(rows).sort_values("n_descriptions", ascending=False)
catalog.to_parquet(MODELS / "archetype_catalog.parquet", index=False)

n_bad = int((~catalog["interpretable"]).sum())
print(f"relabelled {len(catalog)} archetypes; {n_bad} marked uninterpretable\n")
print(catalog.head(15)[["archetype_id", "label", "n_descriptions"]].to_string(index=False))
