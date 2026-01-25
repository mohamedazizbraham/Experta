## Suite de tests automatisée

**Pourquoi**
- Objectif : verrouiller les règles métier sensibles (grossesse, interactions) à chaque modification du code via [test_suite.py](test_suite.py).
- Ancien mode manuel (lecture de logs) = risque d'erreur humaine et de régression silencieuse lors de l'ajout de nouvelles catégories.

**Méthodo adoptée**
- Persona-based testing : chaque scénario incarne un profil patient réaliste pour juger la pertinence médicale.
- Cycle red/green/refactor : les scénarios vérifient la cohérence entre symptômes (cibles), recommandations et filtrage sécurité à partir des JSON dans `data/`.
- Choix `unittest` (standard lib) pour éviter toute dépendance externe et garder l'installation minimale.

**Architecture des tests**
- Unit : vérifie que les catégories issues de `data/` sont bien chargées (mapping `supplements/other/diets` → `complement_alimentaire/sport_et_pratique/regime_alimentaire`) et que des faits `Produit` sont générés.
- Intégration : vérifie que les recommandations ont la bonne *cible* (le champ `cible` de `Recommandation` correspond au symptôme demandé) et qu’on obtient des recommandations multi-catégories quand c’est attendu.
- Régression/Sécurité : vérifie le filtrage strict (grossesse, interactions médicamenteuses) sur des cas sensibles.

**Scénarios couverts**
- S1 Dépression simple → recommande `5-HTP` (complément) + `Yoga` (pratique) et vérifie que la cible recommandée est bien “Dépression”.
- S2 Santé cardiovasculaire générale → recommande `Diète méditerranéenne` (régime) et vérifie la cible.
- S3 Grossesse → bloque `5-HTP` et `Mélatonine` (marqués “éviter” dans `data/`), tout en laissant `Yoga` autorisé.
- S4 Interaction Warfarin → bloque strictement `Mélatonine` lorsque l’utilisateur déclare `Warfarin`.

**État actuel**
- 5 tests passent (unit + intégration + régression) via : `python -m unittest -q`.
- Données réelles utilisées (pas de mocks) pour capturer les erreurs de configuration liées aux fichiers JSON (`data/`).
- Vérifications clés : cibles (`Recommandation.cible`), catégorie d’origine (complément/pratique/régime), et filtrage sécurité (grossesse + interactions).