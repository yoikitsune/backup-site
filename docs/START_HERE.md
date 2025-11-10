# 🚀 Commencer ici

Bienvenue ! Ce fichier te guide pour naviguer dans la documentation du projet backup-site.

---

## ⏱️ 5 minutes pour comprendre le projet

### 1. Lis la vision (2 min)
**Fichier** : [vision.md](docs/planning/vision.md)

**Résumé** : Backup-site est une CLI pour sauvegarder des sites WordPress hébergés sur FOURNISSEUR_HEBERGEMENT et les charger localement dans Docker pour les tester.

### 2. Vois l'architecture (2 min)
**Fichier** : [architecture.md](docs/architecture/architecture.md)

**Résumé** : 
- Sauvegarde via SSH (production → local)
- Chargement via Docker (local → Docker)
- Adaptation WordPress automatique

### 3. Essaie les commandes (1 min)
**Fichier** : [QUICKSTART.md](QUICKSTART.md)

**Résumé** : 
```bash
backup-site backup files config/prod.yaml
backup-site load files archive.tar.gz
backup-site load setup --old-url "https://prod.com" --new-url "http://localhost:8080"
```

---

## 🎯 Selon ton rôle

### 👤 Je suis Product Owner
**Durée** : 15 min

1. [vision.md](docs/planning/vision.md) - Comprendre le projet (5 min)
2. [backlog.md](docs/planning/backlog.md) - Voir les user stories (5 min)
3. [PROGRESS.md](docs/progress/PROGRESS.md) - État d'avancement (5 min)

### 👨‍💻 Je suis Développeur
**Durée** : 30 min

1. [README.md](README.md) - Installation (5 min)
2. [architecture.md](docs/architecture/architecture.md) - Architecture (10 min)
3. [IMPLEMENTATION_NOTES.md](docs/architecture/IMPLEMENTATION_NOTES.md) - Décisions (10 min)
4. [TESTING.md](docs/development/TESTING.md) - Comment tester (5 min)

### 🧪 Je suis Testeur
**Durée** : 20 min

1. [TESTING.md](development/TESTING.md) - Stratégie de test (10 min)
2. [PRODUCTION_TEST_PLAN.md](workflows/PRODUCTION_TEST_PLAN.md) - Plan de test (10 min)

### 🚀 Je suis DevOps
**Durée** : 20 min

1. [docker/production-test/README.md](docker/production-test/README.md) - Configuration Docker (10 min)
2. [COMMANDES_COMPLETES_A_Z.md](COMMANDES_COMPLETES_A_Z.md) - Commandes CLI (10 min)

### 📚 Je suis nouveau
**Durée** : 45 min

1. [README.md](README.md) - Vue d'ensemble (5 min)
2. [QUICKSTART.md](QUICKSTART.md) - Premiers pas (10 min)
3. [vision.md](docs/planning/vision.md) - Comprendre le projet (10 min)
4. [architecture.md](docs/architecture/architecture.md) - Architecture (10 min)
5. [TESTING.md](docs/development/TESTING.md) - Comment tester (10 min)

---

## 📚 Index complet

**Fichier** : [DOCS_INDEX.md](DOCS_INDEX.md)

Contient :
- Index de tous les documents
- Navigation par audience
- Matrice "besoin → document"

---

## 🗂️ Organisation de la documentation

**Fichier** : [DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md)

Contient :
- Structure recommandée
- Correspondance avec ton projet
- Plan de migration

---

## 📋 Besoin d'aide ?

| Besoin | Fichier | Durée |
|--------|---------|-------|
| Démarrer rapidement | [QUICKSTART.md](QUICKSTART.md) | 10 min |
| Comprendre le projet | [vision.md](docs/planning/vision.md) | 10 min |
| Installer | [README.md](README.md) | 5 min |
| Configurer | [config/README.md](config/README.md) | 15 min |
| Utiliser | [COMMANDES_COMPLETES_A_Z.md](workflows/COMMANDES_COMPLETES_A_Z.md) | 20 min |
| Développer | [architecture.md](docs/architecture/architecture.md) + [TESTING.md](docs/development/TESTING.md) | 30 min |
| Tester | [TESTING.md](development/TESTING.md) | 20 min |
| Déployer | [docker/production-test/README.md](docker/production-test/README.md) | 30 min |
| État du projet | [PROGRESS.md](progress/PROGRESS.md) | 10 min |

---

## 🎯 Prochaines étapes

### Immédiat
- [ ] Lire [vision.md](docs/planning/vision.md) (5 min)
- [ ] Lire [README.md](README.md) (5 min)
- [ ] Lire [QUICKSTART.md](QUICKSTART.md) (10 min)

### Court terme
- [ ] Lire [architecture.md](docs/architecture/architecture.md) (10 min)
- [ ] Lire [TESTING.md](docs/development/TESTING.md) (20 min)
- [ ] Essayer les commandes (15 min)

### Moyen terme
- [ ] Lire [IMPLEMENTATION_NOTES.md](docs/architecture/IMPLEMENTATION_NOTES.md) (10 min)
- [ ] Lire [PRODUCTION_TEST_PLAN.md](workflows/PRODUCTION_TEST_PLAN.md) (15 min)
- [ ] Tester le workflow complet (30 min)

---

## 💡 Conseils

1. **Utilisez Ctrl+F** pour chercher dans les documents
2. **Cliquez sur les liens** pour naviguer
3. **Consultez DOCS_INDEX.md** pour l'index complet
4. **Mettez à jour les docs** quand vous changez le code
5. **Posez des questions** si quelque chose n'est pas clair

---

## 🚀 Commandes rapides

### Installation
```bash
git clone https://github.com/votre-utilisateur/backup-site.git
cd backup-site
poetry install
poetry shell
```

### Premiers tests
```bash
backup-site --version
backup-site --help
backup-site config validate config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml
```

### Sauvegarde
```bash
backup-site backup files config/production.yaml -o backups/files.tar.gz
backup-site backup database config/production.yaml -o backups/database.sql.gz
```

### Chargement dans Docker
```bash
backup-site load files backups/files.tar.gz
backup-site load database backups/database.sql.gz
backup-site load setup --old-url "https://prod.com" --new-url "http://localhost:8080"
```

---

## 📞 Besoin d'aide ?

- **Documentation** → [DOCS_INDEX.md](DOCS_INDEX.md)
- **Structure** → [DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md)
- **Bonnes pratiques** → [AGILE_DOCUMENTATION_GUIDE.md](AGILE_DOCUMENTATION_GUIDE.md)
- **Réorganisation** → [REORGANIZE_DOCS.md](REORGANIZE_DOCS.md)

---

**Prêt à commencer ? 🚀**

Choisis ton rôle ci-dessus et commence par le premier lien !
