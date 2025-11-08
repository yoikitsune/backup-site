# Backup Site

Solution CLI de sauvegarde de site web avec support Docker, optimisée pour WordPress sur FOURNISSEUR_HEBERGEMENT.

## 🐛 Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/backup-site.git
cd backup-site

# Installer les dépendances avec Poetry
poetry install

# Activer l'environnement virtuel
poetry shell
```

## ⚙️ Configuration requise

- Python 3.11+
- Docker (pour l'exécution conteneurisée)
- Clés SSH configurées pour FOURNISSEUR_HEBERGEMENT

## 🔧 Structure du projet

```
backup-site/
├── src/backup_site/          # Code source principal
│   ├── cli.py               # Commandes CLI
│   ├── backup/              # Logique de sauvegarde
│   ├── config/              # Gestion des configurations
│   └── utils/               # Utilitaires
├── docker/                  # Configuration Docker
├── config/                  # Templates de configuration
│   └── example-site.yaml    # Exemple de configuration
├── tests/                   # Tests automatisés
├── .gitignore              # Fichiers ignorés par Git
└── pyproject.toml           # Configuration Python/poetry
```

## 💻 Utilisation

### Configuration initiale

1. **Utiliser un template pré-configuré** (recommandé pour WordPress sur FOURNISSEUR_HEBERGEMENT) :
   ```bash
   cp config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml config/mon-site.yaml
   ```

2. **OU créer une configuration de base** :
   ```bash
   backup-site config init config/mon-site.yaml
   ```

3. **Éditer le fichier avec vos informations** :
   ```bash
   nano config/mon-site.yaml
   ```

4. **Valider et tester** :
   ```bash
   backup-site config validate config/mon-site.yaml
   backup-site ssh test config/mon-site.yaml
   ```

## 🛠️ Configuration

Créez un fichier `config/votre-site.yaml` en vous basant sur `config/example-site.yaml`.

## 🛠️ Sécurité

- Les fichiers de configuration contenant des identifiants ne sont pas suivis par Git
- Utilisez toujours des chemins relatifs pour les clés SSH
- Ne partagez jamais vos fichiers de configuration avec des informations sensibles

## 📁 Développement

### Installation des outils de développement

```bash
poetry install --with dev
```

### Vérification du code

```bash
# Formater le code
poetry run black src/

# Vérifier le style
poetry run flake8 src/

# Vérifier les types
poetry run mypy src/

# Exécuter les tests
poetry run pytest
```

## 📝 Licence

MIT
