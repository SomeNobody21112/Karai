"""Read a site photograph or work order and pull the fields that identify a work.

MPLADS works carry a display board at the site: work reference, sanctioned amount,
implementing district. An officer photographs that board; this reads it and matches the
record, so nobody re-types a reference number standing in a field.

**What this is not.** It does not verify that the work exists, or that it matches its
description, or that the money was spent. It reads text off an image the officer supplies.
Every extracted field is returned with its confidence and shown for confirmation — the
officer accepts or corrects it before anything is recorded.

The engine is RapidOCR (ONNX, CPU, no GPU and no external binary). If it is unavailable the
module degrades to manual entry rather than failing: the officer types the reference.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path

LOGGER = logging.getLogger(__name__)

#: Letters an OCR engine returns where a digit was printed. Weathered signage and low
#: light make these the standard substitutions; the reference is all digits, so correcting
#: them is safe in a way it would not be inside free text.
CONFUSIONS = str.maketrans({
    "O": "0", "o": "0",
    "I": "1", "i": "1", "l": "1",
    "Z": "2", "z": "2",
    "S": "5", "s": "5",
    "B": "8",
})

#: The character class the reference may be *read* as — derived from the correction table
#: rather than written out, so the two can never drift apart. That drift is exactly the bug
#: this replaced: the pattern admitted only O, so "W863I6" matched as "W863" and the last
#: two characters were silently dropped from the reference.
_DIGITISH = "[" + re.escape("".join(sorted(chr(o) for o in CONFUSIONS))) + r"\d]"

#: Our canonical reference, e.g. MP3018356-W86316. OCR also drops spaces and renders the
#: hyphen as any dash it likes, so the pattern tolerates that and normalises afterwards.
WORK_REF = re.compile(
    rf"MP\s*({_DIGITISH}{{5,10}})\s*[-–—_]\s*W\s*({_DIGITISH}{{2,10}})", re.I
)

#: "Rs 6,50,00,000" / "₹6.5 Cr" / "Amount: 650000"
AMOUNT = re.compile(
    r"(?:rs|inr|₹)\s*\.?\s*([\d,]+(?:\.\d+)?)\s*(cr|crore|lakh|lac|l)?", re.I
)


@lru_cache(maxsize=1)
def _engine():
    """The OCR engine, or None when it is not installed."""
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        LOGGER.info("rapidocr not installed — photo reading unavailable, manual entry only")
        return None
    try:
        return RapidOCR()
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning("could not start OCR engine: %s", exc)
        return None


def available() -> bool:
    return _engine() is not None


def _normalise_ref(prefix: str, serial: str) -> str:
    return f"MP{prefix.translate(CONFUSIONS)}-W{serial.translate(CONFUSIONS)}"


def _parse_amount(raw: str, unit: str | None) -> float | None:
    try:
        value = float(raw.replace(",", ""))
    except ValueError:
        return None
    unit = (unit or "").lower()
    if unit.startswith("cr"):
        return value * 1e7
    if unit in {"lakh", "lac", "l"}:
        return value * 1e5
    return value


def _line_confidence(fragment: str, lines: list[dict]) -> float:
    """How sure the engine was about the line this fragment came from.

    This is confidence in the *characters*, not in the answer — a weathered board returns
    a wrong digit at high confidence quite happily. It is shown so an officer knows how
    legible the board was, never as a reason to skip confirming the field.
    """
    needle = fragment.replace(" ", "")
    return max(
        (line["confidence"] for line in lines if needle in line["text"].replace(" ", "")),
        default=0.0,
    )


def read(image_path: Path) -> dict:
    """Extract text and identifying fields from one image.

    Returns the raw lines with confidences, plus whichever fields were recognised. Nothing
    here is trusted — the caller shows it to the officer for confirmation.
    """
    engine = _engine()
    if engine is None:
        return {
            "available": False,
            "lines": [],
            "fields": {},
            "note": "Photo reading is unavailable on this machine. Enter the work "
                    "reference manually.",
        }

    import numpy as np
    from PIL import Image

    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as exc:
        return {"available": True, "lines": [], "fields": {}, "error": f"unreadable image: {exc}"}

    # Very large phone photos are downscaled — accuracy is unchanged and it is much faster.
    if max(image.size) > 2000:
        scale = 2000 / max(image.size)
        image = image.resize((int(image.width * scale), int(image.height * scale)))

    result, _ = engine(np.array(image))
    lines = [
        {"text": text, "confidence": round(float(conf), 3)}
        for _, text, conf in (result or [])
    ]
    blob = " ".join(line["text"] for line in lines)

    fields: dict[str, dict] = {}

    match = WORK_REF.search(blob)
    if match:
        fields["work_ref"] = {
            "value": _normalise_ref(match.group(1), match.group(2)),
            "source_text": match.group(0),
            "confidence": _line_confidence(match.group(0), lines),
        }

    money = AMOUNT.search(blob)
    if money:
        parsed = _parse_amount(money.group(1), money.group(2))
        if parsed:
            fields["amount"] = {
                "value": parsed,
                "source_text": money.group(0).strip(),
                "confidence": _line_confidence(money.group(0), lines),
            }

    LOGGER.info("ocr: %s lines, fields found: %s", len(lines), list(fields))
    return {
        "available": True,
        "lines": lines,
        "fields": fields,
        "note": "Extracted text only. It has not been verified against any record — "
                "confirm or correct each field before saving.",
    }


def near_misses(ref: str, known_refs: set[str], limit: int = 4) -> list[str]:
    """Known references one character away from what was read.

    OCR confidence is confidence in the *pixels*, not in the answer. A weathered board can
    return a single wrong digit at 99% confidence, and a reference that is wrong by one
    digit points at a different work just as firmly as one that is wrong by ten. So when a
    read reference is not in the portfolio, we say which real references it almost is, and
    let the officer pick. Exhaustive over single-digit substitutions: about 130 set
    lookups, which is free.
    """
    candidates = []
    for position, character in enumerate(ref):
        if not character.isdigit():
            continue
        for digit in "0123456789":
            if digit == character:
                continue
            candidate = ref[:position] + digit + ref[position + 1:]
            if candidate in known_refs:
                candidates.append(candidate)
    return sorted(set(candidates))[:limit]


def match_to_work(extracted: dict, known_refs: set[str],
                  amounts: dict[str, float] | None = None) -> dict:
    """Decide which work a photographed board belongs to — and how sure that is.

    The failure this is built around is not the unreadable board; it is the *readable* one.
    A weathered board returns "…W136963" at 99.6% character confidence when the board said
    "…W136962", and both are real works — two gym installations at two schools in the same
    block, with the same sanctioned amount. Character confidence cannot separate them and
    neither can the amount.

    So a match is never presented as settled. Every real reference one character away is
    returned alongside it, and where the board also carries an amount it is checked against
    the record. The officer confirms; the machine narrows.
    """
    field = extracted.get("fields", {}).get("work_ref")
    if not field:
        return {"matched": False, "needs_confirmation": True,
                "reason": "no work reference found in the image"}

    ref = field["value"]
    alternatives = near_misses(ref, known_refs)
    result: dict = {
        "work_ref": ref,
        "confidence": field["confidence"],
        "alternatives": alternatives,
    }

    if ref not in known_refs:
        reason = f"{ref} was read from the image but is not a work in this dataset"
        if alternatives:
            reason += (". These real works differ from it by one character: "
                       + ", ".join(alternatives))
        return {**result, "matched": False, "needs_confirmation": True, "reason": reason}

    result["matched"] = True

    board_amount = (extracted.get("fields", {}).get("amount") or {}).get("value")
    on_record = (amounts or {}).get(ref)
    if board_amount and on_record:
        # Cast out of numpy — this dict is serialised to JSON and numpy scalars are not.
        board_amount, on_record = float(board_amount), float(on_record)
        # 1% tolerance: boards are painted with rounded figures.
        agrees = abs(board_amount - on_record) <= max(on_record * 0.01, 1.0)
        result["corroboration"] = {
            "amount_on_board": board_amount,
            "amount_on_record": on_record,
            "agrees": bool(agrees),
        }

    ambiguous = bool(alternatives)
    result["needs_confirmation"] = ambiguous or not result.get(
        "corroboration", {"agrees": True}
    )["agrees"]
    if ambiguous:
        result["reason"] = (
            "Matched, but " + ", ".join(alternatives) + " differ by one character and are "
            "also real works. Character confidence cannot tell them apart — confirm which "
            "board you photographed."
        )
    return result
