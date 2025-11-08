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
- [ ] **T5** : Implémenter la connexion SSH pour accéder aux fichiers distants
- [ ] **T6** : Créer une fonction de sauvegarde des fichiers avec patterns inclusion/exclusion
- [ ] **T7** : Générer une archive tar.gz des fichiers
- **Test manuel** : Lancer une sauvegarde des fichiers d'un site WordPress, vérifier que seuls les dossiers/fichiers spécifiés (wp-content, wp-config.php) sont inclus

### US2 - Sauvegarder une base de données MySQL (Must Have)
- [ ] **T8** : Implémenter la connexion à la BDD via SSH tunnel (localhost)
- [ ] **T9** : Utiliser mysqldump pour exporter la base de données
- [ ] **T10** : Intégrer la sauvegarde BDD dans l'archive globale
- **Test manuel** : Lancer une sauvegarde de la BDD, vérifier que le fichier SQL est présent dans l'archive et lisible

### US7 - Lancer via Docker (Must Have)
- [ ] **T11** : Créer un Dockerfile de base pour l'exécution des sauvegardes
- [ ] **T12** : Configurer un docker-compose.yml pour un lancement simple
- **Test manuel** : Lancer la sauvegarde via Docker, vérifier que la configuration est lue et que l'archive est créée

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
