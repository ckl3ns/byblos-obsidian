# Vault Bíblico-Teológico

Base de conhecimento exegético-teológica construída e mantida em Obsidian,
operada por agentes LLM segundo contrato definido em `agents/AGENTS.md`.

---

## Filosofia do Vault

O vault separa três camadas com regras diferentes:

| Camada | Path | Quem escreve | Quem lê |
|--------|------|--------------|---------|
| **Texto bíblico** | `Bíblia/` | Ninguém (gerado uma vez) | Todos |
| **Conhecimento compilado** | `wiki/` | Agentes (com proveniência) | Todos |
| **Fontes primárias** | `raw/` | Humano (cópia manual) | Agentes |
| **Outputs** | `reports/` | Agentes | Humano |

Nenhum agente modifica `Bíblia/`. Nenhuma afirmação factual vai para `wiki/`
sem uma tag `[Fonte: raw/... | Obra: ... | Nível: N]`. Inferências ficam isoladas
em seções "Lacunas Identificadas".

---

## Estrutura de Diretórios

```
vault/
├── Bíblia/                     ← SOMENTE LEITURA
│   ├── Antigo Testamento/
│   │   ├── Pentateuco/
│   │   ├── Poéticos e Sapienciais/
│   │   ├── Profetas Maiores/
│   │   └── Profetas Menores/
│   └── Novo Testamento/
│       ├── Evangelhos/
│       │   └── Mateus/         — Mt-1.md … Mt-1.1.md … Mt-1.25.md …
│       ├── Epístolas Paulinas/
│       │   └── Filemón/        — Filemon.md, Fm-1.md, Fm-1.1.md … Fm-1.25.md
│       └── (demais livros)
│
├── wiki/
│   ├── conceitos/              — artigos de conceitos teológicos
│   ├── tópicos/                — artigos de temas exegéticos
│   ├── pericopes/              — análises de perícopes
│   └── obras/                  — fichas das fontes em raw/
│
├── raw/
│   ├── IVP-Black/              — DJG2, DPL2, DLNT, DNT-B, DOT-*
│   ├── AYBD/                   — Anchor Yale Bible Dictionary
│   ├── NIDB/                   — New Interpreter's Dict. of the Bible
│   ├── teologicos/             — EDT, DTIB, DBI-R
│   ├── EAC/                    — Estudos Avançados Complementares
│   └── especiais/              — DDD, outros
│
├── reports/
│   ├── lint/                   — relatórios semanais (YYYY-MM-DD.md)
│   ├── qa/                     — respostas Q&A
│   └── exegese/                — relatórios exegéticos longos
│
├── agents/
│   ├── AGENTS.md               ← contrato normativo de agentes
│   ├── INSTRUCTIONS.md         ← guia operacional por tipo de tarefa
│   └── ontology.yaml           ← contrato de entidades e relações
│
└── scripts/
    ├── enrichment_writer.py    — appenda seções em nós de versículo
    ├── raw_searcher.py         — full-text search sobre raw/
    ├── lint_checker.py         — health checks do vault
    └── ntsk_linker.py          — gera bloco NTSK (pipeline original)
```

---

## Convenções de Nomenclatura

### Nós Bíblicos

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Livro | `<NomeLivro>.md` | `Filemon.md`, `Mateus.md` |
| Capítulo | `<SGL>-<cap>.md` | `Fm-1.md`, `Mt-1.md` |
| Versículo | `<SGL>-<cap>.<v>.md` | `Fm-1.1.md`, `Mt-1.25.md` |

### Wiki

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Conceito | `<nome-normalizado>.md` | `justificacao-pela-fe.md` |
| Perícope | `<SGL>-<cap>.<vi>-<vf>.md` | `Fm-1.1-7.md` |
| Obra | `<SIGLA>.md` | `DPL2.md` |

### Reports

| Tipo | Padrão |
|------|--------|
| Lint | `reports/lint/YYYY-MM-DD.md` |
| Q&A | `reports/qa/<slug>-YYYY-MM-DD.md` |
| Alerta de agente | `reports/qa/ALERTA-YYYY-MM-DD.md` |

---

## Grafo NTSK — Símbolos

O campo `NTSK` em cada nó de versículo pode conter um ou mais símbolos.
Cada símbolo implica uma aresta em um subgrafo específico:

| Símbolo | Relação | Subgrafo |
|---------|---------|----------|
| `✡` | AT prefigura NT (tipologia) | Grafo tipológico |
| `▶` | NT cita/alude AT | Grafo de citações AT→NT |
| `⚓` | Ancora passagem doutrinária | Grafo doutrinário |
| `🔀` | Paralelo literário/sinótico | Grafo de paralelos |
| `‡` | Aviso textual/tradução | Grafo de issues textuais |
| `→` | Fluxo narrativo (causa→efeito) | Grafo narrativo |

