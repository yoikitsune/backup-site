# 📋 Vue d'ensemble complète - Commandes de A à Z

**Objectif** : Sauvegarder un site WordPress en production (FOURNISSEUR_HEBERGEMENT) et le charger localement dans Docker avec configuration adaptée.

**Durée totale** : ~14 min 30 sec

---

## 🎯 Phase 1 : Préparation (5 min)

### 1.1 Créer la structure de répertoires

```bash
cd /home/julien/Sources/backup-site

# Créer les répertoires
mkdir -p backups/production
mkdir -p config
mkdir -p scripts
```

### 1.2 Créer la configuration FOURNISSEUR_HEBERGEMENT

```bash
# Créer le fichier de configuration
cat > config/production.yaml << 'EOF'
site:
  name: "mon-site-wordpress"
  provider: "FOURNISSEUR_HEBERGEMENT"
  app_type: "wordpress"
  
ssh:
  host: "ssh.FOURNISSEUR_HEBERGEMENT.net"
  user: "username"
  port: 22
  private_key_path: "~/.ssh/id_rsa"
  public_key_path: "~/.ssh/id_rsa.pub"

files:
  remote_path: "/home/username/www"
  include_patterns:
    - "wp-content/**"
    - "wp-config.php"
    - ".htaccess"
    - "index.php"
  exclude_patterns:
    - "wp-content/cache/**"
    - "*.log"
    - ".well-known/**"

database:
  host: "localhost"
  port: 3306
  name: "username_wp"
  user: "username_wp"
  password: "YOUR_DB_PASSWORD"
  options:
    ssl: false

backup:
  destination: "./backups/production"
  compression: "gzip"
  retention_days: 7
EOF
```

**⚠️ À adapter** : Remplacer `username`, `ssh.FOURNISSEUR_HEBERGEMENT.net` et `YOUR_DB_PASSWORD` par vos vraies valeurs.

### 1.3 Valider la configuration

```bash
.venv/bin/backup-site config validate config/production.yaml
```

**Résultat attendu** :
```
✓ Configuration valide
```

### 1.4 Tester la connexion SSH

```bash
.venv/bin/backup-site ssh test config/production.yaml
```

**Résultat attendu** :
```
✓ Connexion SSH établie
```

---

## 📥 Phase 2 : Sauvegarde depuis FOURNISSEUR_HEBERGEMENT (2 min)

### 2.1 Sauvegarder les fichiers

```bash
.venv/bin/backup-site backup files config/production.yaml -o backups/production/files.tar.gz
```

**Résultat attendu** :
```
✓ Sauvegarde des fichiers réussie
  Archive: files.tar.gz
  Taille: ~76 MB
```

### 2.2 Sauvegarder la base de données

```bash
.venv/bin/backup-site backup database config/production.yaml -o backups/production/database.sql.gz
```

**Résultat attendu** :
```
✓ Sauvegarde de la base de données réussie
  Fichier: database.sql.gz
  Taille: ~1.5 MB
```

### 2.3 Vérifier les fichiers créés

```bash
ls -lh backups/production/
```

**Résultat attendu** :
```
-rw-rw-r-- 1 julien julien 1,5M Nov  9 12:43 database.sql.gz
-rw-rw-r-- 1 julien julien  77M Nov  9 12:43 files.tar.gz
```

---

## 🐳 Phase 3 : Configuration Docker (3 min)

### 3.1 Configurer les versions

```bash
# Éditer docker/production-test/.env
cat > docker/production-test/.env << 'EOF'
# Versions (adaptées à FOURNISSEUR_HEBERGEMENT - feelgoodbymelanie.com)
PHP_VERSION=8.1
MYSQL_VERSION=11.4
WORDPRESS_VERSION=6.8

# Accès MySQL
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=wordpress
MYSQL_USER=wordpress
MYSQL_PASSWORD=wordpress

# Accès SSH (pour les sauvegardes)
SSH_USER=testuser
SSH_PASSWORD=testpass

# Ports
WORDPRESS_PORT=8080
MYSQL_PORT=3307
SSH_PORT=2222
EOF
```

