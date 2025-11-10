# Workflow complet - Test d'une sauvegarde de A à Z

**Objectif** : Sauvegarder un site WordPress en production (FOURNISSEUR_HEBERGEMENT) et le restaurer localement dans Docker pour vérifier que tout fonctionne.

---

## 📋 Vue d'ensemble

```
PRODUCTION (FOURNISSEUR_HEBERGEMENT)          LOCAL (ton ordinateur)
┌─────────────────────┐        ┌──────────────────────────────┐
│ Mon site WordPress  │        │ Docker (test local)          │
│ - Fichiers          │        │ ┌────────────────────────┐   │
│ - BDD WordPress     │        │ │ backup-test-mysql      │   │
│ - PHP 8.1           │        │ │ backup-test-wordpress  │   │
│ - MariaDB 11.4      │        │ │ backup-test-ssh        │   │
│ - WordPress 6.8     │        │ └────────────────────────┘   │
└─────────────────────┘        └──────────────────────────────┘
         │                               ▲
         │ 1. Sauvegarde                │ 5. Chargement
         │ (fichiers + BDD)             │
         ▼                               │
    ┌─────────────────┐                 │
    │ backups/        │                 │
    │ production/     │─────────────────┘
    │ ├── files.tar   │
    │ └── database.sql│
    └─────────────────┘
```

---

## 🎯 Étape 1 : Configuration Docker

### 1.1 Vérifier le fichier .env

**Fichier** : `docker/production-test/.env`

```bash
# Versions (à adapter selon votre production)
PHP_VERSION=8.1
MYSQL_VERSION=11.4
WORDPRESS_VERSION=6.8

# Accès MySQL (Docker local)
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
```

**⚠️ À adapter** : Remplacer les versions par celles de votre serveur de production.
- Vérifiez les versions PHP, MySQL/MariaDB et WordPress sur votre serveur
- Cela garantit que le test local reproduit exactement la production

### ✅ Checklist Étape 1

- [x] `.env` configuré avec les bonnes versions
- [x] Versions correspondent à FOURNISSEUR_HEBERGEMENT

---

## 🐳 Étape 2 : Lancer Docker

### 2.1 Démarrer les services

```bash
cd docker/production-test
docker compose up -d
```

**Qu'est-ce qui se passe ?**

1. **Création du réseau** : `production-test_backup-network`
   - Permet aux containers de communiquer entre eux
   - Isolé du reste de Docker

2. **Création des volumes** :
   - `production-test_mysql_data` : Stockage persistant MySQL
   - `production-test_wordpress_data` : Stockage persistant WordPress
   - `production-test_backups` : Stockage des sauvegardes

3. **Lancement du container MySQL** : `backup-test-mysql`
   - Image : `mariadb:11.4`
   - Port : 3307 (local) → 3306 (container)
   - Base de données : `wordpress` (vierge)
   - Utilisateur : `wordpress` / `wordpress`
   - Healthcheck : Vérifie que MySQL est prêt

4. **Lancement du container WordPress** : `backup-test-wordpress`
   - Image : `wordpress:6.8-apache`
   - Port : 8080 (local) → 80 (container)
   - Dépend de MySQL (attend que MySQL soit prêt)
   - Fichiers : Vierges (seront remplacés par la restauration)

5. **Lancement du container SSH** : `backup-test-ssh`
   - Image : `production-test-ssh-server` (custom)
   - Port : 2222 (local) → 22 (container)
   - Utilisateur SSH : `testuser` / `testpass`
   - Volume monté : `/home/testuser/www` = Fichiers WordPress
   - Permet à backup-site de restaurer les fichiers via SFTP

### 2.2 Vérifier que Docker est prêt

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

### 2.3 Vérifier la connectivité

```bash
# Vérifier MySQL
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SELECT 1;"

# Vérifier WordPress
curl http://localhost:8080

# Vérifier SSH
ssh -p 2222 testuser@localhost "ls -la /home/testuser/www"
```

