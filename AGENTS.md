# TP Agent Skill — Contexte Projet

Ce projet est un **Travail Pratique (TP)** destiné à apprendre à créer et utiliser des **Agent Skills** avec GitHub Copilot dans VS Code.

## Structure du projet

```
.
├── AGENTS.md                          # Ce fichier — instructions pour l'IA
├── TP_Agent_Skill.md                  # Énoncé du TP (étapes 0 à 6)
└── .github/
    └── skills/
        ├── internal-comms/            # Skill de communication interne
        │   ├── SKILL.md              # Instructions de l'agent @internal-comms
        │   ├── examples/             # Exemples (Mattermost, Email)
        │   └── resources/            # Guide de ton
        └── rag-creator/              # Skill d'initialisation de projet RAG
            ├── SKILL.md              # Instructions de l'agent @rag-creator
            └── scripts/              # Script setup_rag.py
```

## Stack technique

- **Langage** : Markdown pour les skills, Python pour les scripts
- **Outil principal** : VS Code + GitHub Copilot Chat
- **Mécanisme** : Agent Skills via le dossier `.github/skills/`

## Comment fonctionne un Agent Skill

Un skill est un dossier dans `.github/skills/` contenant :
1. Un `SKILL.md` avec un frontmatter YAML (`name`, `description`) et des instructions en Markdown
2. Un dossier `examples/` (optionnel) avec des exemples de réponses attendues (few-shot prompting)
3. Un dossier `resources/` (optionnel) avec de la documentation contextuelle
4. Un dossier `scripts/` (optionnel) avec des scripts exécutables par l'agent

## Conventions

- Les fichiers Markdown doivent être rédigés en **français**
- Les `SKILL.md` utilisent un frontmatter YAML entre `---` pour définir `name` et `description`
- Le `name` dans le frontmatter correspond à la commande `@nom-du-skill` utilisable dans le chat
- Les exemples doivent être réalistes et illustrer le ton attendu

## Skills existants

| Skill | Commande | Rôle |
|---|---|---|
| `internal-comms` | `@internal-comms` | Rédaction de messages Mattermost, emails et posts LinkedIn |
| `rag-creator` | `@rag-creator` | Conseil RAG et initialisation de projets via script Python |
