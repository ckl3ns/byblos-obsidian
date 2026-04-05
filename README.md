# byblos-obsidian

> Vault de estudos bíblicos e teológicos com grafo de 31.000+ versículos,
> infraestrutura de agentes LLM e sistema de gestão de conhecimento.

**byblos** (βύβλος) — papiro, livro; origem etimológica de "Bíblia".

---

## Filosofia do Vault

O vault separa três camadas com regras diferentes:

| Camada | Path | Quem escreve | Quem lê |
|--------|------|--------------|---------|
| **Texto bíblico** | `vault/Bíblia/` | Ninguém (gerado uma vez) | Todos |
| **Conhecimento compilado** | `vault/wiki/` | Agentes (com proveniência) | Todos |
| **Fontes primárias** | `raw/` | Humano (cópia manual) | Agentes |
| **Outputs** | `vault/reports/` | Agentes | Humano |

Nenhum agente modifica `vault/Bíblia/`. Nenhuma afirmação factual vai para `vault/wiki/`
sem uma tag `[Fonte: raw/... | Obra: ... | Nível: N]`. Inferências ficam isoladas
em seções "Lacunas Identificadas".

---

## Estrutura do Projeto

```
byblos-obsidian/
├── vault/              ← Vault Obsidian (abrir aqui no Obsidian)
│   ├── Bíblia/         ← Grafo bíblico: 31.102 nós de versículo
│   │   ├── Antigo Testamento/
│   │   │   ├── Pentateuco/
│   │   │   ├── Livros Históricos/
│   │   │   ├── Livros Poéticos/
│   │   │   ├── Profetas Maiores/
│   │   │   └── Profetas Menores/
│   │   └── Novo Testamento/
│   │       ├── Evangelhos/
│   │       ├── Atos dos Apóstolos/
│   │       ├── Epístolas Paulinas/
│   │       ├── Epístolas Gerais/
│   │       └── Apocalipse/
│   ├── wiki/
│   │   ├── conceitos/      ← Artigos de conceitos teológicos
│   │   ├── temas/          ← Artigos de temas exegéticos
│   │   ├── passagens/      ← Análises de perícopes
│   │   ├── autores/        ← Pessoas (autores bíblicos, teólogos)
│   │   ├── obras/          ← Fichas das fontes em raw/
│   │   ├── periodos/       ← Contextos históricos
│   │   └── tradicoes/      ← Tradições interpretativas
│   ├── knowledge/          ← Sistema hipóteses → regras
│   │   ├── cristologia/
│   │   ├── soteriologia/
│   │   ├── pneumatologia/
│   │   ├── escatologia/
│   │   ├── paulinas/
│   │   ├── evangelhos/
│   │   ├── hermeneutica/
│   │   ├── historia-da-interpretacao/
│   │   └── linguistica/
│   ├── reports/
│   │   ├── lint/           ← Relatórios semanais de health check
│   │   ├── qa/             ← Respostas Q&A teológico
│   │   ├── exegeses/       ← Relatórios exegéticos longos
│   │   ├── tematicos/      ← Estudos temáticos
│   │   └── slides/         ← Apresentações
│   └── indices/            ← Índices e metadados do grafo
├── agents/
│   ├── AGENTS.md           ← Contrato normativo de agentes
│   ├── INSTRUCTIONS.md     ← Guia operacional por tipo de tarefa
│   ├── ontology.yaml       ← Contrato de entidades e relações
│   ├── prompts/            ← Prompts de agentes especializados
│   ├── scripts/            ← Scripts Python para processamento
│   ├── tests/              ← Testes automatizados
│   ├── archive/            ← Versões obsoletas (não usar)
│   └── output/             ← Saídas de graph_builder.py
├── raw/                    ← Fontes primárias (local only, não versionado)
│   └── dicionarios-enciclopedias/
│       ├── IVP-Black/      ← DJG2, DPL2, DLNT, DNT-B, DOT-*
│       ├── AYBD/           ← Anchor Yale Bible Dictionary
│       ├── NIDB/           ← New Interpreter's Dict. of the Bible
│       ├── teologicos/     ← EDT, DTIB, DBI-R
│       ├── EAC/            ← Encyclopedia of Ancient Christianity
│       └── especiais/      ← DDD, outros
├── docs/                   ← Documentação do projeto
│   └── convencoes.md       ← Siglas e símbolos NTSK
├── CLAUDE.md               ← Instruções para agentes LLM
├── LICENSE                 ← CC BY-SA 4.0
└── setup.ps1               ← Script de configuração inicial
```

