# Plan d'action - Test réel en production

**Objectif** : Sauvegarder un site WordPress en production (FOURNISSEUR_HEBERGEMENT) et le restaurer localement dans Docker.

**Date de démarrage** : 2025-11-09  
**Statut** : ✅ Étape 1 complétée - Prêt pour la sauvegarde  
**Responsable** : Julien

**Site** : example-prod-site.com (FOURNISSEUR_HEBERGEMENT)

---

## 📋 Checklist pré-test (Environnement)

Avant de commencer, vérifier que l'environnement local est prêt :

- [ ] Docker installé et fonctionnel
- [ ] backup-site installé et testé (`backup-site --help`)
- [ ] Espace disque disponible pour les sauvegardes (~1-10 GB)

---

## 🎯 Étape 1 : Préparer la configuration FOURNISSEUR_HEBERGEMENT

### 1.0 Prérequis - Informations FOURNISSEUR_HEBERGEMENT

Avant de créer la configuration, tu dois avoir :

- [ ] **Accès SSH à FOURNISSEUR_HEBERGEMENT** : Pouvoir se connecter en SSH au serveur
- [ ] **Clé SSH configurée** : Clé privée/publique générée et testée
- [ ] **Informations de connexion notées** :
  - Domaine ou IP du serveur
  - Utilisateur SSH
  - Port SSH (défaut: 22)
  - Chemin vers la clé privée SSH
  - Chemin WordPress sur le serveur
  - Identifiants MySQL (host, user, password, database)
  - Versions PHP, MySQL, WordPress

**📋 Formulaire à remplir** : Voir [O2SWITCH_INFO.md](O2SWITCH_INFO.md)

Ce fichier contient un formulaire complet à remplir avec :
- Infos serveur et SSH
- Chemins WordPress
- Identifiants MySQL
- Versions PHP/MySQL/WordPress
- Checklist de vérification

### ✅ Checklist Étape 1.0

- [ ] Accès SSH à FOURNISSEUR_HEBERGEMENT disponible
- [ ] Clé SSH configurée et testée
- [ ] Informations de connexion FOURNISSEUR_HEBERGEMENT notées (voir exemple ci-dessus)
- [ ] Versions PHP/MySQL/WordPress connues

---

### 1.1 Créer le fichier de configuration

```bash
cd /home/julien/Sources/backup-site
cp config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml config/production.yaml
```

### 1.2 Éditer la configuration avec les infos réelles

```bash
nano config/production.yaml
```

**À modifier** :
- `site.name` : Nom du site
- `ssh.host` : Domaine ou IP FOURNISSEUR_HEBERGEMENT
- `ssh.user` : Utilisateur SSH FOURNISSEUR_HEBERGEMENT
- `ssh.port` : Port SSH (défaut: 22)
- `ssh.private_key_path` : Chemin vers la clé SSH
- `files.remote_path` : Chemin WordPress sur FOURNISSEUR_HEBERGEMENT
- `database.host` : Hôte MySQL (localhost ou tunnel SSH)
- `database.port` : Port MySQL (défaut: 3306)
- `database.name` : Nom de la base de données
- `database.user` : Utilisateur MySQL
- `database.password` : Mot de passe MySQL

**Exemple** :
```yaml
site:
  name: "exemple-site-production"
  provider: "FOURNISSEUR_HEBERGEMENT"
  app_type: "wordpress"

ssh:
  host: "example-prod-site.com"
  user: "example_ssh_user"
  port: 22
  private_key_path: "~/.ssh/id_rsa"
  public_key_path: "~/.ssh/id_rsa.pub"

files:
  remote_path: "/home/example_ssh_user/www"
  include_patterns:
    - "wp-content/**"
    - "wp-config.php"
    - ".htaccess"
  exclude_patterns:
    - "wp-content/cache/**"
    - "*.log"

database:
  host: "localhost"
  port: 3306
  name: "[DATABASE_NAME]"
  user: "[DATABASE_USER]"
  password: "[DATABASE_PASSWORD]"
  options:
    ssl: false

backup:
  destination: "./backups/production"
  compression: "gzip"
  retention_days: 7
```

### ✅ Checklist Étape 1 (Complète) - VALIDÉE ✅

**Prérequis (1.0)** :
- [x] Accès SSH à FOURNISSEUR_HEBERGEMENT disponible ✅
- [x] Clé SSH configurée et testée ✅
- [x] Informations de connexion FOURNISSEUR_HEBERGEMENT notées ✅
- [x] Versions PHP/MySQL/WordPress connues ✅

