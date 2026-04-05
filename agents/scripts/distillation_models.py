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
