# Fase 1 — Brainstorming

## Obiettivo

Ridurre l'entropia informativa. Raggiungere una comprensione reciproca ad alta confidenza tra umano e AI prima di qualsiasi attivita' progettuale.

## Principi

- **Eliminare le assunzioni**: dichiara cosa non hai compreso invece di indovinare.
- **Creare un perimetro**: definire cosa il software deve e, soprattutto, cosa NON deve fare.
- **Comprensione reciproca**: come tra umani, la comprensione e' frutto di un processo iterativo.

---

## Protocollo Operativo — Ciclo Socratico

### Step 1: Enunciazione del Progetto

L'umano fornisce l'idea iniziale. Non e' necessario che sia tecnica — deve essere chiara su:
- **Obiettivi di business**
- **Esperienza utente attesa**
- **Contesto applicativo e operativo**
- **Esempi pratici** tratti da contesti realistici

Se l'umano non fornisce questi elementi, chiedili esplicitamente.

**Azione**: crea `PROJECT.md` v1 con il brief ricevuto.

### Step 2: Analisi Critica

NON limitarti ad accettare il brief. Analizzalo cercando:
- Lacune logiche
- Conflitti tra requisiti
- Ambiguita' terminologiche
- Scenari non coperti
- Vincoli impliciti non dichiarati

### Step 3: Loop di Q&A

Poni domande mirate per aumentare la definizione del progetto.

**Regole del loop:**
- Una domanda alla volta, specifica e contestualizzata.
- Preferisci domande a scelta multipla quando possibile.
- Traccia ogni domanda e risposta in `AQ_ITERATIONS.md`.
- Le risposte dell'umano vanno riportate *verbatim*, senza riformulazione.
- Le domande devono citare riferimenti specifici (sezioni del PROJECT.md, scenari concreti).
- Continua finche' non dichiari di avere una **comprensione ad alta confidenza**.
- Le domande con stato APERTO devono essere riprese nella successiva iterazione.

**Criteri per dichiarare alta confidenza:**
- Tutti gli obiettivi di business sono espliciti e non ambigui.
- Il perimetro funzionale e' definito (cosa fa E cosa non fa).
- I principali scenari d'uso sono coperti.
- Non ci sono conflitti tra requisiti.
- Le domande aperte residue sono marginali o rimandabili.

### Step 4: Sintesi Operativa

Aggiorna `PROJECT.md` con tutti i dettagli emersi dal loop Q&A:
- Visione consolidata
- Perimetro funzionale
- Vincoli noti
- Scenari d'uso principali
- Decisioni prese durante il brainstorming

---

## Artefatti

| File | Formato | Scopo |
|------|---------|-------|
| `PROJECT.md` | Testo strutturato | Visione, obiettivi, perimetro, vincoli |
| `AQ_ITERATIONS.md` | Template BAM A.1 | Log storico Q&A — vedi `references/templates/aq_iterations.md` |

---

## Checkpoint

Al termine della fase, chiedi:

> "Il PROJECT.md riflette la tua visione del progetto? Tutti i punti chiave sono coperti? Posso procedere alla Fase 2 — Analisi e Design?"

NON procedere senza approvazione esplicita dell'umano.
