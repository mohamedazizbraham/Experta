import unittest
from datetime import date, datetime, timezone

from bson import ObjectId
from fastapi.testclient import TestClient
from logic import (
    calculate_recommendation_grade,
    extract_health_conditions_from_supplements,
    normalize_health_condition,
    match_symptoms_with_products,
    MoteurRecommandation,
    Produit
)
from api import (
    PersonalInfoUpdate,
    app,
    _augment_decision_with_goal_groups,
    _build_carried_intake_docs,
    _build_intake_targets_from_decision,
    _coerce_bool,
    _decision_input_from_profile,
    _parse_optional_datetime_input,
)
from database import CATALOGUE_COMPLET
from goals import (
    canonical_goal_for_symptom,
    canonical_goals_for_symptom,
    canonicalize_goal_list,
)
from service import decide


def _norm(s: str) -> str:
    return (s or "").strip().casefold()


def _category_of_product(product_name: str) -> str:
    name_norm = _norm(product_name)
    for cat, items in CATALOGUE_COMPLET.items():
        for it in items:
            if _norm(it.get("name", "")) == name_norm:
                return cat
    return ""


class TestHealthConditionExtraction(unittest.TestCase):
    """Tests pour l'extraction des conditions de santé"""

    def test_extract_health_conditions_returns_dict(self):
        """Vérifie que extract_health_conditions retourne un dictionnaire"""
        conditions = extract_health_conditions_from_supplements()
        self.assertIsInstance(conditions, dict)

    def test_extract_contains_products(self):
        """Vérifie que des produits sont extraits"""
        conditions = extract_health_conditions_from_supplements()
        self.assertGreater(len(conditions), 0, "Aucun produit extrait")

    def test_extract_conditions_format(self):
        """Vérifie le format: {product_name: [condition1, condition2, ...]}"""
        conditions = extract_health_conditions_from_supplements()
        for product_name, conditions_list in conditions.items():
            self.assertIsInstance(product_name, str)
            self.assertIsInstance(conditions_list, list)
            self.assertGreater(len(conditions_list), 0, f"{product_name} n'a pas de conditions")

    def test_alpha_lactalbumin_has_sommeil_condition(self):
        """Vérifie que Alpha-Lactalbumin a une condition pour le sommeil"""
        conditions = extract_health_conditions_from_supplements()
        self.assertIn("Alpha-Lactalbumin", conditions, "Alpha-Lactalbumin non trouvé")
        self.assertTrue(
            any("sommeil" in c.lower() for c in conditions["Alpha-Lactalbumin"]),
            "Aucune condition 'sommeil' pour Alpha-Lactalbumin"
        )


class TestNormalizeHealthCondition(unittest.TestCase):
    """Tests pour la normalisation des conditions de santé"""

    def test_normalize_removes_sante(self):
        """Vérifie que 'santé' est retiré"""
        result = normalize_health_condition("Santé du sommeil")
        self.assertEqual(result, "sommeil")

    def test_normalize_removes_du(self):
        """Vérifie que 'du' est retiré"""
        result = normalize_health_condition("Santé du coeur")
        self.assertEqual(result, "coeur")

    def test_normalize_lowercase(self):
        """Vérifie la conversion en minuscules"""
        result = normalize_health_condition("SOMMEIL")
        self.assertEqual(result, "sommeil")

    def test_normalize_simple_condition(self):
        """Vérifie qu'une condition simple est préservée"""
        result = normalize_health_condition("Sommeil")
        self.assertEqual(result, "sommeil")

    def test_normalize_cardiovasculaire(self):
        """Vérifie une condition cardiovasculaire"""
        result = normalize_health_condition("Santé cardiovasculaire générale")
        self.assertEqual(result, "cardiovasculaire")

    def test_normalize_preserves_hyphens(self):
        """Vérifie que les tirets sont préservés"""
        result = normalize_health_condition("bien-être")
        self.assertIn("bien", result)

    def test_normalize_goal_label_sleep(self):
        """Verifie qu un libelle objectif mappe vers le symptome utile"""
        result = normalize_health_condition("Ameliorer mon sommeil")
        self.assertEqual(result, "sommeil")

    def test_normalize_goal_label_stress(self):
        """Verifie que la normalisation supporte les labels objectifs"""
        result = normalize_health_condition("Reduire mon stress")
        self.assertEqual(result, "stress")

    def test_normalize_goal_label_sleep_with_unicode_escape(self):
        """Verifie le cas frontend exact avec accents UTF-8"""
        result = normalize_health_condition("Am\u00e9liorer mon sommeil")
        self.assertEqual(result, "sommeil")

