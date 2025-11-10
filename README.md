# 🚀 Backup Site

Sauvegarde ton site WordPress depuis FOURNISSEUR_HEBERGEMENT et teste-le localement dans Docker.

## ⚡ Démarrage rapide

```bash
# 1. Installer
pip install backup-site

# 2. Configurer
cp config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml config/mon-site.yaml
nano config/mon-site.yaml

# 3. Sauvegarder
backup-site backup files config/mon-site.yaml
backup-site backup database config/mon-site.yaml

# 4. Charger dans Docker
backup-site load files archive.tar.gz
backup-site load database dump.sql.gz
```

## 📚 Documentation

- **Premiers pas** : [QUICKSTART.md](QUICKSTART.md) - 10 min pour ta première sauvegarde
- **Guide complet** : [docs/START_HERE.md](docs/START_HERE.md) - Navigation par rôle
- **Index complet** : [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md) - Tous les documents

## 🎯 Cas d'usage

Tu développes un site WordPress sur FOURNISSEUR_HEBERGEMENT.  
Tu veux tester une modification avant de la mettre en production.

Backup-site te permet de :
1. **Sauvegarder** le site depuis FOURNISSEUR_HEBERGEMENT
2. **Charger** la sauvegarde dans Docker local
3. **Tester** la modification
4. **Déployer** en production si OK

## 🔗 Liens utiles

- [Installation complète](docs/START_HERE.md)
- [Commandes disponibles](docs/workflows/COMMANDES_COMPLETES_A_Z.md)
- [Architecture technique](docs/architecture/architecture.md)
- [Tests et validation](docs/development/TESTING.md)

## ✨ Fonctionnalités

- ✅ Sauvegarde des fichiers via SSH
- ✅ Sauvegarde de la base de données MySQL/MariaDB
- ✅ Chargement dans Docker local
- ✅ Adaptation automatique des URLs WordPress
- ✅ Configuration YAML simple
- ✅ Tests unitaires complets

## 📝 Licence

MIT
