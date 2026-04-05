# INSTRUCTIONS.md — Guia Operacional por Tipo de Tarefa

> Versão: 1.0 | Atualizado: 2026-04-04
> Leia AGENTS.md antes deste arquivo. Este guia pressupõe conhecimento das regras do vault.

---

## Tarefa 1: Enriquecer um versículo (EnrichmentAgent)

**Pré-condição:** verificar se o nó existe em `Bíblia/`. Se não existir, PARE — não crie o arquivo.

### Passo a passo

**1. Leitura do nó**
- Leia o frontmatter para confirmar: `sigla`, `capitulo`, `versiculo`, `livro`
- Leia o texto KJV e BKJ completo
- Leia as Referências Cruzadas NTSK existentes

**2. Identificação de termos-chave**
- Liste 2–5 termos exegéticos prioritários (substantivos, verbos, títulos, conceitos)
- Para Paulinas: priorize termos teológicos, relacionais, eclesiológicos
- Para Evangelhos: priorize ações de Jesus, títulos messiânicos, contexto geográfico
- Para AT: priorize nomes divinos, rituais, figuras de linguagem semítica

**3. Consulta às obras (sequência por corpus)**

| Corpus | Ordem de consulta |
|--------|-------------------|
| Evangelhos | DJG2 → NIDB → AYBD → DBI-R (se imagem) |
| Atos | NIDB → AYBD → DNT-B |
| Paulinas principais | DPL2 → NIDB → AYBD |
| Paulinas pastorais / Fm | DPL2 → DLNT → NIDB |
| Hebreus | DLNT → NIDB → AYBD |
| Epístolas Gerais | DLNT → NIDB |
| Apocalipse | DLNT → NIDB → AYBD |
| Pentateuco | DOT-P → NIDB → AYBD |
| Profetas | DOT-Pr → NIDB → AYBD |
| Poéticos/Sapienciais | DOT-W → NIDB → AYBD |
| Históricos | NIDB → AYBD |
| Qualquer (contexto histórico) | DNT-B (NT) / AYBD (AT) |
| Qualquer (imagem/metáfora) | DBI-R → AYBD |
| Qualquer (divindades AT) | DDD → AYBD |
| Qualquer (patrística) | EAC → EDT |

**4. Estrutura das seções a adicionar**

Adicione ao final do arquivo, após "Referências Cruzadas NTSK":

```markdown
## Léxico

| Termo | Original | Strong | Transliteração | Definição resumida | Fonte |
|-------|----------|--------|----------------|-------------------|-------|
| {termo PT} | {Hb/Gr} | G/H{nº} | {translit.} | {def.} | [Fonte: raw/.../{arquivo} \| Obra: {SIGLA} \| Nível: 3] |

## Contexto Histórico-Cultural

{parágrafo de contexto}
[Fonte: raw/IVP-Black/{arquivo} | Obra: DNT-B | Nível: 3]

## Posições Exegéticas

### Tradição Reformada / Calvinista
{síntese da posição}
[Fonte: raw/... | Obra: ... | Nível: ...]

### Tradição Pentecostal / Carismática
{síntese da posição}
[Fonte: raw/... | Obra: ... | Nível: ...]

### Tradição Católica *(incluir quando relevante)*
{síntese da posição}
[Fonte: raw/... | Obra: ... | Nível: ...]

## Conexões no Grafo

- [[wiki/conceitos/{conceito-1}]]
- [[wiki/conceitos/{conceito-2}]]
- [[wiki/pessoas/{pessoa}]]

## Lacunas Identificadas

- [INFERÊNCIA DO AGENTE] {hipótese ou detalhe não confirmado em raw/}
- Não encontrado em raw/: {aspecto que merece pesquisa futura}
```

**5. Verificação final antes de salvar**
- [ ] Frontmatter original intacto?
- [ ] Texto KJV/BKJ intacto?
- [ ] Toda afirmação factual tem `[Fonte: ...]`?
- [ ] Inferências estão em "Lacunas" marcadas como `[INFERÊNCIA DO AGENTE]`?
- [ ] Wikilinks apontam para arquivos existentes ou claramente a criar?

---

## Tarefa 2: Criar artigo de conceito em wiki/ (WikiCompilerAgent)

