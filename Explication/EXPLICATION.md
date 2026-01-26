#  Explication du Projet - Moteur de Recommandation de Produits

##  Vue d'ensemble du projet

Ce projet implémente un **système expert basé sur la logique floue** (utilisant la librairie Experta) pour recommander des produits de santé et bien-être adaptés aux besoins des utilisateurs, en tenant compte de leurs contre-indications médicales.

---

##  Structure des fichiers

### 1️ **database.py** - Base de données

**Rôle :** Stocke les données statiques du système

#### Contenu :

- **CATALOGUE_PRODUITS** : Liste de tous les produits disponibles avec leurs propriétés
  - Chaque produit a un `nom` et une `cible` (symptôme/condition qu'il traite)
  - Organisés par catégories : Énergie & Immunité, Stress & Sommeil, Digestion, Articulations & Os
  - 20 produits différents (vitamines, herbes, minéraux, etc.)

- **CONTRE_INDICATIONS** : Liste des restrictions de sécurité
  - Chaque entrée lie un `produit` à une `condition` médicale incompatible
  - Exemples : 
    - Melatonine Spray incompatible avec grossesse
    - Guarana incompatible avec hypertension
    - Curcuma Piperine incompatible avec traitement anticoagulant

---

### 2️ **logic.py** - Moteur d'inférence (Cœur du système)

**Rôle :** Contient la logique d'inférence du système expert

#### Composants principaux :

**Classes (Faits) :**
- `Produit` : Représente un produit avec nom et cible
- `ContreIndication` : Représente une restriction produit/condition
- `BesoinClient` : Le symptôme/besoin du client (déclaré à l'exécution)
- `ConditionClient` : Les conditions médicales du client (déclaré à l'exécution)
- `ProduitInterdit` : Produit interdit pour ce client (généré automatiquement)
- `Recommandation` : Produit recommandé final (généré automatiquement)

**Classe MoteurRecommandation (KnowledgeEngine) :**

- **chargement_initial()** : Initialise le moteur en chargeant :
  - Tous les produits du catalogue
  - Toutes les contre-indications

- **detecter_danger()** - Règle 1 (Sécurité)
  - Si un produit a une contre-indication ET le client a cette condition
  - ALORS marquer ce produit comme interdit
  - ✅ Filtre les produits dangereux

- **generer_recommandation()** - Règle 2 (Recommandation)
  - Si le client a un besoin (symptôme) ET il existe un produit pour ce besoin
  - ET ce produit n'est PAS dans la liste des produits interdits
  - ALORS recommander ce produit
  - ✅ Propose les produits sûrs et adaptés

---

### 3️ **app.py** - Interface d'utilisation

**Rôle :** Interface utilisateur qui teste le système

#### Fonction principale :

**lancer_diagnostic(nom_user, symptomes, conditions_medicales)**

Effectue une requête au moteur :
1. Crée une instance du moteur de recommandation
2. Déclare les besoins du client (symptômes)
3. Déclare les conditions médicales du client
4. Exécute le moteur pour générer les recommandations
5. Affiche les résultats en format lisible

#### Test du système (Banc d'essai) :

4 scénarios de test sont exécutés :

1. **L'Étudiant** : Stress + Fatigue (aucune restriction)
2. **Femme Enceinte** : Fatigue + Sommeil + Stress (restriction : grossesse)
3. **Senior Hypertendu** : Articulation + Fatigue (restriction : hypertension)
4. **Patient Cardiaque** : Immunité + Articulation (restriction : anticoagulant)

---

##  Flux de traitement

```
┌─────────────────────────────┐
│  Données utilisateur         │
│  (symptômes, conditions)     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Moteur d'inférence (logic) │
│  • Charge catalogue + CI     │
│  • Exécute Règle 1 (sécurité)│
│  • Exécute Règle 2 (reco)    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Résultats filtrés          │
│  Produits sûrs recommandés  │
└─────────────────────────────┘
```

---

##  Avantages du système

✅ **Automatisé** : Les recommandations sont générées automatiquement  
✅ **Sécurisé** : Filtre les produits dangereux selon les conditions médicales  
✅ **Extensible** : Facile d'ajouter de nouveaux produits ou contre-indications  
✅ **Maintenable** : Séparation claire entre données (database) et logique (logic)  
✅ **Testé** : Plusieurs scénarios testés dans app.py

---

##  Technologie utilisée

- **Experta** : Framework Python pour les systèmes experts basés sur des règles
- Compatible Python 3.10+ (patch d'historique collections)
