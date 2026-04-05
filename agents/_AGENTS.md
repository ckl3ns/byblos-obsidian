# AGENTS.md — Vault de Estudos Bíblicos e Teológicos
> **Leia este arquivo inteiro antes de qualquer operação.**
> Este é o contrato operacional de todos os agentes LLM que atuam neste vault.
> Violar qualquer regra deste arquivo compromete a integridade do grafo.

---

## 1. Identidade do Vault

| Campo | Valor |
|---|---|
| **Nome** | Byblos-Obsidian: ambiente de estudo bíblico e teológico |
| **Proprietário** | Cristian Klen |
| **Idioma dos artigos wiki** | Português (BR) |
| **Idiomas das fontes** | PT, EN, DE, ES, FR, Grego Koiné/LXX, Hebraico Bíblico, Aramaico, Latim |
| **Tradição hermenêutica base** | Reformada/Batista com abertura Pentecostal-Carismática |
| **Propósito** | Pesquisa acadêmica, ensino teológico, desenvolvimento de plataformas de IA para estudos bíblicos |

---

## 2. Estrutura do Vault

```
vault/
│
├── Bíblia/                     ← ZONA SOMENTE LEITURA (infraestrutura do grafo)
│   ├── Bíblia.md               ← Hub raiz do grafo (31.000+ arestas)
│   ├── Antigo Testamento/
│   │   └── {Canon}/            (Torá, Históricos, Poéticos, Profetas Maiores, Menores)
│   │       └── {Livro}/
│   │           ├── {Livro}.md            ← Nó de livro (Dataview query de capítulos)
│   │           ├── {Sigla}-{N}.md        ← Nó de capítulo (Dataview query de versículos)
│   │           └── {Sigla}-{Cap}.{Vers}.md  ← Nó de VERSÍCULO (conteúdo principal)
│   └── Novo Testamento/
│       └── (mesma estrutura)
│
├── wiki/                       ← ZONA DE CRIAÇÃO E ENRIQUECIMENTO
│   ├── conceitos/              ← Doutrinas, temas, noções teológicas
│   ├── passagens/              ← Análises de perícopes e textos temáticos
│   ├── autores/                ← Teólogos, exegetas, comentaristas
│   ├── obras/                  ← Fichas de léxicos, comentários, sistemáticas
│   ├── periodos/               ← Eras históricas da teologia
│   ├── tradições/              ← Correntes e movimentos teológicos
│   └── temas/                  ← Temas transversais (escatologia, pneumatologia etc.)
│
├── raw/                        ← FONTES CRUAS (nunca editar)
│   ├── biblia/                 ← Textos bíblicos por versão/idioma
│   ├── lexicos/                ← BDB, HALOT, BDAG, TDNT, Louw-Nida, Strong
│   ├── comentarios/            ← ICC, NICNT, NICOT, WBC, Hermeneia, etc.
│   ├── sistematica/            ← Bavinck, Berkhof, Grudem, Erickson, etc.
│   ├── biblica/                ← Teologia bíblica por corpus
│   ├── periodicos/             ← JBL, NTS, JETS, WTJ, etc.
│   ├── ensaios/                ← Ensaios, capítulos, monografias
│   ├── historia/               ← Patrística, Reforma, história da interpretação
│   └── linguagem/              ← Gramáticas BH e NT, introduções
│
├── indices/
│   ├── INDEX.md                ← Índice mestre
│   ├── passagens.md            ← Índice por referência bíblica
│   ├── conceitos.md            ← Índice de conceitos teológicos
│   ├── autores.md              ← Índice de autores e obras
│   └── meta.sqlite             ← Metadados, claims, relações (SQLite)
│
├── reports/
│   ├── exegeses/               ← Análises exegéticas de passagens
│   ├── tematicos/              ← Estudos temáticos transversais
│   ├── lint/                   ← Relatórios de saúde do vault
│   └── slides/                 ← Marp slides para ensino
│
└── agents/
    ├── AGENTS.md               ← Este arquivo
    ├── INSTRUCTIONS.md         ← Guia operacional por tarefa
    ├── ontology.yaml           ← Schema de entidades e relações
    ├── ntsk_linker.py          ← Converte NTSK raw → wikilinks
    └── prompts/                ← Templates de prompt por tipo de tarefa
```