### ✅ Checklist Étape 2

- [x] Tous les containers sont "Up"
- [x] MySQL est "Healthy"
- [x] MySQL accessible
- [x] WordPress accessible sur http://localhost:8080
- [x] SSH accessible sur port 2222

---

## 💾 Étape 3 : Sauvegarder depuis FOURNISSEUR_HEBERGEMENT

### 3.1 Créer le répertoire de sauvegarde

```bash
mkdir -p backups/production
```

### 3.2 Sauvegarder les fichiers

```bash
.venv/bin/backup-site backup files config/production.yaml -o backups/production/files.tar.gz
```

**Qu'est-ce qui se passe ?**

1. **Connexion SSH** à FOURNISSEUR_HEBERGEMENT
   - Host : `grand.FOURNISSEUR_HEBERGEMENT.net`
   - User : `UTILISATEUR_SECURISE`
   - Port : 22

2. **Exécution de la commande tar** sur le serveur
   ```bash
   find /home/UTILISATEUR_SECURISE/feelgoodbymelanie.com -type f \
     -path "wp-content/*" -o -name "wp-config.php" -o -name ".htaccess" \
     | tar -czf - -T - > /tmp/backup.tar.gz
   ```

3. **Téléchargement via SFTP**
   - Transfert du fichier compressé depuis FOURNISSEUR_HEBERGEMENT vers ton ordinateur
   - Compression côté serveur = moins de bande passante

4. **Résultat** :
   ```
   ✓ Sauvegarde des fichiers réussie
   Archive: files.tar.gz
   Taille: 76.41 MB
   ```

### 3.3 Sauvegarder la base de données

```bash
.venv/bin/backup-site backup database config/production.yaml -o backups/production/database.sql.gz
```

**Qu'est-ce qui se passe ?**

1. **Connexion SSH** à FOURNISSEUR_HEBERGEMENT

2. **Exécution de mysqldump** sur le serveur
   ```bash
   mysqldump -h localhost -u UTILISATEUR_SECURISE_wp48 -p'p5]QS6.1tK' \
     --routines --triggers --events \
     UTILISATEUR_SECURISE_wp48 | gzip > /tmp/database.sql.gz
   ```

3. **Téléchargement via SFTP**
   - Transfert du dump compressé

4. **Résultat** :
   ```
   ✓ Sauvegarde de la base de données réussie
   Fichier: database.sql.gz
   Taille: 1515.38 KB
   ```

### 3.4 Vérifier les fichiers créés

```bash
ls -lh backups/production/
```

**Résultat attendu** :
```
-rw-rw-r-- 1 julien julien 1,5M Nov  9 12:43 database.sql.gz
-rw-rw-r-- 1 julien julien  77M Nov  9 12:43 files.tar.gz
```

### ✅ Checklist Étape 3

- [x] Sauvegarde des fichiers réussie (76.41 MB)
- [x] Sauvegarde de la BDD réussie (1515.38 KB)
- [x] Fichiers présents dans `backups/production/`

---

## 📥 Étape 4 : Restaurer les fichiers

### 4.1 Charger l'archive des fichiers

```bash
.venv/bin/backup-site load files backups/production/files.tar.gz --container backup-test-wordpress
```

**Qu'est-ce qui se passe ?**

1. **Connexion SSH** au container Docker
   - Host : `localhost`
   - Port : 2222
   - User : `testuser`
   - Chemin : `/home/testuser/www`

2. **Téléchargement SFTP** de l'archive
   - Transfert du fichier `files.tar.gz` vers `/tmp/restore_files.tar.gz`

3. **Extraction SSH** de l'archive
   ```bash
   tar -xzf /tmp/restore_files.tar.gz -C /home/testuser/www
   ```

4. **Nettoyage** du fichier temporaire
   ```bash
   rm -f /tmp/restore_files.tar.gz
   ```

