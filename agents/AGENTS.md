# AGENTS.md — Vault Bíblico-Teológico
> Versão: 1.1 | 2026-04-04

---

## Estrutura do Vault

```
vault/
├── Bíblia/                        # ⚠️ SOMENTE LEITURA
│   ├── {Livro}.md                 # índice do livro
│   ├── {Sigla}-{cap}.md           # índice do capítulo
│   └── {Sigla}-{cap}.{vs}.md     # nó do versículo
├── raw/                           # obras de referência (NÃO editar)
│   ├── AYBD/
│   ├── IVP-Black/
│   ├── NIDB/
│   ├── teologicos/                # EDT
│   ├── EAC/
│   └── especiais/                 # DDD, DTIB, DBI-R
├── wiki/
│   ├── conceitos/
│   ├── pessoas/
│   ├── obras/
│   └── temas/
├── reports/
│   └── lint/
└── agents/
    ├── AGENTS.md
    ├── INSTRUCTIONS.md
    ├── scripts/
    │   ├── vault_parser.py
    │   ├── ntsk_parser.py
    │   └── graph_builder.py
    └── output/
        ├── nodes.json
        ├── edges.json
        └── graph_stats.json
```

---

## Regras Absolutas

### Zona de somente leitura
- NUNCA criar, modificar ou deletar arquivos em `Bíblia/`
- NUNCA reescrever frontmatter YAML dos nós
- NUNCA alterar textos KJV / BKJ
- NUNCA alterar a navegação canônica (Voltar/Avançar)

### Enriquecimento permitido em nós de versículo
Adicionar APENAS ao final do arquivo, após "Referências Cruzadas NTSK".
Ordem obrigatória das seções:
```
## Léxico
## Contexto Histórico-Cultural
## Posições Exegéticas
## Conexões no Grafo
## Lacunas Identificadas
```

### Proveniência obrigatória
Toda afirmação factual deve conter:
`[Fonte: raw/{pasta}/{arquivo} | Obra: {SIGLA} | Nível: {1-4}]`

Escala de autoridade:
| Nível | Tipo | Exemplos |
|-------|------|---------|
| 1 | Texto canônico | KJV, BKJ, NA28, BHS |
| 2 | Léxico primário | BDAG, BDB, HALOT, TDNT |
| 3 | Dicionário especializado | AYBD, NIDB, IVP-Black, DDD, EAC |
| 4 | Dicionário teológico geral | EDT, DTIB, DBI-R |
| 5 | Inferência do agente |

Inferências vão EXCLUSIVAMENTE em `## Lacunas Identificadas`, marcadas `[INFERÊNCIA DO AGENTE]`.

---

## Catálogo Tier 1 (obras em raw/)

### Dicionários Bíblicos

| Sigla | Obra | Corpus | Nível |
|-------|------|--------|-------|
| AYBD | Anchor Yale Bible Dictionary (6 vols.) | AT + NT | 3 |
| DJG2 | Dictionary of Jesus and the Gospels, 2ª ed. | Evangelhos | 3 |
| DPL2 | Dictionary of Paul and His Letters, 2ª ed. | Paulinas | 3 |
| DLNT | Dictionary of Later NT & Its Developments | Hb, Ep. Gerais, Ap | 3 |
| DNT-B | Dictionary of NT Background | Contexto NT | 3 |
| DOT-P | Dictionary of OT Pentateuch | Gn–Dt | 3 |
| DOT-Pr | Dictionary of OT Prophets | Profetas | 3 |
| DOT-W | Dictionary of OT Wisdom, Poetry & Writings | Jó, Sl, Pv, Ec, Ct | 3 |
| NIDB | New Interpreter's Dict. of the Bible (H-Z) | AT + NT | 3 |
| DDD | Dictionary of Deities and Demons in the Bible | AT semítico | 3 |

### Teologia, Hermenêutica, Patrística

| Sigla | Obra | Domínio | Nível |
|-------|------|---------|-------|
| EDT | Evangelical Dictionary of Theology, 3ª ed. | Sistemática | 4 |
| EAC | Encyclopedia of Ancient Christianity | Patrística | 3 |
| DTIB | Dictionary for Theological Interpretation | Hermenêutica | 4 |
| DBI-R | Dictionary of Biblical Imagery (Ryken) | Literatura/imagem | 4 |

