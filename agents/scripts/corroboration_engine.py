"""Aplica gates epistemicos a grupos de claims."""
from distillation_models import ClaimGroup, CorroborationDecision


def reconcile_existing_state(existing_state: str, contradicted_by_level1: bool) -> CorroborationDecision:
    if contradicted_by_level1 and existing_state == "rule":
        return CorroborationDecision(
            key=existing_state,
            status="downgraded",
            target_state="hypothesis",
            ready_for_promotion=False,
            level1_check="pass",
            supporting_claim_ids=(),
        )

    return CorroborationDecision(
        key=existing_state,
        status="unchanged",
        target_state=existing_state,
        ready_for_promotion=existing_state in {"knowledge", "rule"},
        level1_check="pass",
        supporting_claim_ids=(),
    )


def corroborate_claim_group(group: ClaimGroup, level1_check: str) -> CorroborationDecision:
    supporting_ids = tuple(claim.claim_id for claim in group.claims)

    if level1_check != "pass":
        return CorroborationDecision(
            key=group.key,
            status="staged_manual_review",
            target_state="hypothesis",
            ready_for_promotion=False,
            level1_check=level1_check,
            supporting_claim_ids=supporting_ids,
        )

    if any(claim.claim_kind == "agent_inference" for claim in group.claims):
        return CorroborationDecision(
            key=group.key,
            status="staged_inference",
            target_state="hypothesis",
            ready_for_promotion=False,
            level1_check=level1_check,
            supporting_claim_ids=supporting_ids,
        )

    levels = {claim.source_level for claim in group.claims}
    if max(levels) >= 4 and min(levels) < 4:
        return CorroborationDecision(
            key=group.key,
            status="staged_conflict",
            target_state="hypothesis",
            ready_for_promotion=False,
            level1_check=level1_check,
            supporting_claim_ids=supporting_ids,
        )

    independent_groups = {claim.independence_group for claim in group.claims if 2 <= claim.source_level <= 3}
    traditions = {claim.tradition for claim in group.claims}
    target_state = "hypothesis"
    ready = False
    status = "staged"

    if len(independent_groups) >= 3 and len(traditions) >= 2:
        target_state = "rule"
        ready = True
        status = "corroborated"
    elif len(independent_groups) >= 2:
        target_state = "knowledge"
        ready = True
        status = "corroborated"

    return CorroborationDecision(
        key=group.key,
        status=status,
        target_state=target_state,
        ready_for_promotion=ready,
        level1_check=level1_check,
        supporting_claim_ids=supporting_ids,
    )