Queries Dataview para cada subgrafo estão em `agents/INSTRUCTIONS.md` (Tarefa 4).

---

## Hierarquia de Fontes

| Nível | Tipo | Exemplos |
|-------|------|----------|
| 1 | Texto original com aparato crítico | BHS, NA28, UBS5, LXX |
| 2 | Léxicos acadêmicos | BDAG, BDB, HALOT |
| 3 | Dicionários e comentários técnicos | AYBD, DPL2, DJG2, NIDB |
| 4 | Teologia sistemática | EDT, DTIB, DBI-R |
| 5 | Literatura secundária / Blogs | *(proibido em seções factuais)* |

A tag de citação padrão é:
```
[Fonte: raw/<pasta>/<arquivo> | Obra: <SIGLA> | Nível: N]
```

---

## Scripts

### enrichment_writer.py
Appenda seções de enriquecimento em nós de versículo.
Valida regras de proveniência e ordem de seções antes de gravar.

```python
from scripts.enrichment_writer import EnrichmentSection, append_enrichment

result = append_enrichment(
    "Bíblia/Novo Testamento/Epístolas Paulinas/Filemón/Fm-1.1.md",
    sections=[
        EnrichmentSection(
            title="Léxico",
            content="| δοῦλος | doûlos | escravo | ... | [Fonte: raw/IVP-Black/DPL2.txt | Obra: DPL2 | Nível: 3] |"
        )
    ],
    dry_run=True   # revisar antes de gravar
)
print(result['diff_preview'])
```

### raw_searcher.py
Full-text search sobre obras em raw/.

```python
from scripts.raw_searcher import RawSearcher

searcher = RawSearcher("raw/")
hits = searcher.search_entry("δοῦλος", siglas=["DPL2", "DLNT"])
for h in hits:
    print(h.citation_tag)
    print(h.context)
```

### lint_checker.py
Health checks do vault. Gera relatório em `reports/lint/`.

```bash
python scripts/lint_checker.py vault/ reports/lint/
```

---

## Fluxo de Trabalho Típico

```
1. Adicionar obra a raw/
         ↓
2. Criar ficha em wiki/obras/ (IngestionAgent via Tarefa 5)
         ↓
3. Escolher versículo/perícope para enriquecer
         ↓
4. raw_searcher: localizar fontes relevantes → citation tags
         ↓
5. enrichment_writer: append seções com dry_run=True → revisar → gravar
         ↓
6. Se surgiram conceitos novos → criar artigo em wiki/conceitos/ (Tarefa 3)
         ↓
7. lint_checker: health check → corrigir issues críticos
         ↓
8. git commit -m "[agent:Enrichment] Fm-1.1: léxico + contexto"
```

---

## Git Conventions

Cada sessão de agente gera commits com mensagem padronizada:

| Prefixo | Quando usar |
|---------|-------------|
| `[agent:Ingestion]` | Nova obra indexada em wiki/obras/ |
| `[agent:Enrichment]` | Seções adicionadas a nó de versículo |
| `[agent:Research]` | Novo artigo em wiki/ ou reports/ |
| `[agent:Lint]` | Relatório de health check |
| `[agent:LintFix]` | Correção de issue detectado pelo lint |
| `[ontology:update]` | Modificação em agents/ontology.yaml |
| `[manual]` | Qualquer edição feita diretamente pelo humano |

---

## Próximos Passos Recomendados

1. **Calibração**: rodar Tarefa 1 completa em `Fm-1.1.md` (versículo pequeno, rico).
2. **Indexar fontes**: para cada arquivo em `raw/`, criar ficha em `wiki/obras/` (Tarefa 5).
3. **Primeiro lint**: `python scripts/lint_checker.py . reports/lint/` — estabelecer baseline.
4. **Expandir grafo**: identificar pares AT→NT com símbolo `▶` em Mt 1.1–25 e criar
   artigos de conceito para as tipologias messiânicas encontradas.
5. **Congelar ontologia**: não alterar `ontology.yaml` até 2026-06-04 sem justificativa.

---

## Documentação dos Agentes

- Contrato normativo (o que pode/deve/proibido): `agents/AGENTS.md`
- Guia operacional por tarefa (como executar): `agents/INSTRUCTIONS.md`
- Contrato de entidades e relações: `agents/ontology.yaml`
