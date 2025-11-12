# Refonte du workflow de sauvegarde (Préparation Sprint 2)

## 1. Analyse du workflow A→Z actuel

### 1.1 Initialisation & configuration
- Création manuelle des dossiers `backups/production`, `config/`, `scripts/` via la documentation.
- Génération d'un unique fichier `config/production.yaml` directement dans le guide, avec peu de modularité pour d'autres sites ou hébergeurs.
- Validation et test SSH déclenchés à la main (commande CLI).

### 1.2 Sauvegarde
- Commandes `backup-site backup files` et `backup-site backup database` déposent les artefacts directement à la racine de `backups/production/`.
- Les noms sont statiques (`files.tar.gz`, `database.sql.gz`) ou générés via timestamp côté CLI sans structure par site/date.
- Aucune production de manifeste (hash, taille, contexte) ni de politique de rétention automatisée.

### 1.3 Préparation Docker
- Documentation génère un `.env` dans `docker/production-test/` avec versions, accès MySQL et SSH.
- Création d'un `Dockerfile` spécifique (WordPress + wp-cli) et build via `docker compose`.
- Environnement unique mélangeant besoins SSH et WordPress : difficile à répliquer pour plusieurs sites ou variantes d'hébergement.

### 1.4 Chargement / Restauration
- Commandes `load files` et `load database` transfèrent les archives dans des dossiers temporaires `/tmp/restore_*` avant copie dans les conteneurs.
- Pas de séparation claire entre artefacts sources (sauvegarde) et artefacts restaurés.
- Dépendances implicites : restauration DB lit `wp-config.php` pour récupérer les accès.

### 1.5 Post-traitement & validation
- Ajustements WordPress (perms, URL) via `backup-site load setup` et vérifications manuelles (`docker compose exec ...`).
- Checklists présentes dans la documentation mais aucun journal de run centralisé.
- Workflow global fortement dépendant du guide A→Z, peu industrialisé pour répéter sur plusieurs sites.


### 1.6 Synthèse avant / après

- **Configuration** : aujourd’hui un unique `config/production.yaml` rédigé à la main ; demain un `config.yaml` par site, toujours exhaustif, mais généré à partir de templates provider/app.
- **Sauvegardes** : archives à plat (`files.tar.gz`, `database.sql.gz`) ; cible avec dossiers datés par site, manifestes et lien `latest/` pour suivre l’historique.
- **Connexion SSH** : aujourd’hui guide manuel selon la documentation ; demain flux par défaut `ssh-copy-id` (stockage des clés uniquement) avec gestion spécifique pour FOURNISSEUR_HEBERGEMENT et autres hébergeurs via helpers.
- **Docker / restauration** : aujourd’hui un environnement unique difficile à répliquer ; demain une bibliothèque d’environnements par stack et scripts d’orchestration `run-backup.sh` / `run-restore.sh`.
- **Observabilité** : aujourd’hui pas de trace persistante ; demain logs par run et indicateurs dans les manifestes.

## 2. Vision cible à discuter pour Sprint 2

### 2.1 Workflow cible (v2) pas-à-pas

1. **Initialiser un site géré** : créer `sites/<slug>/` avec `config.yaml` dérivé d'un template provider/app.
2. **Configurer le provider/app** : le `config.yaml` indique `provider = FOURNISSEUR_HEBERGEMENT`, `app_type = wordpress`.
3. **Guidage SSH spécifique** : par défaut l’outil propose `ssh-copy-id` (stockage de clés uniquement, pas de mot de passe) puis, si `provider = FOURNISSEUR_HEBERGEMENT`, affiche le guide `print_ssh_setup_guide` pour gérer l’exception où la copie automatique n’est pas possible.
4. **Vérification SSH** : exécuter un test (`backup-site site verify <slug>`) pour valider les clés/accès avant d'aller plus loin.
5. **Préparation sauvegarde WordPress** : avec un `config.yaml` pleinement défini (includes/excludes, chemins, BDD) on peut déjà lancer `backup files` + `backup database`. Les helpers WordPress se contentent de pré-remplir ces champs (lecture de `wp-config.php`, métadonnées) pour gagner du temps sans retirer la possibilité d’éditer manuellement.
6. **Provisionnement docker local** : sélection de l'environnement `docker/environments/wordpress-FOURNISSEUR_HEBERGEMENT/`, génération `.env` (PHP/MariaDB), lancement des conteneurs, injection des sauvegardes et adaptation WordPress.
7. **Validation** : vérifier la disponibilité locale (curl + ouverture navigateur) et consigner le résultat (log).

