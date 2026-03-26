# Template — AQ_ITERATIONS.md (BAM Appendice A.1)

Traccia il dialogo iterativo tra umano e AI durante il Brainstorming.
Ogni domanda-risposta viene registrata per evitare ridondanze nelle sessioni successive.

## Struttura

```markdown
# Iterazione Domande & Risposte

Progetto: **<nome progetto>** — <descrizione breve>
Documento di riferimento: `PROJECT.md`

---

## Iterazione <N> — <Titolo descrittivo della sessione>

<!-- Le domande sono raggruppate per AREA tematica.
     Ogni area ha un identificativo a lettera (A, B, C, ...). -->

### AREA <LETTERA> — <Nome area tematica>

| ID   | Domanda | Risposta | Stato     |
|------|---------|----------|-----------|
| A.01 | ...     | ...      | RISOLTO   |
| A.02 | ...     | ...      | APERTO    |
| A.03 | ...     | ...      | RIMANDATO |
```

## Regole

- Le iterazioni sono numerate progressivamente (1, 2, 3, ...) e corrispondono a sessioni di lavoro distinte.
- Una nuova iterazione viene aperta quando si riprende il dialogo dopo una pausa o un aggiornamento significativo del `PROJECT.md`.
- **ID formato**: `<LETTERA>.<NUMERO>` (es. A.01, B.03).
- **Stati possibili**: `RISOLTO`, `APERTO`, `RIMANDATO`.
- Le domande con stato `APERTO` devono essere riprese nella successiva iterazione.
- Le risposte dell'umano vanno riportate *verbatim*, senza riformulazione da parte dell'AI.
- Le domande devono citare riferimenti specifici (nomi di file, sezioni del `PROJECT.md`) per evitare ambiguita'.
