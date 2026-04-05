"""Carrega contexto existente do vault antes das decisoes de distillacao."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VaultContext:
    repo_root: Path
    domain: str
    surface: str
    index_path: Path
    existing_wiki_path: Path | None
    hypotheses_path: Path
    knowledge_path: Path
    rules_path: Path
    index_text: str
    existing_wiki_text: str
    hypotheses_text: str
    knowledge_text: str
    rules_text: str
    rules_policy_active: bool = True


def _read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _is_domain_article(path: Path, domain: str) -> bool:
    text = _read_text(path).lower()
    if not text:
        return False
    return domain.lower() in text


def _find_existing_wiki_path(repo_root: Path, domain: str) -> Path | None:
    wiki_root = repo_root / "vault" / "wiki"
    if not wiki_root.exists():
        return None

    for candidate in sorted(wiki_root.rglob("*.md")):
        if _is_domain_article(candidate, domain):
            return candidate

    return None


def load_vault_context(repo_root: Path, domain: str, surface: str) -> VaultContext:
    repo_root = Path(repo_root)
    vault_root = repo_root / "vault"
    index_path = vault_root / "indices" / "INDEX.md"
    knowledge_root = vault_root / "knowledge" / domain
    hypotheses_path = knowledge_root / "hypotheses.md"
    knowledge_path = knowledge_root / "knowledge.md"
    rules_path = knowledge_root / "rules.md"
    existing_wiki_path = _find_existing_wiki_path(repo_root, domain)

    return VaultContext(
        repo_root=repo_root,
        domain=domain,
        surface=surface,
        index_path=index_path,
        existing_wiki_path=existing_wiki_path,
        hypotheses_path=hypotheses_path,
        knowledge_path=knowledge_path,
        rules_path=rules_path,
        index_text=_read_text(index_path),
        existing_wiki_text=_read_text(existing_wiki_path),
        hypotheses_text=_read_text(hypotheses_path),
        knowledge_text=_read_text(knowledge_path),
        rules_text=_read_text(rules_path),
        rules_policy_active=True,
    )
