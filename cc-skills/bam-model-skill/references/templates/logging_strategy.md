# Template — LOGGING_STRATEGY.md (BAM Appendice A.2)

Definisce canali, formati e regole di logging dell'applicazione.
Fornisce agli Agenti AI le specifiche per implementare il logging in modo coerente e sicuro.

## Struttura

```markdown
# Strategia di Logging — <nome progetto>

Formato di riferimento: **Structured JSON Logging**

---

## 1. Livelli di log

| Livello   | Uso                                    | Esempio                            |
|-----------|----------------------------------------|------------------------------------|
| `ERROR`   | Errore che impedisce il completamento  | Query fallita, connessione persa   |
| `WARNING` | Situazione anomala ma gestita          | Conflitto su INSERT, limite vicino |
| `INFO`    | Azione di business completata          | Record inserito, operazione OK     |
| `DEBUG`   | Dettaglio tecnico (solo sviluppo)      | SQL eseguito, parametri request    |

---

## 2. Canali di log

### 2.1 <Nome canale> (<destinazione>)

**Canale**: <destinazione tecnica (tabella DB, stderr, file, ecc.)>
**Quando**: <condizione di attivazione>
**Formato record**:

```json
{
  "timestamp": "ISO 8601",
  "level": "ERROR|WARNING|INFO|DEBUG",
  "channel": "<nome canale>",
  "message": "<descrizione leggibile>",
  "context": {
    "<chiave>": "<valore>"
  }
}
```

**Regole**:
- <regola specifica del canale>

---

## 3. Formato risposta <protocollo>

<!-- Se l'applicazione espone API, descrivere il formato
     standard delle risposte (successo/errore). -->

**Successo**:
```json
{ "success": true, "data": <mixed> }
```

**Errore**:
```json
{ "success": false, "message": "Descrizione leggibile", "code": "<codice errore>" }
```

---

## 4. Sicurezza dei log

| Regola                              | Applicazione                          |
|-------------------------------------|---------------------------------------|
| Mai loggare credenziali o password  | <come viene garantito>                |
| Sanitizzare output in produzione    | <meccanismo di controllo>             |
| PII solo in canali protetti         | <quali canali, come protetti>         |

---

## 5. Retention

| Canale         | Retention                             |
|----------------|---------------------------------------|
| <canale>       | <durata o politica>                   |
```

## Regole

- Ogni canale di log deve avere un esempio JSON concreto del formato record.
- Le regole di sicurezza devono indicare *come* vengono applicate, non solo *cosa* e' vietato.
- La sezione Retention e' obbligatoria per ogni canale.
- I livelli seguono la convenzione PSR-3 / Syslog.
