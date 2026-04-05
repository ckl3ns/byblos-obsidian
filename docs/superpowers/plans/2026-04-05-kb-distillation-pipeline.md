# KB Distillation Pipeline Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a staged distillation pipeline that turns `raw/dicionarios-enciclopedias/` into manifest, indexed units, candidate claims, corroboration decisions, and a pilot report without mutating canonical vault content.

**Architecture:** Add small Python modules under `agents/scripts/` for source metadata, entry indexing, vault preflight loading, claim extraction, corroboration, and report generation. Keep outputs in `agents/output/distillation/` and use synthetic fixtures in tests so we can scale automation without depending on copyrighted raw files or unstable OCR details.

**Tech Stack:** Python 3.13, `pytest`, existing `agents/scripts/raw_searcher.py`, JSON/JSONL outputs, Markdown report generation.

---

## Chunk 1: Data Contracts And Source Manifest

### Task 1: Add distillation data models and manifest builder

**Files:**
- Create: `agents/scripts/distillation_models.py`
- Create: `agents/scripts/distillation_manifest.py`
- Create: `agents/tests/test_distillation_manifest.py`
- Modify: `agents/scripts/raw_searcher.py`

- [ ] **Step 1: Write the failing tests for manifest metadata and provenance helpers**

```python
def test_build_manifest_includes_expected_work_metadata():
    manifest = build_manifest(Path("raw"))
    assert manifest.by_sigla["AYBD"].source_class == "general_dictionary"
    assert manifest.by_sigla["DDD"].target_surface == "wiki"

def test_manifest_preserves_independence_group_and_tradition():
    item = build_manifest(Path("raw")).by_sigla["EAC"]
    assert item.independence_group == "EAC"
    assert item.tradition == "patristic_reference"
```

- [ ] **Step 2: Run manifest tests to verify they fail**

Run: `pytest agents/tests/test_distillation_manifest.py -p no:cacheprovider --basetemp=test-tmp`
Expected: FAIL with missing module or missing builder/function.

- [ ] **Step 3: Implement minimal manifest builder and shared dataclasses**

```python
@dataclass(frozen=True)
class SourceManifestItem:
    sigla: str
    nivel: int
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
```

- [ ] **Step 4: Extend `raw_searcher.py` to reuse shared source metadata instead of a private divergent map**

Run: `pytest agents/tests/test_raw_searcher.py agents/tests/test_distillation_manifest.py -p no:cacheprovider --basetemp=test-tmp`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/scripts/distillation_models.py agents/scripts/distillation_manifest.py agents/scripts/raw_searcher.py agents/tests/test_distillation_manifest.py
git commit -m "feat(kb): add source manifest metadata"
```

## Chunk 2: Vault Preflight And Entry Indexing

**Execution note:** Task 2 and Task 3 may run in parallel only after Task 1 is complete, because Task 1 owns the shared source contracts. After that point:
- Worker A owns `agents/scripts/vault_context_loader.py` and `agents/tests/test_vault_context_loader.py`
- Worker B owns `agents/scripts/distillation_indexer.py` and `agents/tests/test_distillation_indexer.py`
- `agents/scripts/distillation_models.py` stays controller-owned after Task 1 unless a follow-up patch is explicitly assigned.

### Task 2: Load existing vault context before promotion decisions

**Files:**
- Create: `agents/scripts/vault_context_loader.py`
- Create: `agents/tests/test_vault_context_loader.py`

- [ ] **Step 1: Write the failing tests for vault preflight loading**

```python
def test_load_vault_context_reads_index_wiki_and_knowledge_layers(tmp_path):
    context = load_vault_context(tmp_path, domain="hermeneutica", surface="knowledge")
    assert context.index_path.name == "INDEX.md"
    assert context.rules_text.startswith("#")
    assert context.existing_wiki_path.name == "termo.md"
    assert context.hypotheses_path.name == "hypotheses.md"
    assert context.knowledge_path.name == "knowledge.md"

