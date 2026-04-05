# KB Distillation Pipeline Design

**Date:** 2026-04-05
**Branch:** `feature/kb-distillation-pipeline`
**Worktree:** `C:\workspace\byblos-obsidian\.worktrees\feature-kb-distillation-pipeline`

## Goal

Transform the material in `raw/dicionarios-enciclopedias/` into structured, reviewable, and epistemically safe staging artifacts that agents can use to propose persistent knowledge for the vault.

Phase 1 does **not** write directly to `vault/wiki/` or `vault/knowledge/`. It prepares reproducible staging data and proposal-ready outputs.

## Problem Statement

The repository already contains:

- raw corpora in `raw/dicionarios-enciclopedias/`
- high-level source profiles in `vault/wiki/obras/`
- epistemic rules in `CLAUDE.md` and `agents/AGENTS.md`
- a search primitive in `agents/scripts/raw_searcher.py`

The current search layer is useful for retrieving local context with provenance, but it is not enough for knowledge persistence because it operates on text windows rather than stable knowledge units such as entries, concepts, people, practices, or historical topics.

Without an intermediate segmentation and corroboration layer, agents would promote search fragments instead of distilled knowledge.

## Constraints

- Never modify files in `vault/Bíblia/`.
- Never write directly to `vault/knowledge/` without explicit owner approval.
- Factual claims for `vault/wiki/` require Level 1-3 support.
- Level 4 works can shape interpretation, scoping, and hypotheses, but cannot independently justify factual promotion.
- All generated claims must preserve provenance back to `raw/...`.
- The first phase must be additive and reversible.

## Source Classes

The available raw material falls into a few operational classes:

1. General academic Bible dictionaries
   - Examples: `AYBD`, `NIDB`
   - Best for concepts, historical background, people, places, and broad synthesis

2. Corpus-specialized dictionaries
   - Examples: `DJG2`, `DPL2`, `DLNT`, `DNT-B`, `DOT-*`
   - Best for canon-aware distillation tied to NT/OT subcorpora

3. Theme-specialized works
   - Examples: `DDD`, `DBI-R`
   - Best for motifs, imagery, deities, symbols, and semantic networks

4. Theology and hermeneutics references
   - Examples: `EDT`, `DTIB`
   - Best for interpretive framing, doctrinal vocabulary, and hypothesis generation

5. Patristics / ancient Christianity
   - Example: `EAC`
   - Best for reception history, figures, councils, and early Christian contexts

## Options Considered

### Option A: Direct search-to-note promotion

Agents query `raw_searcher`, extract useful paragraphs, and write proposals immediately.

**Pros**
- Fastest to start
- Minimal code changes

**Cons**
- Promotes unstable text windows instead of bounded units
- Hard to deduplicate
- Weak for cross-source corroboration
- Highest epistemic risk

### Option B: Staged segmentation pipeline

Agents first build a normalized index of extractable units, then derive candidate claims, then corroborate those claims before emitting proposals.

**Pros**
- Best fit for repository epistemology
- Repeatable and auditable
- Enables later automation and linting
- Separates extraction from promotion

**Cons**
- More upfront pipeline work
- Requires source-specific heuristics

### Option C: Manual curation only

Use the existing source profiles and have agents manually draft proposals from a small corpus.

**Pros**
- High precision for a pilot
- Low engineering cost

**Cons**
- Does not scale
- Produces little reusable infrastructure

## Recommended Approach

Use **Option B: Staged segmentation pipeline**.

This repository already has strong epistemic rules. The safest and most reusable path is to add a staging layer between raw search and any persistent knowledge proposal.

## Target Architecture

### 1. Source Manifest

Create a machine-readable manifest describing each work:

- `sigla`
- `nivel`
- `source_class`
- `domains`
- `physical_layout`
- `expected_unit_types`
- `preferred_usage`
- `promotion_limits`

This becomes the routing table for downstream distillation.

### 2. Entry Indexer

Parse raw files into bounded units such as:

- concept entries
- people entries
- place entries
- motif / imagery entries
- deity entries
- historical-context entries
- reception-history entries

Each indexed unit should carry:

- `unit_id`
- `unit_type`
- `title`
- `aliases`
- `sigla`
- `independence_group`
- `tradition`
- `target_surface`
- `target_domain`
- `raw_path`
- `start_anchor`
- `end_anchor`
- `see_also`
- `bibliography_present`
- `confidence`

### 3. Claim Extractor

For each indexed unit, produce structured claim candidates separated by type:

- `factual_claims`
- `historical_context`
- `semantic_relations`
- `tradition_markers`
- `crossrefs`
- `open_questions`

Each claim candidate must preserve:

- exact source
- unit id
- source level
- excerpt or anchor reference
- extraction confidence
- canonical provenance string in the format `[Fonte: raw/... | Obra: ... | Nível: ...]`
- `claim_kind = factual | agent_inference`

