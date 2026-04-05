"""Pipeline staged de distillacao para fontes em raw/dicionarios-enciclopedias."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from claim_extractor import extract_claims
from corroboration_engine import corroborate_claim_group
from distillation_indexer import index_source_entries
from distillation_manifest import build_manifest
from distillation_models import ClaimCandidate, ClaimGroup, DistilledEntry
from vault_context_loader import load_vault_context


DEFAULT_PILOT_SIGLAS = ["AYBD", "NIDB", "DJG2", "DDD", "EAC"]
PROPOSAL_FLAG = "[PROPOSTA — aguarda aprovação do proprietário]"


@dataclass(frozen=True)
class PipelineOutputs:
    report_path: Path
    pilot_siglas: list[str]
    proposals: list[dict]


def _resolve_candidate_paths(repo_root: Path, item_path: str) -> list[Path]:
    target = repo_root / "raw" / item_path
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(p for p in target.rglob("*.txt") if p.is_file())
    return []


def _group_claims(claims: list[ClaimCandidate]) -> list[ClaimGroup]:
    grouped: dict[str, list[ClaimCandidate]] = {}
    for claim in claims:
        key = f"{claim.category}|{claim.text}|{claim.target_domain}|{claim.target_surface}"
        grouped.setdefault(key, []).append(claim)
    return [ClaimGroup(key=key, claims=tuple(items)) for key, items in grouped.items()]


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")


def _proposal_from_decision(group: ClaimGroup, decision) -> dict:
    exemplar = group.claims[0]
    return {
        "proposal_flag": PROPOSAL_FLAG,
        "owner_approval_required": True,
        "target_state": decision.target_state,
        "target_surface": exemplar.target_surface,
        "target_domain": exemplar.target_domain,
        "claim_text": exemplar.text,
        "supporting_claim_ids": list(decision.supporting_claim_ids),
        "level1_check": decision.level1_check,
    }


def _report_markdown(proposals: list[dict], pilot_siglas: list[str]) -> str:
    lines = [
        f"# KB Distillation Pilot — {date.today().isoformat()}",
        "",
        "## Pilot Sources",
        "",
    ]
    lines.extend(f"- {sigla}" for sigla in pilot_siglas)
    lines.extend(["", "## Propostas", ""])
    if not proposals:
        lines.append("- Nenhuma proposta pronta para promoção nesta execução.")
    else:
        for proposal in proposals:
            lines.append(
                f"- {proposal['target_state']} | {proposal['target_surface']} | "
                f"{proposal['target_domain']} | {proposal['claim_text']}"
            )
            lines.append(f"  {proposal['proposal_flag']}")
    lines.append("")
    return "\n".join(lines)


def run_distillation_pipeline(repo_root: Path, output_dir: Path, pilot_siglas: list[str] | None = None) -> PipelineOutputs:
    repo_root = Path(repo_root)
    output_dir = Path(output_dir)
    pilot_siglas = pilot_siglas or list(DEFAULT_PILOT_SIGLAS)

    manifest = build_manifest(repo_root / "raw")
    manifest_items = [manifest.by_sigla[sigla] for sigla in pilot_siglas]
    manifest_payload = [asdict(item) for item in manifest_items]
    _write_json(output_dir / "raw_manifest.json", manifest_payload)

    entries: list[DistilledEntry] = []
    for item in manifest_items:
        load_vault_context(repo_root, domain=item.target_domain, surface=item.target_surface)
        for candidate_path in _resolve_candidate_paths(repo_root, item.path):
            entries.extend(index_source_entries(item, candidate_path))

    entry_rows = [asdict(entry) for entry in entries]
    _write_jsonl(output_dir / "distillation" / "entry_index.jsonl", entry_rows)

    claims: list[ClaimCandidate] = []
    for entry in entries:
        claims.extend(extract_claims(entry))
    claim_rows = [asdict(claim) for claim in claims]
    _write_jsonl(output_dir / "distillation" / "claim_candidates.jsonl", claim_rows)

    decisions = []
    proposals = []
    for group in _group_claims(claims):
        decision = corroborate_claim_group(group, level1_check="pass")
        decision_row = asdict(decision) | {"group_key": group.key}
        decisions.append(decision_row)
        if decision.ready_for_promotion:
            proposals.append(_proposal_from_decision(group, decision))
    _write_jsonl(output_dir / "distillation" / "corroborated_claims.jsonl", decisions)

    report_path = repo_root / "vault" / "reports" / "tematicos" / f"{date.today().isoformat()}_kb-distillation-pilot.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_report_markdown(proposals, pilot_siglas), encoding="utf-8")

    return PipelineOutputs(
        report_path=report_path,
        pilot_siglas=pilot_siglas,
        proposals=proposals,
    )


if __name__ == "__main__":
    outputs = run_distillation_pipeline(
        repo_root=Path("."),
        output_dir=Path("agents/output"),
    )
    print(outputs.report_path)
