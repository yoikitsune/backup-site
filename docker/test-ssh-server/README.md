# Serveur SSH de test pour backup-site

Ce serveur Docker simule un environnement FOURNISSEUR_HEBERGEMENT pour tester les sauvegardes en toute sécurité.

## Démarrage

```bash
# Depuis la racine du projet
cd docker/test-ssh-server

# Démarrage du serveur
docker-compose up -d
```

## Configuration de test

1. **Générer des clés SSH de test** :
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/test_id_rsa -N ""
```

2. **Ajouter la clé publique au serveur** :
```bash
ssh-copy-id -i ~/.ssh/test_id_rsa.pub -p 2222 testuser@localhost
```

3. **Créer une configuration de test** :
```bash
backup-site config init config/test-docker.yaml
```

4. **Modifier la configuration** (`config/test-docker.yaml`) :
```yaml
site:
  name: "test-site-docker"
  provider: "FOURNISSEUR_HEBERGEMENT"
  app_type: "wordpress"
  
ssh:
  host: "localhost"
  user: "testuser"
  port: 2222
  private_key_path: "~/.ssh/test_id_rsa"
  public_key_path: "~/.ssh/test_id_rsa.pub"

files:
  remote_path: "/home/testuser/www"
  include_patterns:
    - "wp-content/**"
    - "wp-config.php"
    - ".htaccess"
  exclude_patterns:
    - "wp-content/cache/**"
    - "*.log"

database:
  host: "localhost"  # Le serveur MySQL est accessible via localhost
  port: 3306
  name: "test_wp"
  user: "testuser"
  password: "testpass"

backup:
  destination: "./backups/test-docker"
  compression: "gzip"
  retention_days: 7
```

## Tests

1. **Test de connexion SSH** :
```bash
backup-site ssh test config/test-docker.yaml
```

2. **Validation de la configuration** :
```bash
backup-site config validate config/test-docker.yaml
```

3. **Test de sauvegarde** (quand implémenté) :
```bash
backup-site backup --config config/test-docker.yaml
```

## Arrêt

```bash
docker-compose down
```

## Structure du serveur

- **Utilisateur** : `testuser` (mot de passe: `testpass`)
- **Répertoire web** : `/home/testuser/www`
- **Port SSH** : 2222
- **Base de données** : MySQL 8.0 sur port 3306
- **BDD de test** : `test_wp`
