# byblos-obsidian

> Vault de estudos bíblicos e teológicos com grafo de 31.000+ versículos,
> infraestrutura de agentes LLM e sistema de gestão de conhecimento.

**byblos** (βύβλος) — papiro, livro; origem etimológica de "Bíblia".

## Estrutura

```
byblos-obsidian/
├── vault/          ← Vault Obsidian (abrir aqui no Obsidian)
│   ├── Bíblia/     ← Grafo bíblico: 31.102 nós de versículo
│   ├── wiki/       ← Artigos compilados por agentes
│   ├── knowledge/  ← Sistema hipóteses → regras
│   ├── reports/    ← Exegeses, análises, slides
│   └── indices/    ← Índices e metadados
├── agents/         ← Scripts, prompts, ontologia
├── raw/            ← Fontes primárias (local only, não versionado)
└── docs/           ← Documentação do projeto
```

## Início rápido

```powershell
# Instalar dependências Python
pip install -r agents/requirements.txt

# Preview de conversão NTSK → wikilinks
python agents/scripts/ntsk_linker.py --vault vault/Bíblia --dry-run --report preview.csv

# Lint do vault
python agents/scripts/lint_vault.py --vault vault/

# CLI de Q&A
python agents/scripts/kb_cli.py ask "Qual o significado cristológico de Mt 1:1?"
```

## Configurar Obsidian

1. Abrir Obsidian → "Open folder as vault"
2. Selecionar `C:\workspace\byblos-obsidian\vault`
3. Confirmar que `Bíblia/`, `wiki/`, `knowledge/` aparecem como pastas irmãs

## Documentação

- [`CLAUDE.md`](CLAUDE.md) — instruções para agentes LLM
- [`agents/AGENTS.md`](agents/AGENTS.md) — contrato do vault
- [`agents/INSTRUCTIONS.md`](agents/INSTRUCTIONS.md) — guia de tarefas por tipo
- [`docs/convencoes.md`](docs/convencoes.md) — siglas e símbolos NTSK

## Licença

Conteúdo original: [CC BY-SA 4.0](LICENSE)  
Textos bíblicos incluídos: domínio público (BKJ1611, KJV)