**Acionamento:** conceito aparece em 3+ versículos enriquecidos sem artigo próprio em `wiki/conceitos/`

**Nome do arquivo:** `wiki/conceitos/{conceito-em-kebab-case}.md`

### Template completo

```markdown
---
conceito: {Nome do Conceito}
tags: [wiki, conceito, {domínio: cristologia|soteriologia|eclesiologia|etc}]
fontes_consultadas: [AYBD, DPL2, EDT]
versiculos_relacionados:
  - "[[Bíblia/Mt-1.1]]"
  - "[[Bíblia/Rm-3.24]]"
datacriacao: {YYYY-MM-DD}
dataatualizacao: {YYYY-MM-DD}
status: rascunho
---

## Definição

{Síntese objetiva de 2–4 frases baseada em obras Nível 3–4}
[Fonte: raw/.../{arquivo} | Obra: {SIGLA} | Nível: 3]

## Terminologia Original

| Língua | Termo | Strong | Transliteração | Glosa | Fonte |
|--------|-------|--------|----------------|-------|-------|
| Hebraico | {termo} | H{nº} | {translit.} | {glosa} | [Obra: AYBD \| Nível: 3] |
| Grego | {termo} | G{nº} | {translit.} | {glosa} | [Obra: AYBD \| Nível: 3] |

## Desenvolvimento no Cânon

### Antigo Testamento
{narrativa de desenvolvimento}
[Fonte: ... | Obra: ... | Nível: 3]

### Novo Testamento
{narrativa de desenvolvimento}
[Fonte: ... | Obra: ... | Nível: 3]

## Posições por Tradição

### Reformada / Calvinista
{posição com distinções}
[Fonte: raw/teologicos/{arquivo} | Obra: EDT | Nível: 4]

### Arminian / Wesleyana
{posição com distinções}
[Fonte: ... | Nível: 4]

### Pentecostal / Carismática
{posição com distinções}
[Fonte: ... | Nível: 4]

### Tradição Histórica (Patrística / Medieval)
{posição com distinções}
[Fonte: raw/EAC/{arquivo} | Obra: EAC | Nível: 3]

## O que este conceito NÃO é

*(Distinções negativas — crucial para precisão doutrinária)*
- Não confundir com [[wiki/conceitos/{conceito-adjacente}]]: {distinção}
- Não equivale a: {erro comum}

## Lacunas

- [INFERÊNCIA DO AGENTE] {hipótese não confirmada}
- Não encontrado em raw/: {aspecto que merece pesquisa futura}
```

---

## Tarefa 3: Criar ficha de obra em wiki/obras/ (IngestionAgent)

**Nome do arquivo:** `wiki/obras/{SIGLA}.md`

### Template

```markdown
---
sigla: {SIGLA}
obra: {Nome completo}
editores: [{Editor 1}, {Editor 2}]
ano: {YYYY}
editora: {Editora}
nivel: {3 ou 4}
corpus: [{Evangelhos, Paulinas, AT-Profetas, etc.}]
path_raw: raw/{pasta}/{arquivo(s)}
---

## Sobre a obra

{Descrição em 2–3 frases: escopo, método, orientação teológica}

## Pontos fortes

- {Ponto 1}
- {Ponto 2}

## Limitações e vieses

- {Viés teológico declarado ou identificado}
- {Limitação de cobertura}

## Quando usar

{Em que tipo de consulta esta obra deve ser a primeira escolha}

## Quando NÃO usar

{Casos em que outra obra do vault é mais adequada}
```

---

## Tarefa 4: Q&A (ResearchAgent)

### Formato de entrada recomendado

```
Pergunta: {pergunta clara e delimitada}
Escopo: {versículos específicos / período / livro / tema}
Tradição prioritária: {reformada / pentecostal / ecumênica / histórica}
Profundidade: {superficial | média | técnica}
```

### Fluxo do agente

1. **Decomposição:** quebrar a pergunta em 2–5 sub-perguntas exegéticas
2. **Navegação pelo grafo:**
   - Localizar versículos relevantes em `Bíblia/`
   - Verificar seções de enriquecimento já existentes
   - Consultar `wiki/conceitos/` para conceitos relacionados
3. **Consulta direta a raw/:** quando a wiki não cobre o necessário
4. **Síntese:** produzir relatório em `reports/`
5. **Sugestão de enriquecimento:** se a pesquisa revelou lacunas nos nós, indicar quais versículos precisam de enriquecimento

