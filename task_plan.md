# Task Plan

## Goal
Entender os padrões em `agents/output/graph_stats.json`, com foco em `unresolved_targets`, usando `docs/ntsk` para identificar regras de siglas, símbolos e exceções que ajudem a recuperar referências não extraídas e orientar a próxima implementação.

## Phases
| Status | Phase | Notes |
|---|---|---|
| complete | Criar memória de trabalho da investigação | Arquivos de apoio recriados na raiz do projeto |
| complete | Ler `docs/ntsk` e mapear convenções relevantes | Siglas, símbolos e formato NTSK documentados |
| complete | Cruzar convenções com `unresolved_targets` | Separados casos de cobertura do grafo e ruído do parser |
| complete | Reanalisar o repositório após merges dos agentes | Fix do parser, extractors, lint e docs já integrados |
| complete | Definir desenho da melhoria a implementar | Todos os versículos devem existir como nós do grafo |
| complete | Registrar spec e preparar execução em branch | Branch `feat/ntsk-reference-normalization` criada e plano de parser registrado |
| complete | Corrigir normalização e extração NTSK no parser | Siglas canônicas, qualificadores NTSK e regressões reais cobertos em testes e no grafo |

## Errors Encountered
| Error | Attempt | Resolution |
|---|---|---|
| Leitura completa do vault por `parse_vault('.')` excedeu o tempo limite | 1 | Troca para análise dirigida via `graph_stats.json`, `docs/ntsk` e leitura do código do parser |
| Buscas amplas com `rg` em todo o vault produziram saída excessiva e timeout | 1 | Restringir a análise a amostras, contagens e leitura pontual dos arquivos relevantes |