### Descartadas (raw/_arquivo/)
ISBE-R, ZEB, DJG1, DPL1, DOT-H, EC, EDCSWR, DCS, NDT, GDT

---

## Decisão de Obra por Corpus

| Passagem | 1ª Consulta | 2ª Consulta | Contexto |
|---------|-------------|-------------|---------|
| Evangelhos | DJG2 | NIDB | DNT-B |
| Atos | NIDB | AYBD | DNT-B |
| Paulinas (Rm–Fp) | DPL2 | NIDB | DNT-B |
| Paulinas Pastorais + Fm | DPL2 | DLNT | DNT-B |
| Hebreus | DLNT | NIDB | DNT-B |
| Epístolas Gerais | DLNT | NIDB | DNT-B |
| 1–3Jo + Ap | DLNT | DJG2 | DNT-B |
| Pentateuco | DOT-P | NIDB | AYBD |
| Profetas | DOT-Pr | NIDB | AYBD |
| Sapienciais | DOT-W | NIDB | AYBD |
| Históricos | NIDB | AYBD | AYBD |
| Conceito teológico | EDT | DTIB | — |
| Imagem/símbolo | DBI-R | AYBD | — |
| Divindades AT | DDD | AYBD | — |
| Patrística | EAC | EDT | — |

---

## Mapeamento de Siglas (66 livros)

| Livro (PT) | Sigla | EN | Idx |
|------------|-------|----|-----|
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

## Símbolos NTSK

| Símbolo | Significado | Tipo de aresta no grafo |
|---------|-------------|------------------------|
| * | Referência especialmente clara | especially_clear |
| ✓ | Referência criticamente pertinente | critically_clear |
| + | Coleção mais completa | full_collection |
| ◐ | Contraste / posição alternativa | contrast |
| = | Tipo ou antítipo | type_antitype |
| ⩲ | Tipo/antítipo (base escritural) | type_antitype_scriptural |
| ▶ | Citação AT→NT | ot_quote_in_nt |
| ✡ | Cumprimento de profecia | fulfills_prophecy |
| ∥ | Passagem paralela estrita | parallel_passage |
| ‡ | Doutrina falsa / uso indevido | false_doctrine_proof |
| ❅S# | Strong Hebraico | — (metadado do nó) |
| ✣S# | Strong Grego | — (metadado do nó) |

---

## Scripts (agents/scripts/)

| Script | Função | Entrada | Saída |
|--------|--------|---------|-------|
| vault_parser.py | Parse de qualquer nó .md | arquivo .md | VaultNode |
| ntsk_parser.py | Extrai refs NTSK estruturadas | string NTSK | dict com refs, Strong, notas |
| graph_builder.py | Constrói e exporta o grafo | vault_dir | nodes.json, edges.json, graph_stats.json |

Uso CLI:
```bash
# Exportar grafo completo
python agents/scripts/graph_builder.py . agents/output

# Parse de arquivo individual
python -c "from vault_parser import parse_file; n=parse_file('Bíblia/Mt-1.1.md'); print(n.referencia, n.ntsk_raw[:100])"
```

---

## Agentes

### IngestionAgent
**Responsabilidade:** Indexar nova obra em `raw/` e criar ficha em `wiki/obras/`
**Proibições:** criar arquivos em `Bíblia/`; modificar `raw/`

### EnrichmentAgent
**Responsabilidade:** Adicionar seções aos nós de versículo
**Fluxo:** ler nó → identificar termos → consultar obras na ordem da tabela → adicionar seções com proveniência
**Proibições:** modificar frontmatter; alterar KJV/BKJ; alterar navegação

### WikiCompilerAgent
**Responsabilidade:** Criar/manter artigos em `wiki/conceitos/`, `wiki/pessoas/`, `wiki/temas/`
**Acionamento:** conceito aparece em 3+ versículos sem artigo próprio

### ResearchAgent
**Responsabilidade:** Q&A contra o vault
**Output:** `reports/{YYYY-MM-DD}_{slug}.md` com seções: Resposta / Fatos Citados / Inferências / Lacunas / Versículos Relacionados

### LintAgent
**Responsabilidade:** Health checks periódicos
**Verificações:** seções sem `[Fonte: ...]`; wikilinks quebrados; inferências fora de "Lacunas"; frontmatter intacto; duplicações em wiki/
**Output:** `reports/lint/YYYY-MM-DD.md`