### Template de relatório

```markdown
---
pergunta: "{pergunta original}"
data: {YYYY-MM-DD}
tradição: {tradição prioritária}
profundidade: {superficial|média|técnica}
---

## Resposta

{Resposta direta e estruturada}

## Fatos Citados

| Afirmação | Fonte | Nível |
|-----------|-------|-------|
| {afirmação} | [raw/.../{arquivo} \| Obra: {SIGLA}] | {1-4} |

## Inferências

- [INFERÊNCIA DO AGENTE] {inferência com base nos fatos acima}

## Lacunas

- Não encontrado em raw/: {aspecto não coberto pelas obras disponíveis}
- Versículos que precisam de enriquecimento: [[Bíblia/{nó}]]

## Versículos Relacionados

- [[Bíblia/{Sigla}-{cap}.{vs}]] — {motivo da relação}
```

---

## Tarefa 5: Lint semanal (LintAgent)

### Checklist de execução

**1. Varredura de nós enriquecidos em Bíblia/**
- [ ] Seções adicionadas respeitam a ordem obrigatória?
- [ ] Toda afirmação factual tem `[Fonte: ...]`?
- [ ] Frontmatter original intacto em todos os nós modificados?
- [ ] Há `[INFERÊNCIA DO AGENTE]` fora da seção "Lacunas"? → erro crítico

**2. Varredura de wiki/conceitos/**
- [ ] Todo artigo tem `status:` no frontmatter?
- [ ] Wikilinks internos `[[...]]` resolvem para arquivo existente?
- [ ] Seção "O que este conceito NÃO é" presente?
- [ ] Algum conceito duplicado com nome diferente?

**3. Varredura de wiki/obras/**
- [ ] Todas as 14 obras do Tier 1 têm ficha?
- [ ] Paths `path_raw` apontam para arquivos existentes?

**4. Análise de conexidade do grafo**
- [ ] Versículos enriquecidos que ainda não têm nenhum link para `wiki/conceitos/`
- [ ] Conceitos em `wiki/conceitos/` sem nenhum versículo relacionado no frontmatter

### Template de relatório de lint

```markdown
---
data: {YYYY-MM-DD}
nós_verificados: {n}
artigos_verificados: {n}
---

## Problemas Críticos *(requerem correção imediata)*

- [ ] {descrição} → {arquivo} → {ação corretiva}

## Problemas Menores *(correção na próxima sessão)*

- [ ] {descrição} → {arquivo}

## Sugestões de Enriquecimento

- {versículo} — motivo: {lacuna identificada}

## Métricas do Vault

| Métrica | Valor |
|---------|-------|
| Nós com enriquecimento | {n} / {total} |
| Artigos em wiki/conceitos/ | {n} |
| Artigos com status "publicado" | {n} |
| Wikilinks quebrados | {n} |
| Afirmações sem fonte | {n} |
```

---

## Referência Rápida: Obras por Corpus

| Se você está em... | Abra primeiro | Abra depois |
|--------------------|---------------|-------------|
| Mateus | DJG2 | NIDB, DNT-B |
| Marcos | DJG2 | NIDB, DNT-B |
| Lucas | DJG2 | NIDB, DNT-B |
| João (Evangelho) | DJG2 | DLNT, NIDB |
| Atos | NIDB | AYBD, DNT-B |
| Romanos–Filipenses | DPL2 | NIDB |
| Colossenses–Filemom | DPL2 | DLNT |
| Hebreus | DLNT | NIDB, AYBD |
| Tiago | DLNT | NIDB |
| 1–2 Pedro, Judas | DLNT | NIDB |
| 1–3 João | DLNT | DJG2 |
| Apocalipse | DLNT | NIDB, AYBD |
| Gênesis–Deuteronômio | DOT-P | NIDB, AYBD |
| Josué–Ester | NIDB | AYBD |
| Jó–Cânticos | DOT-W | NIDB, AYBD |
| Isaías–Malaquias | DOT-Pr | NIDB, AYBD |
| Conceito teológico | EDT | DTIB |
| Imagem / símbolo | DBI-R | AYBD |
| Divindade do AT | DDD | AYBD |
| Patrística | EAC | EDT |