**Configuration (1.1 + 1.2)** :
- [x] Fichier `config/production.yaml` créé ✅
- [x] Toutes les infos FOURNISSEUR_HEBERGEMENT remplies ✅
- [x] Fichier sauvegardé ✅

**Tests de connexion** :
- [x] Connexion SSH fonctionnelle ✅
- [x] Chemin WordPress accessible ✅
- [x] MySQL accessible ✅
- [x] Tables WordPress présentes ✅
- [x] Versions confirmées ✅
  - PHP 8.1.33 ✅
  - MariaDB 11.4.9 ✅
  - WordPress 6.8.3 ✅
- [x] Configuration validée par backup-site ✅
- [x] Connexion SSH testée via backup-site ✅

---

## 🔌 Étape 2 : Valider et tester la connexion

### 2.1 Valider la configuration

```bash
.venv/bin/backup-site config validate config/production.yaml
```

**Résultat attendu** :
```
✓ Configuration valide
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Section         ┃ Paramètres                                ┃
...
```

**Si erreur** : Vérifier les chemins et les identifiants

### 2.2 Tester la connexion SSH

```bash
.venv/bin/backup-site ssh test config/production.yaml
```

**Résultat attendu** :
```
Validation des clés SSH...
✓ Clé privée valide
✓ Clé publique valide

Test de la connexion SSH...
✓ Connexion SSH établie
✓ Connexion SSH fonctionnelle!
```

**Si erreur** :
- Vérifier que la clé SSH est correcte
- Vérifier les permissions : `chmod 600 ~/.ssh/id_rsa`
- Vérifier que le serveur SSH est accessible

### ✅ Checklist Étape 2

- [ ] Configuration validée sans erreur
- [ ] Connexion SSH établie avec succès
- [ ] Messages de succès affichés

---

## 💾 Étape 3 : Sauvegarder les fichiers et la BDD

### 3.1 Créer le répertoire de sauvegarde

```bash
mkdir -p backups/production
```

### 3.2 Sauvegarder les fichiers

```bash
.venv/bin/backup-site backup files config/production.yaml -o backups/production/files.tar.gz
```

**Résultat attendu** :
```
Chargement de la configuration...
Validation des clés SSH...
Connexion à example-prod-site.com:22...
✓ Connexion SSH établie

Sauvegarde des fichiers...
Chemin distant: /home/monuser/www
Patterns d'inclusion: 3
Patterns d'exclusion: 2

✓ Sauvegarde des fichiers réussie
  Archive: files.tar.gz
  Taille: X.XX MB
Archive créée: backups/production/files.tar.gz
```

**Temps estimé** : 1-5 minutes selon la taille

**Si erreur** :
- Vérifier que le chemin distant existe : `ssh user@host "ls -la /path/to/www"`
- Vérifier l'espace disque sur le serveur
- Vérifier les permissions

### 3.3 Sauvegarder la base de données

```bash
.venv/bin/backup-site backup database config/production.yaml -o backups/production/database.sql.gz
```

**Résultat attendu** :
```
Chargement de la configuration...
Validation des clés SSH...
Connexion à example-prod-site.com:22...
✓ Connexion SSH établie

Sauvegarde de la base de données...
Hôte: localhost:3306
Base: example_wp_database
Utilisateur: example_db_user

✓ Sauvegarde de la base de données réussie
  Fichier: database.sql.gz
  Taille: X.XX KB
Dump créé: backups/production/database.sql.gz
```

**Temps estimé** : 10-30 secondes

**Si erreur** :
- Vérifier les identifiants MySQL
- Vérifier que MySQL est accessible depuis le serveur
- Vérifier les permissions utilisateur MySQL

### 3.4 Vérifier les fichiers créés

```bash
ls -lh backups/production/
```

**Résultat attendu** :
```
-rw-r--r-- 1 julien julien  X.X M Nov  9 12:00 files.tar.gz
-rw-r--r-- 1 julien julien  X.X K Nov  9 12:00 database.sql.gz
```

### ✅ Checklist Étape 3

- [ ] Sauvegarde des fichiers réussie
- [ ] Sauvegarde de la BDD réussie
- [ ] Fichiers créés dans `backups/production/`
- [ ] Tailles raisonnables (fichiers > 1 MB, BDD > 100 KB)

---

## 🐳 Étape 4 : Configurer Docker avec les bonnes versions

### 4.1 Déterminer les versions FOURNISSEUR_HEBERGEMENT

