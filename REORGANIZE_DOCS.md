# 🚀 Guide de réorganisation de la documentation

## Avant de commencer

Lis ces 3 documents (15 min) :
1. [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md) - Vue d'ensemble
2. [DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md) - Structure détaillée
3. [AGILE_DOCUMENTATION_GUIDE.md](AGILE_DOCUMENTATION_GUIDE.md) - Bonnes pratiques

---

## Phase 1 : Créer la structure (5 min)

### Étape 1.1 : Créer les dossiers

```bash
cd /home/julien/Sources/backup-site

mkdir -p docs/{planning,architecture,guides,development,docker,workflows,progress,maintenance,references}
```

### Étape 1.2 : Vérifier la structure

```bash
tree -L 2 docs/
```

**Résultat attendu** :
```
docs/
├── planning/
├── architecture/
├── guides/
├── development/
├── docker/
├── workflows/
├── progress/
├── maintenance/
└── references/
```

---

## Phase 2 : Déplacer les documents (20 min)

### Étape 2.1 : Planning

```bash
# Créer index
cat > docs/planning/README.md << 'EOF'
# 📋 Planification

Documents de planification et vision du projet.

- [vision.md](../vision.md) - Vision produit
- [backlog.md](../backlog.md) - User stories
- [sprint-planning.md](../sprint-planning.md) - Sprint actuel
EOF

# Les fichiers restent à la racine (pour faciliter l'accès)
# Mais on crée des liens symboliques
cd docs/planning
ln -s ../../vision.md .
ln -s ../../backlog.md .
ln -s ../../sprint-planning.md .
cd ../..
```

### Étape 2.2 : Architecture

```bash
cat > docs/architecture/README.md << 'EOF'
# 🏗️ Architecture

Documents techniques et décisions architecturales.

- [architecture.md](../../architecture.md) - Vue d'ensemble
- [IMPLEMENTATION_NOTES.md](../../IMPLEMENTATION_NOTES.md) - Décisions
EOF

cd docs/architecture
ln -s ../../architecture.md .
ln -s ../../IMPLEMENTATION_NOTES.md .
cd ../..
```

### Étape 2.3 : Development

```bash
cat > docs/development/README.md << 'EOF'
# 👨‍💻 Développement

Documentation pour les développeurs.

- [TESTING.md](../../TESTING.md) - Guide de test
EOF

cd docs/development
ln -s ../../TESTING.md .
cd ../..
```

### Étape 2.4 : Workflows

```bash
cat > docs/workflows/README.md << 'EOF'
# 📈 Workflows

Workflows complets et commandes.

- [WORKFLOW_COMPLET.md](../../WORKFLOW_COMPLET.md) - Workflow A→Z
- [WORKFLOW_VISUAL.md](../../WORKFLOW_VISUAL.md) - Diagrammes
- [COMMANDES_COMPLETES_A_Z.md](../../COMMANDES_COMPLETES_A_Z.md) - Référence CLI
- [PRODUCTION_TEST_PLAN.md](../../PRODUCTION_TEST_PLAN.md) - Plan de test
EOF

cd docs/workflows
ln -s ../../WORKFLOW_COMPLET.md .
ln -s ../../WORKFLOW_VISUAL.md .
ln -s ../../COMMANDES_COMPLETES_A_Z.md .
ln -s ../../PRODUCTION_TEST_PLAN.md .
cd ../..
```

### Étape 2.5 : Progress

```bash
cat > docs/progress/README.md << 'EOF'
# 📊 Suivi du projet

État d'avancement et revues de sprint.

- [PROGRESS.md](../../PROGRESS.md) - État global
- [CLEANUP_SUMMARY.md](../../CLEANUP_SUMMARY.md) - Nettoyages
EOF

cd docs/progress
ln -s ../../PROGRESS.md .
ln -s ../../CLEANUP_SUMMARY.md .
cd ../..
```

### Étape 2.6 : Docker

```bash
cat > docs/docker/README.md << 'EOF'
# 🐳 Docker

Configuration et déploiement Docker.

- [docker/production-test/README.md](../../docker/production-test/README.md) - Configuration
- [docker/production-test/TESTING.md](../../docker/production-test/TESTING.md) - Tests
EOF

cd docs/docker
ln -s ../../docker/production-test/README.md production-test-README.md
ln -s ../../docker/production-test/TESTING.md production-test-TESTING.md
cd ../..
```

---

## Phase 3 : Créer les index (20 min)

### Étape 3.1 : Index racine

```bash
cat > docs/README.md << 'EOF'
# 📚 Documentation

Bienvenue dans la documentation du projet backup-site.

## 🎯 Démarrage rapide

**Nouveau sur le projet ?**
1. [README.md](../README.md) - Vue d'ensemble (5 min)
2. [QUICKSTART.md](../QUICKSTART.md) - Premiers pas (10 min)
3. [vision.md](planning/vision.md) - Comprendre le projet (10 min)

## 📋 Par catégorie

- [📋 Planification](planning/) - Vision, backlog, sprint
- [🏗️ Architecture](architecture/) - Technique et décisions
- [👨‍💻 Développement](development/) - Tests et contribution
- [🐳 Docker](docker/) - Configuration et déploiement
- [📈 Workflows](workflows/) - Workflows complets
- [📊 Suivi](progress/) - État du projet

## 🔍 Par audience

- **Product Owners** : [Planification](planning/)
- **Développeurs** : [Architecture](architecture/) + [Développement](development/)
- **Testeurs** : [Workflows](workflows/) + [Docker](docker/)
- **DevOps** : [Docker](docker/) + [Workflows](workflows/)
- **Nouveaux** : [README.md](../README.md) → [QUICKSTART.md](../QUICKSTART.md)

## 📚 Index complet

Voir [DOCS_INDEX.md](../DOCS_INDEX.md) pour l'index complet.
EOF
```

