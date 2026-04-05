# AGENTS.md — Vault Bíblico-Teológico

> Versão: 1.0 | Atualizado: 2026-04-04
> Este arquivo é o contrato entre agentes e o vault. Leia antes de qualquer operação.

---

## Estrutura do Vault

```
vault/
├── Bíblia/                        # ⚠️ SOMENTE LEITURA — grafo bíblico canônico
│   ├── {Livro}.md                 # Índice do livro (Dataview de capítulos)
│   ├── {Sigla}-{cap}.md           # Índice do capítulo (Dataview de versículos)
│   └── {Sigla}-{cap}.{vs}.md     # Nó do versículo (estrutura canônica)
├── raw/                           # Obras de referência (texto bruto — NÃO editar)
│   ├── AYBD/                      # Anchor Yale Bible Dictionary
│   ├── IVP-Black/                 # IVP Black Dictionaries (DNT, DPL, DJG, DOT...)
│   ├── NIDB/                      # New Interpreter's Dictionary of the Bible
│   ├── teologicos/                # EDT (Evangelical Dictionary of Theology)
│   ├── EAC/                       # Encyclopedia of Ancient Christianity
│   └── especiais/                 # DDD, DTIB, DBI-R
├── wiki/                          # Artigos sintéticos gerados por agentes
│   ├── conceitos/                 # Artigos de conceitos teológicos
│   ├── pessoas/                   # Figuras bíblicas e históricas
│   ├── obras/                     # Fichas das obras de raw/
│   └── temas/                     # Temas transversais e perícopes
├── reports/                       # Outputs de Q&A, análises, relatórios
│   └── lint/                      # Relatórios de health check
└── agents/
    ├── AGENTS.md                  # Este arquivo
    ├── INSTRUCTIONS.md            # Guia operacional por tipo de tarefa
    └── ontology.yaml              # Contrato de entidades e relações (futuro)
```

---

## Regras Absolutas

### Zona de somente leitura (nunca violar)
- NUNCA criar, modificar ou deletar arquivos em `Bíblia/`
- NUNCA reescrever o frontmatter YAML dos nós de versículo
- NUNCA alterar a navegação canônica (Voltar/Avançar nos nós)
- NUNCA alterar os textos KJV e BKJ
- O grafo bíblico é infraestrutura gerenciada por pipeline separado — não é wiki

### Zona de enriquecimento legítima em nós de versículo
Dentro de arquivos `Bíblia/{Sigla}-{cap}.{vs}.md`, o agente pode **apenas adicionar**
seções ao final do arquivo, após a seção "Referências Cruzadas NTSK".

Seções permitidas (em ordem obrigatória):
```
## Léxico
## Contexto Histórico-Cultural
## Posições Exegéticas
## Conexões no Grafo
## Lacunas Identificadas
```

Qualquer outra modificação no nó é proibida.

### Proveniência obrigatória
Toda afirmação factual adicionada ao vault deve conter:

```
[Fonte: raw/{pasta}/{arquivo} | Obra: {SIGLA} | Nível: {1-4}]
```

**Escala de níveis de autoridade:**

| Nível | Tipo | Exemplos |
|-------|------|---------|
| 1 | Texto bíblico canônico | KJV, BKJ, NA28, BHS |
| 2 | Léxico primário | BDAG, BDB, HALOT, TDNT |
| 3 | Dicionário especializado por corpus | AYBD, NIDB, IVP-Black (DPL, DJG, etc.), DDD, EAC |
| 4 | Dicionário teológico geral | EDT, DTIB, DBI-R |
| 5 | Inferência do agente / fonte secundária não listada |

**Regra dura:** seções factuais aceitam apenas Níveis 1–4.
Inferências e hipóteses vão exclusivamente na seção `## Lacunas Identificadas`,
marcadas como `[INFERÊNCIA DO AGENTE]`.

---

## Catálogo de Obras em raw/ (Tier 1 — curadas)

### Dicionários Bíblicos por Corpus

