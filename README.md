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

**Phase 3 - Sauvegarde de la base de données (US2)** ✅
- [x] Sauvegarde MySQL/MariaDB via mysqldump
- [x] Compression gzip optionnelle
- [x] Support SSL optionnel
- [x] Tests unitaires complets
- [x] Commande CLI : `backup-site backup database <config>`

**Phase 4 - Restauration des fichiers (US8)** ✅
- [x] Restauration des fichiers depuis archive tar.gz
- [x] Transfert SFTP + extraction SSH
- [x] Tests unitaires complets
- [x] Commande CLI : `backup-site restore files <archive> <config>`

**Phase 5 - Restauration de la BDD (US8)** ✅
- [x] Restauration MySQL depuis dump SQL
- [x] Support fichiers compressés et non-compressés
- [x] Tests unitaires complets
- [x] Commande CLI : `backup-site restore database <dump> <config>`

**Phase 6 - Docker production-test (US7)** ✅
- [x] docker-compose.yml avec WordPress, MySQL, SSH
- [x] Configuration par variables d'environnement
- [x] Support des versions PHP, MySQL, WordPress
- [x] Documentation complète

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

## 🐳 Docker - Environnement de test production (US7 + US8)

Pour tester vos sauvegardes et vérifier les mises à jour avant production, utilisez l'environnement Docker qui reproduit votre serveur de production.

### Configuration

```bash
# Configurer les versions (PHP, MySQL)
cd docker/production-test
cp .env.example .env
nano .env  # Éditer les versions
```

### Utilisation

```bash
# Démarrer l'environnement
docker compose up -d

# Vérifier que WordPress est accessible
curl http://localhost

# Restaurer une sauvegarde pour la tester
docker compose exec wordpress tar -xzf /backups/backup.tar.gz -C /var/www/html
docker compose exec mysql mysql -u wordpress -p wordpress < /backups/database.sql

# Arrêter l'environnement
docker compose down
```

Pour plus de détails, voir [docker/production-test/WORKFLOW.md](docker/production-test/WORKFLOW.md).

## 🚀 Test en production réelle

Pour tester backup-site avec un vrai serveur en production (FOURNISSEUR_HEBERGEMENT, etc.) :

1. **Préparer la configuration** :
   ```bash
   cp config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml config/production.yaml
   nano config/production.yaml  # Remplir les infos réelles
   ```

2. **Valider et tester** :
   ```bash
   backup-site config validate config/production.yaml
   backup-site ssh test config/production.yaml
   ```

3. **Sauvegarder** :
   ```bash
   backup-site backup files config/production.yaml -o backups/prod_files.tar.gz
   backup-site backup database config/production.yaml -o backups/prod_db.sql.gz
   ```

4. **Restaurer dans Docker** :
   ```bash
   cd docker/production-test
   nano .env  # Adapter les versions PHP/MySQL/WordPress
   docker compose up -d
   cd ../..
   backup-site restore files backups/prod_files.tar.gz config/production.yaml
   backup-site restore database backups/prod_db.sql.gz config/production.yaml
   ```

5. **Vérifier** :
   ```bash
   curl http://localhost:8080
   docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SHOW TABLES;"
   ```

**Plan détaillé** : Voir [PRODUCTION_TEST_PLAN.md](PRODUCTION_TEST_PLAN.md)

---

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