5. **Résultat** :
   ```
   ✓ Restauration des fichiers réussie
   Archive: files.tar.gz
   Destination: /home/testuser/www
   Taille: 76.41 MB
   ```

### 4.2 Vérifier les fichiers restaurés

```bash
docker compose exec ssh-server ls -la /home/testuser/www
```

**Résultat attendu** :
```
total 260
drwxr-x---  7 testuser nobody    4096  7 nov.  17:17 .
drwx--x--x 25 testuser testuser  4096  8 nov.  16:08 ..
-rw-r--r--  1 testuser testuser   561  8 sept. 16:47 .htaccess
-rw-r--r--  1 testuser testuser   405  6 févr.  2020 index.php
-rw-r--r--  1 testuser testuser  3527  4 sept. 18:07 wp-config.php
drwxr-xr-x  9 testuser testuser  4096  4 sept. 18:07 wp-admin
drwxr-xr-x  9 testuser testuser  4096  9 nov.  11:19 wp-content
drwxr-xr-x 30 testuser testuser 12288  4 sept. 18:07 wp-includes
...
```

### ✅ Checklist Étape 4

- [x] Restauration des fichiers réussie
- [x] Fichiers présents dans `/home/testuser/www`
- [x] wp-config.php présent
- [x] wp-content présent
- [x] .htaccess présent

---

## 🗄️ Étape 5 : Restaurer la base de données

### 5.1 Charger le dump SQL

```bash
.venv/bin/backup-site load database backups/production/database.sql.gz
```

**Note** : Les infos de la BDD sont extraites automatiquement depuis `wp-config.php` via wp-cli !

**Qu'est-ce qui se passe ?**

1. **Connexion SSH** au container Docker
   - Host : `localhost`
   - Port : 2222
   - User : `testuser`

2. **Téléchargement SFTP** du dump
   - Transfert du fichier `database.sql.gz` vers `/tmp/restore_database.sql.gz`

3. **Restauration SSH** du dump
   ```bash
   gunzip < /tmp/restore_database.sql.gz | \
   mysql -h localhost -u wordpress -pwordpress wordpress
   ```

4. **Nettoyage** du fichier temporaire
   ```bash
   rm -f /tmp/restore_database.sql.gz
   ```

5. **Résultat** :
   ```
   ✓ Restauration de la base de données réussie
   Dump: database.sql.gz
   Base: wordpress
   Taille: 1515.38 KB
   ```

### 5.2 Configurer WordPress pour Docker local

```bash
.venv/bin/backup-site load setup --old-url "https://www.feelgoodbymelanie.com" --new-url "http://localhost:8080"
```

**Ce que fait la commande** :
1. Configure `FS_METHOD = 'direct'` pour permettre les mises à jour
2. Corrige les permissions et l'owner des dossiers `uploads/`
3. Met à jour `siteurl` et `home` via wp-cli
4. Fait un search-replace sur le contenu
5. Vérifie que tout fonctionne

**Résultat** :
```
✓ Configuration de WordPress réussie
  Filesystem: FS_METHOD = 'direct' configuré
  Permissions: uploads/ corrigées
```

### 5.3 Vérifier les tables restaurées

```bash
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SHOW TABLES;"
```

**Résultat attendu** :
```
Tables_in_wordpress
wp02_actionscheduler_actions
wp02_actionscheduler_claims
wp02_commentmeta
wp02_comments
wp02_jetpack_sync_queue
wp02_links
wp02_options
wp02_postmeta
wp02_posts
wp02_term_relationships
wp02_term_taxonomy
wp02_termmeta
wp02_terms
wp02_usermeta
wp02_users
wp02_wpmailsmtp_debug_events
wp02_wpmailsmtp_tasks_meta
```

### 5.3 Vérifier les données restaurées

```bash
# Compter les posts
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SELECT COUNT(*) as posts FROM wp02_posts;"

# Lister les utilisateurs
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SELECT user_login FROM wp02_users;"

# Vérifier les options WordPress
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SELECT option_name, option_value FROM wp02_options LIMIT 5;"
```

