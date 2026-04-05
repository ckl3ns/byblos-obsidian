"""Testes para o indexador de verbetes da pipeline de destillacao."""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "c:/workspace/byblos-obsidian/.worktrees/feature-kb-distillation-pipeline/agents/scripts")

from distillation_manifest import build_manifest
from distillation_indexer import index_source_entries


TEST_TMP_ROOT = Path("c:/workspace/byblos-obsidian/.pytest_workspace")
TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)


def _test_dir(name: str) -> Path:
    path = TEST_TMP_ROOT / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_index_entries_extracts_bounded_units_from_headings():
    raw_root = _test_dir("distillation-indexer") / "raw"
    source_dir = raw_root / "dicionarios-enciclopedias" / "AYBD"
    source_dir.mkdir(parents=True)
    sample_text_file = source_dir / "sample.txt"
    sample_text_file.write_text(
        "\n".join(
            [
                "ABRAHAM (ABRAM)",
                "Patriarch associated with covenant traditions.",
                "See also ISAAC.",
                "Bibliography: Anchor Bible Dictionary entry.",
                "",
                "ALTAR",
                "Cultic structure used in sacrifice.",
                "See also SACRIFICE.",
            ]
        ),
        encoding="utf-8",
    )

    sample_manifest_item = build_manifest(raw_root).by_sigla["AYBD"]
    entries = index_source_entries(sample_manifest_item, sample_text_file)

    assert [entry.title for entry in entries] == ["ABRAHAM", "ALTAR"]
    assert entries[0].aliases == ("ABRAM",)
    assert entries[0].raw_path.endswith("sample.txt")
    assert entries[0].start_anchor < entries[0].end_anchor
    assert entries[0].target_surface == "wiki"
    assert entries[0].target_domain == "historia-da-interpretacao"
    assert entries[0].confidence > 0


def test_index_entries_carries_see_also_and_bibliography_flags():
    raw_root = _test_dir("distillation-indexer-flags") / "raw"
    source_dir = raw_root / "dicionarios-enciclopedias" / "AYBD"
    source_dir.mkdir(parents=True)
    sample_text_file = source_dir / "sample.txt"
    sample_text_file.write_text(
        "\n".join(
            [
                "ABRAHAM (ABRAM)",
                "Patriarch associated with covenant traditions.",
                "See also ISAAC.",
                "Bibliography: Anchor Bible Dictionary entry.",
            ]
        ),
        encoding="utf-8",
    )

    sample_manifest_item = build_manifest(raw_root).by_sigla["AYBD"]
    entry = index_source_entries(sample_manifest_item, sample_text_file)[0]

    assert "ISAAC" in entry.see_also
    assert entry.bibliography_present is True


def test_index_entries_handles_realistic_ddd_headings_without_front_matter_noise():
    raw_root = _test_dir("distillation-indexer-ddd") / "raw"
    source_file = raw_root / "dicionarios-enciclopedias" / "Dictionary of Deities and Demons in the Bible.txt"
    source_file.parent.mkdir(parents=True)
    source_file.write_text(
        "\n".join(
            [
                "DICTIONARY OF DEITIES AND DEMONS IN THE BIBLE",
                "CONTENTS",
                "",
                "A",
                "",
                "AB →FATHER",
                "",
                "ABADDON",
                "I.      The noun ʾăbaddôn is derived from the Heb root אבד.",
                "III.      Bibliography",
                "J. JEREMIAS, Ἀβαδδών, TWNT 1 (1933) 4.",
                "M. HUTTER",
                "",
                "ABBA →FATHER",
                "",
                "ABEL הבל",
                "I.      Abel is a novelistic figure in Gen 4.",
                "IV.      Bibliography",
                "J. E. FOSSUM, The Name of God and the Angel of the Lord.",
                "B. BECKING",
                "",
                "adonis Ἄδωνις",
                "I.      Adonis is a hero of classical mythology.",
                "IV.      Bibliography",
                "S. RIBICHINI, Adonis. Aspetti orientali di un mito greco.",
                "S. RIBICHINI",
            ]
        ),
        encoding="utf-8",
    )

    sample_manifest_item = build_manifest(raw_root).by_sigla["DDD"]
    entries = index_source_entries(sample_manifest_item, source_file)

    assert [entry.title for entry in entries] == [
        "AB",
        "ABADDON",
        "ABBA",
        "ABEL הבל",
        "ADONIS ἌΔΩΝΙΣ",
    ]
    assert entries[0].see_also == ("FATHER",)
    assert entries[2].see_also == ("FATHER",)
    assert "M. HUTTER" not in entries[1].content
    assert entries[3].title == "ABEL הבל"


def test_index_entries_uses_ddd_specific_extractor_for_realistic_layout():
    raw_root = _test_dir("distillation-indexer-ddd") / "raw"
    source_file = raw_root / "dicionarios-enciclopedias" / "Dictionary of Deities and Demons in the Bible.txt"
    source_file.parent.mkdir(parents=True)
    source_file.write_text(
        "\n".join(
            [
                "DICTIONARY OF DEITIES AND DEMONS IN THE BIBLE",
                "",
                "CONTENTS",
                "",
                "INTRODUCTION",
                "",
                "K. VAN DER TOORN",
                "",
                "A",
                "",
                "AB →FATHER",
                "",
                "ABADDON",
                "I.      The noun ʾăbaddôn means 'place of destruction'.",
                "III.      Bibliography",
                "J. JEREMIAS, Ἀβαδδών.",
                "M. HUTTER",
                "",
                "ABBA →FATHER",
                "",
                "ABEL הבל",
                "I.      Abel is related to hebel 'breath'.",
                "III.      Bibliography",
                "B. BECKING",
                "",
                "AENEAS Αἰνέας/Αἰνείας",
                "I.      Aeneas is a Trojan hero.",
                "IV.      Bibliography",
                "K. DOWDEN",
                "",
                "BAAL-HAZOR בעל חצור",
                "I.      A location near Ophrah.",
                "ABEL (1924) suggested to read 1 Macc 9:15 differently.",
                "III.      Bibliography",
                "N. NAʾAMAN",
                "",
                "ALTAR מזבח",
                "I.      The word 'altar' occurs more than 400 times.",
                "See also SACRIFICE.",
            ]
        ),
        encoding="utf-8",
    )

    sample_manifest_item = build_manifest(raw_root).by_sigla["DDD"]
    entries = index_source_entries(sample_manifest_item, source_file)

    assert [entry.title for entry in entries] == [
        "AB",
        "ABADDON",
        "ABBA",
        "ABEL הבל",
        "AENEAS ΑἸΝΈΑΣ/ΑἸΝΕΊΑΣ",
        "BAAL-HAZOR בעל חצור",
        "ALTAR מזבח",
    ]
    assert entries[0].see_also == ("FATHER",)
    assert entries[2].see_also == ("FATHER",)
    assert entries[3].aliases == ()
    assert entries[4].aliases == ()
    assert entries[5].aliases == ()
    assert entries[5].title != "ABEL"
    assert entries[6].see_also == ("SACRIFICE",)
