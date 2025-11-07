# Backlog du projet

## User Stories (à prioriser)

### Fonctionnalités principales
- [ ] **US1** : En tant que développeur, je veux sauvegarder les fichiers d'un site web
- [ ] **US2** : En tant que développeur, je veux sauvegarder une base de données MySQL/MariaDB
- [ ] **US3** : En tant que développeur, je veux restaurer une sauvegarde complète (fichiers + BDD)

### Configuration
- [ ] **US4** : En tant que développeur, je veux pouvoir créer facilement une configuration pour un site avec son hébergement, son type d'application, la clé SSH, les accès aux fichiers et à la base de données
- [ ] **US5** : En tant que développeur, je veux pouvoir configurer facilement les paramètres de connexion à la base de données
- [ ] **US6** : En tant que développeur, je veux pouvoir spécifier les dossiers à inclure/exclure de la sauvegarde

### Intégration Docker
- [ ] **US7** : En tant que développeur, je veux pouvoir lancer la sauvegarde via une commande Docker simple
- [ ] **US8** : En tant que développeur, je veux pouvoir spécifier la version de PHP/MySQL à utiliser

### Gestion des sauvegardes
- [ ] **US9** : En tant que développeur, je veux lister les sauvegardes disponibles
- [ ] **US10** : En tant que développeur, je veux supprimer des anciennes sauvegardes

## Priorisation (MoSCoW)

### Must Have (MVP) - WordPress + FOURNISSEUR_HEBERGEMENT
- US1, US2, US3, US4, US7
- **Focus spécifique** : Configuration WordPress sur hébergement FOURNISSEUR_HEBERGEMENT avec gestion clés SSH publiques/privées

### Should Have
- US5, US6, US8

### Could Have
- US9, US10

### Won't Have (pour l'instant)
- Support d'autres bases de données que MySQL/MariaDB
- Interface graphique