def test_load_vault_context_marks_rules_as_default_policy(tmp_path):
    context = load_vault_context(tmp_path, domain="hermeneutica", surface="knowledge")
    assert context.rules_policy_active is True
```

- [ ] **Step 2: Run context loader tests to verify they fail**

Run: `pytest agents/tests/test_vault_context_loader.py -p no:cacheprovider --basetemp=test-tmp`
Expected: FAIL with missing loader or missing fields.

- [ ] **Step 3: Implement minimal loader with graceful absence handling**

```python
def load_vault_context(repo_root: Path, domain: str, surface: str) -> VaultContext:
    ...
```

- [ ] **Step 4: Run the tests and confirm green**

Run: `pytest agents/tests/test_vault_context_loader.py -p no:cacheprovider --basetemp=test-tmp`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/scripts/vault_context_loader.py agents/tests/test_vault_context_loader.py
git commit -m "feat(kb): load vault context for distillation"
```

### Task 3: Build a bounded entry indexer for pilot sources

**Files:**
- Create: `agents/scripts/distillation_indexer.py`
- Create: `agents/tests/test_distillation_indexer.py`
- Modify: `agents/scripts/distillation_models.py`

- [ ] **Step 1: Write the failing tests for entry segmentation**

```python
def test_index_entries_extracts_bounded_units_from_headings(tmp_path):
    entries = index_source_entries(sample_manifest_item, sample_text_file)
    assert [entry.title for entry in entries] == ["ABRAHAM", "ALTAR"]
    assert entries[0].aliases == ("ABRAM",)
    assert entries[0].raw_path.endswith("sample.txt")
    assert entries[0].start_anchor < entries[0].end_anchor
    assert entries[0].target_surface == "wiki"
    assert entries[0].target_domain == "historia-da-interpretacao"
    assert entries[0].confidence > 0

def test_index_entries_carries_see_also_and_bibliography_flags(tmp_path):
    entry = index_source_entries(sample_manifest_item, sample_text_file)[0]
    assert "ISAAC" in entry.see_also
    assert entry.bibliography_present is True
```

- [ ] **Step 2: Run indexer tests to verify they fail**

Run: `pytest agents/tests/test_distillation_indexer.py -p no:cacheprovider --basetemp=test-tmp`
Expected: FAIL with missing indexer or incorrect segmentation.

- [ ] **Step 3: Implement heading-based pilot heuristics and confidence scoring**

```python
def index_source_entries(item: SourceManifestItem, text_path: Path) -> list[DistilledEntry]:
    ...
```

- [ ] **Step 4: Run indexer plus previous tests**

Run: `pytest agents/tests/test_distillation_manifest.py agents/tests/test_vault_context_loader.py agents/tests/test_distillation_indexer.py agents/tests/test_raw_searcher.py -p no:cacheprovider --basetemp=test-tmp`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/scripts/distillation_models.py agents/scripts/distillation_indexer.py agents/tests/test_distillation_indexer.py
git commit -m "feat(kb): add entry indexing for pilot sources"
```

## Chunk 3: Claim Extraction, Corroboration, And Report Output

### Task 4: Extract typed claim candidates from indexed entries

**Files:**
- Create: `agents/scripts/claim_extractor.py`
- Create: `agents/tests/test_claim_extractor.py`
- Modify: `agents/scripts/distillation_models.py`

- [ ] **Step 1: Write the failing tests for factual vs inference extraction**

```python
def test_extract_claims_emits_factual_and_inference_items():
    claims = extract_claims(sample_entry)
    assert claims[0].claim_kind == "factual"
    assert any(claim.claim_kind == "agent_inference" for claim in claims)
    assert {"historical_context", "semantic_relations", "tradition_markers", "crossrefs", "open_questions"} <= {
        claim.category for claim in claims
    }

def test_extract_claims_preserves_canonical_provenance_string():
    claim = extract_claims(sample_entry)[0]
    assert claim.provenance.startswith("[Fonte: raw/")
    assert claim.unit_id == sample_entry.unit_id
    assert claim.source_level == sample_entry.nivel
    assert claim.excerpt
    assert claim.extraction_confidence > 0
