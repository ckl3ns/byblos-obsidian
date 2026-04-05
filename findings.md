# Findings

## NTSK Investigation

- `docs/ntsk/ntsk_2_sigla.json` mapeia diretamente as siglas NTSK em inglês para as siglas portuguesas usadas no projeto, por exemplo `Ps -> Sl`, `Mk -> Mc`, `Jn -> Jo`, `Ro -> Rm`, `1 Co -> 1Co`, `1 T -> 1Tm`.
- `docs/ntsk/symbols.txt` documenta que sufixos como `n`, `mg` e letras `a/b/c` apos o versiculo fazem parte da notacao da fonte e nao sao referencias invalidas por si so.
- `docs/ntsk/symbols.txt` tambem documenta que livros de capitulo unico podem aparecer sem `:` e que repeticoes e marcadores editoriais fazem parte do formato original.
- `docs/ntsk/howto.txt` confirma o padrao base de referencia `Livro capitulo:versiculo` e mostra o uso de simbolos como `*` no corpo das referencias.
- Em `unresolved_targets`, `13861` de `15376` entradas ja comecam com uma sigla portuguesa valida presente em `sigla_2_nome.json`; o unico livro fora do mapa identificado na amostra foi `Ex`, com `1515` ocorrencias, sugerindo incompatibilidade por acento em relacao a `Êx`.
- A maior classe de `unresolved_targets` e `clean_dot_ref` (`12381`), isto e, referencias simples como `1Rs 6.10` ou `1Sm 17.21` que parecem validas na notacao interna do projeto.
- Outras classes relevantes: `verse_suffix` (`653`), `embedded_second_ref` (`603`), `text_after_dot` (`601`) e `chapter_ref` (`422`).
- `582` entradas de `unresolved_targets`, apos normalizacao simples `Livro capitulo.versiculo -> Livro capitulo:versiculo`, coincidem com referencias listadas em `docs/ntsk/noref.txt`. Isso sugere que parte dos alvos nao resolvidos sao referencias biblicas validas mesmo quando aparecem em versos sem conjunto proprio de referencias na fonte.
- `agents/scripts/graph_builder.py` mostra que `unresolved_targets` sao targets forward que nao aparecem em `source_ids`, e `source_ids` sao montados apenas a partir de versiculos com `ntsk_raw`. Portanto, um target pode ser um versiculo biblico valido e ainda assim cair em `unresolved_targets` se o versiculo nao tiver bloco NTSK no vault.
- `agents/scripts/ntsk_parser.py` confirma que a notacao interna do projeto usa `Livro capitulo.versiculo` como ID de alvo. Assim, casos como `1Rs 6.10` nao estao errados por usar ponto; o problema tende a ser cobertura do grafo ou residuos de parse, nao o separador em si.
- A classe dominante `clean_dot_ref` precisa ser interpretada com cuidado: parte dela representa versiculos biblicos validos que nao viram source node, enquanto as classes `text_after_dot`, `embedded_second_ref`, `verse_suffix` e `chapter_ref` apontam mais claramente para ruido de parse ou necessidade de normalizacao extra.
- Em `.planning`, o unico trabalho paralelo com risco direto de conflito para a minha futura implementacao e o do agente focado em `ntsk_parser.py`; os demais atuam em extractors, lint e documentacao.

## Repo Update After Agent Merges

- O `main` agora ja contem o commit `0515d0a9` em `agents/scripts/ntsk_parser.py`, que corrige o BUG-001 de expansao de intervalos `cap.vers-vers` como `Lc 24.22-24`.
- O fix do parser adicionou suporte explicito em `_expand_verses()` para o padrao `^\d+\.\d+-\d+$` e incluiu 4 testes novos em `agents/tests/test_ntsk_parser.py`.
- A estrutura base de extratores foi integrada em `agents/scripts/extractors/`, com `BaseExtractor`, `ExtractedEntry`, `AYBDExtractor` e testes dedicados.
- A auditoria de lint gerou `vault/reports/lint/2026-04-05.md`, com 2 problemas criticos de fonte e 34 menores, sobretudo `LINK_QUEBRADO` e `PATH_RAW_INVALIDO`.
- A limpeza de documentacao foi integrada em `agents/AGENTS.md` e `agents/INSTRUCTIONS.md`, sem impacto funcional direto na logica NTSK.
- Depois dessa nova leitura do repositório, o principal risco anterior de conflito no parser caiu bastante, porque a correcao planejada pelo agente de NTSK ja esta presente no `main`.
