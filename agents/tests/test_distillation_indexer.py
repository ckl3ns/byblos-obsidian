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
