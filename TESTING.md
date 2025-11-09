# Guide de test - Backup Site

## ✅ Prérequis

Avant de lancer les tests, assure-toi que tu as :

- **Python 3.11+** : `python --version`
- **Poetry** : `pip install poetry` (si pas encore installé)
- **Docker** : Pour les tests d'intégration (optionnel pour les tests unitaires)

### Installation initiale (une seule fois)
```bash
# Installer les dépendances du projet
poetry install
```

Cela installe :
- Les dépendances principales (click, pydantic, paramiko, etc.)
- Les dépendances de développement (pytest, black, flake8, mypy)

---

## 🚀 Résumé rapide

**Pour lancer les tests unitaires** (pas besoin de Docker) :
```bash
poetry install          # Une seule fois
poetry run pytest tests/test_database.py -v
```

**Pour lancer les tests d'intégration** (avec Docker) :
```bash
poetry install          # Une seule fois
cd docker/test-ssh-server && docker compose -f compose.yml up -d && cd ../../
poetry run pytest tests/ -v
docker compose -f docker/test-ssh-server/compose.yml down
```

---

## 🧪 Tests unitaires

### Exécuter tous les tests
```bash
poetry run pytest tests/ -v
```

### Exécuter les tests du module files
```bash
poetry run pytest tests/test_files.py -v
```

### Exécuter avec couverture
```bash
poetry run pytest tests/ --cov=src/backup_site --cov-report=html
```

### Alternative : Sans Poetry
Si Poetry n'est pas disponible, tu peux installer les dépendances manuellement :
```bash
# Installer les dépendances de test
pip install pytest paramiko pydantic click pyyaml cryptography rich pydantic-settings python-dotenv

# Lancer les tests
python -m pytest tests/ -v
```

## 🐳 Tests d'intégration avec Docker

### 1. Démarrer le serveur SSH de test
```bash
cd docker/test-ssh-server
docker compose -f compose.yml up -d
sleep 5
cd ../../
```

### 2. Vérifier la connexion SSH
```bash
backup-site ssh test config/test-docker.yaml
```

### 3. Tester la sauvegarde des fichiers

#### Créer un répertoire de test sur le serveur
```bash
# Optionnel : vérifier les fichiers de test
ssh -i ~/.ssh/test_id_rsa -p 2222 testuser@localhost ls -la /home/testuser/www/
```

#### Lancer la sauvegarde
```bash
backup-site backup files config/test-docker.yaml -o backups/test_backup.tar.gz
```

#### Vérifier l'archive
```bash
# Lister le contenu
tar -tzf backups/test_backup.tar.gz | head -20

# Vérifier la taille
ls -lh backups/test_backup.tar.gz

# Extraire pour inspection
mkdir -p /tmp/backup_test
tar -xzf backups/test_backup.tar.gz -C /tmp/backup_test
ls -la /tmp/backup_test/
```

### 4. Arrêter le serveur SSH
```bash
cd docker/test-ssh-server
docker compose -f compose.yml down
cd ../../
```

## 📋 Checklist de validation US1

- [ ] Tests unitaires passent : `pytest tests/test_files.py -v`
- [ ] Commande CLI disponible : `backup-site backup files --help`
- [ ] Connexion SSH établie : `backup-site ssh test config/test-docker.yaml`
- [ ] Sauvegarde réussie : `backup-site backup files config/test-docker.yaml`
- [ ] Archive créée et compressée : `ls -lh backups/`
- [ ] Archive contient les bons fichiers : `tar -tzf backups/test_backup.tar.gz`
- [ ] Patterns d'exclusion respectés : pas de `*.log` ni `cache/` dans l'archive

## 🔍 Dépannage

### Erreur : "Impossible de se connecter"
```bash
# Vérifier que le serveur Docker est démarré
docker ps | grep test-ssh-server

# Vérifier les logs
docker logs backup-site-test-ssh-server-1
```

### Erreur : "La commande tar a échoué"
```bash
# Activer le mode verbeux
backup-site -v backup files config/test-docker.yaml

# Vérifier les permissions sur le serveur
ssh -i ~/.ssh/test_id_rsa -p 2222 testuser@localhost ls -la /home/testuser/www/
```

### Archive vide ou trop petite
```bash
# Vérifier les patterns d'inclusion/exclusion
backup-site config validate config/test-docker.yaml

# Vérifier les fichiers sur le serveur
ssh -i ~/.ssh/test_id_rsa -p 2222 testuser@localhost find /home/testuser/www -type f | head -20
```

## 📊 Métriques de test

### Couverture attendue
- `FileBackup` : 100%
- `_build_tar_command()` : 100%
- `backup_to_file()` : 100%
- `backup_to_stream()` : 100%

### Cas de test couverts
1. Construction de la commande tar avec patterns
2. Construction de la commande tar sans patterns d'inclusion
3. Sauvegarde réussie dans un fichier
4. Gestion d'erreur SSH pour fichier
5. Sauvegarde réussie dans un stream
6. Gestion d'erreur SSH pour stream

## 🚀 Prochaines étapes

Après validation de US1 :
- [ ] Implémenter US2 (Sauvegarde BDD)
- [ ] Implémenter US7 (Docker)
- [ ] Intégrer US1 + US2 + US7 dans une sauvegarde complète
