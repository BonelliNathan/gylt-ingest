---
date: YYYY-MM-DD
type: index
projet: GYLT-Ingest
tags: [ingestion, youtube, instagram, telegram, second-cerveau]
source: gylt-ingest
---

# GYLT-Ingest

## Pourquoi

Capitaliser automatiquement le contenu YouTube / Instagram consommé en base de connaissance Obsidian.

## Architecture

```
YouTube / Telegram / Instagram  →  {SCRIPTS_DIR}  →  Inbox/*.md (RAW)
                                                      →  Agent /today Step 2.15
                                                      →  {KNOWLEDGE_DIR}/
```

## Implémentation

| Composant | Chemin |
|-----------|--------|
| Scripts | `{SCRIPTS_DIR}` |
| Repo | https://github.com/BonelliNathan/gylt-ingest |
| RAW | `{SCRIPTS_DIR}/Inbox/` |
| Skill | `{AGENT_FOLDER}/Skills/today.md` |

## Statut

- Installé le : YYYY-MM-DD
- Prochaine étape : configurer `PLAYLIST_URL`, login Telegram si besoin

## Liens

- [[../../10 - Scripts/README]]
- [[../../03 - Knowledge/INDEX]]
