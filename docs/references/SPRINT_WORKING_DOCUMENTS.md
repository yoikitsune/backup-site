# 📝 Documents de travail du Sprint

**Pour qui ?** : Développeurs, Architects, Product Owners  
**Durée** : 10 min  
**Objectif** : Créer et gérer des documents temporaires pour discuter précisément sur certains points

---

## 🎯 Pourquoi des documents temporaires ?

Les documents temporaires permettent de :
- ✅ **Discuter** en profondeur une décision technique
- ✅ **Explorer** plusieurs alternatives
- ✅ **Documenter** les blocages et les solutions
- ✅ **Clarifier** les besoins avant l'implémentation
- ✅ **Tracer** les décisions prises

**Différence clé** : Ce ne sont PAS des docs finales, c'est un **carnet de travail**.

---

## 📚 Les 3 types de documents temporaires

### 1️⃣ **Scratch Pad** (Bloc-notes)

**Quand l'utiliser** :
- Pendant qu'on code/explore
- Pour noter des idées brutes
- Pour tester des approches

**Durée de vie** : Quelques heures à quelques jours

**Exemple de contenu** :
```markdown
# Scratch - US2 MySQL Investigation

## Essai 1 : MySQL sur Alpine
- Problème : Démarrage en arrière-plan complexe
- Raison : Alpine est très léger, pas de systemd
- Résultat : ❌ Trop compliqué

## Essai 2 : MariaDB sur Alpine
- Avantage : Plus léger que MySQL
- Syntaxe mysqldump : Identique
- Résultat : ✅ À explorer plus

## Prochaines étapes
- Tester MariaDB avec docker-compose
```

**Où le mettre** : `docs/progress/SPRINT_WORK/`

**Après le sprint** : Supprimé ou archivé

---

### 2️⃣ **Spike Documentation** (Investigation technique)

**Quand l'utiliser** :
- Pour investiguer une question complexe
- Pour comparer des alternatives
- Pour valider une approche

**Durée de vie** : 1-2 sprints

**Exemple de contenu** :
```markdown
# Spike - Comparaison MySQL vs MariaDB

## Objectif
Déterminer quelle base de données utiliser pour le conteneur Alpine.

## Investigation

### Option A : MySQL
- Pros : Standard de l'industrie
- Cons : Lourd sur Alpine, démarrage complexe
- Temps de setup : 2h

### Option B : MariaDB
- Pros : Léger, compatible mysqldump, démarrage simple
- Cons : Moins connu
- Temps de setup : 30 min

### Option C : PostgreSQL
- Pros : Très robuste
- Cons : Pas compatible avec WordPress
- Rejeté

## Décision
✅ **MariaDB** : Meilleur compromis pour Alpine

## Justification
- Démarrage plus simple
- Fonctionne bien sur Alpine
- Compatible avec mysqldump
- Réduit la complexité du Dockerfile

## Résultats
- Dockerfile simplifié
- Tests unitaires créés
- Intégration réussie
```

**Où le mettre** : `docs/progress/SPRINT_WORK/`

**Après le sprint** : 
- Convertir en décision architecturale → `docs/architecture/IMPLEMENTATION_NOTES.md`
- Archiver dans `docs/progress/SPRINT_REVIEWS/sprint-X/`

---

### 3️⃣ **Sprint Notes / Working Notes** (Carnet de sprint)

**Quand l'utiliser** :
- Pour discuter une User Story ou une tâche
- Pour lister les blocages
- Pour tracer les décisions du sprint

**Durée de vie** : Durée du sprint (1-2 semaines)

**Exemple de contenu** :
```markdown
# Sprint Notes - US2 Testing Plan

## 🎯 Objectif
Implémenter et tester la sauvegarde BDD MySQL.

## 📋 Checklist

### Tests unitaires
- [ ] Mock SSH
- [ ] Mock mysqldump
- [ ] Test construction commande
- [ ] Test gestion erreurs

### Tests d'intégration
- [ ] Serveur Docker avec SSH + MySQL
- [ ] Connexion SSH tunnel
- [ ] Exécution mysqldump
- [ ] Vérification fichier SQL

### Tests complets
- [ ] US1 + US2 dans une archive
- [ ] Vérification archive complète

## ❓ Questions en suspens
1. Quelle version de MySQL/MariaDB ?
2. Comment gérer les erreurs de connexion ?
3. Faut-il supporter les fichiers non-compressés ?

## 🚧 Blocages
- MySQL ne démarre pas sur Alpine (résolu avec MariaDB)
- Besoin d'investiguer SSH tunnel

## ✅ Décisions prises
- Utiliser MariaDB au lieu de MySQL
- Implémenter 2 méthodes : backup_to_file() et backup_to_stream()
- Tester avec docker-compose

## 📝 Notes
- Voir SPIKE_MYSQL.md pour l'investigation complète
- Résultats finaux dans PROGRESS.md après le sprint
```

**Où le mettre** : `docs/progress/SPRINT_WORK/`

**Après le sprint** :
- Archiver dans `docs/progress/SPRINT_REVIEWS/sprint-X/`
- Mettre à jour PROGRESS.md avec les résultats finaux

---

## 📁 Structure des documents temporaires

