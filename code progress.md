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

Le système est passé d'un **prototype "jouet"** à une **architecture structurée et optimisée**.

###  Validations Complétées

** Architecture de Données (Validée)**
- ✓ Transition réussie : liste simple → Dictionnaire Catégorisé (`CATALOGUE_COMPLET`)
- ✓ Format JSON complexe supporté

** Extraction des Health Conditions (Nouveau - Optimisé)**
- ✓ Fonction dédiée : `extract_health_conditions_from_supplements()`
- ✓ Extraction claire et réutilisable des `health_condition_or_goal`
- ✓ Retourne un dictionnaire structuré pour faciliter la réutilisation

** Normalisation des Conditions (Nouveau - Robuste)**
- ✓ Fonction `normalize_health_condition()` pour normaliser les conditions
- ✓ Exemples : "Santé du sommeil" → "sommeil", "Santé cardiovasculaire" → "cardiovasculaire"
- ✓ Utilisée partout pour garantir la cohérence

** Matching Symptômes-Produits (Nouveau - Principal)**
- ✓ Fonction `match_symptoms_with_products()` pour correspondance exacte
- ✓ Prend les symptômes du patient et retourne les produits recommandés
- ✓ Calcule un score basé sur le nombre de symptômes matchés
- ✓ Trie automatiquement par pertinence

** Interface de Test (Refactorisée)**
- ✓ Script `app.py` simplifié et plus lisible
- ✓ Utilise maintenant la fonction `match_symptoms_with_products()` au lieu du moteur Experta complet
- ✓ Affichage amélioré avec scores et symptômes matchés
- ✓ Performance accrue (pas de moteur d'inférence complexe)

---

## 5️⃣ Architecture Actuelle (Current Architecture)

### Flux de Traitement Simplifié

```
Patient Symptoms (ex: ["Sommeil"])
        ↓
[match_symptoms_with_products()]
        ↓
extract_health_conditions_from_supplements()  →  {"Alpha-Lactalbumin": ["Santé du sommeil"], ...}
        ↓
normalize_health_condition()  →  "santé du sommeil" → "sommeil"
        ↓
Matching: "sommeil" (patient) == "sommeil" (product)
        ↓
Return: {"Alpha-Lactalbumin": {"matched_symptoms": ["sommeil"], "score": 1}, ...}
        ↓
Display Results (app.py)
```

### Fonctions Clés dans `logic.py`

| Fonction | Rôle | Retour |
|----------|------|--------|
| `extract_health_conditions_from_supplements()` | Extrait les conditions brutes de la BD | `Dict[str, List[str]]` |
| `normalize_health_condition()` | Normalise une condition | `str` |
| `match_symptoms_with_products()` | Matching patient ↔ produits | `Dict[str, Dict]` (avec score) |

### Évolution du Moteur Experta

**Avant (Complexe):**
- Utilisait un moteur d'inférence Experta complet
- Déclaration de faits : `BesoinClient`, `ConditionClient`, `Recommandation`
- Règles imbriquées pour validation
- Nécessitait un patch Python 3.10+

**Après (Optimisé):**
- Approche fonctionnelle directe
- Pas d'engine d'inférence nécessaire pour le matching basique
- Code plus lisible et maintenable
- Moteur Experta toujours disponible pour règles de sécurité avancées (future)

---

## 6️⃣ Prochaines Étapes (Next Steps)

### Intégration Sécurité
- [ ] Implémenter vérification des contre-indications (`ContreIndication`)
- [ ] Valider les conditions médicales du patient
- [ ] Bloquer les produits dangereux avant affichage

### Enrichissement des Données
- [ ] Ajouter plus de produits avec `health_condition_or_goal`
- [ ] Documenter les grades de preuve (A, B, C, D)
- [ ] Compléter les sections `safety` et `outcomes`

### Performance & Scalabilité
- [ ] Cache les résultats `extract_health_conditions_from_supplements()`
- [ ] Tester avec large volume de produits
- [ ] Optimiser la normalisation (possible regex)