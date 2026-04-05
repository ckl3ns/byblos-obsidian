# NTSK Reference Normalization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize NTSK book abbreviations to the Logos sigla before extraction and fix qualifier, range, and carryover parsing so valid references stop leaking into `unresolved_targets`.

**Architecture:** Replace the stale hardcoded book map with mappings derived from `docs/ntsk/ntsk_2_sigla.json` and `docs/ntsk/bible_books.json`, then tighten the parser around canonical book tokens. Keep the graph builder unchanged and prove behavior through parser regression tests built from real unresolved cases.

**Tech Stack:** Python, pytest, JSON metadata from `docs/ntsk`

---

## Chunk 1: Canonical Book Mapping

### Task 1: Add failing tests for canonical book normalization

**Files:**
- Modify: `agents/tests/test_ntsk_parser.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_ex_maps_to_logos_exodo():
    ref = parse_ntsk_block("Ex 3:2.", "Êx 3.1")["refs"][0]
    assert ref.book_vault == "Êx"


def test_jb_maps_to_logos_jo():
    ref = parse_ntsk_block("Jb 1:1.", "Jó 1.1")["refs"][0]
    assert ref.book_vault == "Jó"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest agents/tests/test_ntsk_parser.py -k "maps_to_logos" -v`
Expected: FAIL because the parser still uses a stale hardcoded map.

- [ ] **Step 3: Write minimal implementation**

Load canonical mappings from `docs/ntsk/ntsk_2_sigla.json` and `docs/ntsk/bible_books.json`, prioritizing `logos` as the canonical output and preserving safe aliases.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest agents/tests/test_ntsk_parser.py -k "maps_to_logos" -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agents/scripts/ntsk_parser.py agents/tests/test_ntsk_parser.py
git commit -m "test(ntsk): cover canonical logos book normalization"
```

## Chunk 2: Qualifiers and Real Unresolved Cases

### Task 2: Add failing tests for qualifiers and mixed ranges

**Files:**
- Modify: `agents/tests/test_ntsk_parser.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_reference_with_mg_qualifier_keeps_verse():
    ref = parse_ntsk_block("Jn 24:24mg.", "Jo 24.23")["refs"][0]
    assert ref.target_id() == "Jo 24.24"


def test_comma_and_range_expand_together():
    ref = parse_ntsk_block("Le 7:24, 26, 30-34.", "Lv 9.21")["refs"][0]
    assert ref.verses == ["24", "26", "30", "31", "32", "33", "34"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest agents/tests/test_ntsk_parser.py -k "qualifier or range_expand" -v`
Expected: FAIL because qualifiers leak into verse parsing and mixed ranges are not fully expanded.

- [ ] **Step 3: Write minimal implementation**

Strip or classify NTSK qualifiers (`mg`, `n`, `g`, `h`, `a`, `b`, `c`) before verse expansion and teach `_expand_verses()` to expand mixed comma-plus-range inputs.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest agents/tests/test_ntsk_parser.py -k "qualifier or range_expand" -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agents/scripts/ntsk_parser.py agents/tests/test_ntsk_parser.py
git commit -m "feat(ntsk): support qualifiers and mixed verse ranges"
```

## Chunk 3: Carryover Regressions and Graph Verification

### Task 3: Add failing tests for chapter carryover regressions

**Files:**
- Modify: `agents/tests/test_ntsk_parser.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_chapter_progression_does_not_collapse_into_previous_chapter():
    refs = parse_ntsk_block(
        "Le 7:37, 38. 11:46. 13:59. 14:54-57. 15:32, 33. 27:34.",
        "Nm 36.13",
    )["refs"]
    ids = [(ref.chapter, ref.verses) for ref in refs]
    assert ids == [
        ("7", ["37", "38"]),
        ("11", ["46"]),
        ("13", ["59"]),
        ("14", ["54", "55", "56", "57"]),
        ("15", ["32", "33"]),
        ("27", ["34"]),
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest agents/tests/test_ntsk_parser.py -k "chapter_progression" -v`
Expected: FAIL because the parser currently merges later chapter references into chapter 7.

- [ ] **Step 3: Write minimal implementation**

Adjust carryover and chain splitting so `cap:vers` sequences after the first explicit reference become chapter transitions when they are part of the same-book chain.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest agents/tests/test_ntsk_parser.py -k "chapter_progression" -v`
Expected: PASS

- [ ] **Step 5: Run broader verification and commit**

Run: `python -m pytest agents/tests/test_ntsk_parser.py agents/tests/test_graph_builder.py -v`
Expected: PASS

Run: `python agents/scripts/graph_builder.py vault agents/output`
Expected: Graph regenerates successfully and `unresolved_targets` no longer include the covered regression cases.

```bash
git add agents/scripts/ntsk_parser.py agents/tests/test_ntsk_parser.py agents/output/graph_stats.json agents/output/edges.json agents/output/nodes.json
git commit -m "fix(ntsk): normalize book aliases before graph extraction"
```
