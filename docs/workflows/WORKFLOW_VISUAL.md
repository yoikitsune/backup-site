# 🎯 Workflow visuel - Vue d'ensemble

## 📊 Flux global

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKUP-SITE WORKFLOW COMPLET                     │
└─────────────────────────────────────────────────────────────────────┘

PHASE 1 : PRÉPARATION (5 min)
├─ Créer répertoires
├─ Créer config/production.yaml
├─ Valider la configuration
└─ Tester la connexion SSH
    ↓
PHASE 2 : SAUVEGARDE O2SWITCH (2 min)
├─ Sauvegarder les fichiers (76 MB)
├─ Sauvegarder la BDD (1.5 MB)
└─ Vérifier les fichiers
    ↓
PHASE 3 : CONFIGURATION DOCKER (3 min)
├─ Configurer .env (versions PHP/MySQL/WordPress)
├─ Créer le Dockerfile WordPress (wp-cli inclus) ✅
├─ Lancer Docker avec build (3 containers)
└─ Vérifier que Docker est prêt
    ↓
PHASE 4 : CHARGER LA SAUVEGARDE DANS DOCKER (2 min)
├─ Charger les fichiers (via Docker)
├─ Charger la BDD (via Docker)
└─ Vérifier les données
    ↓
PHASE 5 : ADAPTATION WORDPRESS (30 sec)
├─ Vérifier que wp-cli est disponible ✅ (déjà installé)
├─ Mettre à jour les URLs (siteurl, home)
├─ Remplacer les URLs dans le contenu
└─ Vérifier les URLs
    ↓
PHASE 6 : VÉRIFICATION FINALE (2 min)
├─ Accéder au site (http://localhost:8080)
├─ Vérifier les fichiers
├─ Vérifier les tables MySQL
└─ Vérifier les données
    ↓
✅ SITE FONCTIONNEL EN LOCAL
```

---

## 🔄 Flux de données

```
PRODUCTION (FOURNISSEUR_HEBERGEMENT)
├─ Fichiers WordPress (76 MB)
│  └─ wp-config.php (config FOURNISSEUR_HEBERGEMENT)
│  └─ wp-content/
│  └─ wp-admin/
│  └─ wp-includes/
│
└─ Base de données (1.5 MB)
   └─ Tables wp02_*
   └─ Préfixe : wp02_
   └─ URLs : feelgoodbymelanie.com

    ↓ SAUVEGARDE
    
LOCAL (backups/)
├─ files.tar.gz (76 MB)
└─ database.sql.gz (1.5 MB)

    ↓ CHARGEMENT
    
DOCKER LOCAL
├─ Container MySQL
│  └─ Base wordpress
│  └─ Tables wp02_*
│  └─ URLs : feelgoodbymelanie.com (AVANT)
│
├─ Container WordPress
│  └─ /var/www/html/
│  └─ wp-config.php (config FOURNISSEUR_HEBERGEMENT - AVANT)
│  └─ wp-content/
│
└─ Container SSH
   └─ /home/testuser/www/
   └─ Fichiers restaurés

    ↓ ADAPTATION (WP-CLI)
    
DOCKER LOCAL (ADAPTÉ)
├─ Container MySQL
│  └─ Base wordpress
│  └─ Tables wp02_*
│  └─ URLs : localhost:8080 (APRÈS) ✅
│
├─ Container WordPress
│  └─ /var/www/html/
│  └─ wp-config.php (config Docker - APRÈS) ✅
│  └─ wp-content/
│
└─ Container SSH
   └─ /home/testuser/www/
   └─ Fichiers adaptés

    ↓ ACCÈS
    
http://localhost:8080 ✅
```

---

## 📋 Commandes par phase

### Phase 1 : Préparation
```bash
mkdir -p backups/production config scripts
cat > config/production.yaml << 'EOF'
# ... configuration ...
EOF
.venv/bin/backup-site config validate config/production.yaml
.venv/bin/backup-site ssh test config/production.yaml
```

### Phase 2 : Sauvegarde
```bash
.venv/bin/backup-site backup files config/production.yaml -o backups/production/files.tar.gz
.venv/bin/backup-site backup database config/production.yaml -o backups/production/database.sql.gz
ls -lh backups/production/
```

### Phase 3 : Docker
```bash
cat > docker/production-test/.env << 'EOF'
PHP_VERSION=8.1
MYSQL_VERSION=11.4
WORDPRESS_VERSION=6.8
# ...
EOF
cd docker/production-test && docker compose up -d
docker compose ps
```

### Phase 4 : Chargement
```bash
cat > config/docker-restore.yaml << 'EOF'
# ... configuration ...
EOF
.venv/bin/backup-site load files backups/production/files.tar.gz config/docker-restore.yaml
gunzip < backups/production/database.sql.gz | docker compose -f docker/production-test/docker-compose.yml exec -T mysql mariadb -u wordpress -pwordpress wordpress
docker compose -f docker/production-test/docker-compose.yml exec mysql mariadb -u wordpress -pwordpress wordpress -e "SHOW TABLES;"
```

### Phase 5 : Adaptation WordPress
```bash
docker compose -f docker/production-test/docker-compose.yml exec wordpress bash -c "
  curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
  chmod +x wp-cli.phar
  mv wp-cli.phar /usr/local/bin/wp
"
docker compose -f docker/production-test/docker-compose.yml exec wordpress wp option update siteurl 'http://localhost:8080'
docker compose -f docker/production-test/docker-compose.yml exec wordpress wp option update home 'http://localhost:8080'
docker compose -f docker/production-test/docker-compose.yml exec wordpress wp search-replace 'feelgoodbymelanie.com' 'localhost:8080'
docker compose -f docker/production-test/docker-compose.yml exec wordpress wp option get siteurl
```

### Phase 6 : Vérification
```bash
curl -s http://localhost:8080 | head -50
docker compose -f docker/production-test/docker-compose.yml exec ssh-server ls -la /home/testuser/www
docker compose -f docker/production-test/docker-compose.yml exec mysql mariadb -u wordpress -pwordpress wordpress -e "SELECT COUNT(*) as posts FROM wp02_posts;"
```

---

## 📊 Statistiques

| Métrique | Valeur |
|----------|--------|
| **Phases** | 6 |
| **Commandes** | 22 |
| **Durée totale** | ~14 min 30 sec |
| **Fichiers sauvegardés** | 76 MB |
| **BDD sauvegardée** | 1.5 MB |
| **Containers Docker** | 3 |
| **Volumes Docker** | 3 |
| **Tables WordPress** | 20+ |
| **Remplacements d'URLs** | 100+ |
| **Optimisation Phase 4** | 33% ⬇️ (3 min → 2 min) |

---

## 🎯 Points clés

✅ **Réutilisable** : Fonctionne pour n'importe quel site WordPress
✅ **Robuste** : Utilise wp-cli (fiable et testé)
✅ **Maintenable** : Code simple et bien documenté
✅ **Open-source** : Prêt pour GitHub public
✅ **Rapide** : ~14 min 30 sec du début à la fin (optimisé)
✅ **Complet** : Sauvegarde + Restauration + Adaptation

---

## 🚀 Prochaines étapes

1. **Automatiser** : Créer un script qui exécute tout
2. **Intégrer CLI** : Commande `backup-site load complete` (fichiers + BDD)
3. **Adapter URLs** : Utiliser wp-cli pour adapter les URLs WordPress
4. **Tester** : Tests unitaires et d'intégration
5. **Publier** : GitHub public
