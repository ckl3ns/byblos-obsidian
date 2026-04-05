---
tags:
  - João
  - Prólogo
---


## Perícope:
```dataview
LIST  BKJ
FROM "Bíblia/Novo Testamento/Evangelhos/João"
WHERE (capitulo = 15 AND versiculo >= 18) OR (capitulo = 16 AND versiculo > 0 AND versiculo < 5)
SORT capitulo ASC, versiculo ASC
```