```
docs/progress/
│
├── PROGRESS.md                      # État global (permanent)
├── CLEANUP_SUMMARY.md               # Nettoyages (permanent)
│
├── SPRINT_WORK/                     # 📝 Documents de travail (temporaire)
│   ├── US2_TESTING_PLAN.md          # Sprint Notes pour US2
│   ├── SPIKE_MYSQL.md               # Investigation MySQL vs MariaDB
│   ├── SPIKE_SSH_TUNNEL.md          # Investigation SSH tunnel
│   └── BLOCAGES.md                  # Problèmes rencontrés
│
└── SPRINT_REVIEWS/                  # 📦 Archives des sprints
    ├── sprint-1/
    │   ├── RETROSPECTIVE.md
    │   ├── DECISIONS.md
    │   └── SPIKE_MYSQL_RESULTS.md   # Résultats finaux
    └── sprint-2/
        └── ...
```

---

## 🔄 Cycle de vie d'un document temporaire

### **Phase 1 : Création (Pendant le sprint)**
```
docs/progress/SPRINT_WORK/US2_TESTING_PLAN.md
├── Créé au début de la tâche
├── Mis à jour au fur et à mesure
└── Contient questions, blocages, décisions
```

### **Phase 2 : Utilisation (Pendant le sprint)**
- Référencé dans les commits : "Voir SPRINT_WORK/US2_TESTING_PLAN.md"
- Utilisé pour discuter avec l'équipe
- Mis à jour avec les résultats

### **Phase 3 : Archivage (Fin du sprint)**
```
docs/progress/SPRINT_WORK/US2_TESTING_PLAN.md
    ↓
docs/progress/SPRINT_REVIEWS/sprint-1/US2_TESTING_PLAN.md
```

### **Phase 4 : Conversion (Après le sprint)**
- **Décisions** → `docs/architecture/IMPLEMENTATION_NOTES.md`
- **Tests** → `docs/development/TESTING.md`
- **Blocages** → `docs/progress/TROUBLESHOOTING.md`
- **Résultats** → `PROGRESS.md`

---

## ✅ Checklist : Créer un document temporaire

- [ ] **Nom clair** : `SPIKE_XXX.md` ou `US_XXX_TESTING_PLAN.md`
- [ ] **Objectif en haut** : "Investiguer XXX"
- [ ] **Questions** : Lister les questions à résoudre
- [ ] **Alternatives** : Documenter les options testées
- [ ] **Décisions** : Tracer les choix faits
- [ ] **Résultats** : Documenter les conclusions
- [ ] **Références** : Lier aux docs permanentes
- [ ] **Date de création** : Pour savoir quand archiver

---

## 💡 Bonnes pratiques

### ✅ À FAIRE

- ✅ Créer un document par investigation/tâche complexe
- ✅ Mettre à jour régulièrement
- ✅ Lier aux docs permanentes
- ✅ Archiver à la fin du sprint
- ✅ Convertir les décisions en docs permanentes

### ❌ À ÉVITER

- ❌ Garder indéfiniment dans SPRINT_WORK/
- ❌ Mélanger avec la documentation permanente
- ❌ Oublier d'archiver
- ❌ Dupliquer les décisions ailleurs
- ❌ Créer trop de documents (max 3-4 par sprint)

---

## 🎯 Exemple complet : US2 MySQL

### Étape 1 : Créer le document
```bash
# Créer docs/progress/SPRINT_WORK/SPIKE_MYSQL.md
# Contenu : Investigation MySQL vs MariaDB
```

### Étape 2 : Utiliser pendant le sprint
```bash
# Dans le commit
git commit -m "US2: Tester MariaDB (voir SPIKE_MYSQL.md)"

# Dans les discussions
"Voir docs/progress/SPRINT_WORK/SPIKE_MYSQL.md pour les résultats"
```

### Étape 3 : Archiver à la fin du sprint
```bash
# Déplacer vers SPRINT_REVIEWS
mv docs/progress/SPRINT_WORK/SPIKE_MYSQL.md \
   docs/progress/SPRINT_REVIEWS/sprint-1/SPIKE_MYSQL_RESULTS.md
```

### Étape 4 : Convertir les résultats
```markdown
# Dans docs/architecture/IMPLEMENTATION_NOTES.md
## Choix de MariaDB
Voir SPIKE_MYSQL_RESULTS.md pour l'investigation complète.
- Raison : Plus léger sur Alpine
- Avantage : Démarrage simple
- Résultat : Dockerfile simplifié
```

---

## 📞 Questions fréquentes

**Q: Combien de documents temporaires créer ?**  
A: Max 3-4 par sprint. Un par investigation complexe.

**Q: Quand archiver ?**  
A: À la fin du sprint, avant de commencer le suivant.

**Q: Peut-on les supprimer ?**  
A: Oui, si les résultats sont documentés ailleurs.

**Q: Faut-il les versionner ?**  
A: Non, c'est du travail en cours. Pas besoin de git.

**Q: Peuvent-ils être dans le README ?**  
A: Non, c'est temporaire. Garder dans SPRINT_WORK/.

---

## 🔗 Voir aussi

- [AGILE_DOCUMENTATION_GUIDE.md](AGILE_DOCUMENTATION_GUIDE.md) - Principes Agile
- [DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md) - Structure générale
- [../progress/PROGRESS.md](../progress/PROGRESS.md) - État du projet

---

**Dernière mise à jour** : Nov 10, 2025  
**Responsable** : Cascade (AgileMentor)
