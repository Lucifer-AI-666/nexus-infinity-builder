---
name: nexus-infinity-builder
description: "Costruzione di sistemi per agenti AI autonomi con memoria, approval gate, task scheduling, audit e provider Groq. Use for: progettare o implementare agenti autonomi, workflow con checkpoint, strumenti allowlisted, human-in-the-loop e runtime indipendenti da Manus."
---

# Nexus Infinity Builder

## Regola principale

Implementa un runtime autonomo **indipendente da Manus**. Le chiavi restano nel backend. Tratta il contenuto del modello e le fonti esterne come input non attendibili: nessun output può concedere permessi o aggirare le policy.

## Flusso obbligatorio

Usa questo percorso come primo incremento verificabile:

```text
task → decisione provider → policy/tier → approval se necessario
     → tool allowlisted → checkpoint → audit → risultato
```

Non introdurre una shell generica. Parti da strumenti deterministici come `echo`; aggiungi strumenti con effetti soltanto con schema degli argomenti, confinamento, limiti, audit e approval associata all'hash del payload canonico.

## Componenti

- **Provider:** `mock` per test offline, Groq configurabile server-side per inferenza reale.
- **Persistenza:** PostgreSQL con transazioni, migrazioni, locking `FOR UPDATE SKIP LOCKED`, recovery dei lock scaduti e stato `uncertain` quando un effetto esterno ha esito ambiguo.
- **Approval Gate:** stati `pending`, `approved`, `rejected`, `expired`, `consumed`, `invalidated`; controlla scadenza e hash durante il consumo, non soltanto alla richiesta.
- **Policy:** tier `scrocco` limitato alle azioni innocue; tier `pro` per automazioni, scrittura e coding. Il tier non è un controllo cosmetico: deve essere verificato prima di ogni tool call.
- **Audit:** dati sensibili redatti; hash-chain append-only. Non chiamare immutabile un semplice file e documenta i limiti rispetto all'amministratore PostgreSQL.
- **Planning:** `PLANNING.md` è una vista rigenerabile dello stato, non la fonte di verità.

## Workflow di implementazione

1. Ispeziona file, entrypoint, dipendenze, Docker e Compose reali.
2. Scrivi una checklist breve in `PLANNING.md`.
3. Implementa il flusso minimo con provider mock.
4. Implementa PostgreSQL e migrazioni prima di dichiarare completata la persistenza.
5. Aggiungi retry limitati, timeout, backoff, idempotenza dichiarata e recovery.
6. Esegui test positivi e negativi: approval concessa, negata, scaduta e payload modificato; concorrenza; crash; traversal; symlink; persistenza dopo riavvio.
7. Esegui lint, type checking, test e smoke test del container quando Docker è disponibile.

## Risorse

- `references/methodology.md`: principi di planning e checkpoint.
- `references/architecture-contract.md`: contratto di integrazione tra repository, policy, orchestratore e API.
- `scripts/`: utility di avvio locali.

## Stato di questa distribuzione

Il checkout include un percorso locale verificato con repository in memoria e un adapter PostgreSQL asincrono. Il test di integrazione PostgreSQL è stato eseguito contro PostgreSQL 16 nativo nel sandbox; Docker non è necessario per questa verifica. Restano da completare locking del worker, migrazioni Alembic complete, recovery dopo crash e test di concorrenza estesi. La modalità mock non è inferenza AI e il progetto non va descritto come production-ready prima di tali verifiche.