---

## Início Rápido

### Instalação

```powershell
# 1. Clonar repositório
git clone https://github.com/seu-usuario/byblos-obsidian.git
cd byblos-obsidian

# 2. Instalar dependências Python
pip install -r agents/requirements.txt

# 3. Configurar Obsidian
# - Abrir Obsidian → "Open folder as vault"
# - Selecionar: C:\workspace\byblos-obsidian\vault
# - Confirmar que Bíblia/, wiki/, knowledge/ aparecem como pastas irmãs
```

### Scripts Principais

```powershell
# Preview de conversão NTSK → wikilinks
python agents/scripts/ntsk_linker.py --vault vault/Bíblia --dry-run --report preview.csv

# Construir grafo completo
python agents/scripts/graph_builder.py vault/Bíblia agents/output

# Parse de arquivo individual
python -c "from agents.scripts.vault_parser import parse_file; n=parse_file('vault/Bíblia/Novo Testamento/Evangelhos/João/Jo-1.1.md'); print(n.referencia)"
```

---

## Convenções de Nomenclatura

### Nós Bíblicos

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Livro | `<NomeLivro>.md` | `João.md`, `Gênesis.md` |
| Capítulo | `<SGL>-<cap>.md` ou `<SGL> <cap>.md` | `Jo-1.md` ou `Jo 1.md` |
| Versículo | `<SGL>-<cap>.<v>.md` ou `<SGL> <cap>.<v>.md` | `Jo-1.1.md` ou `Jo 1.1.md` |

### Wiki

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Conceito | `<nome-normalizado>.md` | `justificacao-pela-fe.md` |
| Passagem | `<SGL>-<cap>.<vi>-<vf>.md` | `Jo-1.1-18.md` |
| Obra | `<SIGLA>.md` | `DPL2.md`, `BDAG.md` |

### Reports

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Lint | `reports/lint/YYYY-MM-DD.md` | `2026-04-05.md` |
| Q&A | `reports/qa/YYYY-MM-DD_{slug}.md` | `2026-04-05_cristologia-joao-1-1.md` |

---

## Grafo NTSK — Símbolos

O campo `NTSK` em cada nó de versículo pode conter símbolos que implicam arestas no grafo:

| Símbolo | Significado | Tipo de aresta no grafo |
|---------|-------------|------------------------|
| * | Referência especialmente clara | `especially_clear` |
| ✓ | Referência criticamente pertinente | `critically_clear` |
| + | Coleção mais completa | `full_collection` |
| ◐ | Contraste / posição alternativa | `contrast` |
| = | Tipo ou antítipo | `type_antitype` |
| ⩲ | Tipo/antítipo (base escritural) | `type_antitype_scriptural` |
| ▶ | Citação AT→NT | `ot_quote_in_nt` |
| ✡ | Cumprimento de profecia | `fulfills_prophecy` |
| ∥ | Passagem paralela estrita | `parallel_passage` |
| ‡ | Doutrina falsa / uso indevido | `false_doctrine_proof` |
| ❅S# | Strong Hebraico | — (metadado do nó) |
| ✣S# | Strong Grego | — (metadado do nó) |

---

## Hierarquia de Fontes

| Nível | Tipo | Exemplos |
|-------|------|----------|
| 1 | Texto bíblico primário | BHS, NA28, LXX, BKJ, KJV |
| 2 | Léxicos técnicos | BDAG, BDB, HALOT, TDNT, Strong |
| 3 | Comentários exegéticos | ICC, NICNT, NICOT, WBC, Hermeneia |
| 4 | Teologia sistemática | Bavinck, Berkhof, Grudem |
| 5 | Periódicos acadêmicos | JBL, NTS, JETS, WTJ |
| 6 | Obras populares | Referência apenas, nunca suporte doutrinário |

