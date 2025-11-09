# Environnement Docker de test production (US7)

Cet environnement reproduit votre serveur de production (WordPress, PHP, MySQL) pour tester les sauvegardes et les restaurations.

## 🚀 Démarrage rapide

### 1. Configuration initiale

```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer les versions si nécessaire (optionnel)
nano .env
```

### 2. Lancer l'environnement

```bash
# Démarrer tous les services
docker compose up -d

# Attendre que WordPress soit prêt (30-60 secondes)
docker compose logs -f wordpress
# Arrêter avec Ctrl+C quand tu vois "WordPress is ready"
```

### 3. Vérifier que tout fonctionne

```bash
# Accéder à WordPress (port 8080 par défaut)
curl http://localhost:8080

# Vérifier la base de données
docker compose exec mysql mysql -u wordpress -pwordpress wordpress -e "SHOW TABLES;"

# Vérifier l'accès SSH
docker compose exec ssh-server ls -la /home/testuser/www
```

## 📋 Variables d'environnement

Édite `.env` pour configurer :

- **PHP_VERSION** : Version de PHP (8.1, 8.2, 8.3, etc.)
- **MYSQL_VERSION** : Version de MySQL (5.7, 8.0, etc.)
- **WORDPRESS_VERSION** : Version de WordPress (6.3, 6.4, etc.)
- **SSH_USER** : Utilisateur SSH pour les sauvegardes
- **SSH_PASSWORD** : Mot de passe SSH
- **Ports** : WORDPRESS_PORT, MYSQL_PORT, SSH_PORT

## 🔄 Workflow complet : Tester une sauvegarde

### Étape 1 : Sauvegarder depuis FOURNISSEUR_HEBERGEMENT

```bash
# Depuis ton ordinateur
backup-site backup files config/FOURNISSEUR_HEBERGEMENT.yaml -o backups/backup.tar.gz
backup-site backup database config/FOURNISSEUR_HEBERGEMENT.yaml -o backups/database.sql.gz
```

### Étape 2 : Restaurer dans Docker

```bash
# Restaurer les fichiers
docker compose exec wordpress tar -xzf /home/testuser/backups/backup.tar.gz -C /var/www/html

# Restaurer la base de données
docker compose exec mysql mysql -u wordpress -p wordpress < /home/testuser/backups/database.sql

# Vérifier que WordPress fonctionne
curl http://localhost
```

### Étape 3 : Tester les modifications

```bash
# Accéder à WordPress
curl http://localhost

# Vérifier les données
docker compose exec mysql mysql -u wordpress -p wordpress -e "SELECT * FROM wp_posts LIMIT 5;"
```

## 🧪 Cas d'usage courants

### Tester une mise à jour WordPress

```bash
# 1. Restaurer la sauvegarde
docker compose exec wordpress tar -xzf /home/testuser/backups/backup.tar.gz -C /var/www/html
docker compose exec mysql mysql -u wordpress -p wordpress < /home/testuser/backups/database.sql

# 2. Mettre à jour WordPress
docker compose exec wordpress wp core update

# 3. Vérifier que tout fonctionne
curl http://localhost
```

### Tester une mise à jour PHP

```bash
# 1. Arrêter l'environnement
docker compose down

# 2. Modifier PHP_VERSION dans .env
nano .env

# 3. Redémarrer
docker compose up -d

# 4. Restaurer et tester
docker compose exec wordpress tar -xzf /home/testuser/backups/backup.tar.gz -C /var/www/html
curl http://localhost
```

### Tester une mise à jour MySQL

```bash
# 1. Arrêter l'environnement
docker compose down

# 2. Modifier MYSQL_VERSION dans .env
nano .env

# 3. Redémarrer
docker compose up -d

# 4. Restaurer et tester
docker compose exec mysql mysql -u wordpress -p wordpress < /home/testuser/backups/database.sql
curl http://localhost
```

## 🛑 Arrêter l'environnement

```bash
# Arrêter tous les services
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

### Impossible de se connecter en SSH

```bash
# Vérifier que le service SSH est prêt
docker compose logs ssh-server

# Tester la connexion
ssh -v -p 2222 testuser@localhost
```

### La base de données ne se restaure pas

```bash
# Vérifier que le fichier existe
ls -lh /home/testuser/backups/

# Vérifier que MySQL est prêt
docker compose exec mysql mysql -u wordpress -p wordpress -e "SHOW DATABASES;"
```

## 📝 Notes

- Les données sont stockées dans des volumes Docker (`mysql_data`, `wordpress_data`)
- Les sauvegardes sont copiées dans le volume `backups`
- Tous les services sont sur le réseau `backup-network`
- SSH est accessible sur le port 2222 (configurable)