### 4. Vault Context Loader

Before any corroboration or proposal emission, the pipeline must load the existing vault context required by `CLAUDE.md`:

- `vault/indices/INDEX.md`
- the existing article in `vault/wiki/` for the current domain, if present
- `vault/knowledge/{dominio}/hypotheses.md`
- `vault/knowledge/{dominio}/knowledge.md`
- `vault/knowledge/{dominio}/rules.md`

This preflight prevents duplicate work, detects existing proposals, and ensures the pipeline routes candidates with awareness of the current epistemic state.

`rules.md` is not loaded as passive context only. It must be applied as the default policy layer for routing, corroboration, and promotion decisions.

### 5. Corroboration Layer

Cross-check claim candidates across sources:

- promote only when 2+ independent Level 2-3 witnesses agree
- verify absence of contradiction with Level 1 evidence
- hold Level 4-only material as framing or hypothesis
- require 3+ independent Level 2-3 witnesses plus 2 traditions for `rule`
- allow epistemic downgrade when later evidence contradicts a prior stronger state
- flag conflicts with corpus-specific routing rules
- keep unresolved items in staging

The corroboration layer must model the full state machine:

- `hypothesis -> knowledge`
- `knowledge -> rule`
- `rule -> hypothesis` when contradicted by stronger evidence

Because Phase 1 starts from `raw/dicionarios-enciclopedias/`, the Level 1 check must expose an explicit gate:

- `level1_check = pass`
- `level1_check = unresolved_manual_review`

If the pipeline cannot verify the claim against primary-text evidence, the candidate remains staged and cannot be emitted as a promotion-ready factual item.

### 6. Proposal Emitter

Emit proposal-ready artifacts, but do not auto-persist them into canonical vault locations in Phase 1.

Outputs should be suitable for later use by:

- `WikiCompilerAgent`
- `ResearchAgent`
- `LintAgent`

## File and Output Strategy

Phase 1 should prefer non-canonical outputs:

- `agents/output/raw_manifest.json`
- `agents/output/distillation/entry_index.jsonl`
- `agents/output/distillation/claim_candidates.jsonl`
- `agents/output/distillation/corroborated_claims.jsonl`
- `vault/reports/tematicos/YYYY-MM-DD_kb-distillation-pilot.md`

No automatic writes to:

- `vault/wiki/`
- `vault/knowledge/`

Those remain downstream, gated actions.

## Agent Responsibilities

### Ingestion / Routing

Use source manifest metadata plus the vault context loader to decide which works are valid for each query, corpus, domain, and target surface.

### Distillation

Agents operate on indexed units, not on ad hoc search windows.

### Persistence

Phase 1 agents may only emit:

- staging artifacts
- reports
- proposal blocks with explicit owner gate:
  - `proposal_flag = [PROPOSTA — aguarda aprovação do proprietário]`
  - `owner_approval_required = true`
  - `target_state = hypothesis | knowledge | rule`
  - `target_surface = wiki | knowledge`
  - `target_domain`

`claim_kind = agent_inference` may only generate:

- a staged review item
- a hypothesis-oriented proposal

It may not be emitted as a promotion-ready factual claim for `wiki` or `knowledge` until later corroboration reclassifies it as factual.

## Initial Scope

The first implementation slice should focus on a representative mix:

- `AYBD`
- `NIDB`
- one IVP-Black dictionary
- `DDD`
- `EAC`

This gives enough variety to validate segmentation heuristics across:

- general dictionary
- corpus-specific dictionary
- motif/deity reference
- reception-history source

## Risks

### OCR / pagination noise

Raw text may contain headers, page breaks, or bibliography spillover that corrupt unit boundaries.

### Work-level versus article-level voice

Collective works do not speak with one voice. The pipeline must treat each unit as authored content, not as a universal position of the whole work.

### Over-promotion

Level 4 material can tempt the agent into doctrinal synthesis that is not yet corroborated by Level 1-3 evidence.

### Weak entry detection

Some files may not expose clean entry headers, requiring heuristics and confidence scoring.

## Success Criteria

Phase 1 is successful when:

1. We can index bounded units from representative sources.
2. We can extract structured claim candidates with provenance.
3. We can separate candidate facts from context, relations, and hypotheses.
4. We can route candidate outputs with awareness of existing wiki and knowledge state.
5. We can produce a pilot report showing what is ready for later promotion.
6. We can emit proposal-ready artifacts with explicit epistemic state and approval gate.
7. No canonical vault area is modified automatically.

## Immediate Next Step

Write an implementation plan for the staged pipeline, starting with:

1. source manifest generation
2. entry indexing for a small pilot set
3. claim extraction schema
4. corroboration rules
5. report generation