| Sigla | Obra completa | Corpus | Nível | Localização em raw/ |
|-------|--------------|--------|-------|---------------------|
| AYBD | Anchor Yale Bible Dictionary (A-Z, 6 vols.) | AT + NT geral | 3 | raw/AYBD/ |
| DJG2 | Dictionary of Jesus and the Gospels, 2ª ed. (IVP) | Evangelhos | 3 | raw/IVP-Black/ |
| DPL2 | Dictionary of Paul and His Letters, 2ª ed. (IVP) | Paulinas | 3 | raw/IVP-Black/ |
| DLNT | Dictionary of Later NT & Its Developments (IVP) | Hb, Ep. Gerais, Ap | 3 | raw/IVP-Black/ |
| DNT-B | Dictionary of NT Background (IVP) | Contexto NT | 3 | raw/IVP-Black/ |
| DOT-P | Dictionary of OT Pentateuch (IVP) | Gn–Dt | 3 | raw/IVP-Black/ |
| DOT-Pr | Dictionary of OT Prophets (IVP) | Profetas | 3 | raw/IVP-Black/ |
| DOT-W | Dictionary of OT Wisdom, Poetry & Writings (IVP) | Jó, Sl, Pv, Ec, Ct | 3 | raw/IVP-Black/ |
| NIDB | New Interpreter's Dict. of the Bible (H-Z) | AT + NT geral | 3 | raw/NIDB/ |
| DDD | Dictionary of Deities and Demons in the Bible | AT — mundo semítico | 3 | raw/especiais/ |

### Teologia, Hermenêutica e Contexto

| Sigla | Obra completa | Domínio | Nível | Localização em raw/ |
|-------|--------------|---------|-------|---------------------|
| EDT | Evangelical Dictionary of Theology, 3ª ed. | Teologia sistemática | 4 | raw/teologicos/ |
| EAC | Encyclopedia of Ancient Christianity | Patrística | 3 | raw/EAC/ |
| DTIB | Dictionary for Theological Interpretation of the Bible | Hermenêutica bíblico-teológica | 4 | raw/especiais/ |
| DBI-R | Dictionary of Biblical Imagery (Ryken/Wilhoit/Longman) | Literatura e imagem | 4 | raw/especiais/ |

### Obras descartadas (movidas para raw/_arquivo/)
ISBE-R, ZEB, DJG1, DPL1, DOT-H, EC, EDCSWR, DCS, NDT, GDT, WHT, DHT, DBI-B (Beck), NIDB A-G

---

## Decisão de Obra por Corpus

| Passagem | 1ª Consulta | 2ª Consulta | Contexto Histórico |
|---------|-------------|-------------|-------------------|
| Evangelhos (Mt, Mc, Lc, Jo) | DJG2 | NIDB | DNT-B |
| Atos | NIDB | AYBD | DNT-B |
| Paulinas principais (Rm–Fl) | DPL2 | NIDB | DNT-B |
| Paulinas pastorais (1Tm–Tt) | DPL2 | DLNT | DNT-B |
| Filemom | DPL2 | DLNT | DNT-B |
| Hebreus | DLNT | NIDB | DNT-B |
| Epístolas gerais (Tg, 1-2Pe, Jd) | DLNT | NIDB | DNT-B |
| João (1-3Jo, Ap) | DLNT | DJG2 | DNT-B |
| Pentateuco (Gn–Dt) | DOT-P | NIDB | AYBD |
| Profetas (Is–Ml) | DOT-Pr | NIDB | AYBD |
| Poéticos/Sapienciais (Jó–Ct) | DOT-W | NIDB | AYBD |
| Históricos (Js–Et) | NIDB | AYBD | AYBD |
| Conceito teológico (qualquer) | EDT | DTIB | — |
| Imagem/metáfora/símbolo | DBI-R | AYBD | — |
| Divindades, pantheon semítico | DDD | AYBD | — |
| Patrística / recepção pós-canônica | EAC | EDT | — |

---

## Mapeamento de Siglas do Vault (PT-BR ↔ EN)

