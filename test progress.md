# Test Progress

## Suite de tests automatisée

**Pourquoi**
- Objectif : valider les fonctions clés (extraction, normalisation, matching) et verrouiller les règles métier via [test_suite.py](test_suite.py).
- Mode automatisé : les tests vérifient la cohérence des données et des recommandations à chaque modification.

**Méthodo adoptée**
- Tests focalisés : chaque classe de tests valide une fonction spécifique (`extract_health_conditions_from_supplements()`, `normalize_health_condition()`, `match_symptoms_with_products()`).
- Persona-based testing : scénarios d'intégration qui incarnent des profils patients réalistes.
- Choix `unittest` (standard lib) pour éviter toute dépendance externe.

**Architecture des tests (Refactorisée)**

### 1. TestHealthConditionExtraction
Vérifie l'extraction des conditions de santé
- Format du dictionnaire retourné
- Présence des produits et de leurs conditions
- Cas spécifiques (ex: Alpha-Lactalbumin pour sommeil)
- Tests: `test_extract_health_conditions_returns_dict`, `test_extract_contains_products`, `test_alpha_lactalbumin_has_sommeil_condition`

### 2. TestNormalizeHealthCondition
Vérifie la normalisation des conditions
- Suppression des stop words ("santé", "du", "générale")
- Conversion en minuscules
- Extraction du mot clé principal (ex: "cardiovasculaire" depuis "Santé cardiovasculaire générale")
- Tests: `test_normalize_removes_santé`, `test_normalize_lowercase`, `test_normalize_cardiovasculaire`

### 3. TestMatchSymptomsWithProducts
Vérifie le matching symptômes ↔ produits
- Retour d'un dictionnaire structuré
- Format correct (score, matched_symptoms, raw_conditions)
- Tri par score décroissant
- Gestion des symptômes inconnus (retour vide)
- Tests: `test_match_sommeil_returns_products`, `test_match_alpha_lactalbumin_for_sommeil`, `test_match_sorting_by_score`

### 4. TestDataLoading
Vérifie le chargement des données
- Catalogue chargé correctement
- Catégories requises présentes
- Produits avec champs obligatoires
- Tests: `test_catalogue_complet_loaded`, `test_each_category_has_products`, `test_products_have_database_field`

### 5. TestIntegrationScenarios
Vérifie les scénarios complets
- Patient D (Sommeil) → Alpha-Lactalbumin recommandé
- Patient A (Dépression) → recommandations trouvées
- Symptômes multiples → score pertinent
- Tests: `test_scenario_patient_d_sommeil`, `test_scenario_patient_a_depression`, `test_scenario_multiple_symptoms`

**État actuel**
- ✅ Tous les tests passent via : `python -m unittest -v` ou `python test_suite.py`
- ✅ 30+ assertions couvrant extraction, normalisation et matching
- ✅ Tests de régression pour les cas limites (symptômes vides, inconnus)
- ✅ Données réelles utilisées (pas de mocks)
- ✅ Validation complète du pipeline : extraction → normalisation → matching
- ✅ Exit code 0 : tous les tests réussissent

**Prochaines étapes**
- Intégrer les tests de sécurité (grossesse, interactions) quand la validation des contraindications sera implémentée
- Ajouter des tests de performance avec large volume de produits
- Tester avec d'autres langues (si applicable)
