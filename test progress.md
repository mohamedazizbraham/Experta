## Suite de tests automatisée

**Pourquoi**
- Objectif : verrouiller les règles métier sensibles (grossesse, interactions) à chaque modification du code via [test_suite.py](test_suite.py).
- Ancien mode manuel (lecture de logs) = risque d'erreur humaine et de régression silencieuse lors de l'ajout de nouvelles catégories.

**Méthodo adoptée**
- Persona-based testing : chaque scénario incarne un profil patient réaliste pour juger la pertinence médicale.
- Cycle red/green/refactor : l'échec initial du scénario anticoagulants a révélé l'oubli d'interaction sur la Mélatonine, corrigé puis verrouillé par le test.
- Choix `unittest` (standard lib) pour éviter toute dépendance externe et garder l'installation minimale.

**Architecture des tests**
- Unit : vérifie le chargement des catégories Sport/Herbe/Complément dans la base de faits ([test_suite.py](test_suite.py#L35-L53)).
- Intégration : scénarios « happy path » pour dépression et insomnie, couvrant la recommandation croisée Chimie/Herbe/Sport ([test_suite.py](test_suite.py#L55-L85)).
- Régression/Sécurité : interdiction stricte selon les conditions sensibles (Pilule, Grossesse, Hypertension, Anticoagulants) ([test_suite.py](test_suite.py#L87-L153)).

**Scénarios couverts**
- S1 Dépression simple → attend 5-HTP + Millepertuis ([test_suite.py](test_suite.py#L58-L71)).
- S2 Sous pilule → bloque Millepertuis ([test_suite.py](test_suite.py#L90-L105)).
- S3 Grossesse (fatigue/stress) → autorise Magnésium + Yoga uniquement ([test_suite.py](test_suite.py#L107-L125)).
- S4 Insomnie → recommande Mélatonine + Yoga Nidra ([test_suite.py](test_suite.py#L72-L85)).
- S5 Hypertension → bloque Guarana, propose alternative sûre Magnésium ([test_suite.py](test_suite.py#L126-L138)).
- S6 Anticoagulants → bloque Millepertuis + Mélatonine, laisse Yoga ([test_suite.py](test_suite.py#L139-L153)).

**État actuel**
- 6 scénarios critiques passent en < 0.01 s.
- Faille corrigée : interaction Mélatonine/Anticoagulants désormais couverte et testée.
- Données réelles utilisées (pas de mocks) pour capturer les erreurs de configuration, principale source de risques dans ce moteur expert.