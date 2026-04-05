"""Testes para lint_checker.py — compatibilidade path_raw/caminho_raw."""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "c:/workspace/byblos-obsidian/agents/scripts")

from lint_checker import run_lint

TEST_TMP_ROOT = Path("c:/workspace/byblos-obsidian/.pytest_workspace")
TEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)


def _test_dir(name: str) -> Path:
    path = TEST_TMP_ROOT / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_note(path, raw_field, raw_value):
    path.write_text(
        "\n".join([
            "---",
            "tipo: obra",
            f"{raw_field}: \"{raw_value}\"",
            "---",
            "",
            "# Teste",
            "",
            "Conteudo simples.",
            "",
        ]),
        encoding="utf-8",
    )


class TestLintChecker:
    def test_rule_7_aceita_path_raw(self):
        repo = _test_dir("lint-path-raw") / "repo"
        raw_file = repo / "raw" / "dicionarios-enciclopedias" / "obra.txt"
        note = repo / "vault" / "wiki" / "obras" / "TST.md"
        raw_file.parent.mkdir(parents=True)
        note.parent.mkdir(parents=True)

        raw_file.write_text("fonte", encoding="utf-8")
        _write_note(note, "path_raw", "raw/dicionarios-enciclopedias/obra.txt")

        report = run_lint(repo)
        assert not any(issue.rule == "PATH_RAW_INVALIDO" for issue in report.issues)

    def test_rule_7_aceita_caminho_raw(self):
        repo = _test_dir("lint-caminho-raw") / "repo"
        raw_file = repo / "raw" / "dicionarios-enciclopedias" / "obra.txt"
        note = repo / "vault" / "wiki" / "obras" / "TST.md"
        raw_file.parent.mkdir(parents=True)
        note.parent.mkdir(parents=True)

        raw_file.write_text("fonte", encoding="utf-8")
        _write_note(note, "caminho_raw", "raw/dicionarios-enciclopedias/obra.txt")

        report = run_lint(repo)
        assert not any(issue.rule == "PATH_RAW_INVALIDO" for issue in report.issues)
