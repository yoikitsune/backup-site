# Progression du projet Backup Site

## 📈 Vue d'ensemble

**Statut global** : Sprint 1 - MVP COMPLÉTÉ ✅ (Nov 10, 2025)

**Objectif** : MVP fonctionnel pour sauvegarder un site WordPress hébergé sur FOURNISSEUR_HEBERGEMENT et le charger localement dans Docker avec adaptation automatique.

## ✅ Sprint 1 - MVP COMPLÉTÉ (Nov 10, 2025)

### Phases complétées
- ✅ Phase 1 : Configuration (US4)
- ✅ Phase 2 : Sauvegarde des fichiers (US1)
- ✅ Phase 3 : Sauvegarde de la BDD (US2)
- ✅ Phase 4 : Docker production-test (US7)
- ✅ Phase 5-7 : Chargement et adaptation WordPress (US8)

---

## ✅ Sprint 1 - Phase 1 : Configuration (COMPLÉTÉE)

### US4 - Configuration pour un site (Must Have)

#### T1 : Créer la structure de base du projet ✅
- Dossiers organisés (`src/backup_site/{backup,config,utils}`)
- `pyproject.toml` avec toutes les dépendances
- `.gitignore` sécurisé
- `README.md` complet

#### T2 : Implémenter un système de configuration YAML ✅
- Modèles Pydantic pour validation robuste
- Chargement sécurisé des configurations
- Commandes CLI `config init` et `config validate`
- Support des variables d'environnement

#### T3 : Gestion sécurisée des clés SSH ✅
- Module `SSHKeyValidator` pour validation des clés
- Vérification des permissions (600 pour clé privée)
- Test de connexion SSH avec Paramiko
- Commandes CLI `ssh setup-guide` et `ssh test`

#### T4 : Template FOURNISSEUR_HEBERGEMENT + WordPress ✅
- Template `config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml` complet
- Patterns WordPress optimisés (inclusions/exclusions)
- Support WP-CLI
- Documentation intégrée

### Tests effectués ✅
- Configuration YAML validée
- Connexion SSH testée avec succès
- Environnement Docker de test fonctionnel
- Template FOURNISSEUR_HEBERGEMENT testé et validé

## ✅ Sprint 1 - Phase 2 : Sauvegarde (COMPLÉTÉE)

### US1 - Sauvegarder les fichiers (Must Have) ✅ IMPLÉMENTÉE

#### T5 : Implémenter la connexion SSH ✅
- Classe `FileBackup` dans `src/backup_site/backup/files.py`
- Pipe SSH direct (`tar --exclude=... | gzip`)
- Aucun script serveur requis, utilise les outils natifs

#### T6 : Créer une fonction de sauvegarde avec patterns ✅
- Patterns d'inclusion/exclusion du template FOURNISSEUR_HEBERGEMENT-wordpress.yaml
- Deux méthodes : `backup_to_file()` et `backup_to_stream()`
- Gestion d'erreurs robuste

#### T7 : Générer une archive tar.gz ✅
- Compression côté serveur via pipe, flux compressé au client
- Commande CLI : `backup-site backup files config/test-docker.yaml`
- Tests unitaires : `tests/test_files.py` avec 6 cas de test

#### Tests ✅
- ✅ Tests unitaires complets (mock SSH) - 6 cas de test
- ✅ Test manuel avec serveur Docker - Archive créée avec succès
  - Archive: 232 bytes (compressée)
  - Fichiers inclus: wp-config.php, .htaccess
  - Patterns d'inclusion/exclusion respectés

### US2 - Sauvegarder une base de données MySQL (Must Have) ✅ IMPLÉMENTÉE

#### T8 : Implémenter la connexion SSH tunnel ✅
- Classe `DatabaseBackup` dans `src/backup_site/backup/database.py`
- Connexion via SSH tunnel (host: test-mysql, port: 3306)
- Support SSL optionnel

#### T9 : Utiliser mysqldump ✅
- Commande mysqldump avec options : --routines, --triggers, --events
- Compression gzip optionnelle
- Gestion d'erreurs robuste

#### T10 : Intégrer dans l'archive ✅
- Commande CLI : `backup-site backup database config/test-docker.yaml`
- Fichier de sortie : `database_{timestamp}.sql.gz`

#### Tests ✅
  - Dump: 924 bytes (compressé)
  - Fichier SQL valide et lisible
  - Table wp_posts avec données incluses