Depuis FOURNISSEUR_HEBERGEMENT, exécuter :
```bash
# Version PHP
php -v

# Version MySQL
mysql --version

# Version WordPress (depuis le répertoire WordPress)
wp core version
```

**Noter les versions** :
- PHP : `_____`
- MySQL : `_____`
- WordPress : `_____`

### 4.2 Configurer Docker

```bash
cd docker/production-test
cp .env.example .env
nano .env
```

**À modifier** :
```bash
# Versions correspondant à FOURNISSEUR_HEBERGEMENT
PHP_VERSION=8.2          # Adapter selon FOURNISSEUR_HEBERGEMENT
MYSQL_VERSION=8.0        # Adapter selon FOURNISSEUR_HEBERGEMENT
WORDPRESS_VERSION=6.4    # Adapter selon FOURNISSEUR_HEBERGEMENT

# Identifiants (peuvent rester par défaut)
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=wordpress
MYSQL_USER=wordpress
MYSQL_PASSWORD=wordpress

SSH_USER=testuser
SSH_PASSWORD=testpass

# Ports (modifier si déjà utilisés)
WORDPRESS_PORT=8080
MYSQL_PORT=3307
SSH_PORT=2222
```

### 4.3 Lancer Docker

```bash
docker compose up -d
```

**Résultat attendu** :
```
✔ Network production-test_backup-network  Created
✔ Container backup-test-mysql             Healthy
✔ Container backup-test-wordpress         Started
✔ Container backup-test-ssh               Started
```

**Temps estimé** : 30-60 secondes

### 4.4 Vérifier que Docker est prêt

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

### ✅ Checklist Étape 4

- [ ] Versions FOURNISSEUR_HEBERGEMENT notées
- [ ] Fichier `.env` configuré avec les bonnes versions
- [ ] Docker lancé avec succès
- [ ] Tous les services sont "Up"
- [ ] MySQL est "Healthy"

---

## 📥 Étape 5 : Restaurer les sauvegardes

### 5.1 Charger les fichiers

```bash
.venv/bin/backup-site load files backups/production/files.tar.gz --container backup-test-wordpress
```

**Résultat attendu** :
```
Chargement de la configuration...
Validation des clés SSH...
Connexion à monsite.com:22...
✓ Connexion SSH établie

Restauration des fichiers...
Archive: files.tar.gz
Destination: /home/monuser/www

✓ Restauration des fichiers réussie
  Archive: files.tar.gz
  Destination: /home/monuser/www
  Taille: X.XX MB
Restauration réussie!
```

**Temps estimé** : 1-5 minutes

**Si erreur** :
- Vérifier que le chemin destination existe
- Vérifier les permissions d'écriture
- Vérifier l'espace disque

### 5.2 Charger la base de données

```bash
.venv/bin/backup-site load database backups/production/database.sql.gz
```

**Note** : Les infos de la BDD sont extraites automatiquement depuis `wp-config.php` via wp-cli !

**Résultat attendu** :
```
Chargement de la configuration...
Validation des clés SSH...
Connexion à monsite.com:22...
✓ Connexion SSH établie

Restauration de la base de données...
Dump: database.sql.gz
Hôte: localhost:3306
Base: monsite_db

✓ Restauration de la base de données réussie
  Dump: database.sql.gz
  Base: monsite_db
  Taille: X.XX KB
Restauration réussie!
```

**Temps estimé** : 10-30 secondes

**Si erreur** :
- Vérifier les identifiants MySQL
- Vérifier que la base de données existe
- Vérifier les permissions utilisateur MySQL

### 5.3 Configurer WordPress pour Docker local

```bash
.venv/bin/backup-site load setup --old-url "https://www.example-prod-site.com" --new-url "http://localhost:8080"
```

**Note** : Cette commande configure automatiquement :
- `FS_METHOD = 'direct'` pour permettre les mises à jour
- Les permissions des dossiers `uploads/`
- Les URLs WordPress (siteurl, home)
- Un search-replace sur le contenu

**Résultat attendu** :
```
✓ Configuration de WordPress réussie
  Container: backup-test-wordpress
  Ancien URL: https://www.example-prod-site.com
  Nouveau URL: http://localhost:8080
  Filesystem: FS_METHOD = 'direct' configuré
  Permissions: uploads/ corrigées

✓ Vérification réussie
  siteurl: http://localhost:8080
  home: http://localhost:8080
Configuration réussie!
```

**Temps estimé** : 1 minute

### ✅ Checklist Étape 5

