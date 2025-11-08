# Templates de configuration

Ce dossier contient les templates de configuration pré-configurés pour différents hébergeurs et CMS.

## Templates disponibles

### FOURNISSEUR_HEBERGEMENT-wordpress.yaml
Template optimisé pour WordPress hébergé sur FOURNISSEUR_HEBERGEMENT.

**Spécificités :**
- Configuration SSH adaptée à FOURNISSEUR_HEBERGEMENT
- Chemins standards FOURNISSEUR_HEBERGEMENT (`/home/identifiant/www`)
- Patterns WordPress optimisés
- Support WP-CLI
- Exclusion des caches et fichiers inutiles

## Utilisation

### Utiliser un template

1. **Copier le template** :
   ```bash
   cp config/FOURNISSEUR_HEBERGEMENT-wordpress.yaml config/mon-site.yaml
   ```

2. **Éditer le fichier** avec vos informations :
   - **SSH** : Remplacez `votre_identifiant_FOURNISSEUR_HEBERGEMENT` par votre identifiant FOURNISSEUR_HEBERGEMENT
   - **Base de données** : Remplacez `votre_identifiant_bdd` et `votre_mot_de_passe_bdd`
   - **Chemins** : Vérifiez que `/home/votre_identifiant/www` correspond à votre site
   - **Clés SSH** : Assurez-vous que les chemins vers vos clés sont corrects
   - **Patterns** : Ajustez les inclusions/exclusions selon vos besoins

3. **Valider la configuration** :
   ```bash
   backup-site config validate config/mon-site.yaml
   ```

4. **Tester la connexion SSH** :
   ```bash
   backup-site ssh test config/mon-site.yaml
   ```

5. **Personnaliser si nécessaire** :
   - Modifier les patterns d'inclusion/exclusion
   - Ajuster les options WP-CLI
   - Configurer les notifications

## Structure d'un template

Un template contient toutes les sections nécessaires :

```yaml
site:          # Informations générales
ssh:           # Configuration connexion SSH
files:         # Patterns de fichiers
database:      # Configuration base de données
backup:        # Options de sauvegarde
options:       # Options avancées
_template:     # Métadonnées du template
```

## Créer un nouveau template

1. Copiez un template existant
2. Adaptez les spécificités de l'hébergeur/CMS
3. Ajoutez les métadonnées `_template`
4. Testez avec `backup-site config create`

## Bonnes pratiques

- **Sécurité** : Ne jamais inclure de vrais mots de passe
- **Documentation** : Commentez chaque section spécifique
- **Patterns** : Soyez précis dans les inclusions/exclusions
- **Options** : Incluez les options recommandées pour l'hébergeur