### 3.1b Créer le Dockerfile WordPress (wp-cli inclus) ✅

```bash
# Créer le répertoire
mkdir -p docker/production-test/wordpress

# Créer le Dockerfile
cat > docker/production-test/wordpress/Dockerfile << 'EOF'
FROM wordpress:${WORDPRESS_VERSION:-6.8}-apache

# Installer wp-cli
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar && \
    chmod +x wp-cli.phar && \
    mv wp-cli.phar /usr/local/bin/wp && \
    wp --version --allow-root

# Installer les dépendances supplémentaires
RUN apt-get update && apt-get install -y \
    less \
    && rm -rf /var/lib/apt/lists/*
EOF
```

**Résultat attendu** :
```
Fichier créé : docker/production-test/wordpress/Dockerfile
```

### 3.2 Lancer Docker (avec wp-cli pré-installé) ✅

```bash
cd docker/production-test

# Build l'image WordPress avec wp-cli
docker compose build wordpress

# Lancer Docker
docker compose up -d
```

**Résultat attendu** :
```
✔ production-test-wordpress  Built
✔ Container backup-test-mysql    Started
✔ Container backup-test-wordpress Started
✔ Container backup-test-ssh       Started
```

### 3.3 Vérifier que Docker est prêt

```bash
docker compose ps
```

**Résultat attendu** :
```
NAME                    STATUS
backup-test-mysql       Up (healthy)
backup-test-wordpress   Up
backup-test-ssh         Up
```

---

## Phase 4 : Charger la sauvegarde dans Docker (2 min)

### 4.1 Charger les fichiers

```bash
.venv/bin/backup-site load files backups/production/files.tar.gz --container backup-test-wordpress --path /var/www/html
```

**Résultat attendu** :
```
✓ Chargement des fichiers réussi
  Archive: files.tar.gz
  Container: backup-test-wordpress
  Destination: /var/www/html
  Taille: 76.41 MB
Chargement réussi!
```

### 4.2 Charger la base de données

```bash
.venv/bin/backup-site load database backups/production/database.sql.gz
```

**Note** : Les infos de la BDD sont extraites automatiquement depuis `wp-config.php` via wp-cli. Pas besoin de spécifier `--db-name`, `--db-user`, `--db-password` !

**Résultat attendu** :
```
✓ Chargement de la base de données réussi
  Dump: database.sql.gz
  Container: backup-test-mysql
  Base: UTILISATEUR_SECURISE_wp48
  Utilisateur: UTILISATEUR_SECURISE_wp48
  Taille: 1515.38 KB
Chargement réussi!
```

### 4.3 Vérifier que les données sont chargées

```bash
docker compose -f docker/production-test/docker-compose.yml exec mysql mariadb -u wordpress -pwordpress wordpress -e "SHOW TABLES;"
```

**Résultat attendu** :
```
wp02_options
wp02_posts
wp02_users
... (20+ tables)
```

---

## ⚙️ Phase 5 : Configurer WordPress pour Docker local (1 min)

### 5.1 Configurer WordPress avec la commande CLI

```bash
.venv/bin/backup-site load setup --old-url "https://www.feelgoodbymelanie.com" --new-url "http://localhost:8080"
```

**Résultat attendu** :
```
✓ Configuration de WordPress réussie
  Container: backup-test-wordpress
  Ancien URL: https://www.feelgoodbymelanie.com
  Nouveau URL: http://localhost:8080
  Filesystem: FS_METHOD = 'direct' configuré
  Permissions: uploads/ corrigées

✓ Vérification réussie
  siteurl: http://localhost:8080
  home: http://localhost:8080
Configuration réussie!
```

**Ce que fait la commande** :
1. Configure `FS_METHOD = 'direct'` pour permettre les mises à jour
2. Corrige les permissions et l'owner des dossiers `uploads/`
3. Met à jour `siteurl` et `home` via wp-cli
4. Fait un search-replace sur tout le contenu
5. Vérifie que la configuration a fonctionné

---

## ✅ Phase 6 : Vérification finale (2 min)

