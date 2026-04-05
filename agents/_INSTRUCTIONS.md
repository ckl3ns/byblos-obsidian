# INSTRUCTIONS.md — Guia de Tarefas por Tipo

> Referência operacional para enriquecimento do vault.
> Para cada tipo de tarefa: o que fazer, passo a passo, com exemplos.
> Leia junto com `AGENTS.md` — este arquivo não repete as regras, apenas especifica a execução.

---

## TAREFA 1 — Exegese de Versículo Individual

**Quando usar**: quero analisar um versículo específico em profundidade.

### Passo a Passo

**1. Localizar o arquivo**
```
Bíblia/{Testamento}/{Cânon}/{Livro}/{Sigla}-{Cap}.{Vers}.md
```

**2. Ler o contexto mínimo**
- Versículo anterior e posterior (links de navegação)
- Arquivo do capítulo (`{Sigla}-{Cap}.md`) para ver a perícope
- `wiki/passagens/{slug-da-pericope}.md` (se já existe)

**3. Verificar o bloco NTSK**
- Se ainda está em formato raw: rodar `ntsk_linker.py --file {path} --run`
- Navegar os links `*` e `✓` prioritariamente
- Anotar os que têm símbolo `✡` (profecia), `▶` (citação AT), `‡` (cuidado)

**4. Consultar fontes em `raw/`**
Por prioridade: léxico (BDB/BDAG) → gramática → comentário técnico (NICNT/WBC) → sistemática

**5. Escrever seção de enriquecimento**
Adicionar ao final do arquivo de versículo (após `[[Glossário do NTSK]]`):

```markdown
---

## 📖 **Notas Exegéticas**

### Contexto Literário
[posição na perícope; gênero literário; estrutura retórica]
[Fonte: raw/comentarios/{obra}, §{seção} | Nível: 3]

### Análise Lexical
| Termo | Idioma | Strong | Glosa | Nota |
|---|---|---|---|---|
| {palavra} | Grego/Heb | G/H{N} | {tradução} | {observação] |
[Fonte: raw/lexicos/{BDAG ou BDB}, p.{N} | Nível: 2]

### Sintaxe e Estrutura
[construções gramaticais relevantes; caso, tempo, voz, modo]
[Fonte: raw/linguagem/{gramática}, §{N} | Nível: 2]

### Questões Textuais
[variantes NA28/BHS; escolha adotada e justificativa — omitir se trivial]

## 🧭 **Teologia da Passagem**

### Contribuição ao Corpus de {Autor}
[como este versículo se relaciona com a teologia do livro/autor]

### Conexão com a Teologia Bíblica
[contribuição ao desenvolvimento progressivo da revelação]

### Posições Divergentes
| Tradição | Interpretação | Referência |
|---|---|---|
| {Reformada/Arminiana/etc.} | {resumo} | [[wiki/obras/{obra}]] |

## 🔀 **Conexões Temáticas**
[[wiki/conceitos/{slug}]] | [[wiki/conceitos/{slug2}]]

## ✍️ **Anotações Pessoais**
[reservado ao proprietário]
```

**6. Atualizar metadados**
- Definir `data_atualizacao` no frontmatter
- Adicionar claim na tabela `claims` do SQLite (se ativo)

---

## TAREFA 2 — Criar Artigo de Perícope

**Quando usar**: quero um artigo sobre um trecho coerente de texto (ex: Mt 5:1-12, Rm 8:28-39).

### Passo a Passo

**1. Definir limites da perícope**
- Verificar comentários técnicos em `raw/comentarios/`
- Checar divisões de parágrafo em NA28/BHS

**2. Criar o arquivo**
```
wiki/passagens/{sigla}-{cap}-{vers-ini}-{vers-fim}.md
```

**3. Template do artigo de perícope**

```markdown
---
titulo: {Nome Descritivo da Perícope}
referencia: {Sigla} {Cap}:{ini}-{fim}
livro: {Livro}
testamento: {AT/NT}
tags: [wiki, passagem, {livro}, {tema1}, {tema2}]
status: draft   ← mudar para publicado após revisão
data_criacao: YYYY-MM-DD
---

# {Título}

> {Sigla} {Cap}:{ini}-{fim} — {Nome do Livro}

## Texto e Delimitação

[[{Sigla}-{Cap}.{ini}]] — [[{Sigla}-{Cap}.{fim}]]

{Breve justificativa dos limites da perícope com base em estrutura literária}
[Fonte: raw/comentarios/{obra} | Nível: 3]

## Estrutura Literária

```
{esboço recuado mostrando divisões internas}
```

## Contexto
### Contexto Literário Imediato
[o que vem antes e depois na narrativa/argumento]

### Contexto Histórico
[situação do autor, destinatários, data]
[Fonte: raw/comentarios/{obra} | Nível: 3]

### Contexto Canônico
[posição na estrutura do livro e no plano redentor]

## Análise Exegética
[por subdivisão da estrutura acima]
[Fonte: ... | Nível: ...]

## Teologia da Passagem
[pontos doutrinais centrais emergentes do texto]
[Fonte: ... | Nível: ...]

## Referências Cruzadas Principais
[links aos versículos com `✡`, `▶`, `*` — do bloco NTSK dos versículos]
{[[Gn-x.y|Gn x:y]] · [[Is-x.y|Is x:y]]}

## Histórico Interpretativo
[como esta passagem foi lida nas tradições: Patrística, Reforma, Modernidade]

## Aplicações e Temas Associados
[[wiki/conceitos/{tema1}]] | [[wiki/conceitos/{tema2}]]

## Lacunas e Questões Abertas
[o que não foi respondido; fontes a consultar]
```