| Livro (PT) | Sigla Vault | Sigla EN | Índice |
|------------|-------------|----------|--------|
| Gênesis | Gn | Gen | 1 |
| Êxodo | Ex | Exod | 2 |
| Levítico | Lv | Lev | 3 |
| Números | Nm | Num | 4 |
| Deuteronômio | Dt | Deut | 5 |
| Josué | Js | Josh | 6 |
| Juízes | Jz | Judg | 7 |
| Rute | Rt | Ruth | 8 |
| 1 Samuel | 1Sm | 1Sam | 9 |
| 2 Samuel | 2Sm | 2Sam | 10 |
| 1 Reis | 1Rs | 1Kgs | 11 |
| 2 Reis | 2Rs | 2Kgs | 12 |
| 1 Crônicas | 1Cr | 1Chr | 13 |
| 2 Crônicas | 2Cr | 2Chr | 14 |
| Esdras | Ed | Ezra | 15 |
| Neemias | Ne | Neh | 16 |
| Ester | Et | Esth | 17 |
| Jó | Jó | Job | 18 |
| Salmos | Sl | Ps | 19 |
| Provérbios | Pv | Prov | 20 |
| Eclesiastes | Ec | Eccl | 21 |
| Cânticos | Ct | Song | 22 |
| Isaías | Is | Isa | 23 |
| Jeremias | Jr | Jer | 24 |
| Lamentações | Lm | Lam | 25 |
| Ezequiel | Ez | Ezek | 26 |
| Daniel | Dn | Dan | 27 |
| Oséias | Os | Hos | 28 |
| Joel | Jl | Joel | 29 |
| Amós | Am | Amos | 30 |
| Obadias | Ob | Obad | 31 |
| Jonas | Jn | Jonah | 32 |
| Miquéias | Mq | Mic | 33 |
| Naum | Na | Nah | 34 |
| Habacuque | Hc | Hab | 35 |
| Sofonias | Sf | Zeph | 36 |
| Ageu | Ag | Hag | 37 |
| Zacarias | Zc | Zech | 38 |
| Malaquias | Ml | Mal | 39 |
| Mateus | Mt | Matt | 40 |
| Marcos | Mc | Mark | 41 |
| Lucas | Lc | Luke | 42 |
| João | Jo | John | 43 |
| Atos | At | Acts | 44 |
| Romanos | Rm | Rom | 45 |
| 1 Coríntios | 1Co | 1Cor | 46 |
| 2 Coríntios | 2Co | 2Cor | 47 |
| Gálatas | Gl | Gal | 48 |
| Efésios | Ef | Eph | 49 |
| Filipenses | Fp | Phil | 50 |
| Colossenses | Cl | Col | 51 |
| 1 Tessalonicenses | 1Ts | 1Thess | 52 |
| 2 Tessalonicenses | 2Ts | 2Thess | 53 |
| 1 Timóteo | 1Tm | 1Tim | 54 |
| 2 Timóteo | 2Tm | 2Tim | 55 |
| Tito | Tt | Titus | 56 |
| Filemom | Fm | Phlm | 57 |
| Hebreus | Hb | Heb | 58 |
| Tiago | Tg | Jas | 59 |
| 1 Pedro | 1Pe | 1Pet | 60 |
| 2 Pedro | 2Pe | 2Pet | 61 |
| 1 João | 1Jo | 1John | 62 |
| 2 João | 2Jo | 2John | 63 |
| 3 João | 3Jo | 3John | 64 |
| Judas | Jd | Jude | 65 |
| Apocalipse | Ap | Rev | 66 |

---

## Agentes

### IngestionAgent
**Responsabilidade:** Indexar nova obra em `raw/` e criar ficha em `wiki/obras/`
**Proibições:** Criar qualquer arquivo em `Bíblia/`; modificar obras existentes em `raw/`
**Output:** `wiki/obras/{SIGLA}.md` com: nome completo, editores, ano, editora, sigla, nível, corpus coberto, path em raw/, notas de uso

### EnrichmentAgent
**Responsabilidade:** Adicionar seções a nós de versículo consultando `raw/`
**Fluxo:**
1. Identificar termos exegéticos-chave do versículo (máx. 5)
2. Consultar obras na ordem da tabela "Decisão de Obra por Corpus"
3. Extrair trechos relevantes com localização exata no arquivo raw/
4. Adicionar seções com proveniência completa
5. Criar/atualizar wikilinks para `wiki/conceitos/` e `wiki/pessoas/`
**Proibições:** Modificar frontmatter; alterar texto do versículo; alterar navegação

### WikiCompilerAgent
**Responsabilidade:** Criar e manter artigos em `wiki/conceitos/`, `wiki/pessoas/`, `wiki/temas/`
**Acionamento:** Quando um conceito aparece em 3+ versículos enriquecidos sem artigo próprio
**Estrutura obrigatória de artigo:**
```
## Definição
## Terminologia Original (Hb/Gr com Strong's)
## Desenvolvimento no Cânon
### Antigo Testamento
### Novo Testamento
## Posições por Tradição
## O que este conceito NÃO é
## Lacunas
```

### ResearchAgent
**Responsabilidade:** Q&A sobre qualquer aspecto do vault
**Output obrigatório:** `reports/{YYYY-MM-DD}_{slug}.md` com seções:
```
## Resposta
## Fatos Citados (com proveniência Nível 1-4)
## Inferências (marcadas explicitamente)
## Lacunas (o que não foi encontrado em raw/)
## Versículos Relacionados (wikilinks)
```

### LintAgent
**Responsabilidade:** Health checks periódicos do vault
**Verificações:**
- Seções sem `[Fonte: ...]` em conteúdo factual
- Wikilinks quebrados
- Afirmações de Nível 5 em seções factuais
- Duplicação de conceitos em `wiki/`
- Frontmatter de nós em `Bíblia/` intacto
**Output:** `reports/lint/YYYY-MM-DD.md`