---

## Phase 4 : Mettre à jour les liens (30 min)

### Étape 4.1 : Vérifier les liens

```bash
# Chercher les liens internes
grep -r "\.md" docs/ | grep -v "Binary" | head -20
```

### Étape 4.2 : Mettre à jour README.md

```bash
# Ajouter une section "Documentation" à la racine README.md
cat >> README.md << 'EOF'

## 📚 Documentation

La documentation est organisée par catégorie :

- **[📋 Planification](docs/planning/)** - Vision, backlog, sprint
- **[🏗️ Architecture](docs/architecture/)** - Architecture technique
- **[👨‍💻 Développement](docs/development/)** - Tests et contribution
- **[🐳 Docker](docs/docker/)** - Configuration Docker
- **[📈 Workflows](docs/workflows/)** - Workflows complets
- **[📊 Suivi](docs/progress/)** - État du projet

Voir [DOCS_INDEX.md](DOCS_INDEX.md) pour l'index complet.
EOF
```

### Étape 4.3 : Vérifier les liens

```bash
# Vérifier que tous les liens fonctionnent
grep -r "\[.*\](.*\.md)" docs/ | grep -v "Binary" | wc -l
```

---

## Phase 5 : Vérification finale (10 min)

### Étape 5.1 : Checklist

```bash
# Vérifier que tous les dossiers existent
ls -la docs/

# Vérifier que les README.md existent
find docs -name "README.md" | sort

# Vérifier que les liens symboliques fonctionnent
find docs -type l | sort
```

### Étape 5.2 : Tester la navigation

1. Ouvrir [docs/README.md](docs/README.md)
2. Cliquer sur chaque lien
3. Vérifier que les liens fonctionnent

### Étape 5.3 : Mettre à jour PROGRESS.md

```bash
# Ajouter une ligne à PROGRESS.md
cat >> PROGRESS.md << 'EOF'

## 📚 Documentation réorganisée (Nov 10, 2025)

- ✅ Créé DOCUMENTATION_STRUCTURE.md
- ✅ Créé DOCS_INDEX.md
- ✅ Créé AGILE_DOCUMENTATION_GUIDE.md
- ✅ Créé DOCUMENTATION_SUMMARY.md
- ✅ Créé dossiers docs/
- ✅ Créé index par dossier
- ✅ Mis à jour les liens
EOF
```

---

## 🎯 Résumé des commandes

### Créer la structure
```bash
mkdir -p docs/{planning,architecture,guides,development,docker,workflows,progress,maintenance,references}
```

### Créer les liens symboliques
```bash
cd docs/planning && ln -s ../../*.md . && cd ../..
cd docs/architecture && ln -s ../../architecture.md . && ln -s ../../IMPLEMENTATION_NOTES.md . && cd ../..
cd docs/development && ln -s ../../TESTING.md . && cd ../..
cd docs/workflows && ln -s ../../WORKFLOW*.md . && ln -s ../../COMMANDES*.md . && ln -s ../../PRODUCTION*.md . && cd ../..
cd docs/progress && ln -s ../../PROGRESS.md . && ln -s ../../CLEANUP*.md . && cd ../..
```

### Vérifier
```bash
tree -L 2 docs/
find docs -name "README.md" | sort
find docs -type l | sort
```

---

## ⏱️ Durée totale

| Phase | Durée | Cumulé |
|-------|-------|--------|
| Phase 1 : Créer structure | 5 min | 5 min |
| Phase 2 : Déplacer documents | 20 min | 25 min |
| Phase 3 : Créer index | 20 min | 45 min |
| Phase 4 : Mettre à jour liens | 30 min | 75 min |
| Phase 5 : Vérification | 10 min | 85 min |
| **TOTAL** | | **~1h 30 min** |

---

## ✅ Checklist finale

- [ ] Dossiers docs/ créés
- [ ] README.md créé dans chaque dossier
- [ ] Liens symboliques fonctionnent
- [ ] docs/README.md créé
- [ ] DOCS_INDEX.md créé
- [ ] Tous les liens internes fonctionnent
- [ ] PROGRESS.md mis à jour
- [ ] README.md racine mis à jour

---

## 🚀 Prochaines étapes

Après la réorganisation :

1. **Créer les documents manquants** :
   - CHANGELOG.md
   - TROUBLESHOOTING.md
   - FAQ.md
   - SECURITY.md
   - MIGRATION_GUIDE.md

2. **Mettre à jour chaque document** :
   - Ajouter "Pour qui ?" et "Pourquoi ?"
   - Ajouter durée estimée
   - Ajouter date de mise à jour
   - Ajouter statut (✅ À jour / ⚠️ À vérifier / ❌ Obsolète)

3. **Maintenance continue** :
   - Mettre à jour PROGRESS.md chaque sprint
   - Vérifier les liens internes chaque mois
   - Archiver les docs obsolètes

---

## 📞 Besoin d'aide ?

- **Structure** → [DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md)
- **Index** → [DOCS_INDEX.md](DOCS_INDEX.md)
- **Bonnes pratiques** → [AGILE_DOCUMENTATION_GUIDE.md](AGILE_DOCUMENTATION_GUIDE.md)
- **Résumé** → [DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)

---

**Prêt à réorganiser ? 🚀**

Commence par la Phase 1 !