```

- [ ] **Step 2: Run extractor tests to verify they fail**

Run: `pytest agents/tests/test_claim_extractor.py -p no:cacheprovider --basetemp=test-tmp`
Expected: FAIL with missing extractor/schema.

- [ ] **Step 3: Implement minimal typed extraction heuristics**

```python
def extract_claims(entry: DistilledEntry) -> list[ClaimCandidate]:
    ...
```

- [ ] **Step 4: Run extractor and dependency tests**

Run: `pytest agents/tests/test_claim_extractor.py agents/tests/test_distillation_indexer.py -p no:cacheprovider --basetemp=test-tmp`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/scripts/distillation_models.py agents/scripts/claim_extractor.py agents/tests/test_claim_extractor.py
git commit -m "feat(kb): extract typed claim candidates"
```

### Task 5: Corroborate claims and enforce epistemic gates

**Files:**
- Create: `agents/scripts/corroboration_engine.py`
- Create: `agents/tests/test_corroboration_engine.py`
- Modify: `agents/scripts/distillation_models.py`

- [ ] **Step 1: Write the failing tests for epistemic transitions and gates**

```python
def test_corroboration_promotes_to_knowledge_with_two_independent_level_2_3_sources():
    result = corroborate_claim_group(sample_group, level1_check="pass")
    assert result.target_state == "knowledge"

def test_agent_inference_stays_staged_until_reclassified():
    result = corroborate_claim_group(inference_only_group, level1_check="pass")
    assert result.ready_for_promotion is False

def test_rule_requires_three_sources_and_two_traditions():
    result = corroborate_claim_group(rule_group, level1_check="pass")
    assert result.target_state == "rule"

def test_unresolved_level1_check_blocks_promotion():
    result = corroborate_claim_group(sample_group, level1_check="unresolved_manual_review")
    assert result.ready_for_promotion is False

def test_stronger_contradiction_can_downgrade_rule_to_hypothesis():
    result = reconcile_existing_state(existing_state="rule", contradicted_by_level1=True)
    assert result.target_state == "hypothesis"

def test_routing_conflict_keeps_item_staged():
    result = corroborate_claim_group(conflicting_group, level1_check="pass")
    assert result.status == "staged_conflict"
```

- [ ] **Step 2: Run corroboration tests to verify they fail**

Run: `pytest agents/tests/test_corroboration_engine.py -p no:cacheprovider --basetemp=test-tmp`
Expected: FAIL with missing engine or wrong thresholds.

- [ ] **Step 3: Implement minimal corroboration engine with explicit `level1_check` gate**

```python
def corroborate_claim_group(group: ClaimGroup, level1_check: str) -> CorroborationDecision:
    ...
```

- [ ] **Step 4: Run corroboration and extractor tests**

Run: `pytest agents/tests/test_corroboration_engine.py agents/tests/test_claim_extractor.py -p no:cacheprovider --basetemp=test-tmp`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/scripts/distillation_models.py agents/scripts/corroboration_engine.py agents/tests/test_corroboration_engine.py
git commit -m "feat(kb): enforce epistemic corroboration rules"
```

### Task 6: Generate staging outputs and a pilot report

**Files:**
- Create: `agents/scripts/distillation_pipeline.py`
- Create: `agents/tests/test_distillation_pipeline.py`
- Modify: `agents/scripts/distillation_manifest.py`
- Modify: `agents/scripts/distillation_indexer.py`
- Modify: `agents/scripts/claim_extractor.py`
- Modify: `agents/scripts/corroboration_engine.py`

**Ownership:** controller-owned integration task. Do not run in parallel with Tasks 4 or 5.

- [ ] **Step 1: Write the failing integration tests for pipeline outputs**

```python
def test_pipeline_writes_manifest_index_claims_and_report(tmp_path):
    outputs = run_distillation_pipeline(repo_root=tmp_path, output_dir=tmp_path / "agents" / "output")
    assert (tmp_path / "agents" / "output" / "raw_manifest.json").exists()
    assert (tmp_path / "agents" / "output" / "distillation" / "entry_index.jsonl").exists()
    assert (tmp_path / "agents" / "output" / "distillation" / "claim_candidates.jsonl").exists()
    assert (tmp_path / "agents" / "output" / "distillation" / "corroborated_claims.jsonl").exists()
    assert outputs.report_path == tmp_path / "vault" / "reports" / "tematicos" / "2026-04-05_kb-distillation-pilot.md"

