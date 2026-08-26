"""Human-readable archetype labels from cluster contents — or an honest 'uninterpretable'.

Two problems make a naive top-c-TF-IDF label unreadable:

1. **Transliterated function words.** MPLADS descriptions mix English with Hindi, Gujarati
   and other languages written in Latin script. Terms like `ke`, `ki`, `nu`, `mein`, `tak`
   are grammatical glue, not work types, and they dominate some clusters. A label reading
   "lai / ke / lai ki" tells a reader nothing.
2. **Nested n-grams.** "hall / community hall / community" is one idea printed three times.

So: strip the glue, collapse nested phrases, and — where what remains is not a work type —
say so. A cluster we cannot interpret is labelled `Mixed / uninterpretable`, never given an
invented name. That honesty is a product requirement, not a style choice.
"""

from __future__ import annotations

import re

#: Transliterated function words and administrative filler. These are grammatical or
#: generic, never a kind of work. Kept deliberately narrow: `gram panchayat`, `anganwadi`
#: and similar are real nouns and must NOT be listed here.
GLUE = {
    # Hindi / Marathi / Bhojpuri particles and pronouns
    "ke", "ki", "ka", "ko", "se", "me", "mein", "par", "aur", "hai", "tak", "ke liye",
    "liye", "wale", "wali", "vala", "vali", "yah", "vah", "is", "us", "jo", "ho", "kar",
    "karne", "hetu", "evam", "tatha", "sthit", "lai", "lai ki", "che", "chi", "cha",
    "ek", "do", "pas", "pass", "wala", "tha", "ki sthapana", "ke pas", "pas ek",
    # Gujarati particles
    "nu", "ni", "no", "na", "game", "thi", "mate", "ane",
    # English filler that carries no work meaning
    "work", "works", "new", "old", "various", "etc", "no", "nos", "shri", "smt",
    "district", "block", "area", "place", "side", "front", "back", "upto",
    "from", "to", "at", "in", "of", "the", "and", "for", "with", "const", "ward",
    "near", "house",
}

#: Common Hindi/Gujarati work nouns, glossed to English. This is translation of terms the
#: cluster actually contains — not invention. Multi-word keys are matched first.
GLOSS = {
    "nirman": "construction",
    "ka nirman": "construction",
    "sthapana": "installation",
    "ki sthapana": "installation",
    "marg": "road",
    "sadak": "road",
    "rasta": "road",
    "ghar": "house",
    "ke ghar": "house",
    "makan": "house",
    "ke makan": "house",
    "bhavan": "building",
    "mandir": "temple",
    "vidyalaya": "school",
    "shauchalaya": "toilet",
    "samudayik": "community",
    "chabutaro": "bird feeder",
    "smashan": "crematorium",
    "kabristan": "graveyard",
    "talab": "pond",
    "naali": "drain",
    "nali": "drain",
    "pulia": "culvert",
    "boring": "borewell",
    "prakash": "lighting",
    "vyayamshala": "gym",
    "mandap": "hall",
    "kalyan mandap": "community hall",
    "rungmanch": "stage",
    "manch": "stage",
}

#: A cluster whose distinctive terms are mostly non-English is grouped by *language*, not
#: by work type. We say so rather than pretending the label means something.
LANGUAGE_MARKERS = set(GLOSS) | {
    "gram", "panchayat", "anganwadi", "sthal", "chowk", "tola", "nagar", "puram",
}

#: Generic nouns that are fine *inside* a phrase but useless alone as a label.
WEAK_ALONE = {"construction", "installation", "purchase", "repair", "providing", "village",
              "gp", "panchayat", "gram", "public", "gram panchayat"}

PRETTY = {
    "cc": "CC",
    "cc road": "CC road",
    "rcc": "RCC",
    "led": "LED",
    "gp": "gram panchayat",
    "pcc": "PCC",
}


def _clean(term: str) -> str:
    term = re.sub(r"\s+", " ", term.strip().lower())
    if term in GLOSS:
        return GLOSS[term]
    # Gloss word-by-word so "ka nirman road" becomes "construction road".
    words = [GLOSS.get(w, w) for w in term.split() if w not in GLUE]
    glossed = " ".join(dict.fromkeys(words))  # de-duplicate, preserve order
    return PRETTY.get(glossed, glossed or term)


def _language_share(terms: list[str]) -> float:
    """Fraction of the original terms that are transliterated rather than English."""
    words = [w for t in terms for w in t.split()]
    if not words:
        return 0.0
    return sum(1 for w in words if w in LANGUAGE_MARKERS or w in GLUE) / len(words)


def _is_glue(term: str) -> bool:
    words = term.split()
    return all(w in GLUE for w in words)


def _collapse_nested(terms: list[str]) -> list[str]:
    """Drop a term that is wholly contained in a longer one already kept."""
    kept: list[str] = []
    for term in sorted(terms, key=lambda t: -len(t)):
        if not any(re.search(rf"\b{re.escape(term)}\b", k) for k in kept):
            kept.append(term)
    # Restore the original ranking order among survivors.
    return [t for t in terms if t in kept]


def build_label(ranked_terms: list[str], max_parts: int = 3) -> tuple[str, bool, str]:
    """Return (label, interpretable, note). Feed c-TF-IDF terms in descending rank."""
    language_share = _language_share(ranked_terms)

    cleaned = [_clean(t) for t in ranked_terms]
    # Glossing can map two different source terms onto the same English phrase.
    cleaned = list(dict.fromkeys(t for t in cleaned if t))
    meaningful = [t for t in cleaned if not _is_glue(t)]
    meaningful = _collapse_nested(meaningful)

    strong = [t for t in meaningful if t not in WEAK_ALONE]
    note = ""
    if language_share >= 0.55:
        note = (
            "Grouped partly by language: these descriptions are written in transliterated "
            "Hindi/Gujarati, so the cluster reflects script as well as work type."
        )

    if not strong:
        hint = " · ".join(meaningful[:2])
        label = f"Mixed / uninterpretable ({hint})" if hint else "Mixed / uninterpretable"
        return label, False, note or "Distinctive terms are grammatical filler, not a work type."

    parts = strong[:max_parts]
    if len(parts) < max_parts:
        parts += [t for t in meaningful if t not in parts][: max_parts - len(parts)]

    label = " · ".join(parts)
    return label[0].upper() + label[1:], True, note