---

## TAREFA 3 — Criar Artigo de Conceito Teológico

**Quando usar**: preciso de um artigo sobre uma doutrina ou tema (ex: Justificação, Kenose, Pacto da Redenção).

**Arquivo**: `wiki/conceitos/{slug-em-kebab-case}.md`

### Template

```markdown
---
titulo: {Conceito em Título Descritivo}
tags: [wiki, conceito, {área: cristologia|soteriologia|pneumatologia|...}]
status: draft
data_criacao: YYYY-MM-DD
---

# {Conceito}

## Definição
{1-2 parágrafos de definição técnica, com base em Nível 1-2}
[Fonte: raw/lexicos/{BDAG/TDNT}, s.v. "{termo}" | Nível: 2]

## Base Bíblica
### Antigo Testamento
{passagens fundacionais do AT com wikilinks}
[[{Sigla}-{Cap}.{Vers}]] — {breve nota}

### Novo Testamento
[[{Sigla}-{Cap}.{Vers}]] — {breve nota}
[Fonte: raw/sistematica/{Grudem/Bavinck}, cap.{N} | Nível: 4]

## Terminologia Original
| Termo | Idioma | Strong | Ocorrências | Glosa |
|---|---|---|---|---|
| {termo} | Hebraico/Grego | {N} | {N}x | {tradução PT} |

## Desenvolvimento Histórico
{como o conceito foi desenvolvido na história da teologia}
[Fonte: raw/historia/{González/Pelikan}, p.{N} | Nível: 4]

## Posições Doutrinais

| Tradição | Posição | Referência |
|---|---|---|
| Reformada | {resumo} | [[wiki/obras/{obra}]] |
| Arminiana | {resumo} | |
| Católica | {resumo} | |
| {outras relevantes} | | |

## Distinções Importantes
{o que este conceito NÃO é; erros históricos comuns — usar `‡` se necessário}

## Passagens Relacionadas
[[wiki/passagens/{slug}]]

## Conceitos Associados
→ [[wiki/conceitos/{pressupõe}]]  (pressupõe)
← [[wiki/conceitos/{fundamenta}]] (é pressuposto por)
↔ [[wiki/conceitos/{contrasta}]]  (contrasta)

## Lacunas
[o que falta; fontes pendentes]
```

---

## TAREFA 4 — Análise de Grafo NTSK

**Quando usar**: quero explorar o grafo estruturalmente.

### 4.1 Extrair subgrafo tipológico (AT→NT)

Pesquisar todos os arquivos de versículo NT que contêm links com `✡` ou `=`/`⩲`.

```dataview
LIST file.name
FROM "Bíblia/Novo Testamento"
WHERE contains(file.content, "✡") OR contains(file.content, "⩲")
```

Gerar `reports/tematicos/YYYY-MM-DD_grafo-tipologico.md` com:
- Lista de pares AT → NT por símbolo
- Livros do AT mais citados tipologicamente no NT
- Candidatos a artigos de tipologia em `wiki/conceitos/`

### 4.2 Extrair subgrafo de citações AT→NT

```dataview
LIST file.name
FROM "Bíblia/Novo Testamento"
WHERE contains(file.content, "▶")
```

### 4.3 Encontrar versículos hub (mais citados)

Usar o grafo de backlinks do Obsidian:
- Filtrar notas com > 10 backlinks dentro de `Bíblia/`
- Esses são candidatos a artigos de passagem em `wiki/passagens/`

### 4.4 Encontrar versículos órfãos

```dataview
LIST file.name
FROM "Bíblia"
WHERE length(file.inlinks) = 0
```
Esses versículos não são citados por nenhum outro no vault — candidatos a análise ou preenchimento.

---

## TAREFA 5 — Ingesta de Fonte em `raw/`

**Quando usar**: adicionei um novo arquivo (comentário, léxico, artigo).

**1. Colocar o arquivo em `raw/{subdiretório}/`**

**2. Criar ficha em `wiki/obras/{slug}.md`**

