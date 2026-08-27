"""Perceptual hashing, and the re-used-photograph check built on it.

The claim being tested is narrow and specific: a photograph that has been re-saved,
resized, re-compressed or brightened is still recognised as the same picture, while a
different picture of a similar thing is not. Both halves matter — a check that fires on
everything is not a check.
"""

from __future__ import annotations

import hashlib
from io import BytesIO

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageEnhance

from mplads import field, photohash


def board(seed: int, text: str = "MPLADS WORK BOARD") -> Image.Image:
    """A deterministic stand-in for a site photograph: textured, with a light panel."""
    rng = np.random.default_rng(seed)
    noise = (rng.random((60, 90, 3)) * 255).astype("uint8")
    image = Image.fromarray(noise).resize((720, 480), Image.Resampling.BICUBIC)
    draw = ImageDraw.Draw(image)
    draw.rectangle([60, 60, 660, 200], fill="white")
    draw.text((90, 120), f"{text} {seed}", fill="black")
    return image


def as_bytes(image: Image.Image, fmt: str = "PNG", **kw) -> bytes:
    buffer = BytesIO()
    image.save(buffer, fmt, **kw)
    return buffer.getvalue()


# ------------------------------------------------------------------ the hash itself


def test_a_hash_is_sixty_four_bits():
    data = as_bytes(board(1))
    assert len(photohash.phash(data)) == 16   # 64 bits as hex
    assert len(photohash.dhash(data)) == 16


def test_the_same_bytes_always_hash_the_same():
    data = as_bytes(board(1))
    assert photohash.fingerprint(data) == photohash.fingerprint(data)


@pytest.mark.parametrize("transform, description", [
    (lambda i: i.resize((540, 360)), "resized"),
    (lambda i: ImageEnhance.Brightness(i).enhance(1.25), "brightened"),
    (lambda i: ImageEnhance.Contrast(i).enhance(0.8), "faded"),
])
def test_a_photograph_survives_the_edits_a_resubmission_actually_makes(transform, description):
    original = board(7)
    edited = transform(original)
    match = photohash.compare(
        photohash.fingerprint(as_bytes(edited)),
        photohash.fingerprint(as_bytes(original)).as_dict(),
    )
    assert match["match"] is True, f"{description} copy was not recognised"


def test_re_compression_defeats_the_checksum_but_not_the_perceptual_hash():
    """The whole reason this module exists."""
    original = board(11)
    resubmitted = as_bytes(
        ImageEnhance.Brightness(original.resize((560, 373))).enhance(1.1),
        "JPEG", quality=70,
    )
    first = as_bytes(original)

    assert hashlib.sha256(first).hexdigest() != hashlib.sha256(resubmitted).hexdigest()
    match = photohash.compare(
        photohash.fingerprint(resubmitted), photohash.fingerprint(first).as_dict()
    )
    assert match["match"] is True
    assert match["similarity"] > 0.85


def test_two_different_photographs_of_similar_things_do_not_match():
    a, b = as_bytes(board(1)), as_bytes(board(2))
    match = photohash.compare(photohash.fingerprint(b), photohash.fingerprint(a).as_dict())
    assert match["match"] is False
    assert match["level"] == "DIFFERENT"


def test_bytes_that_are_not_an_image_are_refused_not_crashed_on():
    assert photohash.fingerprint(b"this is not a photograph") is None


def test_a_verdict_needs_both_hashes_to_agree():
    """One hash agreeing is not enough — flat, overexposed boards collide on pHash."""
    assert photohash.verdict(0, 40)["match"] is False
    assert photohash.verdict(40, 0)["match"] is False
    assert photohash.verdict(1, 1)["match"] is True


def test_distance_is_symmetric_and_zero_against_itself():
    a = photohash.phash(as_bytes(board(3)))
    b = photohash.phash(as_bytes(board(4)))
    assert photohash.distance(a, a) == 0
    assert photohash.distance(a, b) == photohash.distance(b, a)


# --------------------------------------------------------------- the re-use check


@pytest.fixture
def store(monkeypatch, tmp_path):
    monkeypatch.setattr(field, "DB", tmp_path / "verifications.sqlite")
    monkeypatch.setattr(field, "PHOTOS", tmp_path / "photos")
    return field


def _upload(store, image_bytes: bytes, work_ref: str, filename: str = "photo.png") -> dict:
    name = store.save_photo(image_bytes, filename)
    return store.check_photo(image_bytes, name, work_ref, actor="officer")


def test_the_first_photograph_for_a_work_is_not_re_use(store):
    result = _upload(store, as_bytes(board(1)), "MP1-W1")
    assert result["fingerprinted"] is True
    assert result["reuse"] == []


def test_the_same_photograph_for_the_same_work_is_not_re_use(store):
    """Photographing one work twice is normal. Only crossing works is a question."""
    data = as_bytes(board(1))
    _upload(store, data, "MP1-W1")
    again = _upload(store, data, "MP1-W1")
    assert again["reuse"] == []


def test_a_re_shot_photograph_submitted_for_another_work_is_caught(store):
    original = board(21)
    _upload(store, as_bytes(original), "MP1-W1", "site.png")

    resubmitted = as_bytes(
        ImageEnhance.Brightness(original.resize((562, 374))).enhance(1.09),
        "JPEG", quality=72,
    )
    result = _upload(store, resubmitted, "MP2-W2", "different-name.jpg")

    assert len(result["reuse"]) == 1
    hit = result["reuse"][0]
    assert hit["work_ref"] == "MP1-W1"
    assert hit["exact_file"] is False      # a genuinely different file
    assert hit["match"] is True


def test_an_unrelated_photograph_for_another_work_is_left_alone(store):
    _upload(store, as_bytes(board(1)), "MP1-W1")
    result = _upload(store, as_bytes(board(2)), "MP2-W2")
    assert result["reuse"] == []


def test_the_portfolio_report_only_lists_pictures_spanning_works(store):
    shared = as_bytes(board(31))
    for ref in ("MP1-W1", "MP2-W2"):
        name = store.save_photo(shared, "board.png")
        store.check_photo(shared, name, ref, actor="officer")
        store.record(ref, "VERIFIED_COMPLETE", actor="officer", role="auditor", photo=name)

    solo = as_bytes(board(32))
    solo_name = store.save_photo(solo, "solo.png")
    store.check_photo(solo, solo_name, "MP3-W3", actor="officer")
    store.record("MP3-W3", "VERIFIED_COMPLETE", actor="officer", role="auditor",
                 photo=solo_name)

    report = store.photo_reuse_report()
    assert report["photographs"] == 3
    assert report["shared_across_works"] == 1
    assert report["clusters"][0]["works"] == ["MP1-W1", "MP2-W2"]


def test_the_report_frames_re_use_as_a_question(store):
    """A recycled photograph is a lead. Two phases of one road look identical."""
    assert "not a conclusion" in store.photo_reuse_report()["note"]
