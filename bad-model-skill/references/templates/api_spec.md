# Template — API_SPEC.md (BAD Appendice A.3)

Documenta tutti gli endpoint esposti dal backend con parametri, risposte attese e logica.
Rappresenta il contratto di interfaccia tra frontend e backend.

## Struttura

```markdown
# Specifica API — <nome progetto>

Formato: **Endpoint-Action Reference**

---

## 1. Convenzioni generali

### 1.1 Base URL

<pattern di base per tutti gli endpoint>

### 1.2 Formato richiesta

- Metodi HTTP supportati: GET, POST, PUT, DELETE
- Content-Type: application/json (salvo upload file)

### 1.3 Formato risposta

**Successo** (HTTP 200):
```json
{
  "success": true,
  "data": <mixed>
}
```

**Errore** (HTTP 400/500):
```json
{
  "success": false,
  "message": "Descrizione leggibile",
  "code": "<codice errore opzionale>"
}
```

**Non autorizzato** (HTTP 401/403):
```json
{
  "success": false,
  "message": "Accesso negato"
}
```

---

## <N>. <Nome modulo> — <file endpoint>

### <N.M> <METHOD> <path>?action=<action> — <Descrizione>

**Parametri**:

| Nome   | Tipo   | Obbligatorio | Descrizione           |
|--------|--------|--------------|-----------------------|
| `nome` | string | Si           | Descrizione parametro |

**Risposta** (`data`):
```json
{ "campo": "valore" }
```

**Logica backend**:
1. Validazione parametri
2. <Passo operativo>
3. <Passo operativo>
4. Return risposta

**Note transazionali**: <se richiede transazione atomica, specificare>
```

## Regole

- Ogni endpoint deve avere almeno un esempio JSON di risposta.
- I parametri obbligatori devono essere esplicitamente marcati.
- La logica backend e' descritta in passi numerati.
- Se coinvolge transazioni atomiche, specificarlo nella sezione "Note transazionali".
- Campi nascosti (es. `id` presenti nei dati ma non visibili all'utente) devono essere documentati con nota esplicita.
- Raggruppare gli endpoint per modulo funzionale.
