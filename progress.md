# Progress

- Sessão iniciada para analisar `unresolved_targets` com apoio de `docs/ntsk`.
- Lidos `docs/ntsk/howto.txt`, `docs/ntsk/symbols.txt`, `docs/ntsk/ntsk_2_sigla.json`, `docs/ntsk/sigla_2_nome.json` e `docs/ntsk/noref.txt`.
- Cruzados `unresolved_targets` com o mapa de siglas e com `noref.txt` para separar referencias validas, alias de livro e ruido editorial.
- Verificado no codigo que `unresolved_targets` significa `target` sem `source_id` correspondente no grafo atual, e nao necessariamente referencia biblica inexistente.
- Inspecionada `.planning` para avaliar risco de conflito com outros agentes; o ponto principal de sobreposicao futura esta em `ntsk_parser.py`.
- Aguardando a versao final do codigo antes de implementar alteracoes.
- Reanalisado o repositório apos merges recentes: `main` ja contem o fix de BUG-001 no `ntsk_parser.py`, alem das frentes de extractors, lint e limpeza de documentacao.
- Branch `feat/graph-full-verse-nodes` criada para concentrar a proxima fase do trabalho.
- Spec de design escrito em `docs/superpowers/specs/2026-04-05-unresolved-targets-graph-nodes-design.md`.
- Plano de implementacao escrito em `docs/superpowers/plans/2026-04-05-full-verse-nodes-graph.md`.
- Nova branch `feat/ntsk-reference-normalization` criada para a frente de normalizacao do parser NTSK.
- Reabertos `docs/ntsk/bible_books.json`, `docs/ntsk/ntsk_2_sigla.json` e `docs/ntsk/symbols.txt` para guiar a padronizacao de siglas e qualificadores.
- Confirmado por experimentos dirigidos que o parser atual falha em `Ex -> Êx`, `Jb -> Jó`, refs com `mg` e ranges mistos com carryover de capitulo.
- Novo plano de implementacao salvo em `docs/superpowers/plans/2026-04-05-ntsk-reference-normalization.md`.
- Testes de regressao escritos em `agents/tests/test_ntsk_parser.py` para siglas canonicas, qualificadores NTSK e casos reais de `unresolved_targets`.
- `agents/scripts/ntsk_parser.py` atualizado para carregar o mapeamento a partir de `docs/ntsk`, normalizar siglas antes do parse e expandir corretamente ranges mistos e cadeias de capitulos.
- Verificacao executada: `python -m pytest agents/tests/ agents/scripts/extractors/tests/ -v` com `87 passed`.
- Grafo regenerado com `python agents/scripts/graph_builder.py vault agents/output`; resultado atual: `30989` nos, `1082304` arestas e `5058` unresolved targets.