---

## 3. Anatomia dos Arquivos de Versículo

Todo arquivo `{Sigla}-{Cap}.{Vers}.md` em `Bíblia/` tem esta estrutura **imutável**:

```markdown
---
referencia: {Sigla} {Cap}.{Vers}
alias:
  - {8-13 variantes de abreviação PT/EN}
livro: {Nome completo PT-BR}
sigla: {Sigla PT-BR}           ← ex: Mt, Rm, Gn, 1Cr
indice_livro: {N}              ← Posição canônica (1=Gênesis, 66=Apocalipse)
capitulo: {N}
versiculo: {N}
KJV: {texto em inglês}
BKJ: {texto em português BKJ1611}
testamento: Antigo Testamento | Novo Testamento
canon_judaico: {Torá|Profetas|Escritos|}
canon_cristao: {Pentateuco|Evangelhos|Epístolas Paulinas|...}
data_criacao: YYYY-MM-DD
data_atualizacao:
status: publicado
tags: [Bíblia, {Testamento}, {Canon}, {Livro}]
---

[[Bíblia]] ➜ [[Testamento]] ➜ [[Cânon]] ➜ [[Livro]] ➜ [[Cap]]
[[Sigla-Cap.Vers-1|Voltar]] ❮ [[Sigla-Cap.Vers]] ❯ [[Sigla-Cap.Vers+1|Avançar]]

## 📜 **Texto do Versículo**
| BKJ1611 | ... |
| KJV     | ... |

## 🔗 **Referências Cruzadas (NTSK)**
{bloco raw OU wikilinks gerados por ntsk_linker.py}

[[Glossário do NTSK]]
```

**Regra absoluta**: Agentes **NUNCA** alteram o frontmatter, o breadcrumb, a navegação sequencial, o texto do versículo ou o bloco NTSK já convertido. Esses campos são sagrados.

---

## 4. Convenções de Nomenclatura

### 4.1 Siglas (Vault PT-BR → NTSK EN)

| Vault | NTSK | Livro | | Vault | NTSK | Livro |
|---|---|---|---|---|---|---|
| Gn | Ge | Gênesis | | Mt | Mt | Mateus |
| Ex | Ex | Êxodo | | Mc | Mk | Marcos |
| Lv | Le | Levítico | | Lc | Lk | Lucas |
| Nm | Nu | Números | | Jo | Jn | João |
| Dt | Dt | Deuteronômio | | At | Ac | Atos |
| Js | Jsh | Josué | | Rm | Ro | Romanos |
| Jz | Jg | Juízes | | 1Co | 1 Co | 1 Coríntios |
| Rt | Ru | Rute | | 2Co | 2 Co | 2 Coríntios |
| 1Sm | 1 S | 1 Samuel | | Gl | Ga | Gálatas |
| 2Sm | 2 S | 2 Samuel | | Ef | Ep | Efésios |
| 1Rs | 1 K | 1 Reis | | Fp | Ph | Filipenses |
| 2Rs | 2 K | 2 Reis | | Cl | Col | Colossenses |
| 1Cr | 1 Ch | 1 Crônicas | | 1Ts | 1 Th | 1 Tessalonicenses |
| 2Cr | 2 Ch | 2 Crônicas | | 2Ts | 2 Th | 2 Tessalonicenses |
| Ed | Ezr | Esdras | | 1Tm | 1 Ti | 1 Timóteo |
| Ne | Ne | Neemias | | 2Tm | 2 Ti | 2 Timóteo |
| Et | Es | Ester | | Tt | Tit | Tito |
| Jó | Jb | Jó | | Fm | Phm | Filemom |
| Sl | Ps | Salmos | | Hb | He | Hebreus |
| Pv | Pr | Provérbios | | Tg | Ja | Tiago |
| Ec | Ec | Eclesiastes | | 1Pe | 1 Pe | 1 Pedro |
| Ct | SS | Cânticos | | 2Pe | 2 Pe | 2 Pedro |
| Is | Is | Isaías | | 1Jo | 1 Jn | 1 João |
| Jr | Je | Jeremias | | 2Jo | 2 Jn | 2 João |
| Lm | La | Lamentações | | 3Jo | 3 Jn | 3 João |
| Ez | Eze | Ezequiel | | Jd | Ju | Judas |
| Dn | Da | Daniel | | Ap | Re | Apocalipse |
| Os | Ho | Oséias | | Jn | Jon | Jonas |
| Jl | Jl | Joel | | Mq | Mi | Miquéias |
| Am | Am | Amós | | Hc | Hab | Habacuque |
| Ob | Ob | Obadias | | Sf | Zp | Sofonias |
| Ml | Ml | Malaquias | | Ag | Hg | Ageu |
| | | | | Zc | Zc | Zacarias |

