# Architecture technique

## Choix technologiques

### Langage principal
- **Python 3.11+** : Idéal pour les scripts CLI, excellent support des bases de données et des opérations système

### Gestion des dépendances
- **Poetry** : Gestion des dépendances et packaging simplifié
- **Click** : Framework CLI pour créer des commandes intuitives

### Base de données
- **MySQL/MariaDB** : Support natif via `mysql-connector-python` ou `PyMySQL`
- **mysqldump** : Utilisation de l'outil natif pour la fiabilité

### Docker
- **docker-compose.yml** : Environnement de test reproduisant la production
  - Services : WordPress, MySQL/MariaDB, SSH
  - Versions configurables (PHP, MySQL)
  - Permet de tester les sauvegardes et les restaurations
  - Permet de valider les mises à jour avant production

### Stockage
- **Format d'archive** : Tar.gz pour la compression
- **Structure** : `backup-{timestamp}/` contenant `files/` et `database.sql`

## Structure du projet

```
backup-site/
├── src/
│   └── backup_site/
│       ├── __init__.py
│       ├── cli.py              # Commandes CLI principales
│       ├── backup/
│       │   ├── __init__.py
│       │   ├── files.py        # FileBackup - Sauvegarde des fichiers (SSH)
│       │   └── database.py     # DatabaseBackup - Sauvegarde BDD (SSH tunnel)
│       ├── docker_load/        # Chargement dans Docker (MVP)
│       │   ├── __init__.py
│       │   ├── files.py        # DockerFileLoad
│       │   ├── database.py     # DockerDatabaseLoad
│       │   └── wordpress.py    # DockerWordPressAdapter
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py     # Configuration par défaut
│       │   └── validators.py   # Validation des configurations
│       └── utils/
│           ├── __init__.py
│           └── helpers.py      # Fonctions utilitaires
├── docker/
│   ├── test-ssh-server/        # Serveur SSH de test (pour tester les sauvegardes)
│   │   ├── Dockerfile
│   │   ├── compose.yml
│   │   └── entrypoint.sh
│   └── production-test/        # Environnement de test production (pour tester les chargements)
│       ├── docker-compose.yml
│       ├── .env.example
│       ├── wordpress/          # Dockerfile WordPress avec wp-cli
│       └── ssh-server/         # Dockerfile SSH server
├── config/
│   ├── FOURNISSEUR_HEBERGEMENT-wordpress.yaml # Configuration FOURNISSEUR_HEBERGEMENT WordPress
│   └── example-site.yaml       # Configuration générique
├── tests/
├── pyproject.toml
└── README.md
```

## Architecture des composants

### 1. CLI Layer (`cli.py`)
- Commande principale : `backup-site`
- Sous-commandes : `backup`, `restore`, `list`, `config`

### 2. Backup Engine
- **FileBackup** : Sauvegarde des fichiers avec exclusion/inclusion (SSH)
- **DatabaseBackup** : Sauvegarde MySQL/MariaDB via mysqldump (SSH tunnel)

### 2b. Docker Load Engine
- **DockerFileLoad** : Chargement des fichiers dans Docker via `docker cp` + `docker exec`
- **DockerDatabaseLoad** : Chargement de la BDD dans Docker via `docker exec`
- **DockerWordPressAdapter** : Adaptation automatique des URLs WordPress via wp-cli

### 3. Configuration System
- **SiteConfig** : Configuration complète du site (hébergeur, CMS, SSH, BDD)
- **ProviderConfig** : Templates par hébergeur (FOURNISSEUR_HEBERGEMENT, etc.)
- **Settings** : Configuration par défaut et validation
- **SecretManager** : Gestion sécurisée des mots de passe et clés SSH

### 4. Docker Integration (US7 + US8)
- **ProductionTestEnv** : Environnement Docker reproduisant la production
  - Services : WordPress (avec wp-cli pré-installé), MySQL/MariaDB, SSH
  - Versions configurables (PHP_VERSION, MYSQL_VERSION, WORDPRESS_VERSION)
  - Permet de tester les sauvegardes et restaurations
  - Fichier : `docker/production-test/docker-compose.yml`
- **DockerLoad** : Classes pour charger les sauvegardes dans Docker
  - `DockerFileLoad` : Chargement des fichiers via `docker cp` + extraction
  - `DockerDatabaseLoad` : Chargement de la BDD via `docker exec`
  - `DockerWordPressAdapter` : Adaptation des URLs et configuration WordPress

## Format des configurations

### Structure d'une configuration de site
```yaml
# site-config.yaml - WordPress sur FOURNISSEUR_HEBERGEMENT
site:
  name: "mon-site-wordpress"
  provider: "FOURNISSEUR_HEBERGEMENT"
  app_type: "wordpress"
  
ssh:
  host: "ssh.FOURNISSEUR_HEBERGEMENT.net"
  user: "username"
  public_key_path: "~/.ssh/id_rsa.pub"  # FOURNISSEUR_HEBERGEMENT nécessite la clé publique
  private_key_path: "~/.ssh/id_rsa"
  port: 22

files:
  remote_path: "/home/username/www"
  include_patterns:
    - "wp-content/**"
    - "wp-config.php"
    - ".htaccess"
  exclude_patterns:
    - "wp-content/cache/**"
    - "wp-content/upgrades/**"
    - "*.log"
    - "node_modules/**"

database:
  host: "localhost"  # FOURNISSEUR_HEBERGEMENT : BDD accessible via localhost depuis SSH
  name: "username_wp"
  user: "username_wp"
  password: "encrypted_password"
  port: 3306

backup:
  destination: "./backups"
  compression: "gzip"
  retention_days: 30
```

### Spécificités FOURNISSEUR_HEBERGEMENT
- **Gestion SSH** : FOURNISSEUR_HEBERGEMENT utilise un système de clés publiques/privées spécifique
- **Accès BDD** : Connexion localhost depuis SSH (pas d'accès direct externe)
- **Chemins standards** : `/home/username/www` pour les fichiers WordPress
- **Configuration WordPress** : `wp-config.php` dans le répertoire www

### Templates par hébergeur
- **FOURNISSEUR_HEBERGEMENT.yaml** : Configuration spécifique FOURNISSEUR_HEBERGEMENT
- **wordpress.yaml** : Template WordPress avec chemins standards
- **custom.yaml** : Configuration personnalisée

## Workflow technique

### Backup
1. Chargement de la configuration (provider + site)
2. Validation des accès (fichiers + base de données)
3. Backup des fichiers (tar avec exclusions)
4. Backup de la base de données (mysqldump)
5. Création de l'archive finale
6. Stockage local avec métadonnées

### Restore
1. Lecture des métadonnées de l'archive
2. Extraction des fichiers
3. Restauration de la base de données
4. Vérification de l'intégrité

## Points techniques à considérer

### Sécurité
- Chiffrement optionnel des archives
- Gestion sécurisée des mots de passe BDD
- Validation des chemins de fichiers

### Performance
- **Compression côté serveur** : Via pipe SSH (`tar --exclude=... | gzip`)
  - Justification : Réduit la bande passante réseau, accélère la récupération des backups
  - Implémentation : Aucun script côté serveur requis, utilise les outils natifs
  - Flux : Client SSH → Commande tar compressée → Pipe direct au client
- Compression adaptative selon la taille
- Parallélisation possible pour gros volumes
- Progress indicators

### Extensibilité
- Plugin system pour nouveaux providers
- Support futur d'autres bases de données
- API REST optionnelle
