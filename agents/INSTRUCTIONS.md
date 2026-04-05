# INSTRUCTIONS.md — Guia Operacional por Tarefa
> Vault Bíblico-Teológico | v1.0 | 2026-04-04

---

## Tarefa 1 — Enriquecimento de Versículo

**Agente:** EnrichmentAgent  
**Gatilho:** `kb enrich Fm-1.1` ou pedido direto

### Passo a passo

1. **Ler o nó** (`Bíblia/{Sigla}-{cap}.{vs}.md`)
   - Extrair: referência, testamento, texto KJV/BKJ, bloco NTSK
   - Executar `ntsk_parser.py` para obter Strong numbers e referências tipológicas

2. **Consultar léxico** (Nível 2)
   - Para cada Strong hebraico: HALOT → BDB
   - Para cada Strong grego: BDAG → TDNT
   - Registrar: `lemma | transliteração | glosa | domínio semântico | usos paralelos relevantes`

3. **Consultar dicionário** (Nível 3)
   - Usar a tabela "Decisão de Obra por Corpus" de AGENTS.md
   - Prioridade: obra 1ª consulta → obra 2ª consulta → contexto
   - Extrair apenas o que o versículo especificamente evoca (não resuma o artigo inteiro)

4. **Registrar posições exegéticas**
   - Mínimo 2 tradições: reformada/luterana, católica/patrística, pentecostal (quando relevante)
   - Anotar ponto de divergência específico, não apenas "há debate"

5. **Escrever as seções** (ao final do arquivo, nesta ordem):

```markdown
## Léxico

| Strong | Termo | Transliteração | Glosa | Domínio | Nota |
|--------|-------|----------------|-------|---------|------|
| G5547  | Χριστός | Christos | Ungido/Messias | título | ... |

[Fonte: raw/bdag/christos.md | Obra: BDAG | Nível: 2]

## Contexto Histórico-Cultural

{2–4 parágrafos, máximo. Foco no que o versículo pressupõe culturalmente.}

[Fonte: raw/... | Obra: ... | Nível: ...]

## Posições Exegéticas

**Tradição reformada/luterana:**
{posição + justificativa textual}

**Tradição católica/patrística:**
{posição + fonte patrística se houver}

**Tradição pentecostal/carismática:** *(se relevante)*
{posição}

**Ponto de divergência central:**
{o que especificamente está em debate}

## Conexões no Grafo

- Referências tipológicas (✡): {lista ou "nenhuma"}
- Citações AT→NT (▶): {lista ou "nenhuma"}
- Versículos em contraste (◐): {lista ou "nenhuma"}
- Temas cruzados em wiki/: {links ou "pendente"}

## Lacunas Identificadas

- [INFERÊNCIA DO AGENTE] {hipótese ou conexão sugerida, sem fonte confirmada}
- Fontes ainda não consultadas para esta passagem: {lista de siglas}
```

---

## Tarefa 2 — Artigo de Perícope

**Agente:** WikiCompilerAgent  
**Output:** `wiki/conceitos/{sigla}_{ref}.md`

### Template

```markdown
---
tipo: pericope
referencia: "{e.g. Fm 1:1-7}"
sigla_livro: Fm
capitulo: 1
versiculo_inicio: 1
versiculo_fim: 7
testamento: NT
criado: YYYY-MM-DD
revisado: YYYY-MM-DD
tags: [epistolar, saudação, ecclesiologia]
---

# {Referência} — {Título Descritivo}

## Delimitação

{Justificativa da fronteira literária. Por que começa aqui e termina ali?}

[Fonte: ... | Nível: ...]

## Estrutura Literária

{Diagrama textual ou lista hierárquica dos movimentos internos da perícope}

## Contexto Canônico

- **Contexto imediato:** {o que vem antes/depois no mesmo livro}
- **Macro-contexto:** {posição no corpus autoral/testamentário}
- **Contexto do cânon:** {conexões com outras partes da Bíblia}

## Análise Versículo a Versículo

{Links para nós individuais: [[Fm-1.1]], [[Fm-1.2]], etc.}

## Teologia da Perícope

{2–5 afirmações teológicas derivadas diretamente do texto. Com proveniência.}

## Lacunas e Agenda de Pesquisa

- [ ] {questão aberta}
- [ ] {fonte ainda não consultada}
```

---

## Tarefa 3 — Artigo de Conceito Teológico

**Agente:** WikiCompilerAgent  
**Gatilho:** conceito aparece em 3+ versículos no grafo sem página própria  
**Output:** `wiki/conceitos/{slug}.md`

### Template

