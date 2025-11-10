# Vision du projet

## Nom du projet
backup-site

## Objectif
Créer une solution CLI de sauvegarde de site (fichiers + base de données) avec la possibilité de charger et tester les sauvegardes localement via Docker.

## Utilisateurs cibles
- Développeur (moi-même) : Pour sauvegarder facilement mes projets de développement locaux, en particulier les sites web avec base de données

## Valeur ajoutée
- **Simplicité** : Une commande unique pour sauvegarder/charger/adapter un projet entier
- **Configuration facile** par type d'hébergeur (ex: FOURNISSEUR_HEBERGEMENT) et CMS (ex: WordPress)
- **Support natif de Docker** pour tester différentes versions de langages (PHP, MySQL, WordPress)
- **Portabilité** des sauvegardes entre différents environnements de développement
- **Adaptation automatique** : URLs WordPress, configuration BDD, permissions

---

## 📊 État du projet

### ✅ Sprint 1 - MVP COMPLÉTÉ (Nov 10, 2025)

**Fonctionnalités livrées** :
- ✅ **Sauvegarde des fichiers** (US1) : Compression côté serveur via SSH
- ✅ **Sauvegarde de la BDD** (US2) : MySQL/MariaDB via mysqldump
- ✅ **Docker production-test** (US7) : Environnement reproduisant la production
- ✅ **Chargement des fichiers** (US8.1) : Via docker cp + extraction
- ✅ **Chargement de la BDD** (US8.2) : Via docker exec + mariadb
- ✅ **Adaptation WordPress** (US8.3) : URLs + configuration automatiques

**Commandes CLI** :
```bash
# Sauvegarde (depuis production)
backup-site backup files <config>
backup-site backup database <config>

# Chargement (dans Docker local)
backup-site load files <archive>
backup-site load database <dump>
backup-site load setup --old-url <url> --new-url <url>
```

---

## 🚀 Prochaines étapes (Sprint 2)

### À planifier
- **US3** : Restauration complète (fichiers + BDD en une commande)
- **US9** : Gestion des sauvegardes (lister, supprimer anciennes)
- **US10** : Planification (sauvegardes automatiques via cron)

### Améliorations futures
- Chiffrement des sauvegardes
- Vérification d'intégrité (checksums)
- Notifications (email, webhook)
- Dashboard de monitoring
- Support d'autres hébergeurs (Kinsta, WP Engine, etc.)

---

## 📚 Documentation

- **README.md** : Guide complet d'installation et utilisation
- **architecture.md** : Détails techniques et structure du projet
- **PROGRESS.md** : Historique des phases complétées
- **COMMANDES_COMPLETES_A_Z.md** : Workflow complet étape par étape
- **WORKFLOW_COMPLET.md** : Diagramme et détails du workflow
- **TESTING.md** : Guide de test et validation
