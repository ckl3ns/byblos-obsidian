# CLAUDE.md — byblos-obsidian Knowledge System

> Versão: 1.3 | 2026-04-05
> 
> Leia este arquivo antes de qualquer tarefa neste projeto.
> Para regras detalhadas: `agents/AGENTS.md`
> Para guias de execução: `agents/INSTRUCTIONS.md`

---

## Antes de começar qualquer tarefa

1. Leia `agents/AGENTS.md` — contrato e regras absolutas do vault
2. Consulte `vault/indices/INDEX.md` — estado atual do grafo
3. Verifique se existe artigo em `vault/wiki/` para o domínio da tarefa
4. Leia `vault/knowledge/{domínio}/hypotheses.md` — há hipóteses testáveis com esta tarefa?
5. Aplique `vault/knowledge/{domínio}/rules.md` por padrão

**Domínios disponíveis em vault/knowledge/:**
- Teológicos: `cristologia/`, `soteriologia/`, `pneumatologia/`, `escatologia/`
- Por Corpus: `paulinas/`, `evangelhos/`
- Metodológicos: `hermeneutica/`, `historia-da-interpretacao/`, `linguistica/`

## Ao final de cada tarefa

1. Extraia insights e classifique em `vault/knowledge/{domínio}/`:
   - `hypotheses.md`  → plausível mas sem confirmação multi-fonte ainda
   - `knowledge.md`   → fato confirmado por 2+ fontes Nível 2-3
   - `rules.md`       → confirmado 3+ vezes em fontes Nível 2-3, 2+ tradições
2. Arquive o output em `vault/reports/{tipo}/YYYY-MM-DD_{slug}.md`
   - Tipos disponíveis: `lint/`, `qa/`, `exegeses/`, `tematicos/`, `slides/`
3. Proponha enriquecimentos ao proprietário — nunca execute sem aprovação explícita

## Regras de promoção epistêmica

```
HIPÓTESE → KNOWLEDGE quando:
  ✓ Confirmada por 2+ fontes independentes de Nível 2-3
  ✓ Sem contradição em Nível 1 (texto grego/hebraico)

KNOWLEDGE → RULE quando:
  ✓ Confirmada por 3+ fontes independentes de Nível 2-3
  ✓ Sem contradição em Nível 1
  ✓ Representada em pelo menos 2 tradições distintas
    (ou explicitamente marcada como posição de uma tradição específica)

RULE → HIPÓTESE (rebaixamento) quando:
  ✗ Contradita por evidência de Nível 1 (texto primário)
  ✗ Contradita por revisão crítica em Nível 2 publicada após a rule
```

## Zona proibida

**NUNCA** criar, editar ou deletar arquivos em `vault/Bíblia/`
(exceto adicionar seções de enriquecimento APÓS o conteúdo existente — ver AGENTS.md seção "Enriquecimento permitido em nós de versículo")

## Hierarquia de fontes (resumo)

```
Nível 1  Texto bíblico primário (BHS, NA28, LXX, BKJ, KJV)
Nível 2  Léxicos técnicos (BDB, HALOT, BDAG, TDNT, Strong)
Nível 3  Comentários exegéticos (ICC, NICNT, NICOT, WBC, Hermeneia)
Nível 4  Teologia sistemática (Bavinck, Berkhof, Grudem)
Nível 5  Periódicos (JBL, NTS, JETS, WTJ)
Nível 6  Obras populares (referência apenas, nunca suporte doutrinário)
```

Afirmações em seções factuais de `vault/wiki/` exigem Nível 1-3 mínimo.