**Tag de citação padrão:**
```
[Fonte: raw/<pasta>/<arquivo> | Obra: <SIGLA> | Nível: N]
```

---

## Git Conventions

Cada commit segue padrão semântico com escopo:

| Prefixo | Quando usar |
|---------|-------------|
| `feat(agents):` | Nova funcionalidade em agentes |
| `fix(docs):` | Correção em documentação |
| `refactor(structure):` | Reorganização de estrutura |
| `chore(deps):` | Atualização de dependências |
| `docs(readme):` | Atualização de README |

---

## Documentação

- **[`CLAUDE.md`](CLAUDE.md)** — Bootstrap: leia ANTES de qualquer tarefa
- **[`agents/AGENTS.md`](agents/AGENTS.md)** — Contrato do vault (versão autoritativa)
- **[`agents/INSTRUCTIONS.md`](agents/INSTRUCTIONS.md)** — Guia de tarefas por tipo
- **[`agents/ontology.yaml`](agents/ontology.yaml)** — Contrato de entidades e relações
- **[`docs/convencoes.md`](docs/convencoes.md)** — Siglas e símbolos NTSK

---

## Agentes Disponíveis

### IngestionAgent
Indexa nova obra em `raw/` e cria ficha em `vault/wiki/obras/`

### EnrichmentAgent
Adiciona seções aos nós de versículo (Léxico, Contexto, Posições Exegéticas)

### WikiCompilerAgent
Cria/mantém artigos em `vault/wiki/conceitos/`, `vault/wiki/autores/`, `vault/wiki/temas/`

### ResearchAgent
Q&A contra o vault + gestão de `vault/knowledge/` (hipóteses → regras)

### GraphAnalystAgent
Análise do grafo NTSK via scripts e queries Dataview

### LintAgent
Health checks periódicos com output em `vault/reports/lint/`

---

## Sistema de Conhecimento Epistêmico

O vault implementa um sistema de promoção epistêmica em `vault/knowledge/{domínio}/`:

```
HIPÓTESE (hypotheses.md)
  ↓ 2+ fontes Nível 2-3, sem contradição Nível 1
KNOWLEDGE (knowledge.md)
  ↓ 3+ fontes Nível 2-3, 2+ tradições
RULE (rules.md)
```

Domínios disponíveis:
- **Teológicos**: cristologia, soteriologia, pneumatologia, escatologia
- **Por Corpus**: paulinas, evangelhos
- **Metodológicos**: hermeneutica, historia-da-interpretacao, linguistica

---

## Fluxo de Trabalho Típico

1. **Adicionar obra** a `raw/dicionarios-enciclopedias/`
2. **Criar ficha** em `vault/wiki/obras/` (IngestionAgent)
3. **Escolher versículo/perícope** para enriquecer
4. **Consultar fontes** via tabela "Decisão de Obra por Corpus" (AGENTS.md)
5. **Adicionar enriquecimento** ao nó de versículo
6. **Se surgirem conceitos novos**, criar artigo em `vault/wiki/conceitos/`
7. **Classificar conhecimento** em `vault/knowledge/{domínio}/`
8. **Commit semântico** com prefixo apropriado

---

## Licença

- Conteúdo original: [CC BY-SA 4.0](LICENSE)
- Textos bíblicos incluídos: domínio público (BKJ1611, KJV)

---

## Próximos Passos Recomendados

1. **Calibração**: rodar enriquecimento completo em `Jo-1.1.md` (versículo rico, teologicamente denso)
2. **Indexar fontes**: criar fichas em `vault/wiki/obras/` para cada diretório em `raw/`
3. **Primeiro lint**: estabelecer baseline com `agents/scripts/lint_checker.py` (quando criado)
4. **Expandir grafo**: identificar pares AT→NT com símbolo `▶` e criar artigos de conceito
5. **Congelar ontologia**: não alterar `agents/ontology.yaml` sem justificativa documentada

---

**Estado**: Atualizado em 2026-04-05 | Repositório em limpeza ativa
