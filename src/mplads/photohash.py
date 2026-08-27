"""Perceptual hashing: is this the same photograph we were shown for another work?

A cryptographic hash answers "is this the same *file*", which anyone can defeat by
re-saving the image. A perceptual hash answers "is this the same *picture*", and survives
re-compression, resizing, a slight crop and a change in brightness. That difference is the
entire point: a recycled site photograph is almost never submitted as the identical file.

**This is a lead, not a finding.** The same photograph legitimately appears twice — a road
resurfaced in two phases, two works at one school, a single visit covering adjacent
sanctions. The system says "this picture was already submitted for MP…-W… on <date>";
a human decides whether that is expected.

Two independent hashes are computed, because they fail differently:

- **pHash** (DCT of a 32x32 greyscale) keys on low-frequency structure. Robust to
  compression and resizing; can be fooled by a heavy crop.
- **dHash** (adjacent-pixel gradients on a 9x8 greyscale) keys on relative brightness.
  Robust to gamma and exposure; more sensitive to rotation.

Agreement between them is what makes a match worth showing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO

import numpy as np

LOGGER = logging.getLogger(__name__)

HASH_BITS = 64

#: Hamming distance bands, out of 64 bits. The literature puts "same image" at <= 10 for a
#: 64-bit pHash; we are stricter for the top band because this is shown to an auditor.
IDENTICAL = 2
NEAR_IDENTICAL = 8
SAME_SCENE = 14


@dataclass(frozen=True)
class Fingerprint:
    """Both hashes for one image, as hex strings."""

    phash: str
    dhash: str

    def as_dict(self) -> dict[str, str]:
        return {"phash": self.phash, "dhash": self.dhash}


def _greyscale(data: bytes, size: tuple[int, int]) -> np.ndarray:
    from PIL import Image

    image = Image.open(BytesIO(data)).convert("L").resize(size, Image.Resampling.LANCZOS)
    return np.asarray(image, dtype=np.float64)


def _dct_matrix(n: int) -> np.ndarray:
    """Orthonormal DCT-II basis. Built here rather than pulled from scipy — it is four
    lines, and the project does not carry scipy for one transform."""
    k = np.arange(n).reshape(-1, 1)
    i = np.arange(n).reshape(1, -1)
    basis = np.cos(np.pi * (2 * i + 1) * k / (2 * n)) * np.sqrt(2 / n)
    basis[0] /= np.sqrt(2)
    return basis


def _bits_to_hex(bits: np.ndarray) -> str:
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def phash(data: bytes) -> str:
    """DCT-based perceptual hash. Survives re-compression and resizing."""
    pixels = _greyscale(data, (32, 32))
    basis = _dct_matrix(32)
    coefficients = basis @ pixels @ basis.T
    block = coefficients[:8, :8]
    # The DC term carries overall brightness, not structure — excluding it from the median
    # is what makes the hash indifferent to how bright the day was.
    reference = np.median(block.flatten()[1:])
    return _bits_to_hex(block > reference)


def dhash(data: bytes) -> str:
    """Gradient hash: each bit is "is this pixel brighter than the one to its right"."""
    pixels = _greyscale(data, (9, 8))
    return _bits_to_hex(pixels[:, :-1] > pixels[:, 1:])


def fingerprint(data: bytes) -> Fingerprint | None:
    """Both hashes, or None if the bytes are not a readable image."""
    try:
        return Fingerprint(phash=phash(data), dhash=dhash(data))
    except Exception as exc:  # pragma: no cover - defensive; Pillow raises many types
        LOGGER.warning("could not fingerprint image: %s", type(exc).__name__)
        return None


def distance(left: str, right: str) -> int:
    """Hamming distance between two hex hashes, in bits."""
    return bin(int(left, 16) ^ int(right, 16)).count("1")


def verdict(phash_distance: int, dhash_distance: int) -> dict:
    """Turn two distances into something an officer can read.

    Both hashes must agree before we call it a match. A pHash collision alone is a known
    weakness of the method on flat, low-detail images — a wall, an empty plot, an
    overexposed board — which is exactly what a site photograph often is.
    """
    worst = max(phash_distance, dhash_distance)
    if worst <= IDENTICAL:
        level, note = "IDENTICAL", "the same photograph"
    elif worst <= NEAR_IDENTICAL:
        level, note = ("NEAR_IDENTICAL",
                       "the same photograph, re-saved, resized or lightly edited")
    elif worst <= SAME_SCENE:
        level, note = "SAME_SCENE", "possibly the same place, photographed again"
    else:
        return {"match": False, "level": "DIFFERENT", "phash_distance": phash_distance,
                "dhash_distance": dhash_distance}
    return {
        "match": True,
        "level": level,
        "note": note,
        "phash_distance": phash_distance,
        "dhash_distance": dhash_distance,
        "similarity": round(1 - worst / HASH_BITS, 3),
    }


def compare(candidate: Fingerprint, known: dict[str, str]) -> dict:
    """Compare one fingerprint against a stored pair of hashes."""
    return verdict(
        distance(candidate.phash, known["phash"]),
        distance(candidate.dhash, known["dhash"]),
    )