### 2.2 Axes de conception

1. **Structure par site (config centrale + sauvegardes)**
   - Chaque site dispose d'un dossier `sites/<slug>/` contenant un `config.yaml` de référence.
   - Sous-dossier `backups/<YYYYMMDD>/` par run, avec lien `latest/` pour l'accès courant.
   - Manifestes par run (hash, taille, versions CLI, environnement) et politique de rétention configurable (préparation US9/US10).

2. **Configurations templatisées**
   - `config/templates/<provider>-<stack>.yaml` comme base pour générer un `config.yaml` complet (SSH, fichiers, BDD, backup) utilisable immédiatement, avec sections includes/excludes.
   - `config/sites/<slug>.yaml` pour chaque client, validés par CLI, éditables librement et priorisés avant même l’ajout de helpers.
   - Métadonnées (slug, stack, URL, contacts) pour suivre plusieurs sites et guider les helpers qui automatisent le remplissage.

3. **Bibliothèque d’environnements Docker**
   - `docker/environments/<stack>/` contenant `docker-compose.yml`, `.env.example`, scripts d’amorçage.
   - Séparation claire des images (WordPress, SSH, MySQL) et des données persistantes.
   - Guides courts pour choisir et lancer l’environnement adapté.

4. **Scripts d’orchestration workflow**
   - `scripts/run-backup.sh <site>` : crée la structure, lance les commandes CLI, produit le manifeste et les logs.
   - `scripts/run-restore.sh <site> --env <stack>` : provisionne Docker, restaure fichiers + BDD, applique post-traitements.
   - Centralisation des logs dans `backups/<site>/<date>/run.log`; un dossier `report/` par site pourra être ajouté plus tard si nécessaire.

5. **Documentation & observabilité**
   - Mise à jour de `COMMANDES_COMPLETES_A_Z.md` et `WORKFLOW_COMPLET.md` pour refléter la nouvelle architecture.
   - Ajout d’un schéma de workflow et d’un glossaire des artefacts.
   - Indicateurs clés (taille sauvegardes, durée run) consignés dans les logs et, à terme, dans des rapports si cette option est retenue.

> **Point d'attention** : la structure Docker par site reste à préciser (quelle part mutualiser vs. specific overrides). Ce sujet fera l'objet d'un focus dédié pendant le raffinement.

### 2.3 User stories candidates (ordre chronologique)

| ID | Description | Objectif principal |
| --- | --- | --- |
| **US-A** | `backup-site site init <slug>` crée la structure `sites/<slug>/` et le `config.yaml` basé sur le template provider/app. | Démarrer un site géré avec conventions multi-sites. |
| **US-B** | `backup-site site guide/verify <slug>` propose `ssh-copy-id` par défaut puis affiche le guide provider (FOURNISSEUR_HEBERGEMENT, etc.) et encapsule le test SSH. | Sécuriser la connexion avant sauvegarde sans stocker de mot de passe. |
| **US-C** | Détection WordPress pour la sauvegarde (lecture `wp-config.php`, manifestes par run). | Lancer une sauvegarde cohérente sans saisie répétitive. |
| **US-D** | Provisionner Docker selon provider/app (`docker/environments/<stack>/`). | Rejouer l’environnement production en local automatiquement. |
| **US-E** | `backup-site site restore <slug>` orchestre chargement fichiers+BDD + setup WordPress. | Restauration bout-en-bout pilotée. |
| **US-F** | `backup-site site validate <slug>` réalise les checks post-restore (curl, logs). | Vérifier la sauvegarde en conditions réelles. |

## 3. Prochaine discussion Agile
- Valider ensemble la vision (priorisation MoSCoW des axes et stories US-A → US-F).
- Identifier les dépendances (notamment périmètre Docker et gestion des providers SSH) et estimer l’effort.
- Préparer la mise à jour de `backlog.md` et `sprint-planning.md` avec les éléments retenus.
- Décider des livrables documentaires (mise à jour workflows, guides) synchronisés avec les stories.
