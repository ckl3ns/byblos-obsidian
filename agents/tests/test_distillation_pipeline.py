"""Testes de integracao para a pipeline de distillacao."""
import os
import sys
import uuid
from pathlib import Path

script_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(script_dir))

from distillation_pipeline import run_distillation_pipeline


TEST_TMP_ROOT = Path(".pytest_workspace")
TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)


def _test_dir(name: str) -> Path:
    path = TEST_TMP_ROOT / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_repo(repo_root: Path) -> None:
    _write(
        repo_root / "raw" / "dicionarios-enciclopedias" / "AYBD" / "A.txt",
        "ABRAHAM\nPatriarch entry.\nSee also ISAAC.\nBibliography.\n",
    )
    _write(
        repo_root / "raw" / "dicionarios-enciclopedias" / "NIDB" / "A.txt",
        "ABRAHAM\nHistorical context.\nSee also ISAAC.\n",
    )
    _write(
        repo_root / "raw" / "dicionarios-enciclopedias" / "IVP-Black"
        / "Joel B. Green & Jeannine K. Brown & Nicholas Perrin (eds.) - Dictionary of Jesus and the Gospels, 2nd ed. (IVP DNT).txt",
        "ABRAHAM\nGospel usage.\n",
    )
    _write(
        repo_root / "raw" / "dicionarios-enciclopedias" / "Dictionary of Deities and Demons in the Bible.txt",
        "ABRAHAM\nAncient context.\n",
    )
    _write(
        repo_root / "raw" / "dicionarios-enciclopedias" / "Encyclopedia of Ancient Christianity.txt",
        "ABRAHAM\nReception history.\n",
    )

    _write(repo_root / "vault" / "indices" / "INDEX.md", "# Index\n")
    _write(repo_root / "vault" / "wiki" / "temas" / "abraham.md", "# Abraham\n")
    _write(repo_root / "vault" / "knowledge" / "historia-da-interpretacao" / "hypotheses.md", "# Hypotheses\n")
    _write(repo_root / "vault" / "knowledge" / "historia-da-interpretacao" / "knowledge.md", "# Knowledge\n")
    _write(repo_root / "vault" / "knowledge" / "historia-da-interpretacao" / "rules.md", "# Rules\n")


def test_pipeline_writes_manifest_index_claims_and_report():
    repo_root = _test_dir("pipeline") / "repo"
    _seed_repo(repo_root)

    outputs = run_distillation_pipeline(repo_root=repo_root, output_dir=repo_root / "agents" / "output")

    assert (repo_root / "agents" / "output" / "raw_manifest.json").exists()
    assert (repo_root / "agents" / "output" / "distillation" / "entry_index.jsonl").exists()
    assert (repo_root / "agents" / "output" / "distillation" / "claim_candidates.jsonl").exists()
    assert (repo_root / "agents" / "output" / "distillation" / "corroborated_claims.jsonl").exists()
    assert outputs.report_path == repo_root / "vault" / "reports" / "tematicos" / "2026-04-05_kb-distillation-pilot.md"


def test_pipeline_never_writes_canonical_wiki_or_knowledge():
    repo_root = _test_dir("pipeline-canonical") / "repo"
    _seed_repo(repo_root)

    run_distillation_pipeline(repo_root=repo_root, output_dir=repo_root / "agents" / "output")

    assert not any((repo_root / "vault" / "wiki").rglob("*.generated.md"))
    assert not any((repo_root / "vault" / "knowledge").rglob("*.generated.md"))
    assert not any((repo_root / "vault" / "Bíblia").rglob("*.generated.md"))


def test_pipeline_uses_expected_pilot_sources_and_emits_proposal_gates():
    repo_root = _test_dir("pipeline-proposals") / "repo"
    _seed_repo(repo_root)

    outputs = run_distillation_pipeline(repo_root=repo_root, output_dir=repo_root / "agents" / "output")

    assert outputs.pilot_siglas == ["AYBD", "NIDB", "DJG2", "DDD", "EAC"]
    assert outputs.proposals
    assert all(item["proposal_flag"] == "[PROPOSTA — aguarda aprovação do proprietário]" for item in outputs.proposals)
    assert all(item["owner_approval_required"] is True for item in outputs.proposals)