```markdown
---
titulo: {Título Completo}
autor: {Autor(es)}
ano: {AAAA}
editora: {Editora}
isbn: {ISBN ou DOI}
idioma: {PT|EN|DE|...}
tipo: comentário | léxico | sistemática | teologia bíblica | monografia | artigo
nivel: 2 | 3 | 4 | 5   ← conforme hierarquia do AGENTS.md
sigla_citacao: {ex: BDAG, WBC-Mt, NICNT-Rm}
tags: [wiki, obra, {nível_sigla}]
raw_path: raw/{subdiretório}/{filename}
---

# {Título}

## Identificação
[campo de sigla + dados bibliográficos completos]

## Escopo e Método
[o que cobre; método hermenêutico; posição confessional do autor]

## Passagens com Comentário Extenso
{lista de referências onde a obra tem conteúdo denso}
[[{Sigla}-{Cap}.{Vers}]] — "{citação chave ou título da seção}"

## Posição Teológica do Autor
[tradição; teses centrais; divergências com outras posições]
[AVISO: posição do AUTOR, não do vault]

## Avaliação
[pontos fortes e limitações para os propósitos deste vault]
```

**3. Atualizar `indices/autores.md` e `indices/INDEX.md`**

---

## TAREFA 6 — Lint Semanal

**Executar toda semana (sugestão: domingo)**

### Checklist

```
[ ] Artigos wiki/ com status: draft há > 30 dias → listar no relatório
[ ] Seções factuais sem [Fonte: ...] → marcar como CRÍTICO
[ ] Wikilinks quebrados [[X]] sem arquivo correspondente → CRÍTICO
[ ] Termos Strong sem correspondência em raw/lexicos/ → MODERADO
[ ] Autor de wiki confundido com posição do vault → CRÍTICO
[ ] Símbolo ‡ sem aviso no artigo de conceito relacionado → MODERADO
[ ] Passagens com símbolo ✡ sem artigo em wiki/passagens/ → SUGESTÃO
[ ] Versículos com enriquecimento há > 6 meses sem revisão → SUGESTÃO
```

**Output**: `reports/lint/YYYY-MM-DD.md`

```markdown
# Lint Report — YYYY-MM-DD

## CRÍTICO ({N} itens)
- [ ] {path} — {descrição do problema}

## MODERADO ({N} itens)
- [ ] {path} — {descrição}

## SUGESTÕES ({N} itens)
- [ ] {ação} — {motivação}

## Métricas do Vault
| Métrica | Valor |
|---|---|
| Artigos wiki/ publicados | {N} |
| Artigos wiki/ em draft | {N} |
| Versículos com enriquecimento | {N} / 31102 |
| Links NTSK convertidos | {N} |
| Claims em SQLite | {N} |
| % de afirmações com fonte | {%} |
```

---

## TAREFA 7 — Responder Pergunta Teológica/Bíblica

**Quando usar**: o usuário faz uma pergunta e quer um relatório fundamentado.

**1. Decompor a pergunta**
Identificar: passagens relevantes | conceitos envolvidos | posições divergentes | período histórico

**2. Navegar o grafo**
- Começar por `indices/INDEX.md` → localizar passagens e conceitos centrais
- Navegar via backlinks dos conceitos
- Usar links `*` e `✓` como prioridade

**3. Consultar `raw/` para confirmação**
Mínimo 2 fontes de Nível 2-3 para cada afirmação central.

**4. Gerar relatório em `reports/`**
Seguir o template de output do ResearchAgent (seção 7.3 do AGENTS.md).

**5. Propor enriquecimento**
Ao final do relatório, incluir:
```markdown
## Sugestões de Enriquecimento
- Criar artigo: wiki/conceitos/{slug} (cobre tópico central desta pesquisa)
- Enriquecer versículo: {Sigla}-{Cap}.{Vers}.md (hub desta análise)
- Arquivar este relatório como insumo: wiki/passagens/{slug} (stub já existe)
```

---

## Referência Rápida — Estrutura de Seção de Enriquecimento

```
## 📖 Notas Exegéticas     ← linguagem original, gramática, contexto
## 🧭 Teologia da Passagem ← teologia bíblica, sistemática, posições
## 🔀 Conexões Temáticas   ← links para wiki/conceitos/ e wiki/passagens/
## ✍️ Anotações Pessoais   ← reservado ao proprietário (agente: NÃO editar)
```

## Referência Rápida — Prefixos de Nível de Fonte

```
[Fonte: raw/lexicos/BDAG, s.v. "logos"  | Nível: 2]
[Fonte: raw/comentarios/NICNT-Jo, p.42  | Nível: 3]
[Fonte: raw/sistematica/Bavinck-v3, §12 | Nível: 4]
[INFERÊNCIA HERMENÊUTICA — não verificada em fonte]
```
