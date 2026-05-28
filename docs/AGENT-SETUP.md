# Agent setup — guide détaillé

Ce document complète le README pour les agents qui installent GYLT Ingest dans un second cerveau existant ou neuf.

## Décision : vault existant ou bootstrap

```
Utilisateur a un vault Obsidian ?
├── OUI → clone dans {VAULT_PATH}/10 - Scripts (ou SCRIPTS_DIR custom)
│         → fusionner templates dans rules/skills existants
└── NON → créer arborescence minimale (voir README § bootstrap)
          → copier skill-today-minimal.md + vault-settings.md
```

## Fichiers templates

| Template | Destination |
|----------|-------------|
| `cursor-rule-ingest.mdc` | `.cursor/rules/gylt-ingest.mdc` |
| `skill-today-ingest-snippet.md` | fusion dans `{AGENT_FOLDER}/Skills/today.md` |
| `skill-today-minimal.md` | vault neuf sans skill today |
| `project-index.md` | `04 - Projects/GYLT-Ingest/INDEX.md` |
| `vault-settings.md` | `{AGENT_FOLDER}/config/vault-settings.md` |

## Placeholders à remplacer

| Placeholder | Exemple |
|-------------|---------|
| `{VAULT_PATH}` | `/Users/me/ObsidianVault` |
| `{SCRIPTS_DIR}` | `/Users/me/ObsidianVault/10 - Scripts` |
| `{AGENT_FOLDER}` | `/Users/me/ObsidianVault/99 - Cursor` |
| `{KNOWLEDGE_DIR}` | `/Users/me/ObsidianVault/03 - Knowledge` |

## Validation automatique

```bash
cd "{SCRIPTS_DIR}"
test -x venv/bin/python || ./setup.sh
./run_ingest.sh
ls Inbox/Youtube/*.md Inbox/Instagram/*.md 2>/dev/null | head -5
grep -l "status: raw" Inbox/Youtube/*.md Inbox/Instagram/*.md 2>/dev/null | wc -l
```

## Interactions humaines requises

| Étape | Automatisable ? |
|-------|-----------------|
| `brew install ffmpeg` | Oui (si brew présent) |
| `config.py` PLAYLIST_URL | Demander URL playlist à l'utilisateur |
| `.env` Telegram api_id/hash | Demander ou pointer vers my.telegram.org |
| `telegram_login.py` | **Non** — code SMS / 2FA interactif |

## Intégration Claude Code (alternative Cursor)

- Copier le snippet Step 0.5 / 2.15 dans `CLAUDE.md` ou skill `today`
- Chemins identiques ; shell = Bash tool

## Mise à jour

```bash
cd "{SCRIPTS_DIR}" && git pull origin main
./venv/bin/pip install -r requirements.txt
```