### 6.1 Accéder au site

```bash
curl -s http://localhost:8080 | head -50
```

**Résultat attendu** :
```
<!DOCTYPE html>
<html lang="fr-FR">
<head>
    <title>Feelgood by Mélanie</title>
    ...
```

### 6.2 Ouvrir dans le navigateur

```
http://localhost:8080
```

**Résultat attendu** :
- ✅ Page d'accueil du site affichée
- ✅ Pas de redirection vers /wp-admin/install.php
- ✅ Tous les articles visibles
- ✅ Tous les styles chargés

### 6.3 Vérifier l'admin WordPress

```bash
curl -s http://localhost:8080/wp-admin/ | grep -o "<title>.*</title>"
```

**Résultat attendu** :
```
<title>Tableau de bord &lsaquo; Feelgood by Mélanie — WordPress</title>
```

### 6.4 Vérifier les fichiers restaurés

```bash
docker compose -f docker/production-test/docker-compose.yml exec ssh-server ls -la /home/testuser/www | head -20
```

**Résultat attendu** :
```
-rw-r--r--  1 testuser testuser   261 Nov  4 07:39 .htaccess
-rw-r--r--  1 testuser testuser   405 Feb  6  2020 index.php
-rw-r--r--  1 testuser testuser  3527 Sep  4 18:07 wp-config.php
drwxr-xr-x  9 testuser testuser  4096 Sep 30 17:30 wp-admin
drwxr-xr-x  5 testuser testuser  4096 Jul 15 18:17 wp-content
drwxr-xr-x 30 testuser testuser 16384 Sep 30 17:30 wp-includes
```

### 6.5 Vérifier les tables MySQL

```bash
docker compose -f docker/production-test/docker-compose.yml exec mysql mariadb -u wordpress -pwordpress wordpress -e "SELECT COUNT(*) as posts FROM wp02_posts;"
```

**Résultat attendu** :
```
posts
XX (nombre d'articles)
```

### 6.6 Vérifier que wp-cli fonctionne ✅

```bash
docker compose -f docker/production-test/docker-compose.yml exec wordpress wp core is-installed --allow-root
```

**Résultat attendu** :
```
Success: WordPress is installed.
```

---

## 🧹 Phase 7 : Nettoyage (optionnel)

### 7.1 Arrêter Docker

```bash
cd docker/production-test
docker compose down
```

### 7.2 Supprimer les volumes (attention : données perdues)

```bash
cd docker/production-test
docker compose down -v
```

---

## 📊 Résumé des commandes par phase

| Phase | Commandes | Durée |
|-------|-----------|-------|
| 1. Préparation | 4 commandes | 5 min |
| 2. Sauvegarde | 3 commandes | 2 min |
| 3. Docker | 3 commandes | 3 min |
| 4. Chargement | 3 commandes | 2 min |
| 5. Configuration | 3 commandes | 30 sec |
| 6. Vérification | 6 commandes | 2 min |
| **TOTAL** | **22 commandes** | **~14 min 30 sec** |

---

## 🎯 Checklist finale

- [x] Configuration FOURNISSEUR_HEBERGEMENT créée et validée
- [x] Connexion SSH testée
- [x] Fichiers sauvegardés (76 MB)
- [x] BDD sauvegardée (1.5 MB)
- [x] Docker lancé avec les bonnes versions
- [x] Fichiers chargés dans Docker
- [x] BDD chargée dans Docker
- [x] wp-cli installé
- [x] URLs mises à jour
- [x] Site accessible sur http://localhost:8080
- [x] wp-admin accessible sans erreur SSL
- [x] Données visibles et correctes

---

## 🚀 Prochaines étapes

1. **Créer commande `load complete`** : Charger fichiers + BDD + adapter URLs en une commande
2. **Créer tests unitaires** : Tests pour `DockerWordPressAdapter`
3. **Créer tests d'intégration** : Workflow complet de A à Z
4. **Publier** : Mettre sur GitHub en public
5. **Sprint 2** : Restauration en production, sauvegardes automatiques, etc.