class TestMatchSymptomsWithProducts(unittest.TestCase):
    """Tests pour le matching symptômes-produits"""

    def test_match_returns_dict(self):
        """Vérifie que match_symptoms retourne un dictionnaire"""
        result = match_symptoms_with_products(["Sommeil"])
        self.assertIsInstance(result, dict)

    def test_match_sommeil_returns_products(self):
        """Vérifie que "Sommeil" retourne des produits"""
        result = match_symptoms_with_products(["Sommeil"])
        self.assertGreater(len(result), 0, "Aucun produit pour 'Sommeil'")

    def test_match_alpha_lactalbumin_for_sommeil(self):
        """Vérifie que Alpha-Lactalbumin est recommandé pour Sommeil"""
        result = match_symptoms_with_products(["Sommeil"])
        self.assertIn("Alpha-Lactalbumin", result, "Alpha-Lactalbumin non trouvé pour Sommeil")

    def test_match_result_has_score(self):
        """Vérifie que chaque résultat a un score"""
        result = match_symptoms_with_products(["Sommeil"])
        for product_name, match_info in result.items():
            self.assertIn("score", match_info)
            self.assertIsInstance(match_info["score"], int)
            self.assertGreater(match_info["score"], 0)

    def test_match_result_has_matched_symptoms(self):
        """Vérifie que chaque résultat a des symptômes matchés"""
        result = match_symptoms_with_products(["Sommeil"])
        for product_name, match_info in result.items():
            self.assertIn("matched_symptoms", match_info)
            self.assertIsInstance(match_info["matched_symptoms"], list)
            self.assertGreater(len(match_info["matched_symptoms"]), 0)

    def test_match_multiple_symptoms(self):
        """Vérifie le matching avec plusieurs symptômes"""
        result = match_symptoms_with_products(["Sommeil", "Dépression"])
        self.assertGreater(len(result), 0, "Aucun produit pour symptômes multiples")

    def test_match_sorting_by_score(self):
        """Vérifie que les résultats sont triés par score (décroissant)"""
        result = match_symptoms_with_products(["Sommeil", "Dépression"])
        scores = [info["score"] for info in result.values()]
        # Vérifie que les scores sont en ordre décroissant
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_match_empty_symptoms(self):
        """Vérifie le comportement avec symptômes vides"""
        result = match_symptoms_with_products([])
        self.assertIsInstance(result, dict)

    def test_match_unknown_symptom(self):
        """Vérifie le comportement avec symptôme inconnu"""
        result = match_symptoms_with_products(["XYZ_SYMPTOME_INCONNU_123"])
        self.assertEqual(len(result), 0, "Des produits ont été trouvés pour symptôme inconnu")


