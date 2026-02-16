# TP : Créer et Utiliser un Agent Skill dans VS Code

**Durée estimée :** 1 heure
**Objectif :** Comprendre la structure d'un Agent Skill et l'utiliser avec GitHub Copilot pour générer du contenu de communication interne.

## Prérequis
- VS Code (Version Insiders recommandée pour les dernières fonctionnalités).
- Extension GitHub Copilot & GitHub Copilot Chat installées.
- **Configuration** : Assurez-vous que le paramètre `chat.useAgentSkills` est activé dans vos settings VS Code (si disponible/nécessaire selon la version).

---

## Étape 0 : Configurer les Instructions Personnalisées pour l'IA

Avant même de créer un Agent Skill, il est essentiel de donner du **contexte** à votre assistant IA. C'est le rôle des fichiers d'instructions personnalisées : ils permettent de fournir automatiquement à l'IA des informations sur votre projet, vos conventions et vos préférences, **sans avoir à les répéter à chaque conversation**.

### 🤔 Pourquoi c'est important ?

Sans instructions personnalisées, l'IA part de zéro à chaque interaction. Elle ne connaît pas :
- La stack technique de votre projet
- Vos conventions de nommage ou de style
- Les commandes pour build/test/déployer
- L'architecture de votre codebase

Avec un fichier d'instructions, ces informations sont **préchargées** dans le contexte de l'IA, ce qui la rend immédiatement plus pertinente et productive.

### 📄 Les différents formats

Il existe plusieurs fichiers d'instructions selon l'outil IA que vous utilisez :

| Fichier | Outil principal | Portée |
|---|---|---|
| `.github/copilot-instructions.md` | GitHub Copilot | Projet (workspace) |
| `AGENTS.md` | Multi-agents (Copilot, Codex…) | Projet + sous-dossiers (monorepo) |
| `CLAUDE.md` | Claude Code / Claude dans VS Code | Projet + utilisateur (`~/.claude/CLAUDE.md`) |

> **💡 Bonne nouvelle** : VS Code détecte automatiquement **les trois formats**. Vous pouvez choisir celui qui correspond le mieux à votre usage, ou même en combiner plusieurs !

### 📝 Que mettre dans ce fichier ?

Voici les sections les plus utiles :

1. **Contexte du projet** — Description courte, stack technique, architecture
2. **Structure des répertoires** — Les dossiers clés et leur rôle
3. **Conventions de code** — Nommage, style, patterns à suivre ou éviter
4. **Commandes courantes** — Build, test, lint, déploiement
5. **Flux de travail** — Process de review, stratégie de branches, etc.
6. **Outils et intégrations** — Serveurs MCP, scripts personnalisés, etc.

### 🧪 Exemple de fichier

Voici un exemple de fichier `AGENTS.md` (ou `CLAUDE.md`) pour un projet Python :

```markdown
# Contexte du projet

API REST FastAPI pour la gestion d'utilisateurs.
Utilise SQLAlchemy pour la base de données et Pydantic pour la validation.

## Répertoires clés
- `app/models/` — Modèles de base de données
- `app/api/` — Gestionnaires de routes
- `app/core/` — Configuration et utilitaires
- `tests/` — Tests unitaires et d'intégration

## Conventions
- Type hints obligatoires sur toutes les fonctions
- pytest pour les tests (fixtures dans `tests/conftest.py`)
- PEP 8 avec une limite de 100 caractères par ligne
- Utiliser `date-fns` plutôt que `moment.js` (déprécié)

## Commandes courantes
\```bash
uvicorn app.main:app --reload  # Serveur de dev
pytest tests/ -v               # Lancer les tests
\```

## Notes
- Toutes les routes utilisent le préfixe `/api/v1`
- Les tokens JWT expirent après 24 heures
```

### 👉 Challenge : Créez votre propre fichier

1. **Choisissez un format** parmi `AGENTS.md`, `CLAUDE.md` ou `.github/copilot-instructions.md`
2. **Créez le fichier** à la racine du projet (ou dans `.github/` pour `copilot-instructions.md`)
3. **Rédigez les instructions** adaptées à ce projet de TP. Inspirez-vous de l'exemple ci-dessus et incluez au minimum :
   - Une description du projet
   - La structure des dossiers
   - Les conventions à suivre
4. **Testez** : Ouvrez le chat Copilot et posez une question sur le projet. L'IA devrait désormais avoir connaissance du contexte que vous avez défini.

