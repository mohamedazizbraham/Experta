# Progression du Projet Experta

---

## 1️⃣ Pourquoi cette évolution ? (Why)

### Contexte Initial
L'objectif initial était de créer un simple système de recommandation de compléments. Cependant, **la santé ne se limite pas à la prise de gélules**. Nous avons fait évoluer le système pour qu'il adopte une approche **holistique (globale)**.

### Évolution de l'Architecture

| Aspect | Avant | Maintenant |
|--------|-------|-----------|
| **Approche** | Simple (produits chimiques) | Holistique (multidisciplinaire) |
| **Champs Gérés** | "Produits" uniquement | Interventions par catégories |
| **Catégories** | N/A | Compléments, Herbes, Pratiques Sportives |

### Objectif Final
Permettre au système de recommander une **solution mixte** :
- Exemple : *"Magnésium"* (chimie) + *"Yoga"* (comportemental) pour traiter le stress

---

## 2️⃣ Sources d'Inspiration (Inspiration)

La structure de la base de données a été repensée pour imiter les **standards des bases de connaissances médicales réelles** (ex: Examine.com, Vidal).

### Points Clés

** Modèle de Document**
- Au lieu d'une liste plate, chaque entrée est un "Document" riche
- Contient des métadonnées imbriquées : `overview`, `safety`, `outcomes`

** Preuve par la Donnée**
- Ajout des champs `database` et `studies`
- Justification des recommandations par niveaux de preuve : Grade A, B, C
- Renforce la crédibilité du système expert

---

## 3️⃣ Compromis Techniques (Tradeoffs)

Pour atteindre ce niveau de détail, nous avons dû accepter certains compromis techniques.

###  Complexité du Parsing vs Simplicité

| Aspect | Détail |
|--------|--------|
| **Choix** | Abandon de la lecture simple → Parser complexe dans `logic.py` (boucles imbriquées) |
| **Coût** | Code plus verbeux, puissance CPU accrue au démarrage |
| **Gain** | Flexibilité totale (ajout de catégories sans casser le moteur) |

###  Dette Technique (Bibliothèque Experta)

**Problème :**
- La bibliothèque Experta n'est plus maintenue activement
- Incompatible avec Python 3.10+

**Solution Appliquée :**
- Monkey Patch (`collections.abc`) en tête de fichier
- Évite une réécriture complète du moteur

**Limitation :**
- Solution acceptable pour prototype
- Nécessite migration à long terme : Drools ou code natif pour la production industrielle

---

## 4️⃣ État d'Avancement (Progress)

Le système est passé d'un **prototype "jouet"** à une **architecture structurée**.

###  Validations Complétées

** Architecture de Données (Validée)**
- ✓ Transition réussie : liste simple → Dictionnaire Catégorisé (`CATALOGUE_COMPLET`)
- ✓ Format JSON complexe supporté

** Moteur d'Inférence (Opérationnel)**
- ✓ Lecture récursive des sous-catégories
- ✓ Règles de sécurité (`safety`) scannent correctement
- ✓ Détection des interactions médicamenteuses et conditions (Grossesse, etc.)
- ✓ Couverture multi-catégories

** Interface de Test (Fonctionnelle)**
- ✓ Script `app.py` pour simuler des scénarios complexes
- ✓ Résultats mixtes (Chimie + Sport)
- ✓ Filtrage automatique des produits dangereux