def test_pipeline_never_writes_canonical_wiki_or_knowledge(tmp_path):
    run_distillation_pipeline(repo_root=tmp_path, output_dir=tmp_path / "agents" / "output")
    assert not any((tmp_path / "vault" / "wiki").rglob("*.generated.md"))
    assert not any((tmp_path / "vault" / "knowledge").rglob("*.generated.md"))
    assert not any((tmp_path / "vault" / "Bíblia").rglob("*.generated.md"))

def test_pipeline_uses_expected_pilot_sources_and_emits_proposal_gates(tmp_path):
    outputs = run_distillation_pipeline(repo_root=tmp_path, output_dir=tmp_path / "agents" / "output")
    assert outputs.pilot_siglas == ["AYBD", "NIDB", "DJG2", "DDD", "EAC"]
    assert all(item["proposal_flag"] == "[PROPOSTA — aguarda aprovação do proprietário]" for item in outputs.proposals)
    assert all(item["owner_approval_required"] is True for item in outputs.proposals)
```

- [ ] **Step 2: Run integration tests to verify they fail**

Run: `pytest agents/tests/test_distillation_pipeline.py -p no:cacheprovider --basetemp=test-tmp`
Expected: FAIL with missing pipeline or missing outputs.

- [ ] **Step 3: Implement the pipeline CLI and report generation**

```python
def run_distillation_pipeline(repo_root: Path, output_dir: Path, pilot_siglas: list[str] | None = None) -> PipelineOutputs:
    ...
```

- [ ] **Step 4: Run focused suite for all new pipeline tests**

Run: `pytest agents/tests/test_distillation_manifest.py agents/tests/test_vault_context_loader.py agents/tests/test_distillation_indexer.py agents/tests/test_claim_extractor.py agents/tests/test_corroboration_engine.py agents/tests/test_distillation_pipeline.py agents/tests/test_raw_searcher.py agents/tests/test_lint_checker.py -p no:cacheprovider --basetemp=test-tmp`
Expected: PASS.

- [ ] **Step 4.1: Verify canonical vault trees remain untouched**

Run: `git diff --name-only -- vault/wiki vault/knowledge "vault/Bíblia"`
Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add agents/scripts/distillation_pipeline.py agents/scripts/distillation_manifest.py agents/scripts/distillation_indexer.py agents/scripts/claim_extractor.py agents/scripts/corroboration_engine.py agents/tests/test_distillation_pipeline.py
git commit -m "feat(kb): add staged distillation pipeline"
```

## Chunk 4: Final Verification

### Task 7: Run end-to-end verification and summarize residual risk

**Files:**
- Modify: `docs/superpowers/plans/2026-04-05-kb-distillation-pipeline.md`

- [ ] **Step 1: Run the complete relevant suite fresh**

Run: `pytest agents/tests/test_distillation_manifest.py agents/tests/test_vault_context_loader.py agents/tests/test_distillation_indexer.py agents/tests/test_claim_extractor.py agents/tests/test_corroboration_engine.py agents/tests/test_distillation_pipeline.py agents/tests/test_raw_searcher.py agents/tests/test_lint_checker.py -p no:cacheprovider --basetemp=test-tmp`
Expected: PASS.

- [ ] **Step 2: Review outputs and confirm canonical vault paths were untouched**

Run: `git status --short`
Expected: only intended script/test/output changes in this branch.

- [ ] **Step 3: Mark plan state and commit if needed**

```bash
git add docs/superpowers/plans/2026-04-05-kb-distillation-pipeline.md
git commit -m "docs(kb): record distillation execution plan"
```