> **📚 Ressources** :
> - [Custom Instructions dans VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
> - [Utilisation des fichiers CLAUDE.md](https://claude.com/fr-fr/blog/using-claude-md-files)
> - [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

### 💡 Bonnes pratiques

- **Restez concis** : le fichier est ajouté au contexte à chaque interaction, évitez les pavés
- **Expliquez le "pourquoi"** : plutôt que « Utilisez X », écrivez « Utilisez X plutôt que Y car Y est déprécié »
- **Donnez des exemples concrets** : l'IA réagit mieux à des exemples qu'à des règles abstraites
- **Évoluez progressivement** : commencez simple, puis enrichissez au fil des besoins réels
- **Ne les auto-génèrez pas** : les fichiers d'instructions sont vraiment la base de votre IA, elles doivent être rédigées par vous-même pour éviter des erreurs d'interprétation
- **Ne stockez jamais de secrets** : pas de clés API, mots de passe ou tokens dans ce fichier !

---

## Étape 1 : Comprendre la Structure

### 🧩 Qu'est-ce qu'un Agent Skill ?

Un **Agent Skill** est un format ouvert et léger permettant d'étendre les capacités d'un agent IA avec des connaissances et des workflows spécialisés. Concrètement, c'est un **simple dossier** contenant des fichiers qu'un agent peut lire pour adopter une expertise spécifique.

> 📖 **Référence** : Ce format est basé sur la spécification ouverte [Agent Skills](https://agentskills.io) — un standard conçu pour être portable entre différents agents et outils.

### 📂 Structure d'un Skill

Un skill suit une arborescence bien définie :

```
mon-skill/
├── SKILL.md          # ✅ Obligatoire : instructions + métadonnées
├── scripts/          # 📜 Optionnel : code exécutable
├── references/       # 📚 Optionnel : documentation additionnelle
└── assets/           # 🎨 Optionnel : templates, ressources statiques
```

| Dossier/Fichier | Rôle |
|---|---|
| `SKILL.md` | **Le cerveau de l'agent.** Contient les métadonnées (nom, description) et les instructions principales en Markdown. |
| `scripts/` | Code exécutable (Python, Bash, JS…) que l'agent peut lancer. Les scripts doivent être autonomes et bien documentés. |
| `references/` | Documentation détaillée chargée **à la demande** (guides techniques, templates de formulaires, docs spécialisées…). |
| `assets/` | Ressources statiques : templates de documents, images, schémas, fichiers de données. |

### ⚙️ Comment fonctionne un Skill ? (Progressive Disclosure)

Les skills utilisent un mécanisme de **divulgation progressive** pour gérer efficacement le contexte de l'IA.

1. **Découverte** : Au démarrage, l'agent charge **uniquement** le `name` et la `description` de chaque skill disponible (~100 tokens chacun). C'est suffisant pour savoir quand un skill pourrait être pertinent.

2. **Activation** : Quand une tâche correspond à la description d'un skill, l'agent lit le **contenu complet** du `SKILL.md` (instructions, exemples, règles…).

3. **Exécution** : L'agent suit les instructions et charge **à la demande** les fichiers référencés (`scripts/`, `references/`, `assets/`).

> 💡 Cette approche garde l'agent **rapide et économe en contexte** tout en lui donnant accès à des connaissances approfondies quand c'est nécessaire.

### 📝 Le fichier `SKILL.md` en détail

Chaque skill commence par un fichier `SKILL.md` composé de deux parties :

#### 1. Le Frontmatter YAML (obligatoire)

Le bloc entre `---` au début du fichier définit les métadonnées :

```yaml
---
name: internal-comms
description: Rédige des messages de communication interne (Mattermost, emails) avec un ton professionnel et engageant.
---
```

| Champ | Obligatoire | Description |
|---|---|---|
| `name` | ✅ Oui | Identifiant court (max 64 car.). Minuscules, chiffres et tirets uniquement. C'est le nom que vous utiliserez avec `@` dans le chat. |
| `description` | ✅ Oui | Ce que fait le skill et quand l'utiliser (max 1024 car.). Incluez des mots-clés pour que l'agent sache quand l'activer. |
| `license` | Non | Licence du skill. |
| `compatibility` | Non | Prérequis d'environnement (produit cible, packages système…). |
| `metadata` | Non | Métadonnées libres (auteur, version…). |

> ⚠️ **Bonnes pratiques pour la `description`** :
> - ✅ *« Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents. »*
> - ❌ *« Helps with PDFs. »* — Trop vague, l'agent ne saura pas quand activer le skill.

#### 2. Le contenu Markdown (instructions)

Après le frontmatter, le corps du fichier contient les **instructions en Markdown** — sans restriction de format. Écrivez tout ce qui aide l'agent à accomplir la tâche :

- Des instructions étape par étape
- Des exemples d'entrées/sorties (**Few-Shot Prompting**)
- Les cas limites à gérer
- Les règles de style ou de ton

> 📏 **Recommandation** : Gardez le `SKILL.md` sous **500 lignes**. Si vous avez beaucoup de contenu de référence, déplacez-le dans des fichiers séparés dans `references/`.

### Explorez le Skill du TP

📂 Ouvrez le dossier `.github/skills/internal-comms` que nous avons créé.
Vous y trouverez :
- `SKILL.md` : Le cerveau de l'agent avec le frontmatter et les instructions.
- `examples/` : Des fichiers Markdown montrant à l'agent ce qu'on attend de lui (Few-Shot Prompting).
- `resources/` : De la documentation contextuelle (ex: Guide de ton).

👉 **Action** : Lisez le fichier `SKILL.md`. Repérez :
1. Le **frontmatter** : quel `name` définit-il ? C'est ce nom que vous utiliserez avec `/` dans le chat.
2. Les **instructions** : quelles règles de style ou de ton sont données à l'agent ?
3. Les **références aux fichiers** : le `SKILL.md` fait-il référence à des fichiers dans `examples/` ou `resources/` ?

## Étape 2 : Première Interaction
Ouvrez le Chat Copilot (CTRL+CMD+I ou via la barre latérale).

👉 **Action** : Tapez la commande suivante :
```
/internal-comms Aide-moi à rédiger un message Mattermost pour annoncer que le serveur de prod va être redémarré dans 10 minutes.
```

**Observation** :
- L'agent a-t-il utilisé des emojis ? (C'est dans ses instructions !)
- Le ton est-il court et direct ?

## Étape 3 : Modifier le Comportement (Tuning)
Nous allons modifier le skill pour voir comment cela affecte ses réponses.

1. Ouvrez `.github/skills/internal-comms/SKILL.md`.
2. Modifiez la section **Mattermost** pour ajouter une nouvelle règle :
   - *"Termine toujours tes messages par une blague de développeur."*
3. Sauvegardez le fichier.

👉 **Action** : Retestez dans le chat :
```
/internal-comms Annonce que la machine à café est en panne via Mattermost.
```
*Note : Il peut être nécessaire de recharger la fenêtre VS Code (Developer: Reload Window) pour que les changements soient pris en compte.*

## Étape 4 : Ajouter un nouveau canal
Imaginez que nous voulons aussi gérer des posts **LinkedIn** (X).

👉 **Challenge** :
1. Créez un fichier `examples/linkedin_example.md` avec 1 ou 2 exemples de posts (courts, hashtags). Vous pouvez vous inspirer des posts de notre influvoleur préféré : NCV ou des posts d'OCTO, La Grosse Conf, etc.
2. Modifiez `SKILL.md` pour ajouter une section "LinkedIn".
3. Testez : `/internal-comms Rédige un post LinkedIn pour annoncer ta participation à la Grosse Conf`

## Étape 5 : Skills Avancés & Scripts
Les Agents Skills peuvent aussi exécuter des tâches techniques. Nous avons préparé un second skill (`rag-creator`) capable d'initialiser un projet.

1. Regardez le fichier `.github/skills/rag-creator/scripts/setup_rag.py`.
2. Dans le chat, tapez :
```
/rag-creator Crée-moi un nouveau projet RAG.
```
3. L'agent va détecter le script et vous proposer de l'exécuter. Validez la demande.
4. Une fois terminé, vous verrez apparaître les dossiers `data`, `src` et `notebooks` dans votre explorateur de fichiers.

## Étape 6 : Avoir ces Skills toujours à portée de main
Pour utiliser vos skills dans n'importe quel projet VS Code, vous pouvez les copier dans le dossier des skills utilisateur de Copilot.

👉 **Action** : Retestez dans le chat :
```
mv .github/skills/internal-comms ~/.copilot/skills/
```
ou pour ceux qui utilise Claude :
```
mv .github/skills/internal-comms ~/.claude/skills/
```

## Etape 7 : Explorer les skills existants

👉 **Action** : Regardez le dossier `.github/skills/` et explorez les autres skills disponibles en particulier le skill `pdf-to-markdown`. Observez comment les dépendances sont gérées au début du script.

---
> **📚 Ressources** :
> - [OpenAI Agent Skills](https://github.com/openai/skills/tree/main)
> - [VS Code and Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
> - [Agent Skills](https://agentskills.io)

---
**Bravo !** Vous avez créé, testé et itéré sur votre premier Agent Skill. 🚀
