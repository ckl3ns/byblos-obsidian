"""Modelos compartilhados da pipeline de distillacao."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceManifestItem:
    sigla: str
    nivel: int
    path: str
    source_class: str
    domains: tuple[str, ...]
    physical_layout: str
    expected_unit_types: tuple[str, ...]
    preferred_usage: str
    promotion_limits: tuple[str, ...]
    independence_group: str
    tradition: str
    target_surface: str
    target_domain: str


@dataclass(frozen=True)
class SourceManifest:
    raw_root: Path
    items: tuple[SourceManifestItem, ...]

    @property
    def by_sigla(self) -> dict[str, SourceManifestItem]:
        return {item.sigla: item for item in self.items}


@dataclass(frozen=True)
class DistilledEntry:
    unit_id: str
    unit_type: str
    title: str
    aliases: tuple[str, ...]
    sigla: str
    nivel: int
    independence_group: str
    tradition: str
    target_surface: str
    target_domain: str
    raw_path: str
    start_anchor: int
    end_anchor: int
    see_also: tuple[str, ...]
    bibliography_present: bool
    confidence: float
    content: str


@dataclass(frozen=True)
class ClaimCandidate:
    claim_id: str
    unit_id: str
    category: str
    claim_kind: str
    text: str
    provenance: str
    source_level: int
    source_sigla: str
    independence_group: str
    tradition: str
    excerpt: str
    extraction_confidence: float
    target_surface: str
    target_domain: str


@dataclass(frozen=True)
class ClaimGroup:
    key: str
    claims: tuple[ClaimCandidate, ...]


@dataclass(frozen=True)
class CorroborationDecision:
    key: str
    status: str
    target_state: str
    ready_for_promotion: bool
    level1_check: str
    supporting_claim_ids: tuple[str, ...]