```markdown
---
tipo: conceito
titulo: "{e.g. Apóstolo}"
dominio: [ecclesiologia, missão]
testamentos: [AT, NT]
Strong_H: []
Strong_G: [G652]
criado: YYYY-MM-DD
---

# {Título}

## Terminologia Original

| Língua | Termo | Strong | Transliteração | Glosa básica |
|--------|-------|--------|----------------|--------------|

## O que este conceito NÃO é

{Distinções negativas são tão importantes quanto as positivas. Delimitar o campo.}

## Desenvolvimento Canônico

### No AT
### No NT — Evangelhos
### No NT — Paulinas
### No NT — Epístolas Gerais e Apocalipse

## Posições Teológicas

| Tradição | Posição | Base textual |
|----------|---------|-------------|

## Versículos-Chave no Vault

{Dataview ou lista manual de [[links]] com breve comentário de cada um}

## Lacunas
```

---

## Tarefa 4 — Análise de Grafo NTSK

**Agente:** ResearchAgent + GraphAnalystAgent  
**Uso:** entender o estado do grafo, encontrar conexões não óbvias

### Queries Dataview úteis

```dataview
TABLE referencia, testamento, canon_cristao
FROM "Bíblia"
WHERE versiculo != null AND ntsk_raw != null
SORT referencia ASC
```

```dataview
TABLE referencia, target, edge_type
FROM "agents/output"
WHERE edge_type = "fulfills_prophecy"
LIMIT 50
```

### Via Python (para grafos maiores)

```bash
python agents/scripts/graph_builder.py . agents/output
# Abre agents/output/graph_stats.json para ver distribuição de arestas
```

---

## Tarefa 5 — Ingesta de Obra em raw/

**Agente:** IngestionAgent  
**Output:** `wiki/obras/{sigla}.md` + arquivo na pasta correta em `raw/`

### Template da ficha de obra

```markdown
---
tipo: obra
sigla: AYBD
nivel_autoridade: 3
autor: David Noel Freedman (ed.)
editora: Yale University Press
ano: 1992
volumes: 6
dominio: [AT, NT, arqueologia, história]
caminho_raw: raw/AYBD/
---

# {Sigla} — {Título Completo}

## Perfil do Autor/Editor

## Posição Hermenêutica

{Qual a postura crítica e teológica? Histórico-crítica? Evangélica? Ecumênica?}

## Pontos Fortes

## Limitações e Vieses Conhecidos

## Como Usar neste Vault

{Orientação específica: para que tipo de pergunta esta obra é a primeira consulta?}
```

---

## Tarefa 6 — Lint Semanal

**Agente:** LintAgent  
**Output:** `reports/lint/YYYY-MM-DD.md`

### Checklist de verificação

```
[ ] Nós de versículo sem seção ## Léxico mas com Strong numbers no NTSK
[ ] Seções factuais sem [Fonte: ...] — regex: /^(?!.*\[Fonte:).*[A-Z].{20,}/m
[ ] Inferências fora de "## Lacunas Identificadas"
[ ] Wikilinks apontando para arquivos inexistentes
[ ] Frontmatter de Bíblia/ modificado após data de criação original
[ ] Artigos em wiki/conceitos/ referenciando < 2 versículos
[ ] Duplicatas em wiki/ (mesmo conceito, nomes diferentes)
[ ] Obras em raw/ sem ficha em wiki/obras/
```

### Template do relatório

```markdown
# Lint — {DATA}

## Sumário

| Categoria | Total encontrado | Críticos | Resolvidos esta semana |
|-----------|-----------------|---------|----------------------|

## Problemas Críticos (Nível A)
{Afirmações sem fonte, frontmatter alterado}

## Problemas Moderados (Nível B)
{Wikilinks quebrados, duplicatas}

## Melhorias Sugeridas (Nível C)
{Conceitos órfãos, fontes não consultadas}

## Métricas do Vault

- Total de nós de versículo: X
- Nós com enriquecimento completo: X (X%)
- Total de arestas no grafo: X
- Arestas tipológicas (✡): X
- Arestas AT→NT (▶): X
- Obras indexadas: X / {total disponível}
```

---

## Tarefa 7 — Q&A Teológico

**Agente:** ResearchAgent  
**Output:** `reports/{YYYY-MM-DD}_{slug}.md`

### Fluxo de execução

1. **Decomposição da pergunta**
   - Quais termos originais estão implícitos?
   - Quais tradições têm posições divergentes?
   - Há passagens obrigatórias a consultar?

2. **Navegação pelo grafo**
   - Identificar nós de versículo relevantes
   - Seguir arestas tipológicas e AT→NT
   - Consultar artigos de conceito em wiki/

3. **Saída estruturada**

```markdown
---
tipo: report
pergunta: "..."
data: YYYY-MM-DD
versiculos_consultados: []
obras_consultadas: []
---

# {Título da Resposta}

## Resposta Direta

{2–4 frases. Sem evasão.}

## Fatos Citados (com fonte)

{Lista de afirmações com [Fonte: ... | Nível: N]}

## Posições Divergentes

{Tabela ou parágrafos por tradição}

## Inferências do Agente

{Marcadas explicitamente. Podem estar erradas.}

## Lacunas — O que este relatório não sabe

{O que precisaria ser pesquisado para resposta mais completa}

## Versículos Relacionados

{Links para nós do vault que aprofundam o tema}
```
