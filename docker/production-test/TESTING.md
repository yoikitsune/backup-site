# Guide de test - Environnement Docker production (US7)

## ✅ Vérification que tout fonctionne

### 1. Lancer l'environnement

```bash
cd docker/production-test
cp .env.example .env
docker compose up -d
```

### 2. Vérifier les services

```bash
# Vérifier que tous les services sont en cours d'exécution
docker compose ps

# Résultat attendu :
# - backup-test-mysql : Healthy
# - backup-test-wordpress : Started
# - backup-test-ssh : Started
```

### 3. Tester WordPress

```bash
# Accéder à WordPress
curl http://localhost:8080

# Résultat attendu : Redirection 302 vers /wp-admin/setup-config.php
```

### 4. Tester la base de données

```bash
# Vérifier que MySQL fonctionne
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SHOW TABLES;"

# Résultat attendu : Liste des tables WordPress (wp_posts, wp_users, etc.)
```

### 5. Tester SSH

```bash
# Vérifier que SSH fonctionne et que WordPress est accessible
docker compose exec ssh-server ls -la /home/testuser/www

# Résultat attendu : Listing des fichiers WordPress
```

## 🧪 Cas de test complets

### Test 1 : Vérifier les versions

```bash
# Vérifier la version de PHP
docker compose exec wordpress php -v

# Vérifier la version de MySQL
docker compose exec mysql mysql --version

# Vérifier la version de WordPress
docker compose exec wordpress wp core version
```

### Test 2 : Tester avec différentes versions

```bash
# 1. Arrêter l'environnement
docker compose down

# 2. Modifier les versions dans .env
nano .env
# Changer PHP_VERSION=8.3, MYSQL_VERSION=5.7, etc.

# 3. Relancer
docker compose up -d

# 4. Vérifier les nouvelles versions
docker compose exec wordpress php -v
docker compose exec mysql mysql --version
```

### Test 3 : Tester la sauvegarde via SSH

```bash
# 1. Créer un fichier de test dans WordPress
docker compose exec wordpress touch /var/www/html/test-file.txt

# 2. Sauvegarder via SSH (depuis ton ordinateur)
# À faire une fois que backup-site est configuré

# 3. Vérifier que le fichier est dans la sauvegarde
tar -tzf backups/backup.tar.gz | grep test-file.txt
```

## 🛑 Arrêter l'environnement

```bash
# Arrêter les services
docker compose down

# Arrêter et supprimer les volumes (attention : supprime les données)
docker compose down -v
```

## 🐛 Dépannage

### WordPress ne démarre pas

```bash
# Vérifier les logs
docker compose logs wordpress

# Vérifier que MySQL est prêt
docker compose logs mysql
```

### SSH ne fonctionne pas

```bash
# Vérifier les logs SSH
docker compose logs ssh-server

# Vérifier que le conteneur SSH est en cours d'exécution
docker compose ps ssh-server
```

### Port déjà utilisé

```bash
# Modifier les ports dans .env
nano .env
# Changer WORDPRESS_PORT=8081, MYSQL_PORT=3308, SSH_PORT=2223

# Relancer
docker compose down && docker compose up -d
```

## ✅ Checklist de validation (T12)

- [x] docker-compose.yml créé et fonctionnel
- [x] Services lancent correctement
- [x] WordPress accessible sur http://localhost:8080
- [x] MySQL fonctionne et accessible
- [x] SSH fonctionne et accessible
- [x] Volumes persistants fonctionnent
- [x] Variables d'environnement configurables
- [x] Documentation complète
- [ ] Tester la restauration d'une sauvegarde (US8)
- [ ] Tester avec différentes versions de PHP/MySQL
