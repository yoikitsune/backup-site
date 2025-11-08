# Quick Start - Backup Site

## 🚀 Démarrage rapide

### 1. Installation

```bash
# Cloner le projet
git clone <url-du-projet>
cd backup-site

# Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -e .
```

### 2. Configurer votre site

```bash
# Copier le template FOURNISSEUR_HEBERGEMENT
cp config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml config/mon-site.yaml

# Éditer avec vos informations
nano config/mon-site.yaml
```

**À modifier dans le fichier :**
- `site.name` : Nom de votre site
- `ssh.user` : Votre identifiant FOURNISSEUR_HEBERGEMENT
- `files.remote_path` : Chemin de votre site (`/home/identifiant/www`)
- `database.name` : Nom de votre base de données
- `database.user` : Utilisateur de la base de données
- `database.password` : Mot de passe de la base de données

### 3. Valider la configuration

```bash
backup-site config validate config/mon-site.yaml
```

### 4. Tester la connexion SSH

```bash
backup-site ssh test config/mon-site.yaml
```

## 📋 Commandes principales

```bash
# Afficher l'aide
backup-site --help

# Voir le guide SSH
backup-site ssh setup-guide

# Valider une configuration
backup-site config validate config/mon-site.yaml

# Tester la connexion SSH
backup-site ssh test config/mon-site.yaml
```

## 🧪 Tester avec Docker

```bash
# Démarrer le serveur SSH de test
cd docker/test-ssh-server
docker compose -f compose.yml up -d

# Attendre 5 secondes
sleep 5

# Tester avec la configuration de test
cd ../../
backup-site ssh test config/test-docker.yaml

# Arrêter le serveur
cd docker/test-ssh-server
docker compose -f compose.yml down
```

## 📚 Documentation complète

- **README.md** : Vue d'ensemble et installation
- **config/README.md** : Guide des templates et configurations
- **PROGRESS.md** : État du projet et roadmap
- **sprint-planning.md** : Tâches et priorités

## 🆘 Troubleshooting

### Erreur : "backup-site: commande introuvable"
```bash
# Assurez-vous que l'environnement virtuel est activé
source .venv/bin/activate

# Réinstallez le package
pip install -e .
```

### Erreur : "Connexion SSH échouée"
```bash
# Vérifiez votre configuration
backup-site config validate config/mon-site.yaml

# Vérifiez les clés SSH
ls -la ~/.ssh/

# Testez la connexion SSH manuelle
ssh -i ~/.ssh/id_rsa -p 22 votre_identifiant@ssh.FOURNISSEUR_HEBERGEMENT.net
```

### Erreur : "Template non trouvé"
```bash
# Vérifiez que le template existe
ls -la config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml

# Copiez-le s'il manque
cp config/example-site.yaml config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml
```

## 📞 Support

Pour plus d'informations, consultez la documentation complète dans le README.md ou les fichiers de configuration.