class TestDataLoading(unittest.TestCase):
    """Tests pour le chargement des données"""

    def test_catalogue_complet_loaded(self):
        """Vérifie que le catalogue est chargé"""
        self.assertIsInstance(CATALOGUE_COMPLET, dict)
        self.assertGreater(len(CATALOGUE_COMPLET), 0)

    def test_catalogue_has_required_categories(self):
        """Vérifie que les catégories requises existent"""
        self.assertIn("complement_alimentaire", CATALOGUE_COMPLET)
        self.assertIn("sport_et_pratique", CATALOGUE_COMPLET)
        self.assertIn("regime_alimentaire", CATALOGUE_COMPLET)

    def test_each_category_has_products(self):
        """Vérifie que chaque catégorie a des produits"""
        for category, products in CATALOGUE_COMPLET.items():
            self.assertGreater(len(products), 0, f"Catégorie {category} vide")

    def test_products_have_names(self):
        """Vérifie que chaque produit a un nom"""
        for category, products in CATALOGUE_COMPLET.items():
            for product in products:
                self.assertIn("name", product, f"Produit dans {category} sans 'name'")
                self.assertTrue(product["name"], f"Produit dans {category} avec nom vide")

    def test_products_have_database_field(self):
        """Vérifie que les produits ont la section database"""
        for category, products in CATALOGUE_COMPLET.items():
            for product in products:
                if category == "complement_alimentaire":
                    # Les suppléments doivent avoir database
                    self.assertIn("database", product, f"{product.get('name')} sans 'database'")


class TestIntegrationScenarios(unittest.TestCase):
    """Tests d'intégration pour les scénarios complets"""

    def test_scenario_patient_d_sommeil(self):
        """
        SCÉNARIO : Patient D (Sommeil)
        Attendu : Doit obtenir des recommandations pour 'Sommeil'
        """
        result = match_symptoms_with_products(["Sommeil"])
        
        # Doit avoir des résultats
        self.assertGreater(len(result), 0, "Aucune recommandation pour 'Sommeil'")
        
        # Alpha-Lactalbumin doit être recommandé
        self.assertIn("Alpha-Lactalbumin", result)
        
        # Le symptôme doit être "sommeil" (normalisé)
        matched_symptoms = result["Alpha-Lactalbumin"]["matched_symptoms"]
        self.assertIn("sommeil", matched_symptoms)

    def test_scenario_patient_a_depression(self):
        """
        SCÉNARIO : Patient A (Dépression)
        Attendu : Doit obtenir des recommandations pour 'Dépression'
        """
        result = match_symptoms_with_products(["Dépression"])
        
        # Doit avoir des résultats
        self.assertGreater(len(result), 0, "Aucune recommandation pour 'Dépression'")

    def test_scenario_multiple_symptoms(self):
        """
        SCÉNARIO : Plusieurs symptômes
        Attendu : Les produits matching plusieurs symptômes ont un score plus élevé
        """
        result = match_symptoms_with_products(["Sommeil", "Dépression"])
        
        # Doit avoir des résultats
        self.assertGreater(len(result), 0, "Aucune recommandation pour symptômes multiples")
        
        # Le premier produit (plus haut score) doit avoir score >= 1
        first_product = next(iter(result.values()))
        self.assertGreaterEqual(first_product["score"], 1)


