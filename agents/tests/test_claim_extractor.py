"""Testes para o extrator de claims tipadas."""
import os
import sys

script_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, os.path.abspath(script_dir))

from distillation_models import DistilledEntry
from claim_extractor import extract_claims


def _sample_entry() -> DistilledEntry:
    return DistilledEntry(
        unit_id="AYBD:ABRAHAM",
        unit_type="person",
        title="ABRAHAM",
        aliases=("ABRAM",),
        sigla="AYBD",
        nivel=3,
        independence_group="AYBD",
        tradition="academic_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
        raw_path="dicionarios-enciclopedias/AYBD/A.txt",
        start_anchor=10,
        end_anchor=80,
        see_also=("ISAAC",),
        bibliography_present=True,
        confidence=0.9,
        content=(
            "ABRAHAM. Patriarch associated with covenant traditions. "
            "Historical context: second-millennium debates remain disputed. "
            "See also ISAAC. Some interpreters infer later editorial shaping."
        ),
    )


def test_extract_claims_emits_factual_and_inference_items():
    claims = extract_claims(_sample_entry())

    assert claims[0].claim_kind == "factual"
    assert any(claim.claim_kind == "agent_inference" for claim in claims)
    assert {"historical_context", "semantic_relations", "tradition_markers", "crossrefs", "open_questions"} <= {
        claim.category for claim in claims
    }


def test_extract_claims_preserves_canonical_provenance_string():
    claim = extract_claims(_sample_entry())[0]

    assert claim.provenance.startswith("[Fonte: raw/")
    assert claim.unit_id == "AYBD:ABRAHAM"
    assert claim.source_level == 3
    assert claim.excerpt
    assert claim.extraction_confidence > 0
