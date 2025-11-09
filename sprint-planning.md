# Sprint 1 - MVP WordPress + FOURNISSEUR_HEBERGEMENT

## Objectif du Sprint
Livrer un MVP fonctionnel pour sauvegarder un site WordPress hébergé sur FOURNISSEUR_HEBERGEMENT avec configuration SSH spécifique.

## Durée estimée
- 1 semaine (ou selon ton rythme)

## Tâches techniques (issues)

### US4 - Configuration pour un site (Must Have)
- [x] **T1** : Créer la structure de base du projet (dossiers, pyproject.toml) ✅
- [x] **T2** : Implémenter un système de configuration YAML de base ✅
- [x] **T3** : Ajouter la gestion sécurisée des clés SSH publiques/privées pour FOURNISSEUR_HEBERGEMENT ✅
- [x] **T4** : Créer un template de configuration FOURNISSEUR_HEBERGEMENT + WordPress ✅
- **Test manuel** : Créer une configuration pour un site WordPress sur FOURNISSEUR_HEBERGEMENT, vérifier que les clés SSH et accès BDD sont bien stockés ✅
  - ✅ Configuration YAML validée avec Pydantic
  - ✅ Connexion SSH testée avec succès
  - ✅ Template FOURNISSEUR_HEBERGEMENT-wordpress fonctionnel
  - ✅ Environnement Docker de test opérationnel
  - ✅ Commandes CLI validées

### US1 - Sauvegarder les fichiers (Must Have)
- [x] **T5** : Implémenter la connexion SSH pour accéder aux fichiers distants ✅
  - *Approche* : Pipe SSH direct (`tar --exclude=... | gzip`) sans script serveur
  - Implémentation: `src/backup_site/backup/files.py` - Classe `FileBackup`
- [x] **T6** : Créer une fonction de sauvegarde des fichiers avec patterns inclusion/exclusion ✅
  - *Détail* : Utiliser les patterns du template FOURNISSEUR_HEBERGEMENT-wordpress.yaml
  - Méthodes: `backup_to_file()` et `backup_to_stream()`
- [x] **T7** : Générer une archive tar.gz des fichiers ✅
  - *Détail* : Compression côté serveur via pipe, réception du flux compressé au client
  - Commande CLI: `backup-site backup files config/test-docker.yaml`
- **Test manuel** : Lancer une sauvegarde des fichiers d'un site WordPress, vérifier que seuls les dossiers/fichiers spécifiés (wp-content, wp-config.php) sont inclus ✅
  - ✅ Archive créée avec succès (232 bytes compressée)
  - ✅ Patterns d'inclusion/exclusion respectés (wp-config.php, .htaccess inclus)
  - ✅ Testé avec le serveur SSH Docker
  - ✅ Tests unitaires: `tests/test_files.py` (6 cas de test)
  - ✅ Commande CLI validée : `backup-site backup files config/test-docker.yaml`

### US2 - Sauvegarder une base de données MySQL (Must Have)
- [x] **T8** : Implémenter la connexion à la BDD via SSH tunnel (localhost) ✅
  - Classe `DatabaseBackup` dans `src/backup_site/backup/database.py`
  - Connexion via SSH tunnel (host: test-mysql)
- [x] **T9** : Utiliser mysqldump pour exporter la base de données ✅
  - Commande mysqldump avec options : --routines, --triggers, --events
  - Compression gzip optionnelle
- [x] **T10** : Intégrer la sauvegarde BDD dans l'archive globale ✅
  - Commande CLI : `backup-site backup database config/test-docker.yaml`
- **Test manuel** : Lancer une sauvegarde de la BDD, vérifier que le fichier SQL est présent dans l'archive et lisible ✅
  - ✅ Dump créé avec succès (924 bytes compressé)
  - ✅ Fichier SQL valide et lisible
  - ✅ Table wp_posts avec données incluses
  - ✅ Tests unitaires: `tests/test_database.py` (6 cas de test)

### US7 - Configurer Docker pour reproduire la production (Must Have)
- [x] **T11** : Créer un docker-compose.yml configurable avec WordPress, PHP, MySQL/MariaDB ✅
  - Variables d'environnement pour les versions (PHP_VERSION, MYSQL_VERSION)
  - Service SSH pour accéder aux fichiers
  - Service MySQL pour la base de données
  - Service WordPress avec Apache
  - Fichiers créés :
    - `docker/production-test/docker-compose.yml`
    - `docker/production-test/.env.example`
    - `docker/production-test/ssh-server/Dockerfile`
    - `docker/production-test/ssh-server/entrypoint.sh`
    - `docker/production-test/README.md`
- [x] **T12** : Tester l'environnement et documenter les cas d'usage ✅
  - Environnement testé et fonctionnel
  - Services : WordPress (PHP 8.2), MySQL 8.0, SSH
  - Documentation complète : `docker/production-test/README.md`
  - Guide de test : `docker/production-test/TESTING.md`
  - Ports configurables : WordPress 8080, MySQL 3307, SSH 2222
- **Test manuel** : ✅ Lancer `docker compose up` avec différentes versions, vérifier que WordPress est accessible

### US8 - Intégrer une sauvegarde dans Docker pour la tester (Must Have)
- [ ] **T13** : Créer un script pour restaurer les fichiers d'une sauvegarde dans le Docker
- [ ] **T14** : Créer un script pour restaurer la BDD d'une sauvegarde dans le Docker
- **Test manuel** : Restaurer une sauvegarde, vérifier que WordPress fonctionne correctement

## Priorités
1. US4 (Configuration) - Base essentielle
2. US1 + US2 (Sauvegarde fichiers + BDD) - Fonctionnalité core
3. US7 (Docker) - Facilité d'exécution

## Définition de 'Done'
- Code fonctionnel pour chaque US
- Test manuel réussi par toi
- Documentation minimale dans README.md

## Prochaines étapes après validation
- Review du Sprint 1
- Planification Sprint 2 (US3 - Restauration + autres US prioritaires)
