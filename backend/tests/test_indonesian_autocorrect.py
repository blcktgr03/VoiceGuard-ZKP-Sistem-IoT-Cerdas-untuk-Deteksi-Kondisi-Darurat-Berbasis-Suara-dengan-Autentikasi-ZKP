from backend.speech.indonesian_autocorrect import (
    correct_indonesian_text,
    levenshtein_distance,
)
import pytest


def test_corrects_emergency_words_with_at_most_three_edits() -> None:
    corrected, changes = correct_indonesian_text("Dalong ada keperkaran")

    assert corrected == "Tolong ada kebakaran"
    assert changes == [
        ("Dalong", "Tolong", 2),
        ("keperkaran", "kebakaran", 3),
    ]


def test_corrects_recent_inmp441_whisper_errors() -> None:
    corrected, changes = correct_indonesian_text("Talong, kubakaran")

    assert corrected == "Tolong, kebakaran"
    assert changes == [("Talong", "Tolong", 1), ("kubakaran", "kebakaran", 1)]


def test_maps_short_whisper_help_alias_to_tolong() -> None:
    corrected, changes = correct_indonesian_text("Tung, bantu dia")

    assert corrected == "Tolong, bantu dia"
    assert changes[0] == ("Tung", "Tolong", 3)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("tolongg", "tolong"),
        ("bantuam", "bantuan"),
        ("kebakran", "kebakaran"),
        ("kecelakan", "kecelakaan"),
        ("darura", "darurat"),
        ("ambulance", "ambulans"),
        ("sakir", "sakit"),
        ("pinsan", "pingsan"),
        ("tertipa", "tertimpa"),
        ("terjbak", "terjebak"),
        ("efakuasi", "evakuasi"),
        ("banjer", "banjir"),
        ("gemba", "gempa"),
        ("tangaku", "tanganku"),
    ],
)
def test_corrects_reviewed_dataset_and_emergency_aliases(
    raw: str,
    expected: str,
) -> None:
    corrected, changes = correct_indonesian_text(raw)

    assert corrected == expected
    assert changes


def test_does_not_rewrite_valid_dataset_words_that_resemble_keywords() -> None:
    text = "badai tapi media rumah daerah jalan akan suka atap"

    corrected, changes = correct_indonesian_text(text)

    assert corrected == text
    assert changes == []


def test_preserves_negation_and_words_outside_edit_limit() -> None:
    corrected, changes = correct_indonesian_text(
        "semua aman bukan keadaan darurat xyzabc"
    )

    assert corrected == "semua aman bukan keadaan darurat xyzabc"
    assert changes == []


def test_levenshtein_limit_reports_words_beyond_limit() -> None:
    assert levenshtein_distance("keperkaran", "kebakaran", 3) == 3
    assert levenshtein_distance("xyzabc", "kebakaran", 3) > 3
