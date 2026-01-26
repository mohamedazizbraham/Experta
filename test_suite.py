import unittest
from logic import (
    extract_health_conditions_from_supplements,
    normalize_health_condition,
    match_symptoms_with_products,
    MoteurRecommandation,
    Produit
)
from database import CATALOGUE_COMPLET


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

    def test_normalize_removes_santé(self):
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


if __name__ == '__main__':
    # Lance tous les tests et affiche le rapport
    unittest.main()