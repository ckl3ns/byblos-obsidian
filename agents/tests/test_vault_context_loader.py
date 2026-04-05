"""Testes para carregamento de contexto do vault antes da distillacao."""
import os
import sys
import uuid
from pathlib import Path

script_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(script_dir))

from vault_context_loader import load_vault_context


TEST_TMP_ROOT = Path(".pytest_workspace")
TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)


def _test_dir(name: str) -> Path:
    path = TEST_TMP_ROOT / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_file(path: Path, content: str = "# ok\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_load_vault_context_reads_index_wiki_and_knowledge_layers():
    repo_root = _test_dir("vault-context")

    _write_file(repo_root / "vault" / "indices" / "INDEX.md")
    _write_file(repo_root / "vault" / "wiki" / "temas" / "termo.md", "---\ndominio: hermeneutica\n---\n# Termo\n")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "hypotheses.md")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "knowledge.md")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "rules.md")

    context = load_vault_context(repo_root, domain="hermeneutica", surface="knowledge")

    assert context.index_path == repo_root / "vault" / "indices" / "INDEX.md"
    assert context.rules_text.startswith("#")
    assert context.existing_wiki_path.name == "termo.md"
    assert context.hypotheses_path.name == "hypotheses.md"
    assert context.knowledge_path.name == "knowledge.md"
    assert context.rules_path.name == "rules.md"
    assert context.index_text.startswith("#")
    assert context.existing_wiki_text.startswith("---")
    assert context.hypotheses_text.startswith("#")
    assert context.knowledge_text.startswith("#")


def test_load_vault_context_marks_rules_as_default_policy():
    repo_root = _test_dir("vault-context-policy")

    _write_file(repo_root / "vault" / "indices" / "INDEX.md")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "hypotheses.md")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "knowledge.md")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "rules.md")

    context = load_vault_context(repo_root, domain="hermeneutica", surface="knowledge")

    assert context.rules_policy_active is True


def test_load_vault_context_handles_missing_wiki_article():
    repo_root = _test_dir("vault-context-no-wiki")

    _write_file(repo_root / "vault" / "indices" / "INDEX.md")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "hypotheses.md")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "knowledge.md")
    _write_file(repo_root / "vault" / "knowledge" / "hermeneutica" / "rules.md")

    context = load_vault_context(repo_root, domain="hermeneutica", surface="knowledge")

    assert context.existing_wiki_path is None