### 4.2 Nomeação de Arquivos

```
Bíblia/: {Sigla}-{Cap}.{Vers}.md          ex: Mt-1.1.md, Fm-1.1.md, Dt-1.10.md
wiki/:   {tipo}/{slug-em-kebab-case}.md   ex: conceitos/justificacao-pela-fe.md
reports/: {tipo}/{YYYY-MM-DD}_{slug}.md   ex: exegeses/2026-04-03_rm-3-21-26.md
```

---

## 5. Símbolos Semânticos do NTSK

Estes símbolos prefixam os wikilinks gerados por `ntsk_linker.py`. Cada um carrega significado teológico crítico — **nunca remover**.

| Símbolo | Significado | Implicação exegética |
|---|---|---|
| `*` | Referência especialmente clara | Priorize em exegese básica |
| `✓` | Referência criticamente pertinente | Essencial — use em definições |
| `+` | Coleção mais completa de refs | Indica tópico com loci clássicos |
| `✡` | Cumprimento de profecia | **Grafo de tipologia AT→NT** |
| `▶` | Citação AT→NT | **Grafo de citações diretas** |
| `◐` | Contraste doutrinário | Marcar como `CONTRASTA` no SQLite |
| `=` / `⩲` | Tipo/Antítipo | **Grafo tipológico** |
| `‡` | Doutrina falsa (uso indevido do texto) | Alertar em artigos de conceito |
| `❅S#Nh` | Strong Hebraico | Linkar com léxico Strong (AT) |
| `✣S#Ng` | Strong Grego | Linkar com léxico Strong (NT) |
| `ƒN` | Figura de linguagem (Bullinger) | Preservar para análise retórica |

---

## 6. Hierarquia de Autoridade das Fontes

```
Nível 1 — Texto Primário
  Bíblia (BHS, NA28/UBS5, LXX, TR, BKJ, KJV)
  Confissões históricas (WCF, HC, LBCF, Augsburg, Barmen)

Nível 2 — Fontes Técnicas
  Léxicos: BDB, HALOT, BDAG, TDNT, TDOT, Louw-Nida, Strong
  Gramáticas: GKC, Joüon-Muraoka, Wallace, Mounce
  Crítica textual: NA28, UBS5, BHQ

Nível 3 — Comentários Exegéticos Acadêmicos
  Séries: ICC, NICNT, NICOT, WBC, BECNT, NIGTC, Hermeneia, PNTC
  Monografias revisadas por pares

Nível 4 — Teologia Sistemática e Histórica
  Bavinck, Berkhof, Grudem, Erickson, Turretin, Owen
  Pelikan, González (história da teologia)

Nível 5 — Periódicos e Ensaios
  JBL, NTS, JETS, WTJ, CBQ, JSOT, JSNT

Nível 6 — Obras Populares
  Válidas como perspectiva prática; NUNCA como suporte doutrinário primário
```

**Regra**: Afirmações em seções factuais de `wiki/` exigem Nível 1-3 mínimo.

---

## 7. Regras por Agente

