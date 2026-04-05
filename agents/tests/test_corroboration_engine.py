"""Testes para a camada de corroboracao epistemica."""
import os
import sys

script_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(script_dir))

from corroboration_engine import corroborate_claim_group, reconcile_existing_state
from distillation_models import ClaimCandidate, ClaimGroup


def _claim(*, sigla: str, tradition: str, kind: str = "factual") -> ClaimCandidate:
    return ClaimCandidate(
        claim_id=f"{sigla}:{tradition}:{kind}",
        unit_id=f"{sigla}:ENTRY",
        category="historical_context",
        claim_kind=kind,
        text="Shared claim text",
        provenance=f"[Fonte: raw/{sigla}/entry.txt | Obra: {sigla} | Nível: 3]",
        source_level=3,
        source_sigla=sigla,
        independence_group=sigla,
        tradition=tradition,
        excerpt="Shared claim text",
        extraction_confidence=0.9,
        target_surface="knowledge",
        target_domain="historia-da-interpretacao",
    )


def test_corroboration_promotes_to_knowledge_with_two_independent_level_2_3_sources():
    group = ClaimGroup(
        key="shared",
        claims=(
            _claim(sigla="AYBD", tradition="academic_reference"),
            _claim(sigla="NIDB", tradition="academic_reference"),
        ),
    )

    result = corroborate_claim_group(group, level1_check="pass")

    assert result.target_state == "knowledge"


def test_agent_inference_stays_staged_until_reclassified():
    group = ClaimGroup(
        key="inference-only",
        claims=(
            _claim(sigla="AYBD", tradition="academic_reference", kind="agent_inference"),
            _claim(sigla="NIDB", tradition="academic_reference", kind="agent_inference"),
        ),
    )

    result = corroborate_claim_group(group, level1_check="pass")

    assert result.ready_for_promotion is False


def test_rule_requires_three_sources_and_two_traditions():
    group = ClaimGroup(
        key="rule-group",
        claims=(
            _claim(sigla="AYBD", tradition="academic_reference"),
            _claim(sigla="NIDB", tradition="evangelical_reference"),
            _claim(sigla="DDD", tradition="academic_reference"),
        ),
    )

    result = corroborate_claim_group(group, level1_check="pass")

    assert result.target_state == "rule"


def test_unresolved_level1_check_blocks_promotion():
    group = ClaimGroup(
        key="manual-review",
        claims=(
            _claim(sigla="AYBD", tradition="academic_reference"),
            _claim(sigla="NIDB", tradition="academic_reference"),
        ),
    )

    result = corroborate_claim_group(group, level1_check="unresolved_manual_review")

    assert result.ready_for_promotion is False


def test_stronger_contradiction_can_downgrade_rule_to_hypothesis():
    result = reconcile_existing_state(existing_state="rule", contradicted_by_level1=True)

    assert result.target_state == "hypothesis"


def test_routing_conflict_keeps_item_staged():
    group = ClaimGroup(
        key="routing-conflict",
        claims=(
            _claim(sigla="AYBD", tradition="academic_reference"),
            ClaimCandidate(
                claim_id="EDT:conflict",
                unit_id="EDT:ENTRY",
                category="tradition_markers",
                claim_kind="factual",
                text="Shared claim text",
                provenance="[Fonte: raw/EDT/A.txt | Obra: EDT | Nível: 4]",
                source_level=4,
                source_sigla="EDT",
                independence_group="EDT",
                tradition="evangelical_reference",
                excerpt="Shared claim text",
                extraction_confidence=0.8,
                target_surface="knowledge",
                target_domain="hermeneutica",
            ),
        ),
    )

    result = corroborate_claim_group(group, level1_check="pass")

    assert result.status == "staged_conflict"
