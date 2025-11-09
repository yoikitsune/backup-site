# Workflow complet : Sauvegarde → Restauration → Vérification

Ce guide montre comment utiliser `backup-site` pour sauvegarder et restaurer un site WordPress dans l'environnement Docker de test.

## 🎯 Objectif

Valider que les sauvegardes (fichiers + BDD) peuvent être restaurées correctement dans Docker.

## 📋 Prérequis

1. **Environnement Docker lancé** :
   ```bash
   cd docker/production-test
   cp .env.example .env
   docker compose up -d
   ```

2. **backup-site installé** :
   ```bash
   cd /path/to/backup-site
   .venv/bin/pip install -e .
   ```

3. **Configuration Docker** :
   - Fichier : `config/test-docker.yaml`
   - Utilisateur SSH : `testuser` / `testpass`
   - Port SSH : 2222
   - Chemin WordPress : `/home/testuser/www`

## 🔄 Workflow complet

### Étape 1 : Sauvegarder les fichiers

```bash
cd /path/to/backup-site

# Sauvegarder les fichiers WordPress
.venv/bin/backup-site backup files config/test-docker.yaml -o backups/wordpress_backup.tar.gz

# Résultat attendu :
# ✓ Sauvegarde des fichiers réussie
#   Archive: wordpress_backup.tar.gz
#   Taille: X.XX MB
```

**Fichiers inclus** :
- `wp-config.php`
- `wp-content/` (plugins, thèmes, uploads)
- `.htaccess`
- Autres fichiers WordPress

### Étape 2 : Sauvegarder la base de données

```bash
# Sauvegarder la base de données WordPress
.venv/bin/backup-site backup database config/test-docker.yaml -o backups/wordpress_database.sql.gz

# Résultat attendu :
# ✓ Sauvegarde de la base de données réussie
#   Fichier: wordpress_database.sql.gz
#   Taille: X.XX KB
```

**Contenu du dump** :
- Tables WordPress (wp_posts, wp_users, wp_options, etc.)
- Routines, triggers, events
- Données complètes

### Étape 3 : Restaurer les fichiers

```bash
# Restaurer l'archive des fichiers
.venv/bin/backup-site restore files backups/wordpress_backup.tar.gz config/test-docker.yaml

# Résultat attendu :
# ✓ Restauration des fichiers réussie
#   Archive: wordpress_backup.tar.gz
#   Destination: /home/testuser/www
#   Taille: X.XX MB
```

**Vérification** :
```bash
# Vérifier que les fichiers sont restaurés
docker compose exec ssh-server ls -la /home/testuser/www

# Résultat attendu : Listing des fichiers WordPress
# -rw-r--r-- 1 testuser testuser  wp-config.php
# -rw-r--r-- 1 testuser testuser  .htaccess
# drwxr-xr-x 1 testuser testuser  wp-content/
```

### Étape 4 : Restaurer la base de données

```bash
# Restaurer le dump SQL
.venv/bin/backup-site restore database backups/wordpress_database.sql.gz config/test-docker.yaml

# Résultat attendu :
# ✓ Restauration de la base de données réussie
#   Dump: wordpress_database.sql.gz
#   Base: wordpress
#   Taille: X.XX KB
```

**Vérification** :
```bash
# Vérifier que les tables sont restaurées
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SHOW TABLES;"

# Résultat attendu : Liste des tables WordPress
# wp_commentmeta
# wp_comments
# wp_links
# wp_options
# wp_postmeta
# wp_posts
# wp_term_relationships
# wp_term_taxonomy
# wp_termmeta
# wp_terms
# wp_usermeta
# wp_users
```

### Étape 5 : Vérifier que WordPress fonctionne

```bash
# Accéder à WordPress
curl http://localhost:8080

# Résultat attendu : Page WordPress (redirection vers /wp-admin/setup-config.php)
```

**Vérification avancée** :
```bash
# Vérifier les données de la BDD
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SELECT * FROM wp_posts LIMIT 5;"

# Résultat attendu : Listing des posts restaurés
```

## 🧪 Cas de test complets

### Test 1 : Workflow complet (Sauvegarde → Restauration)

**Commandes** :
```bash
# 1. Sauvegarder
.venv/bin/backup-site backup files config/test-docker.yaml -o backups/test1_files.tar.gz
.venv/bin/backup-site backup database config/test-docker.yaml -o backups/test1_db.sql.gz

# 2. Restaurer
.venv/bin/backup-site restore files backups/test1_files.tar.gz config/test-docker.yaml
.venv/bin/backup-site restore database backups/test1_db.sql.gz config/test-docker.yaml

# 3. Vérifier
docker compose exec ssh-server ls -la /home/testuser/www
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SHOW TABLES;"
curl http://localhost:8080
```

