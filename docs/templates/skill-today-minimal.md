---
name: today
description: Plan du jour + ingestion contenu (YouTube/Instagram/Telegram) + traitement RAW → Knowledge. Trigger /today, bonjour, good morning.
---

## Step 0.5 — Ingestion

```bash
cd "{SCRIPTS_DIR}" && ./run_ingest.sh
```

Non-bloquant. Si échec → noter dans le plan et continuer.

## Step 2.15 — RAW → Knowledge

Traiter **toutes** les notes `{SCRIPTS_DIR}/Inbox/{Youtube,Instagram}/*.md` avec `status: raw`.

WebSearch → notes `{KNOWLEDGE_DIR}/` → archive `Inbox/_archived/`.

Voir `docs/templates/skill-today-ingest-snippet.md` pour le détail.

## Plan du jour

Lire `{VAULT_PATH}/00 - Daily notes/YYYY-MM-DD.md`, proposer priorités, afficher `INGEST_SUMMARY`.
