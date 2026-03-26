# Fase 4 — Planning

## Obiettivo

Definire la roadmap operativa passo per passo per gli Agenti AI che eseguiranno la generazione del codice. Suddividere il lavoro in task atomici assegnabili.

## Principi

1. **Competenza**: ogni Agente deve avere una competenza verticale specifica.
2. **Contesto**: il contesto operativo va ritagliato per massima focalizzazione.
3. **Granularita'**: minimizzare le dipendenze tra Agenti per permettere parallelizzazione.

## Bilanciamento

Troppi micro-task → alta efficienza per singola operazione ma difficolta' di integrazione e consumo token elevato.
Troppo pochi task → perdita di parallelismo e contesti troppo ampi.

**Riferimento pratico**: tra 3 e 7 Agenti per progetto (salvo complessita' superiore).

---

## Protocollo Operativo

### Step 1: Piano di Esecuzione — `EXECUTION_PLAN.md`

Suddividi l'operativita' in sub-task atomici per ambito operativo.

**Contenuto** (vedi template `references/templates/execution_plan.md`):

Per ogni Agente definisci:
- **Modello**: haiku (task semplici), sonnet (task standard), opus (task complessi)
- **Tipo**: descrizione del tipo di lavoro
- **Dipendenze**: quali Agenti devono completare prima
- **Docs da leggere**: lista dei file del blueprint da consultare
- **Files**: file da creare (Create) e da modificare (Modify)
- **Pre-check**: condizioni da verificare prima di iniziare
- **Contesto**: briefing testuale per l'Agente
- **Steps**: checklist con checkbox Markdown, ogni step atomico e verificabile
- L'ultimo step di ogni Agente e' un commit con messaggio convenzionale

**Struttura in fasi**:
- Le fasi (Phase) raggruppano Agenti paralleli o sequenziali
- Tra una fase e la successiva: checkpoint umano
- Diagramma ASCII delle dipendenze

**Regole**:
- Ogni step e' una checkbox Markdown (`- [ ]`) per tracciamento progresso.
- La sezione "Docs da leggere" elenca i file del blueprint da consultare *prima* di iniziare.
- La sezione "Files" distingue tra Create e Modify.

**Standard di riferimento**: BAM Appendice A.5

### Step 2: README — `README.md`

Presentazione del progetto come entry point per l'utente finale.

**Contenuto**:
- Overview del progetto
- Requisiti di sistema
- Istruzioni di installazione
- Guida rapida all'uso
- Link alla documentazione completa
- Informazioni su licenza e autori

---

## Artefatti

| File | Template | Standard |
|------|----------|----------|
| `EXECUTION_PLAN.md` | `templates/execution_plan.md` | BAM A.5 |
| `README.md` | — | Standard GitHub |

---

## Transizione all'Implementazione

Dopo la validazione del piano:

1. Annuncia: *"Il blueprint e' completo. Passo alla fase di implementazione."*
2. Attiva **coding-standards-skill** per la metodologia di codifica.
3. Le skill di linguaggio si attivano in base allo stack definito in `TECH_STACK.md`:
   - PHP → **php82-dev-skill**
   - Go → **go-dev-skill**
   - TypeScript/Vue → **ts-vue-dev-skill**
   - PostgreSQL → **postgresql16-dev-skill**
4. Segui `EXECUTION_PLAN.md` per l'ordine di esecuzione e l'assegnazione degli Agenti.

---

## Checkpoint

Al termine della fase, chiedi:

> "Il piano di esecuzione e' pronto: agenti definiti, dipendenze mappate, checkpoint pianificati. Vuoi validarlo prima di avviare l'implementazione?"

NON procedere senza approvazione esplicita dell'umano.