class TestDecisionRankingWithGrades(unittest.TestCase):
    """Tests de classement et de compatibilité du service de décision."""

    def test_explicit_grade_breaks_ties_for_best_decision(self):
        decision = decide(["Sommeil"])

        caffeine_grade = calculate_recommendation_grade("Caffeine", ["sommeil"])
        alpha_grade = calculate_recommendation_grade("Alpha-Lactalbumin", ["sommeil"])

        self.assertGreater(caffeine_grade["grade_score"], alpha_grade["grade_score"])
        self.assertEqual(decision["best_decision"]["produit"], "Caffeine")
        self.assertEqual(decision["best_decision"]["grade"], "B")

    def test_grade_priority_can_outrank_higher_symptom_coverage(self):
        decision = decide(["stress", "taille"])

        self.assertEqual(decision["best_decision"]["produit"], "Kava")
        self.assertEqual(decision["best_decision"]["grade"], "A")
        self.assertEqual(decision["best_decision"]["score_symptomes"], 1)

    def test_missing_explicit_grade_is_inferred(self):
        grade_info = calculate_recommendation_grade("L-Tyrosine", ["stress"])

        self.assertEqual(grade_info["grade"], "A")
        self.assertEqual(grade_info["grade_score"], 4)
        self.assertEqual(grade_info["grade_source"], "inferred")

    def test_score_field_remains_compatible(self):
        decision = decide(["Sommeil"])

        self.assertGreater(len(decision["recommendations"]), 0)
        for item in decision["recommendations"]:
            self.assertIn("score", item)
            self.assertIn("score_symptomes", item)
            self.assertEqual(item["score"], item["score_symptomes"])
            self.assertIsInstance(item["score"], int)

    def test_best_decision_matches_first_sorted_recommendation(self):
        decision = decide(["Sommeil"])

        self.assertGreater(len(decision["recommendations"]), 0)
        self.assertEqual(decision["best_decision"], decision["recommendations"][0])

    def test_decision_caps_supplements_to_five_items(self):
        decision = decide(["Sommeil"])

        supplements = [
            item for item in decision["recommendations"]
            if item.get("category_type") == "recommendation"
        ]
        self.assertLessEqual(len(supplements), 5)

    def test_contraindications_still_exclude_products(self):
        decision = decide(["depression"], ["grossesse"])
        product_names = {item["produit"] for item in decision["recommendations"]}

        self.assertNotIn("5-HTP", product_names)
        self.assertIn("5-HTP", decision["forbidden_products"])

    def test_decide_endpoint_still_returns_valid_payload(self):
        client = TestClient(app)

        response = client.post(
            "/decide",
            json={"symptomes": ["Sommeil"], "conditions_medicales": []},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("best_decision", payload)
        self.assertIn("recommendations", payload)
        self.assertLessEqual(
            len([item for item in payload["recommendations"] if item.get("category_type") == "recommendation"]),
            5,
        )
        self.assertIn("score", payload["best_decision"])
        self.assertIn("score_symptomes", payload["best_decision"])
        self.assertIn("grade", payload["best_decision"])
        self.assertIn("grade_score", payload["best_decision"])
        self.assertIn("grade_source", payload["best_decision"])


class TestCanonicalGoals(unittest.TestCase):
    """Tests de normalisation et regroupement des objectifs."""

    def test_canonicalize_goal_list_deduplicates_variants(self):
        values = [
            "Sleep Health",
            "sante du sommeil",
            "sleep_support",
            "Ameliorer mon sommeil",
        ]
        out = canonicalize_goal_list(values)
        self.assertEqual(out, ["sleep_support"])

    def test_goal_for_symptom_maps_weight_variants(self):
        self.assertEqual(canonical_goal_for_symptom("Perte de poids et maintien"), "weight_loss")
        self.assertEqual(canonical_goal_for_symptom("Obesity"), "weight_loss")

    def test_goal_for_symptom_supports_multiple_goal_matches(self):
        goals = canonical_goals_for_symptom("surpoids")
        self.assertIn("weight_loss", goals)
        self.assertIn("appetite_control", goals)

    def test_decision_input_from_profile_uses_canonical_goals(self):
        prepared = _decision_input_from_profile(
            {
                "goals": [
                    "Sleep Health",
                    "Amelioration de l'humeur",
                    "Stress anxiety support",
                ]
            }
        )
        self.assertIn("sleep_support", prepared["goals"])
        self.assertIn("mood_depression_support", prepared["goals"])
        self.assertIn("stress_anxiety_support", prepared["goals"])
        self.assertIn("sommeil", prepared["symptomes"])

    def test_augmented_decision_groups_recommendations_by_goal(self):
        prepared = _decision_input_from_profile(
            {"goals": ["sleep_support", "stress_anxiety_support"]}
        )
        decision = decide(prepared["symptomes"], prepared["conditions_medicales"])
        augmented = _augment_decision_with_goal_groups(decision, prepared)

        grouped = augmented.get("recommendations_by_goal") or {}
        self.assertIn("sleep_support", grouped)
        self.assertIn("stress_anxiety_support", grouped)
        self.assertIsInstance(grouped["sleep_support"], list)
        self.assertIsInstance(grouped["stress_anxiety_support"], list)

    def test_augmented_decision_exposes_best_decision_by_goal(self):
        prepared = _decision_input_from_profile(
            {"goals": ["sleep_support", "stress_anxiety_support"]}
        )
        decision = decide(prepared["symptomes"], prepared["conditions_medicales"])
        augmented = _augment_decision_with_goal_groups(decision, prepared)

        grouped = augmented.get("recommendations_by_goal") or {}
        best_by_goal = augmented.get("best_decision_by_goal") or {}

        self.assertIn("sleep_support", best_by_goal)
        self.assertIn("stress_anxiety_support", best_by_goal)
        self.assertEqual(best_by_goal["sleep_support"], grouped["sleep_support"][0])
        self.assertEqual(
            best_by_goal["stress_anxiety_support"],
            grouped["stress_anxiety_support"][0],
        )

    def test_augmented_decision_respects_selected_goal_for_shared_symptom(self):
        prepared = {"goals": ["appetite_control"]}
        decision = {
            "recommendations": [
                {
                    "produit": "Test Product",
                    "symptomes_couverts": ["surpoids"],
                }
            ]
        }

        augmented = _augment_decision_with_goal_groups(decision, prepared)
        grouped = augmented.get("recommendations_by_goal") or {}
        self.assertIn("appetite_control", grouped)
        self.assertEqual(len(grouped["appetite_control"]), 1)
        self.assertEqual(grouped["appetite_control"][0].get("goal"), "appetite_control")


class TestIntakeCarryOver(unittest.TestCase):
    """Tests du maintien d'etat des prises entre recommandations."""

    def test_build_intake_targets_from_decision(self):
        decision = {
            "recommendations_by_goal": {
                "sleep_support": [
                    {"produit": "Melatonine"},
                    {"produit": "Magnesium"},
                ]
            }
        }
        targets = _build_intake_targets_from_decision(decision)

        self.assertIn(("sleep_support", "melatonine"), targets)
        self.assertIn(("sleep_support", "magnesium"), targets)
        self.assertEqual(
            targets[("sleep_support", "melatonine")]["supplement_id"],
            "sleep_support::0",
        )

    def test_build_carried_intake_docs_keeps_latest_known_state(self):
        targets = {
            ("sleep_support", "melatonine"): {
                "supplement_id": "sleep_support::0",
                "supplement_name": "Melatonine",
                "objective_key": "sleep_support",
                "objective_label": "Ameliorer mon sommeil",
            }
        }
        previous_intakes = [
            {
                "supplement_name": "Melatonine",
                "objective_key": "sleep_support",
                "taken": False,
                "taken_at": datetime(2026, 2, 24, 12, 0, tzinfo=timezone.utc),
            },
            {
                "supplement_name": "Melatonine",
                "objective_key": "sleep_support",
                "taken": True,
                "taken_at": datetime(2026, 2, 24, 9, 0, tzinfo=timezone.utc),
            },
        ]

        docs = _build_carried_intake_docs(
            previous_intakes=previous_intakes,
            targets=targets,
            user_id=ObjectId(),
            recommendation_id=ObjectId(),
        )

        self.assertEqual(len(docs), 1)
        self.assertFalse(docs[0]["taken"])
        self.assertEqual(docs[0]["supplement_id"], "sleep_support::0")

    def test_parse_optional_datetime_input_accepts_iso_z(self):
        dt = _parse_optional_datetime_input("2026-04-12T10:30:00.000Z")
        self.assertIsNotNone(dt)
        assert dt is not None
        self.assertEqual(dt.tzinfo, timezone.utc)

    def test_coerce_bool_accepts_string_values(self):
        self.assertTrue(_coerce_bool("true"))
        self.assertFalse(_coerce_bool("false", default=True))


class TestProfilePayloadSchema(unittest.TestCase):
    def test_personal_info_update_accepts_birth_date(self):
        payload = PersonalInfoUpdate(
            first_name="Ada",
            last_name="Lovelace",
            birth_date=date(1815, 12, 10),
        )
        self.assertEqual(payload.birth_date.isoformat(), "1815-12-10")


if __name__ == '__main__':
    # Lance tous les tests et affiche le rapport
    unittest.main()