### US7 - Configurer Docker pour reproduire la production (Must Have)
- [x] **T11** : Créer un docker-compose.yml configurable avec WordPress, PHP, MySQL/MariaDB ✅
  - Services : WordPress (PHP 8.2), MySQL 8.0, SSH
  - Variables d'environnement pour les versions
  - Volumes pour les données persistantes
  - Healthchecks pour vérifier que les services sont prêts
  - Fichiers créés :
    - `docker/production-test/docker-compose.yml`
    - `docker/production-test/.env.example`
    - `docker/production-test/ssh-server/Dockerfile`
    - `docker/production-test/ssh-server/entrypoint.sh`
    - `docker/production-test/README.md`
- [x] **T12** : Tester l'environnement et documenter les cas d'usage ✅
  - Environnement testé et fonctionnel
  - Services : WordPress (PHP 8.2), MySQL 8.0, SSH
  - Documentation : `docker/production-test/README.md` et `TESTING.md`
  - Ports : WordPress 8080, MySQL 3307, SSH 2222

### US8 - Intégrer une sauvegarde dans Docker pour la tester (Must Have) ✅ IMPLÉMENTÉE

#### T13 : Chargement des fichiers ✅
- Classe `DockerFileLoad` dans `src/backup_site/docker_load/files.py`
- Méthodes : `load_from_file()` et `load_from_stream()`
- Transfert Docker via `docker cp` + extraction via `docker exec`
- Nettoyage automatique des fichiers temporaires

#### T14 : Chargement de la BDD ✅
- Classe `DockerDatabaseLoad` dans `src/backup_site/docker_load/database.py`
- Extraction automatique des infos BDD via wp-cli
- Création automatique de la base et l'utilisateur
- Support fichiers compressés (.sql.gz) et non compressés (.sql)
- Chargement via `docker exec` + `mariadb`

#### T15 : Configuration WordPress ✅
- Classe `DockerWordPressAdapter` dans `src/backup_site/docker_load/wordpress.py`
- Configuration `FS_METHOD = 'direct'` pour permettre les mises à jour
- Correction des permissions et owner des dossiers `uploads/`
- Adaptation automatique des URLs via wp-cli
- Search-replace sur tout le contenu
- Vérification de la configuration

#### T16 : Commande CLI ✅
- `backup-site load setup --old-url <url> --new-url <url>`
- Configuration complète + vérification automatiques
- Messages clairs et détaillés
- Alias `adapt-urls` disponible pour compatibilité

#### Tests ✅
- ✅ Tests unitaires pour FileLoad et DatabaseLoad
- ✅ Tests d'intégration réussis avec production.yaml
- ✅ Configuration WordPress testée et validée
- ✅ Site WordPress accessible sans erreur SSL
- ✅ wp-admin accessible sans erreurs de permissions
- ✅ Mises à jour WordPress possibles

#### Commandes CLI ✅
- `backup-site load files archive.tar.gz` (options Docker)
- `backup-site load database dump.sql.gz` (infos BDD extraites via wp-cli)
- `backup-site load setup --old-url <url> --new-url <url>` (configuration complète)
- Extraction automatique des infos BDD depuis wp-config.php
- Création automatique de la base et l'utilisateur
- Configuration automatique des permissions
- Messages d'erreur clairs et détaillés

#### Documentation ✅
- COMMANDES_COMPLETES_A_Z.md : Phases 1-6 documentées
- WORKFLOW_VISUAL.md : Phases 1-4 documentées
- README.md : Phases 1-7 documentées
- Workflow complet testé et validé

## Statistiques

### Code
- **Fichiers Python** : 7 modules (backup + restore)
- **Lignes de code** : ~1500 LOC
- **Tests unitaires** : 31 tests (13 backup + 18 restore)
- **Couverture** : Sauvegarde + Restauration complètes

### Documentation
- **README.md** : Complet avec exemples
- **config/README.md** : Guide des templates
- **TESTING.md** : Guide de test complet
- **IMPLEMENTATION_NOTES.md** : Décisions architecturales
- **docker/production-test/WORKFLOW.md** : Workflow complet
- **Commentaires** : Documentés et clairs

### Dépendances
- **Click** : CLI framework
- **Pydantic** : Validation de données
- **Paramiko** : SSH/SFTP
- **Rich** : Interface utilisateur
- **PyYAML** : Parsing YAML