**Résultat attendu** : ✅ Tous les fichiers et données sont restaurés correctement

### Test 2 : Restauration avec archive compressée

**Commandes** :
```bash
# Sauvegarder (compression automatique)
.venv/bin/backup-site backup files config/test-docker.yaml -o backups/test2_files.tar.gz

# Restaurer (détecte automatiquement la compression)
.venv/bin/backup-site restore files backups/test2_files.tar.gz config/test-docker.yaml

# Vérifier
docker compose exec ssh-server ls -la /home/testuser/www
```

**Résultat attendu** : ✅ Archive compressée restaurée correctement

### Test 3 : Restauration avec dump compressé

**Commandes** :
```bash
# Sauvegarder (compression automatique)
.venv/bin/backup-site backup database config/test-docker.yaml -o backups/test3_db.sql.gz

# Restaurer (détecte automatiquement la compression)
.venv/bin/backup-site restore database backups/test3_db.sql.gz config/test-docker.yaml

# Vérifier
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SELECT COUNT(*) FROM wp_posts;"
```

**Résultat attendu** : ✅ Dump compressé restauré correctement

### Test 4 : Restauration avec dump non compressé

**Commandes** :
```bash
# Sauvegarder sans compression
.venv/bin/backup-site backup database config/test-docker.yaml -o backups/test4_db.sql

# Restaurer (détecte automatiquement que ce n'est pas compressé)
.venv/bin/backup-site restore database backups/test4_db.sql config/test-docker.yaml

# Vérifier
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SELECT COUNT(*) FROM wp_posts;"
```

**Résultat attendu** : ✅ Dump non compressé restauré correctement

## 📝 Checklist de validation (US8)

- [ ] Sauvegarde des fichiers réussie
- [ ] Sauvegarde de la BDD réussie
- [ ] Restauration des fichiers réussie
- [ ] Restauration de la BDD réussie
- [ ] WordPress fonctionne après restauration
- [ ] Les fichiers sont présents dans `/home/testuser/www`
- [ ] Les tables WordPress sont présentes dans la BDD
- [ ] Les données sont correctes après restauration
- [ ] Commandes CLI fonctionnent correctement
- [ ] Tests unitaires passent (18/18)

## 🐛 Dépannage

### Erreur : "Archive not found"

```bash
# Vérifier que le fichier existe
ls -lh backups/wordpress_backup.tar.gz

# Vérifier le chemin absolu
file backups/wordpress_backup.tar.gz
```

### Erreur : "SSH connection failed"

```bash
# Vérifier la connexion SSH
ssh -v -p 2222 testuser@localhost

# Vérifier que le conteneur SSH est en cours d'exécution
docker compose ps ssh-server
```

### Erreur : "MySQL connection failed"

```bash
# Vérifier que MySQL est prêt
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SHOW DATABASES;"

# Vérifier les logs MySQL
docker compose logs mysql
```

### Erreur : "Tar extraction failed"

```bash
# Vérifier que l'archive est valide
tar -tzf backups/wordpress_backup.tar.gz | head

# Vérifier l'espace disque
docker compose exec ssh-server df -h /home/testuser/www
```

## 📊 Métriques

| Métrique | Valeur |
|----------|--------|
| Temps de sauvegarde des fichiers | < 5 secondes |
| Temps de sauvegarde de la BDD | < 2 secondes |
| Temps de restauration des fichiers | < 5 secondes |
| Temps de restauration de la BDD | < 2 secondes |
| Taille de l'archive (compressée) | ~1-10 MB |
| Taille du dump (compressé) | ~100-500 KB |

## 🎓 Concepts clés

### Compression côté serveur

Les sauvegardes utilisent la compression côté serveur pour réduire la bande passante :
- Fichiers : `find | tar -czf - -T -` (compression gzip)
- BDD : `mysqldump | gzip` (compression gzip)

### Restauration via SFTP + SSH

La restauration utilise deux étapes :
1. **Téléchargement SFTP** : Transfert du fichier depuis le client vers le serveur
2. **Extraction SSH** : Extraction/restauration sur le serveur

### Détection automatique de la compression

La restauration détecte automatiquement si le fichier est compressé :
- Fichiers : Détecte `.tar.gz` vs `.tar`
- BDD : Détecte `.sql.gz` vs `.sql`

## 📚 Ressources

- **Sauvegarde** : `src/backup_site/backup/`
- **Restauration** : `src/backup_site/restore/`
- **Tests** : `tests/test_restore_*.py`
- **CLI** : `src/backup_site/cli.py`
- **Configuration** : `config/test-docker.yaml`
