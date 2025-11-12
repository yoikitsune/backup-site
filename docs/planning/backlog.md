# Backlog du projet

## User Stories (à prioriser)

### Fonctionnalités principales
- [x] **US1** : En tant que développeur, je veux sauvegarder les fichiers d'un site web ✅
  - *Détail* : Compression côté serveur via pipe SSH (`tar | gzip`) pour accélérer la récupération
- [x] **US2** : En tant que développeur, je veux sauvegarder une base de données MySQL/MariaDB ✅
- [ ] **US3** : En tant que développeur, je veux restaurer une sauvegarde complète (fichiers + BDD) _(postposé, hors périmètre Sprint 2)_

### Configuration
- [x] **US4** : En tant que développeur, je veux pouvoir créer facilement une configuration pour un site avec son hébergement, son type d'application, la clé SSH, les accès aux fichiers et à la base de données ✅ _livré Sprint 1_
- [x] **US5** : En tant que développeur, je veux pouvoir configurer facilement les paramètres de connexion à la base de données ✅ _livré Sprint 1_
- [x] **US6** : En tant que développeur, je veux pouvoir spécifier les dossiers à inclure/exclure de la sauvegarde ✅ _livré Sprint 1_

### Intégration Docker
- [x] **US7** : En tant que développeur, je veux pouvoir configurer facilement un docker pour refleter au mieux le serveur de production (version php, version mysql ou mariadb) ✅
- [x] **US8** : En tant que développeur, je veux pouvoir intégrer facilement dans le docker une sauvegarde pour la tester ET adapter automatiquement la configuration WordPress ✅
  - [x] **US8.1** : Charger les fichiers dans Docker ✅
  - [x] **US8.2** : Charger la BDD dans Docker ✅
  - [x] **US8.3** : Adapter la configuration WordPress (URLs, DB) ✅
    - [x] Créer classe `DockerWordPressAdapter` avec wp-cli
    - [x] Adapter les URLs (siteurl, home)
    - [x] Faire search-replace sur le contenu
  - [x] **US8.4** : Créer commande CLI `load adapt-urls` ✅
  - [x] **US8.5** : Tester que le site fonctionne correctement ✅

### Gestion des sauvegardes
- [ ] **US9** : En tant que développeur, je veux lister les sauvegardes disponibles
- [ ] **US10** : En tant que développeur, je veux supprimer des anciennes sauvegardes

### Candidats Sprint 2 – Workflow multi-sites
- [ ] **US-A** (config structure) : En tant qu'admin, je veux générer `sites/<slug>/config.yaml` complet (SSH, includes/excludes, BDD, backup) depuis un template pour disposer d'une config fonctionnelle immédiatement.
- [ ] **US-B** (bootstrap SSH) : En tant qu'admin, je veux que `backup-site site guide/verify <slug>` propose `ssh-copy-id` par défaut et, selon le provider, affiche un guide dédié (FOURNISSEUR_HEBERGEMENT…) avant de tester la connexion.
- [ ] **US-C** (helpers app) : En tant qu'admin, je veux que les helpers WordPress pré-remplissent les sections du `config.yaml` (lecture `wp-config.php`, métadonnées) sans m'empêcher de les modifier.
- [ ] **US-D** (orchestration Docker) : À définir après revue des environnements – préparer la restauration locale automatique (sera détaillé ultérieurement).
- [ ] **US-E** (restore orchestrée) : Orchestrer le chargement fichiers + BDD + setup WordPress depuis `sites/<slug>/backups/<date>/`.
- [ ] **US-F** (validation) : Automatiser les vérifications post-restore (curl, logs, checklist) et consigner le résultat.

## Sprint 1 - COMPLÉTÉE ✅ (Nov 9, 2025)

### MVP - Sauvegarde + Chargement + Adaptation WordPress

**Objectif** : Créer un MVP complet pour sauvegarder et charger des sites WordPress en local

**État** : ✅ COMPLÉTÉE

**Tâches complétées** :
- ✅ **T15** : Créer classe `DockerWordPressAdapter` (15 min)
- ✅ **T16** : Créer commande CLI `load adapt-urls` (10 min)
- ✅ **T17** : Tester avec le site actuel (10 min)
- ✅ **T18** : Mettre à jour la documentation (5 min)

**Durée totale** : 40 minutes

**Livrable** :
- ✅ Classe `DockerWordPressAdapter` fonctionnelle
- ✅ Commande `backup-site load adapt-urls` intégrée
- ✅ Site WordPress accessible sans erreur SSL
- ✅ wp-admin accessible
- ✅ Documentation mise à jour

---

## Priorisation (MoSCoW)

### Must Have (MVP) - WordPress + FOURNISSEUR_HEBERGEMENT
- US1, US2, US4, US7 _(réalisés)_
- **Focus spécifique** : Configuration WordPress sur hébergement FOURNISSEUR_HEBERGEMENT avec gestion clés SSH publiques/privées

### Dépriorisé (postposé)
- US3 : restauration complète sur serveur distant (à revoir quand l'application sera plus mûre)

### Should Have
- US5, US6, US8

### Could Have
- US9, US10

### Won't Have (pour l'instant)
- Support d'autres bases de données que MySQL/MariaDB
- Interface graphique