- [ ] Chargement des fichiers réussi
- [ ] Chargement de la BDD réussi
- [ ] Configuration WordPress réussie
- [ ] Pas d'erreurs affichées

---

## ✅ Étape 6 : Vérifier que le site fonctionne

### 6.1 Vérifier les fichiers restaurés

```bash
docker compose exec ssh-server ls -la /home/testuser/www
```

**Résultat attendu** :
```
total X
drwxr-xr-x 1 testuser testuser  4096 Nov  9 12:00 .
drwxr-xr-x 1 testuser testuser  4096 Nov  9 12:00 ..
-rw-r--r-- 1 testuser testuser  XXXX Nov  9 12:00 wp-config.php
-rw-r--r-- 1 testuser testuser  XXXX Nov  9 12:00 .htaccess
drwxr-xr-x 1 testuser testuser  4096 Nov  9 12:00 wp-content
...
```

### 6.2 Vérifier les tables MySQL

```bash
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SHOW TABLES;"
```

**Résultat attendu** :
```
Tables_in_wordpress
wp_commentmeta
wp_comments
wp_links
wp_options
wp_postmeta
wp_posts
wp_term_relationships
wp_term_taxonomy
wp_termmeta
wp_terms
wp_usermeta
wp_users
```

### 6.3 Vérifier les données WordPress

```bash
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SELECT COUNT(*) as posts FROM wp_posts;"
```

**Résultat attendu** :
```
posts
X
```

### 6.4 Accéder à WordPress

```bash
curl http://localhost:8080
```

**Résultat attendu** : Page WordPress (redirection vers setup ou admin)

### 6.5 Vérifier les logs

```bash
docker compose logs wordpress | tail -20
```

**Résultat attendu** : Pas d'erreurs critiques

### ✅ Checklist Étape 6

- [ ] Fichiers présents dans `/home/testuser/www`
- [ ] Tables WordPress présentes dans la BDD
- [ ] Données WordPress restaurées (posts, users, etc.)
- [ ] WordPress accessible sur http://localhost:8080
- [ ] Pas d'erreurs dans les logs

---

## 📊 Résumé du test

### Métriques

| Métrique | Valeur |
|----------|--------|
| Temps total | ___ minutes |
| Taille fichiers sauvegardés | ___ MB |
| Taille BDD sauvegardée | ___ KB |
| Temps sauvegarde fichiers | ___ secondes |
| Temps sauvegarde BDD | ___ secondes |
| Temps restauration fichiers | ___ secondes |
| Temps restauration BDD | ___ secondes |

### Résultats

**Sauvegarde** :
- [ ] ✅ Fichiers sauvegardés avec succès
- [ ] ✅ BDD sauvegardée avec succès

**Restauration** :
- [ ] ✅ Fichiers restaurés avec succès
- [ ] ✅ BDD restaurée avec succès

**Vérification** :
- [ ] ✅ Fichiers présents dans Docker
- [ ] ✅ Tables présentes dans Docker
- [ ] ✅ Données correctes
- [ ] ✅ WordPress fonctionne

### Conclusion

- [ ] ✅ Test réussi - MVP fonctionnel en production
- [ ] ❌ Test échoué - Problèmes à corriger

**Notes** :
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 🐛 Dépannage

### Erreur : "SSH connection failed"

```bash
# Vérifier la connexion SSH directe
ssh -v user@host "ls"

# Vérifier les permissions de la clé
chmod 600 ~/.ssh/id_rsa

# Vérifier que la clé est dans le ssh-agent
ssh-add ~/.ssh/id_rsa
```

### Erreur : "Archive not found"

```bash
# Vérifier que les fichiers existent
ls -lh backups/production/

# Vérifier les chemins
file backups/production/files.tar.gz
```

### Erreur : "MySQL connection failed"

```bash
# Vérifier les identifiants
mysql -h localhost -u user -p -e "SELECT 1;"

# Vérifier que MySQL est accessible
ssh user@host "mysql -u user -p -e 'SELECT 1;'"
```

### Erreur : "Docker not running"

```bash
# Vérifier que Docker est lancé
docker ps

# Redémarrer Docker
docker compose restart

# Relancer les services
cd docker/production-test
docker compose down
docker compose up -d
```

---

## 📚 Ressources

- **Configuration** : `config/production.yaml`
- **Sauvegardes** : `backups/production/`
- **Docker** : `docker/production-test/`
- **Documentation** : `docker/production-test/WORKFLOW.md`
- **Tests** : `tests/test_*.py`

---

## 📝 Notes

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```