### 7.1 IngestionAgent
**Responsabilidade**: Processar arquivos em `raw/` e criar/atualizar artigos em `wiki/`.

**Pipeline obrigatório**:
1. Identificar tipo de obra via análise do conteúdo
2. Criar `wiki/obras/{slug}.md` com ficha completa
3. Criar ou atualizar `wiki/autores/{autor}.md`
4. Identificar passagens e conceitos centrais → criar stubs em `wiki/passagens/` e `wiki/conceitos/`
5. Atualizar `indices/INDEX.md`, `indices/autores.md`
6. Registrar claims em `meta.sqlite` com `source_path` e `level`

**Proibido**:
- NÃO criar ou editar arquivos em `Bíblia/`
- NÃO inferir posições teológicas não declaradas explicitamente pelo autor
- NÃO misturar posição do autor com posição do vault

---

### 7.2 EnrichmentAgent
**Responsabilidade**: Adicionar seções de enriquecimento exegético a arquivos existentes em `Bíblia/`.

**Pode adicionar** (somente após as seções existentes):
```markdown
## 📖 **Notas Exegéticas**
[análise linguística, contexto, estrutura]
[Fonte: raw/comentarios/X, §Y | Nível: 3]

## 🧭 **Teologia da Passagem**
[contribuição ao corpus e à teologia bíblica]

## 🔀 **Conexões Temáticas**
[[wiki/conceitos/X]] | [[wiki/conceitos/Y]]

## ✍️ **Anotações Pessoais**
[espaço para o proprietário — NÃO editar por agente]
```

**Proibido**:
- NÃO tocar em frontmatter, breadcrumb, navegação, texto, bloco NTSK ou link ao Glossário
- NÃO adicionar conteúdo em `## ✍️ Anotações Pessoais`
- NÃO criar nova nota de versículo (já existem todas)

---

### 7.3 ResearchAgent
**Responsabilidade**: Responder perguntas e produzir relatórios em `reports/`.

**Estratégia de busca**:
1. Consultar `indices/INDEX.md` para orientação
2. Buscar em `wiki/conceitos/` e `wiki/passagens/` por artigos existentes
3. Navegar o grafo via wikilinks do NTSK (começando pelos símbolos `*` e `✓`)
4. Consultar `raw/` quando precisar ir à fonte primária
5. Usar Dataview queries para agrupar versículos por critério

**Output obrigatório** (`reports/{tipo}/{data}_{slug}.md`):
```markdown
# [Título da Pesquisa]

## Resposta
[afirmações suportadas por Nível 1-3]

## Evidência e Fontes
[lista com sigla do nível e path raw/]

## Posições Divergentes
[quando houver controvérsia real entre tradições]

## Inferências (não verificadas)
[o que o agente infere sem suporte direto no vault]

## Lacunas
[o que não foi encontrado; sugestões de fontes a adquirir]
```

---

### 7.4 GraphAnalystAgent
**Responsabilidade**: Explorar o grafo NTSK para análise estrutural do texto bíblico.

**Capacidades**:
- Extrair subgrafos temáticos (ex: todos os links `✡` → profecia cumprida)
- Identificar versículos com maior grau de entrada (hubs de referência)
- Detectar clusters de co-citação (versículos sempre citados juntos)
- Mapear cadeia tipológica AT→NT via símbolos `=` e `✡`
- Encontrar passagens "órfãs" (sem nenhum link de entrada no grafo)

**Output**: relatórios em `reports/tematicos/` ou tabelas em `indices/`

---

### 7.5 LintAgent
**Responsabilidade**: Saúde e integridade do vault. Rodar semanalmente.

**Verificações**:
- Artigos `wiki/` com `status: draft` há mais de 30 dias
- Afirmações factuais sem `[Fonte: ...]`
- Links `[[X]]` para arquivos inexistentes no vault
- Conceitos com posição do autor confundida com posição do vault
- Strong numbers (`❅S#`) sem correspondência em léxico de Nível 2
- Símbolo `‡` (doutrina falsa) sem aviso explícito no artigo de conceito