### ✅ Checklist Étape 5

- [x] Restauration de la BDD réussie
- [x] Tables WordPress présentes
- [x] Données présentes (posts, users, options)
- [x] Nombre de tables correct

---

## 🌐 Étape 6 : Afficher le site en local

### 6.1 Accéder à WordPress

```bash
curl http://localhost:8080
```

**Résultat attendu** : Page WordPress (HTML complet)

### 6.2 Ouvrir dans le navigateur

```
http://localhost:8080
```

**Qu'est-ce qui se passe ?**

1. **Requête HTTP** vers `localhost:8080`

2. **Docker redirige** vers le container WordPress
   - Port 8080 (local) → Port 80 (container)

3. **WordPress charge** :
   - Fichiers restaurés depuis `/home/testuser/www`
   - Configuration depuis `wp-config.php` restauré
   - Données depuis la BDD restaurée

4. **Affichage du site** :
   - Accueil du site
   - Tous les posts
   - Tous les utilisateurs
   - Tous les plugins/thèmes

### 6.3 Vérifier les pages principales

```bash
# Accueil
curl http://localhost:8080/

# Admin
curl http://localhost:8080/wp-admin/

# API WordPress
curl http://localhost:8080/wp-json/wp/v2/posts
```

### 6.4 Vérifier les logs

```bash
# Logs WordPress
docker compose logs wordpress | tail -20

# Logs MySQL
docker compose logs mysql | tail -20

# Logs SSH
docker compose logs ssh-server | tail -20
```

### ✅ Checklist Étape 6

- [x] Site accessible sur http://localhost:8080
- [x] Page d'accueil affichée
- [x] Pas d'erreurs 404
- [x] Pas d'erreurs MySQL
- [x] Tous les fichiers chargés correctement

---

## 📊 Résumé complet du workflow

| Étape | Action | Durée | Résultat |
|-------|--------|-------|----------|
| 1 | Configuration Docker | 1 min | .env configuré ✅ |
| 2 | Lancer Docker | 2-3 min | Containers prêts ✅ |
| 3 | Sauvegarder FOURNISSEUR_HEBERGEMENT | 1 min | 78 MB sauvegardés ✅ |
| 4 | Restaurer fichiers | 1 min | 76.41 MB restaurés ✅ |
| 5 | Restaurer BDD | 30 sec | 1515.38 KB restaurés ✅ |
| 6 | Afficher le site | Immédiat | Site visible ✅ |
| **TOTAL** | **Workflow complet** | **~7-8 min** | **MVP fonctionnel** ✅ |

---

## 🎯 Validation finale

**Le test est réussi si** :

- ✅ Docker lancé avec les bonnes versions
- ✅ Sauvegardes créées depuis FOURNISSEUR_HEBERGEMENT
- ✅ Fichiers restaurés dans Docker
- ✅ BDD restaurée dans Docker
- ✅ Site accessible sur http://localhost:8080
- ✅ Données visibles et correctes
- ✅ Pas d'erreurs dans les logs

**Cela signifie** :
- ✅ Les sauvegardes sont correctes
- ✅ La restauration fonctionne
- ✅ Le site peut être restauré en production si nécessaire
- ✅ backup-site est prêt pour la production

---

## 🚀 Prochaines étapes

1. **Nettoyer Docker** (optionnel)
   ```bash
   docker compose down -v
   ```

2. **Documenter les résultats** dans `PRODUCTION_TEST_PLAN.md`

3. **Déployer en production** si tout est OK

---

## 📝 Notes

- Tous les chemins sont relatifs à `/home/julien/Sources/backup-site/`
- Les versions Docker correspondent exactement à FOURNISSEUR_HEBERGEMENT
- Le test peut être répété autant de fois que nécessaire
- Les données restaurées sont exactes et complètes
