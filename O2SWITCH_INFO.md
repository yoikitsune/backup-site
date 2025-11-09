# Informations FOURNISSEUR_HEBERGEMENT - À remplir avant le test

**Remplir ce formulaire avec les infos de votre serveur FOURNISSEUR_HEBERGEMENT**

---

## 🖥️ Informations serveur

### Connexion SSH

```
Domaine/IP du serveur : grand.FOURNISSEUR_HEBERGEMENT.net
Utilisateur SSH : UTILISATEUR_SECURISE
Port SSH : _________ (défaut: 22)
Chemin clé privée SSH : _________________________________
Chemin clé publique SSH : _________________________________
```

### Chemins WordPress

```
Chemin WordPress : /home/UTILISATEUR_SECURISE/feelgoodbymelanie.com
Chemin wp-config.php : /home/UTILISATEUR_SECURISE/feelgoodbymelanie.com/wp-config.php
Chemin wp-content : /home/UTILISATEUR_SECURISE/feelgoodbymelanie.com/wp-content
```

---

## 🗄️ Informations MySQL

### Connexion

```
Hôte MySQL : localhost
Port MySQL : _________ (défaut: 3306)
Utilisateur MySQL : UTILISATEUR_SECURISE_wp48
Mot de passe MySQL : p5]QS6.1tK
Nom base de données : UTILISATEUR_SECURISE_wp48
```

### Vérification

Pour vérifier les infos MySQL, exécuter sur FOURNISSEUR_HEBERGEMENT :
```bash
# Vérifier la version MySQL
mysql --version

# Vérifier la connexion
mysql -u USERNAME -p -e "SELECT 1;"

# Lister les bases de données
mysql -u USERNAME -p -e "SHOW DATABASES;"
```

---

## 📦 Versions

### Déterminer les versions

Sur FOURNISSEUR_HEBERGEMENT, exécuter :
```bash
# Version PHP
php -v

# Version MySQL
mysql --version

# Version WordPress (depuis le répertoire WordPress)
cd /home/USERNAME/www
wp core version
```

### Versions à noter

```
Version PHP : 8.1.33
Version MySQL : 11.4.9-MariaDB
Version WordPress : 6.8.3
```

---

## ✅ Checklist de vérification

Avant de commencer le test, vérifier :

- [ ] Connexion SSH fonctionnelle : `ssh -p PORT USER@HOST "ls"`
- [ ] Clé SSH accessible : `ls -la ~/.ssh/id_rsa`
- [ ] Permissions clé SSH correctes : `chmod 600 ~/.ssh/id_rsa`
- [ ] Chemin WordPress existe : `ssh USER@HOST "ls -la /path/to/www"`
- [ ] MySQL accessible : `ssh USER@HOST "mysql -u USER -p -e 'SELECT 1;'"`
- [ ] Versions PHP/MySQL/WordPress notées

---

## 📝 Notes

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 🚀 Prochaines étapes

Une fois ce formulaire rempli :

1. Créer `config/production.yaml` avec ces infos
2. Valider la configuration : `backup-site config validate config/production.yaml`
3. Tester la connexion : `backup-site ssh test config/production.yaml`
4. Suivre le plan d'action : `PRODUCTION_TEST_PLAN.md`
