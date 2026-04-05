# ROADMAP DE EXTRAÇÃO — Dicionários e Enciclopédias

*Criado em: 05 de Abril de 2026*
*Objetivo: Estabelecer as bases arquiteturais e o pipeline de execução para a extração do conteúdo bruto (`raw/`) para o Vault.*

Este documento serve como mapa mental para os próximos Agentes encarregados de processar e injetar conteúdo teológico (Níveis 3 e 4) no Vault Obsidian.

---

## 1. O Problema da Extração (Desafios Mapeados)

Os arquivos em `raw/dicionarios-enciclopedias/*.txt` são extrações brutas (OCR, PDFs convertidos, etc). Eles apresentam:
1. **Falta de Padronização Estrutural:** O AYBD formata artigos diferentemente do EDT ou do IVP-Black.
2. **"Lixo" de Paginação:** Quebras de linha de fim de página, cabeçalhos de impressora, números de páginas espalhados no meio do texto.
3. **Barreira Idiomática:** As fontes estão em Inglês (ex: `JUSTIFICATION`, `ABRAHAM`), mas o Vault Obsidian é em Português (`Justificação.md`, `Abraão.md`).
4. **Resolução de Autoria:** Nomes de autores costumam ficar flutuando ao final do verbete textual ou em bibliografias.

---

## 2. A Arquitetura Proposta (Pipeline Modular)

A construção não deve ser monolítica. Crie um orquestrador genérico e *"Parsers"* textuais voltados a cada selo editorial:

### Fase 1: O Extrator Base (`BaseExtractor`)
Uma classe abstrata responsável por:
- Carregar arquivos `.txt` gigantes em memória fragmentada (yield chunks).
- Limpar quebras de linha sujas (Regex para consertar palavras truncadas com hífen, ex: `theo-\nlogical` -> `theological`).
- Limpar números de página isolados (Regex `^\s*\d+\s*$`).

### Fase 2: Parsers de Selo (Implementações Específicas)
**`AYBD_Parser.py`**
- Padrão identificável: Verbetes geralmente começam em Caps Lock forte ou com metadados bibliográficos bem definidos.
- Output: Uma lista ou generator de dicionários `{"title": "...", "body": "...", "author": "...", "bibliography": "..."}`.

**`IVP_Parser.py`** (Para DJG, DPL, DOT-H, etc)
- As coleções Black Dictionary formam uma família unida. É possível reaproveitar o mesmo Extrator para todos os dicionários dessa linha da IVP.

**`EDT_Parser.py`**
- Processa os volumes *Evangelical Dictionary of Theology*.

### Fase 3: Roteamento & Injeção (O "Alinhador Ontológico")
Não podemos simplesmente jogar os textos em Inglês dentro do Vault. Precisamos de uma etapa de mapeamento:
1. O pipeline lê um verbete (Ex: AYBD -> *"AARON"*).
2. O "Alinhador Ontológico" consulta a `ontology.yaml` ou o catálogo do cofre para saber que *"AARON"* = `vault/wiki/autores/Arão.md`.
3. Ele escreve o verbete extraído, já sanitizado e preferencialmente traduzido (via LLM call ou preservado enriquecido sob rubrica `## Perspectiva AYBD`) no fim da nota oficial do Arão.

---

## 3. Estrutura de Diretórios Recomendada

Para manter o repositório limpo, suba esse trabalho em uma nova pasta `agents/scripts/extractors/`:

```
agents/scripts/extractors/
  ├── __init__.py
  ├── base_extractor.py     # Cleaners de regex e leitura base
  ├── aybd_extractor.py     # Regras do Anchor Yale Bible Dictionary
  ├── ivp_extractor.py      # Regras do InterVarsity Press Dictionaries
  ├── edt_extractor.py      # Regras do Evangelical Dict of Theology
  └── mapper.py             # Trilha o título em inglês -> Nota em pt-br do Vault
```

---

## 4. Instruções e Regras Para os Agentes de Extração

**Para Agentes executando a Fase de Extração no Futuro:**

1. **Nunca Apague o Bruto:** Acesse sempre `raw/` no formato "Read-Only". As informações originais lá são imutáveis.
2. **Trabalhe em Etapas:** Não tente processar todos os 6 gigabytes de texto ao mesmo tempo. Execute testes (*dry-runs*) com extratores dumpando em arquivos JSON parciais em `agents/output/extract_staging/` para aferir a qualidade da Extração.
3. **O Respeito à Hierarquia de CLAUDE.md:** Se o extrator criar conhecimento cru, registre na frontmatter sob qual Nível de Fonte ele se encontra (ex: `AYBD` é Nível 3, `EDT` é Nível 4).
4. **Revisão Manual do Dicionário (Glossário):** A etapa mais sensível é o mapeamento de "Inglês -> Português" dos títulos dos verbetes. Sugere-se gastar parte do orçamento da API gerando primeiro uma lista de equivalências (ex: `en2pt_ontology.json`) e pedir validação humana antes de prosseguir com gravações de centenas de arquivos `*.md`.

---
*Prossiga construindo a classe `BaseExtractor` ao ligar os motores na próxima oportunidade.*