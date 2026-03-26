# Template — QUERY_REFERENCE.md (BAM Appendice A.4)

Documenta le query SQL critiche o complesse dell'applicazione.
Fornisce agli Agenti AI esempi Gold Standard per la generazione del codice di persistenza.

## Struttura

```markdown
# Query Reference — <nome progetto>

Questo documento raccoglie le query SQL critiche o complesse,
organizzate per modulo. Ogni query ha un ID univoco e serve
come riferimento per gli Agenti durante la generazione del codice.

---

## <N>. <Nome modulo/operazione>

### Q-<MODULO>-<NUMERO>: <Titolo descrittivo>

**Scopo**: <cosa fa la query>
**Tabella**: <tabella/e coinvolta/e> (<volume approssimativo>)
**Tipo**: <SELECT | INSERT | UPDATE | DELETE> <particolarita': JOIN, LIKE, ON CONFLICT, ecc.>

```sql
-- Statement SQL completo con named parameters
SELECT colonna
  FROM schema.tabella
 WHERE condizione = :parametro;
```

| Parametro    | Tipo   | Esempio    | Note                      |
|--------------|--------|------------|---------------------------|
| `:parametro` | string | `'valore'` | Descrizione del parametro |

**Performance**: <note su indici utilizzati, volume dati, LIMIT, partizionamento>

**Note**: <logica applicativa, vincoli, avvertenze>
```

### Query Transazionali

Per query che devono essere eseguite in un'unica transazione atomica,
raggrupparle esplicitamente:

```markdown
### Transazione: <Nome operazione>

Le seguenti query DEVONO essere eseguite in un'unica transazione:

1. Q-MOD-01: <descrizione>
2. Q-MOD-02: <descrizione>

**Rollback**: in caso di fallimento su qualsiasi step, rollback completo.
```

## Regole

- **ID univoco**: formato `Q-<MODULO>-<NUMERO>` (es. `Q-NRC-01`, `Q-FA-03`).
- **Named parameters**: sempre `:nome`, mai valori hardcoded.
- **Volume tabelle**: indicare il volume approssimativo per orientare scelte di performance.
- **Note performance**: obbligatorie per query su tabelle con volume significativo.
- **Raggruppamento transazionale**: query atomiche esplicitamente raggruppate con nota.
