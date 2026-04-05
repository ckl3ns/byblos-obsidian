# Full Verse Nodes Graph Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Incluir todos os versículos do vault como nós do grafo NTSK, deixando versos sem bloco NTSK explícitos com `ref_count = 0` e removendo falsos positivos de `unresolved_targets`.

**Architecture:** O `vault` continua sendo a fonte principal dos nós. `graph_builder.py` passa a registrar todos os nós de versículo em `metas`, enquanto o parse NTSK continua sendo executado apenas para versos com `ntsk_raw`. `unresolved_targets` passa a ser calculado contra o conjunto completo de versículos reais.

**Tech Stack:** Python, pytest, parser NTSK existente, builder do grafo.

---

## Chunk 1: Graph Builder Behavior

### Task 1: Cobrir o novo comportamento com testes

**Files:**
- Modify: `agents/tests/test_graph_builder.py`
- Reference: `agents/scripts/graph_builder.py`
- Reference: `agents/scripts/vault_parser.py`

- [ ] **Step 1: Write the failing tests**

Adicionar testes para:
- versículo sem `ntsk_raw` aparecer em `nodes` com `ref_count = 0`
- target válido apontando para versículo sem NTSK não entrar em `unresolved_targets`
- target inválido continuar em `unresolved_targets`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest agents/tests/test_graph_builder.py -v`
Expected: FAIL nos novos testes, porque o builder atual só inclui versículos com `ntsk_raw`.

- [ ] **Step 3: Write minimal implementation**

Modificar `build_graph()` para:
- incluir todos os `node_type == "versiculo"` em `metas`
- preencher `ref_count = 0`, `strong_h = []`, `strong_g = []` quando `ntsk_raw` ausente
- gerar arestas apenas quando houver `ntsk_raw`
- calcular `source_ids` a partir de todos os nós de versículo

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest agents/tests/test_graph_builder.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agents/tests/test_graph_builder.py agents/scripts/graph_builder.py
git commit -m "feat(graph): include all verse nodes in graph metadata"
```

### Task 2: Verificar regressões do parser e builder

**Files:**
- Test: `agents/tests/test_ntsk_parser.py`
- Test: `agents/tests/test_graph_builder.py`

- [ ] **Step 1: Run targeted regression suite**

Run: `python -m pytest agents/tests/test_ntsk_parser.py agents/tests/test_graph_builder.py -v`
Expected: PASS

- [ ] **Step 2: Commit if needed**

Se houve ajuste pequeno de teste/documentação de comportamento, commitar com mensagem semântica apropriada.

## Chunk 2: Full Verification

### Task 3: Validar a suíte completa antes de merge

**Files:**
- Reference: `agents/tests/`

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest agents/tests/ agents/scripts/extractors/tests/ -v`
Expected: PASS completo

- [ ] **Step 2: Generate fresh graph stats if needed for spot-check**

Run: `python agents/scripts/graph_builder.py vault agents/output`
Expected: comando concluído com JSONs atualizados e `unresolved_targets` mais próximos de erros reais

- [ ] **Step 3: Review git diff**

Run: `git status --short` and `git diff --stat`
Expected: apenas mudanças intencionais

- [ ] **Step 4: Merge and push only after fresh verification**

```bash
git checkout main
git merge --no-ff feat/graph-full-verse-nodes -m "merge: include full verse nodes in NTSK graph"
git push origin main
```
