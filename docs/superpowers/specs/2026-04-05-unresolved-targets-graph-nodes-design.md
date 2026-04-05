# Full Verse Nodes for NTSK Graph Design

## Context

O grafo NTSK atual monta `nodes` e `source_ids` apenas a partir de versiculos que possuem `ntsk_raw`. Isso cria uma ambiguidade em `unresolved_targets`: uma parte da lista representa targets realmente invalidos ou mal normalizados, mas outra parte representa versiculos biblicos validos que existem no vault e nao possuem bloco NTSK proprio.

O objetivo desta mudanca e deixar explicito no grafo quando um versiculo existe, mas nao possui referencias cruzadas locais, para facilitar a auditoria de extracao e reduzir falsos positivos em `unresolved_targets`.

## Goal

Todos os versiculos biblicos do vault devem aparecer como nos no grafo. Versiculos sem bloco NTSK devem entrar com metadados basicos, `ref_count = 0` e sem arestas de saida. Com isso, `unresolved_targets` deve passar a representar apenas targets que continuam sem correspondencia no conjunto completo de versiculos.

## Recommended Approach

Modificar `agents/scripts/graph_builder.py` para incluir todos os `node_type == "versiculo"` em `metas`, independentemente de possuirem `ntsk_raw`. O parse NTSK continua sendo executado apenas quando `ntsk_raw` existir, preservando o custo atual da extracao. O calculo de `source_ids` passa entao a refletir todos os versiculos reais do vault.

Essa abordagem atende ao requisito funcional com a menor mudanca estrutural: nao exige remodelar o parser NTSK, nao mistura o problema com extractors e nao depende de listas paralelas para explicar a ausencia de referencias.

## Alternatives Considered

### 1. Criar lista separada para `valid_targets_without_ntsk`

Melhora o diagnostico do relatorio, mas mantem o grafo incompleto. O consumidor ainda precisaria interpretar duas estruturas para saber se um versiculo existe ou nao.

### 2. Apenas normalizar melhor `unresolved_targets`

E uma melhora parcial, mas nao resolve o problema de representacao. Versiculos validos sem NTSK continuariam parecendo anomalias em vez de nos explicitos sem arestas.

## Design Details

### Node Construction

- Incluir em `metas` todos os versiculos do vault.
- Para versiculos com `ntsk_raw`:
  - manter parse atual
  - preencher `ref_count`, `strong_h`, `strong_g`
  - gerar arestas forward e inverse
- Para versiculos sem `ntsk_raw`:
  - manter `id`, `sigla`, `livro`, `capitulo`, `versiculo`, `testamento`, `canon_cristao`
  - definir `ref_count = 0`
  - definir `strong_h = []` e `strong_g = []`
  - nao gerar arestas forward

### Unresolved Semantics

- `source_ids` deve ser derivado de todos os nos de versiculo presentes em `metas`, nao apenas dos que possuem `ntsk_raw`.
- `unresolved_targets` deve manter apenas targets forward que nao correspondem a nenhum versiculo real do vault.
- Isso deve reduzir `unresolved_targets` para um conjunto muito mais proximo de:
  - erros reais de parse
  - alias nao normalizados
  - ruido editorial residual

### Compatibility

- O formato geral do JSON exportado permanece o mesmo.
- Consumidores existentes continuam recebendo `nodes`, `edges` e `stats`.
- A mudanca principal e semantica: `nodes` passa a cobrir todo o universo de versiculos, e `unresolved_targets` fica mais confiavel como sinal de erro real.

## Testing Strategy

Seguir TDD em `agents/tests/` com foco nestes cenarios:

1. Um versiculo sem `ntsk_raw` deve aparecer em `nodes` com `ref_count = 0`.
2. Um target forward que aponta para um versiculo real sem `ntsk_raw` nao deve entrar em `unresolved_targets`.
3. Um target realmente invalido deve continuar em `unresolved_targets`.
4. O comportamento corrigido de intervalos `cap.vers-vers` deve continuar preservado.

## Risks

- Algumas metricas de `total_nodes` vao aumentar, porque agora refletirao todos os versiculos do vault em vez de apenas os versiculos com bloco NTSK.
- Testes ou scripts que assumam implicitamente a definicao antiga de `nodes` podem precisar de ajuste.
- Se houver consumidores externos interpretando `unresolved_targets` com a semantica antiga, a documentacao deve deixar a mudanca explicita.

## Out of Scope

- Reescrever o parser NTSK para resolver todos os residuos editoriais observados em `unresolved_targets`.
- Criar novas categorias de stats para classificacao detalhada de targets invalidos.
- Alterar o pipeline de extractors ou o lint do vault.
