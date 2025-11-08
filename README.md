# Backup Site

Solution CLI de sauvegarde de site web avec support Docker, optimisée pour WordPress sur FOURNISSEUR_HEBERGEMENT.

## 📊 État du projet

### ✅ Fonctionnalités complètes et testées

**Phase 1 - Configuration (US4)** ✅
- [x] Configuration YAML avec validation Pydantic
- [x] Gestion sécurisée des clés SSH
- [x] Test de connexion SSH
- [x] Template optimisé pour WordPress sur FOURNISSEUR_HEBERGEMENT
- [x] Support des patterns inclusion/exclusion
- [x] Environnement de test Docker

**Phase 2 - Sauvegarde des fichiers (US1)** ✅
- [x] Sauvegarde des fichiers via SSH avec compression côté serveur
- [x] Patterns d'inclusion/exclusion (compatible GNU tar et BusyBox tar)
- [x] Archive tar.gz compressée
- [x] Tests unitaires et d'intégration
- [x] Commande CLI : `backup-site backup files <config>`

### 🚀 En développement

- [ ] Sauvegarde de la base de données MySQL (US2)
- [ ] Exécution via Docker (US7)

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

### Fichiers de configuration disponibles

- **`config/example-site.yaml`** : Configuration générique de base
- **`config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml`** : Template optimisé pour WordPress sur FOURNISSEUR_HEBERGEMENT (recommandé)

### Créer votre configuration

1. Copiez un template :
   ```bash
   cp config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml config/mon-site.yaml
   ```

2. Éditez avec vos paramètres :
   ```bash
   nano config/mon-site.yaml
   ```

3. Validez la configuration :
   ```bash
   backup-site config validate config/mon-site.yaml
   ```

4. Testez la connexion SSH :
   ```bash
   backup-site ssh test config/mon-site.yaml
   ```

### Structure d'une configuration

Voir `config/README.md` pour les détails sur les templates et les sections disponibles.

## 📋 Commandes disponibles

### Configuration
```bash
backup-site config init <output>          # Créer une config de base
backup-site config validate <config>      # Valider une configuration
```

### SSH
```bash
backup-site ssh setup-guide               # Afficher le guide de configuration SSH
backup-site ssh test <config>             # Tester la connexion SSH
```

### Sauvegarde
```bash
backup-site backup files <config>         # Sauvegarder les fichiers
backup-site backup files <config> -o <path>  # Sauvegarder avec chemin personnalisé
```

### Utilitaires
```bash
backup-site --version                     # Afficher la version
backup-site --help                        # Afficher l'aide
backup-site -v <commande>                 # Mode verbose
```

## 🛠️ Sécurité

- Les fichiers de configuration contenant des identifiants ne sont pas suivis par Git
- Utilisez toujours des chemins relatifs pour les clés SSH
- Ne partagez jamais vos fichiers de configuration avec des informations sensibles

## 🧪 Tests

Pour plus de détails sur les tests, voir [TESTING.md](TESTING.md).

### Tests unitaires
```bash
poetry run pytest tests/ -v
```

### Tests d'intégration avec Docker
```bash
# Démarrer le serveur SSH de test
cd docker/test-ssh-server && docker compose -f compose.yml up -d && sleep 5 && cd ../../

# Lancer la sauvegarde
backup-site backup files config/test-docker.yaml -o backups/test_backup.tar.gz

# Vérifier l'archive
tar -tzf backups/test_backup.tar.gz

# Arrêter le serveur
cd docker/test-ssh-server && docker compose -f compose.yml down && cd ../../
```

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