## 🚀 Sprint actuel - Optimisation Phase 3 (Nov 9, 2025)

### Objectif
Pré-installer wp-cli dans le container WordPress pour optimiser la Phase 5 (Adaptation WordPress)

### US8.3 - Adapter la configuration WordPress ✅ COMPLÉTÉE

#### T1 : Créer le Dockerfile WordPress avec wp-cli ✅
- [x] Fichier : `docker/production-test/wordpress/Dockerfile`
- [x] Installer wp-cli via curl
- [x] Tester que wp-cli fonctionne (WP-CLI 2.12.0)

#### T2 : Modifier docker-compose.yml ✅
- [x] Ajouter section `build` au service WordPress
- [x] Passer les arguments (WORDPRESS_VERSION)
- [x] Tester le build (Build réussi)

#### T3 : Tester le setup ✅
- [x] Nettoyer l'ancien setup
- [x] Rebuild l'image
- [x] Lancer Docker
- [x] Vérifier que wp-cli est disponible (WP-CLI 2.12.0)
- [x] Vérifier que WordPress fonctionne (Redirection vers install)

#### T4 : Mettre à jour la documentation ✅
- [x] COMMANDES_COMPLETES_A_Z.md (Sections 3.1b, 3.2, 5, 6.6)
- [x] WORKFLOW_VISUAL.md (Flux, durées, statistiques)
- [ ] README.md (optionnel)

### Impact
- **Durée Phase 5** : 2 min → 30 sec (75% d'optimisation)
- **Durée totale workflow** : 17 min → 15 min 30 sec
- **Bénéfice** : Itération plus rapide pour les tests

### Statistiques d'optimisation
| Métrique | Avant | Après | Gain |
|----------|-------|-------|------|
| Phase 5 | 2 min | 30 sec | 75% ⬇️ |
| Durée totale | 17 min | 15 min 30 sec | 9% ⬇️ |
| Installation wp-cli | À chaque test | Une seule fois | ✅ |

---

## 🎯 Prochaines étapes

### Sprint 1 - COMPLÉTÉE ✅
- ✅ US4 : Configuration pour un site
- ✅ US1 : Sauvegarde des fichiers
- ✅ US2 : Sauvegarde de la BDD
- ✅ US7 : Docker production-test
- ✅ US8.1-8.2 : Chargement des sauvegardes (fichiers + BDD)
- ✅ **US8.3-8.5 : Adaptation WordPress** (COMPLÉTÉE)
  - ✅ T15 : Créer classe `DockerWordPressAdapter`
  - ✅ T16 : Créer commande CLI `load adapt-urls`
  - ✅ T17 : Tester avec le site actuel
  - ✅ T18 : Mettre à jour la documentation

### Sprint 2 (À planifier)
1. **US3 - Restauration complète** : Script pour restaurer fichiers + BDD en une commande
2. **US9 - Gestion des sauvegardes** : Lister et supprimer les anciennes sauvegardes
3. **US10 - Planification** : Sauvegardes automatiques (cron)
4. **Améliorations** :
   - Chiffrement des sauvegardes
   - Vérification d'intégrité (checksums)
   - Notifications (email, webhook)
   - Dashboard de monitoring

## 🧪 Environnement de test

### Docker SSH Server
- **Port** : 2222
- **Utilisateur** : testuser
- **Répertoire web** : `/home/testuser/www`
- **Structure WordPress** : Simulée avec fichiers de test

### Configuration de test
- **Fichier** : `config/test-docker.yaml`
- **Clés SSH** : `~/.ssh/test_id_rsa`
- **Statut** : ✅ Fonctionnel

## 📝 Notes importantes

### Sécurité
- Les fichiers de configuration ne sont pas versionés (`.gitignore`)
- Les clés SSH restent locales
- Les mots de passe sont masqués dans les affichages

### Flexibilité
- Support de multiples hébergeurs (template system)
- Patterns d'inclusion/exclusion personnalisables
- Options avancées pour chaque section

### Maintenabilité
- Code modulaire et réutilisable
- Tests avec environnement Docker
- Documentation complète et à jour

## 🔗 Ressources

- **Sprint Planning** : `sprint-planning.md`
- **Architecture** : `architecture.md`
- **Vision** : `vision.md`
- **Notes d'implémentation** : `IMPLEMENTATION_NOTES.md`
- **Guide de test** : `TESTING.md`
- **Templates** : `config/`
- **Code source** : `src/backup_site/`
