"""Extrai claims tipadas a partir de entradas destiladas."""
from distillation_models import ClaimCandidate, DistilledEntry


def _claim(
    entry: DistilledEntry,
    *,
    suffix: str,
    category: str,
    claim_kind: str,
    text: str,
    excerpt: str,
) -> ClaimCandidate:
    return ClaimCandidate(
        claim_id=f"{entry.unit_id}:{suffix}",
        unit_id=entry.unit_id,
        category=category,
        claim_kind=claim_kind,
        text=text,
        provenance=f"[Fonte: raw/{entry.raw_path} | Obra: {entry.sigla} | Nível: {entry.nivel}]",
        source_level=entry.nivel,
        source_sigla=entry.sigla,
        independence_group=entry.independence_group,
        tradition=entry.tradition,
        excerpt=excerpt,
        extraction_confidence=entry.confidence,
        target_surface=entry.target_surface,
        target_domain=entry.target_domain,
    )


def extract_claims(entry: DistilledEntry) -> list[ClaimCandidate]:
    claims = [
        _claim(
            entry,
            suffix="historical",
            category="historical_context",
            claim_kind="factual",
            text=f"{entry.title} is treated as a bounded historical reference entry.",
            excerpt=entry.content[:120],
        ),
        _claim(
            entry,
            suffix="semantic",
            category="semantic_relations",
            claim_kind="factual",
            text=f"{entry.title} preserves semantic relations through aliases and linked terms.",
            excerpt=", ".join(entry.aliases) or entry.title,
        ),
        _claim(
            entry,
            suffix="tradition",
            category="tradition_markers",
            claim_kind="factual",
            text=f"{entry.title} is routed through the {entry.tradition} tradition marker.",
            excerpt=entry.tradition,
        ),
        _claim(
            entry,
            suffix="crossrefs",
            category="crossrefs",
            claim_kind="factual",
            text=f"{entry.title} connects to cross-references through see-also links.",
            excerpt=", ".join(entry.see_also) or entry.title,
        ),
        _claim(
            entry,
            suffix="questions",
            category="open_questions",
            claim_kind="agent_inference",
            text=f"{entry.title} may require further review for unresolved editorial or contextual questions.",
            excerpt=entry.content[-120:],
        ),
    ]
    return claims
