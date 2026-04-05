# Bugs e Correções Pendentes — NTSKParser

*Criado em: 05 de Abril de 2026*

---

## BUG-001: Intervalos tipo "cap.vers-vers" não expandem corretamente

**Severidade:** Alta
**Arquivo:** `agents/scripts/ntsk_parser.py`

**Descrição:**
Quando o NTSK usa o padrão `Lc 24.22-24` (i.e. capítulo com ponto, depois intervalo de versículos), o parser NÃO expande o intervalo e gera um target_id malformado como `"Lc 24.22-24"` em vez de gerar 3 referências separadas: `Lc 24.22`, `Lc 24.23`, `Lc 24.24`.

**CausaRaiz:**
O regex `_REF_NO_BOOK` captura `(\d+)` para capítulo e `(\d+)` para versículo. Porém, quando existe um intervalo como `24.22-24`, o post_syms recebe `22-24` como string, mas `_expand_verses` só processa intervalos com `-` quando encontra `^\d+-\d+$` — ou seja, espera `22-24` e não recebe porque `24.22-24` é formatado como `cap.vers-vers`.

**Exemplo de entrada problemática:**
```
Lc 24.22-24. Mc 16.9-11.
```

**Comportamento atual:**
- Gera 1 ref com `verses=['22-24']` → target_id `Lc 24.22-24` ❌

**Comportamento esperado:**
- Gera 3 refs: `Lc 24.22`, `Lc 24.23`, `Lc 24.24` ✅

**Solução proposta:**
No método `_expand_verses`, quando o input é `cap.vers-vers` (ex: `24.22-24`), fazer:
1. Detectar padrão `^\d+\.\d+-\d+$`
2. Separar capítulo (`24`) de versículos (`22-24`)
3. Reconstruir a lógica de expansão de intervalo usando o chapter correto

---

## Histórico de Bugs Corrigidos

| ID | Descrição | Status | Data | Commit |
|----|-----------|--------|------|--------|
| BUG-001 | "cap.vers-vers" não expande | **Corrigido** | 05/04/2026 | 0515d0a9 |