**Output**: `reports/lint/YYYY-MM-DD.md` (CRÍTICO | MODERADO | SUGESTÃO)

---

## 8. Ontologia de Entidades (`ontology.yaml`)

```yaml
entities:
  - Conceito       # doutrina, tema, noção teológica
  - Passagem       # perícope ou texto bíblico
  - Obra           # livro, comentário, léxico, artigo
  - Autor          # teólogo, exegeta, pesquisador
  - Tradição       # corrente ou movimento teológico
  - Período        # época histórica da teologia
  - TermoOriginal  # palavra em grego/hebraico/aramaico

relations:
  - DEFINE:         [Obra → Conceito]
  - COMENTA:        [Obra → Passagem]
  - CONTRASTA:      [Conceito ↔ Conceito]
  - PRESSUPÕE:      [Conceito → Conceito]
  - ESCRITO_POR:    [Obra → Autor]
  - PERTENCE_A:     [Autor → Tradição]
  - TRADUZ:         [TermoOriginal → Conceito]
  - APOIA:          [Tradição → Conceito | Passagem]
  - REFUTA:         [Tradição → Conceito | Passagem]
  - CITA:           [Passagem_NT → Passagem_AT]      # símbolo ▶
  - CUMPRE:         [Passagem_NT → Passagem_AT]      # símbolo ✡
  - TIPO_DE:        [Passagem_AT → Passagem_NT]      # símbolos = ⩲
```

---

## 9. Regras Absolutas (nunca violar)

1. **Nunca apague ou edite arquivos em `raw/`** — são fontes imutáveis.
2. **Nunca crie arquivos em `Bíblia/`** — toda essa estrutura já existe.
3. **Nunca edite frontmatter, breadcrumb, navegação, texto bíblico ou bloco NTSK** de arquivos em `Bíblia/`.
4. **Nunca atribua posição ao "vault"** sem que o proprietário tenha marcado `posicao_vault: true` no frontmatter do artigo.
5. **Nunca gere afirmações sobre variantes textuais** sem base em NA28, UBS5, BHS ou BHQ.
6. **Nunca misture exegese com eisegese** sem marcar `[INFERÊNCIA HERMENÊUTICA]` explicitamente.
7. **Nunca resolva silenciosamente divergências entre tradições** (arminianismo vs. calvinismo, cessacionismo vs. continuacionismo, etc.) — represente ambas, indique a posição base do vault, deixe a decisão ao proprietário.
8. **Nunca use o símbolo `‡` (doutrina falsa do NTSK) como validação** de uma posição teológica — é um marcador de uso indevido do texto, não um endosso.

---

## 10. Ferramentas Disponíveis

| Ferramenta | Tipo | Função |
|---|---|---|
| `agents/ntsk_linker.py` | Script Python | Converte NTSK raw em wikilinks |
| Dataview (Obsidian) | Plugin | Queries dinâmicas sobre frontmatter |
| Obsidian Graph View | Visual | Navegação e análise do grafo |
| `meta.sqlite` | SQLite | Claims, metadados, relações |
| `indices/*.md` | Markdown | Índices navegáveis |
| CLI `kb ask "..."` | A definir | Q&A via terminal |

---

## 11. Glossário Rápido

- **Nó de versículo**: arquivo `{Sigla}-{Cap}.{Vers}.md` em `Bíblia/`
- **Nó de capítulo**: arquivo `{Sigla}-{Cap}.md`
- **Nó de livro**: arquivo `{Livro}.md`
- **Hub**: nó com grau de entrada alto (ex: `[[Bíblia]]`, `[[João]]`, `[[Gênesis]]`)
- **Aresta NTSK**: wikilink gerado por `ntsk_linker.py` a partir do bloco de referências cruzadas
- **Aresta semântica**: aresta com símbolo `✡`, `▶`, `=` etc. (subgrafo tipológico/profético)
- **Perícope**: unidade literária coerente (pode abranger múltiplos versículos)
- **Grafo de tipologia**: subconjunto de arestas `=`, `⩲`, `✡` mapeando AT→NT
