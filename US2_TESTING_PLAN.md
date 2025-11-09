# Plan de test US2 - Sauvegarde BDD MySQL

## 🎯 Objectif

Implémenter et tester la sauvegarde de la base de données MySQL via SSH tunnel avec mysqldump.

## 🧪 Stratégie de test

### 1. Tests unitaires (rapides, isolés)
- Mock la connexion SSH
- Mock mysqldump
- Teste la construction de la commande mysqldump
- Teste la gestion d'erreurs

### 2. Tests d'intégration (réalistes)
- Serveur Docker avec SSH + MySQL
- Connexion SSH tunnel vers MySQL
- Exécution réelle de mysqldump
- Vérification du fichier SQL

### 3. Tests complets (US1 + US2)
- Sauvegarde fichiers + BDD dans une seule archive
- Vérification de l'archive complète

## 🐳 Serveur Docker de test

### Configuration

Le serveur Docker a été modifié pour inclure MySQL :

**Dockerfile** :
- Alpine Linux
- OpenSSH Server
- MySQL Server
- Base de données de test `test_wp`

**entrypoint.sh** :
- Initialise MySQL
- Crée la base `test_wp`
- Crée l'utilisateur `testuser` avec accès à `test_wp`
- Insère des données de test (table `wp_posts`)

### Démarrer le serveur

```bash
cd docker/test-ssh-server
docker compose -f compose.yml up -d
sleep 5
cd ../../
```

### Vérifier que MySQL fonctionne

```bash
# Via SSH tunnel
ssh -i ~/.ssh/test_id_rsa -p 2222 testuser@localhost -L 3306:localhost:3306

# Dans un autre terminal
mysql -h localhost -u testuser -p test_wp
# Mot de passe : testpass

# Vérifier les données
SELECT * FROM wp_posts;
```

### Arrêter le serveur

```bash
cd docker/test-ssh-server
docker compose -f compose.yml down
cd ../../
```

## 📋 Checklist d'implémentation US2

### T8 : Connexion SSH tunnel vers MySQL

- [ ] Créer classe `DatabaseBackup` dans `src/backup_site/backup/database.py`
- [ ] Implémenter SSH tunnel vers MySQL (port 3306)
- [ ] Tester la connexion avec le serveur Docker

### T9 : Utiliser mysqldump

- [ ] Construire la commande mysqldump
- [ ] Exécuter via SSH tunnel
- [ ] Capturer le flux SQL

### T10 : Intégrer dans l'archive

- [ ] Créer le fichier `database.sql`
- [ ] Ajouter à l'archive tar.gz

## 🧪 Tests à implémenter

### Tests unitaires (`tests/test_database.py`)

```python
def test_build_mysqldump_command():
    """Teste la construction de la commande mysqldump"""
    # Vérifier que la commande contient les bons paramètres
    # mysqldump -u testuser -p testpass test_wp

def test_backup_to_file_success():
    """Teste la sauvegarde réussie dans un fichier"""
    # Mock SSH, vérifier que le fichier SQL est créé

def test_backup_to_stream_success():
    """Teste la sauvegarde en mémoire"""
    # Mock SSH, vérifier que le stream contient du SQL

def test_ssh_tunnel_error():
    """Teste la gestion d'erreur SSH tunnel"""
    # Vérifier que l'erreur est bien capturée
```

### Tests d'intégration

```bash
# Démarrer le serveur
cd docker/test-ssh-server && docker compose -f compose.yml up -d && sleep 5 && cd ../../

# Tester la sauvegarde BDD
backup-site backup database config/test-docker.yaml -o backups/test_database.sql

# Vérifier le fichier SQL
head -20 backups/test_database.sql
wc -l backups/test_database.sql

# Vérifier que le SQL est valide
mysql -u testuser -p test_wp < backups/test_database.sql

# Arrêter le serveur
cd docker/test-ssh-server && docker compose -f compose.yml down && cd ../../
```

## 📊 Résultats attendus

### Fichier SQL généré

```sql
-- Dump de la base de données test_wp
CREATE TABLE wp_posts (
  ID bigint(20) NOT NULL AUTO_INCREMENT,
  ...
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO wp_posts VALUES (1, 1, '2025-11-09 ...', ...);
INSERT INTO wp_posts VALUES (2, 1, '2025-11-09 ...', ...);
```

### Taille attendue

- Fichier SQL non compressé : ~2-5 KB
- Archive tar.gz : ~1-2 KB

## 🔗 Configuration

La configuration de test `config/test-docker.yaml` est déjà prête :

```yaml
database:
  host: "localhost"
  port: 3306
  name: "test_wp"
  user: "testuser"
  password: "testpass"
```

## ⚠️ Points d'attention

1. **SSH tunnel** : Doit être établi avant mysqldump
2. **Permissions** : L'utilisateur SSH doit pouvoir accéder à MySQL
3. **Mot de passe** : Passer en paramètre ou via fichier `.my.cnf`
4. **Compression** : mysqldump peut être compressé avec gzip

## 🚀 Prochaines étapes

1. ✅ Modifier le Dockerfile pour ajouter MySQL
2. ✅ Modifier entrypoint.sh pour créer la base de test
3. ⏳ Implémenter `DatabaseBackup` dans `files.py`
4. ⏳ Ajouter commande CLI `backup database`
5. ⏳ Créer tests unitaires
6. ⏳ Tester avec le serveur Docker
7. ⏳ Intégrer US1 + US2 dans une archive complète
