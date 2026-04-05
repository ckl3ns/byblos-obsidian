"""Testes para o manifesto de fontes da pipeline de destilacao."""
import os
import sys
from pathlib import Path

script_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(script_dir))

from distillation_manifest import build_manifest


def test_build_manifest_includes_expected_work_metadata():
    manifest = build_manifest(Path("raw"))

    assert manifest.by_sigla["AYBD"].source_class == "general_dictionary"
    assert manifest.by_sigla["DDD"].target_surface == "wiki"
    assert manifest.by_sigla["AYBD"].physical_layout == "directory"
    assert "concept" in manifest.by_sigla["AYBD"].expected_unit_types
    assert manifest.by_sigla["AYBD"].preferred_usage
    assert manifest.by_sigla["AYBD"].promotion_limits


def test_manifest_preserves_independence_group_and_tradition():
    item = build_manifest(Path("raw")).by_sigla["EAC"]

    assert item.independence_group == "EAC"
    assert item.tradition == "patristic_reference"
    assert item.target_domain == "historia-da-interpretacao"
