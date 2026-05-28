# GYLT Ingest — Index

*Pipeline YouTube + Instagram + Telegram → Obsidian RAW → Knowledge*

## Documentation

| Fichier | Description |
|---------|-------------|
| [[README]] | Installation humaine + **procédure agent automatique** |
| [[docs/AGENT-SETUP]] | Guide détaillé intégration vault / rules / skills |
| [[docs/templates/cursor-rule-ingest]] | Rule Cursor à copier |
| [[docs/templates/skill-today-ingest-snippet]] | Steps 0.5 + 2.15 pour `/today` |
| [[docs/templates/skill-today-minimal]] | Skill today minimal (vault neuf) |
| [[docs/templates/project-index]] | INDEX projet vault optionnel |
| [[docs/templates/vault-settings]] | Config vault minimal |

## Scripts

| Fichier | Rôle |
|---------|------|
| [[setup.sh]] | venv + dépendances + dossiers |
| [[run_ingest.sh]] | YouTube → Telegram → Instagram |
| [[youtube_ingest.py]] | Playlist → Inbox/Youtube |
| [[instagram_ingest.py]] | Liens → Inbox/Instagram |
| [[telegram_fetch_links.py]] | Telegram → instagram_links.txt |
| [[telegram_login.py]] | Login Telethon (une fois) |
| [[config.py]] | PLAYLIST_URL, Whisper, chemins |
| [[.env.example]] | Template Telegram |

## Repo

https://github.com/BonelliNathan/gylt-ingest
