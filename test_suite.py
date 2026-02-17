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
    """Tests pour l'extraction des conditions de santÃ©"""

    def test_extract_health_conditions_returns_dict(self):
        """VÃ©rifie que extract_health_conditions retourne un dictionnaire"""
        conditions = extract_health_conditions_from_supplements()
        self.assertIsInstance(conditions, dict)

    def test_extract_contains_products(self):
        """VÃ©rifie que des produits sont extraits"""
        conditions = extract_health_conditions_from_supplements()
        self.assertGreater(len(conditions), 0, "Aucun produit extrait")

    def test_extract_conditions_format(self):
        """VÃ©rifie le format: {product_name: [condition1, condition2, ...]}"""
        conditions = extract_health_conditions_from_supplements()
        for product_name, conditions_list in conditions.items():
            self.assertIsInstance(product_name, str)
            self.assertIsInstance(conditions_list, list)
            self.assertGreater(len(conditions_list), 0, f"{product_name} n'a pas de conditions")

    def test_alpha_lactalbumin_has_sommeil_condition(self):
        """VÃ©rifie que Alpha-Lactalbumin a une condition pour le sommeil"""
        conditions = extract_health_conditions_from_supplements()
        self.assertIn("Alpha-Lactalbumin", conditions, "Alpha-Lactalbumin non trouvÃ©")
        self.assertTrue(
            any("sommeil" in c.lower() for c in conditions["Alpha-Lactalbumin"]),
            "Aucune condition 'sommeil' pour Alpha-Lactalbumin"
        )


class TestNormalizeHealthCondition(unittest.TestCase):
    """Tests pour la normalisation des conditions de santÃ©"""

    def test_normalize_removes_sante(self):
        """VÃ©rifie que 'santÃ©' est retirÃ©"""
        result = normalize_health_condition("SantÃ© du sommeil")
        self.assertEqual(result, "sommeil")

    def test_normalize_removes_du(self):
        """VÃ©rifie que 'du' est retirÃ©"""
        result = normalize_health_condition("SantÃ© du coeur")
        self.assertEqual(result, "coeur")

    def test_normalize_lowercase(self):
        """VÃ©rifie la conversion en minuscules"""
        result = normalize_health_condition("SOMMEIL")
        self.assertEqual(result, "sommeil")

    def test_normalize_simple_condition(self):
        """VÃ©rifie qu'une condition simple est prÃ©servÃ©e"""
        result = normalize_health_condition("Sommeil")
        self.assertEqual(result, "sommeil")

    def test_normalize_cardiovasculaire(self):
        """VÃ©rifie une condition cardiovasculaire"""
        result = normalize_health_condition("SantÃ© cardiovasculaire gÃ©nÃ©rale")
        self.assertEqual(result, "cardiovasculaire")

    def test_normalize_preserves_hyphens(self):
        """VÃ©rifie que les tirets sont prÃ©servÃ©s"""
        result = normalize_health_condition("bien-Ãªtre")
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
    """Tests pour le matching symptÃ´mes-produits"""

    def test_match_returns_dict(self):
        """VÃ©rifie que match_symptoms retourne un dictionnaire"""
        result = match_symptoms_with_products(["Sommeil"])
        self.assertIsInstance(result, dict)

    def test_match_sommeil_returns_products(self):
        """VÃ©rifie que "Sommeil" retourne des produits"""
        result = match_symptoms_with_products(["Sommeil"])
        self.assertGreater(len(result), 0, "Aucun produit pour 'Sommeil'")

    def test_match_alpha_lactalbumin_for_sommeil(self):
        """VÃ©rifie que Alpha-Lactalbumin est recommandÃ© pour Sommeil"""
        result = match_symptoms_with_products(["Sommeil"])
        self.assertIn("Alpha-Lactalbumin", result, "Alpha-Lactalbumin non trouvÃ© pour Sommeil")

    def test_match_result_has_score(self):
        """VÃ©rifie que chaque rÃ©sultat a un score"""
        result = match_symptoms_with_products(["Sommeil"])
        for product_name, match_info in result.items():
            self.assertIn("score", match_info)
            self.assertIsInstance(match_info["score"], int)
            self.assertGreater(match_info["score"], 0)

    def test_match_result_has_matched_symptoms(self):
        """VÃ©rifie que chaque rÃ©sultat a des symptÃ´mes matchÃ©s"""
        result = match_symptoms_with_products(["Sommeil"])
        for product_name, match_info in result.items():
            self.assertIn("matched_symptoms", match_info)
            self.assertIsInstance(match_info["matched_symptoms"], list)
            self.assertGreater(len(match_info["matched_symptoms"]), 0)

    def test_match_multiple_symptoms(self):
        """VÃ©rifie le matching avec plusieurs symptÃ´mes"""
        result = match_symptoms_with_products(["Sommeil", "DÃ©pression"])
        self.assertGreater(len(result), 0, "Aucun produit pour symptÃ´mes multiples")

    def test_match_sorting_by_score(self):
        """VÃ©rifie que les rÃ©sultats sont triÃ©s par score (dÃ©croissant)"""
        result = match_symptoms_with_products(["Sommeil", "DÃ©pression"])
        scores = [info["score"] for info in result.values()]
        # VÃ©rifie que les scores sont en ordre dÃ©croissant
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_match_empty_symptoms(self):
        """VÃ©rifie le comportement avec symptÃ´mes vides"""
        result = match_symptoms_with_products([])
        self.assertIsInstance(result, dict)

    def test_match_unknown_symptom(self):
        """VÃ©rifie le comportement avec symptÃ´me inconnu"""
        result = match_symptoms_with_products(["XYZ_SYMPTOME_INCONNU_123"])
        self.assertEqual(len(result), 0, "Des produits ont Ã©tÃ© trouvÃ©s pour symptÃ´me inconnu")


class TestDataLoading(unittest.TestCase):
    """Tests pour le chargement des donnÃ©es"""

    def test_catalogue_complet_loaded(self):
        """VÃ©rifie que le catalogue est chargÃ©"""
        self.assertIsInstance(CATALOGUE_COMPLET, dict)
        self.assertGreater(len(CATALOGUE_COMPLET), 0)

    def test_catalogue_has_required_categories(self):
        """VÃ©rifie que les catÃ©gories requises existent"""
        self.assertIn("complement_alimentaire", CATALOGUE_COMPLET)
        self.assertIn("sport_et_pratique", CATALOGUE_COMPLET)
        self.assertIn("regime_alimentaire", CATALOGUE_COMPLET)

    def test_each_category_has_products(self):
        """VÃ©rifie que chaque catÃ©gorie a des produits"""
        for category, products in CATALOGUE_COMPLET.items():
            self.assertGreater(len(products), 0, f"CatÃ©gorie {category} vide")

    def test_products_have_names(self):
        """VÃ©rifie que chaque produit a un nom"""
        for category, products in CATALOGUE_COMPLET.items():
            for product in products:
                self.assertIn("name", product, f"Produit dans {category} sans 'name'")
                self.assertTrue(product["name"], f"Produit dans {category} avec nom vide")

    def test_products_have_database_field(self):
        """VÃ©rifie que les produits ont la section database"""
        for category, products in CATALOGUE_COMPLET.items():
            for product in products:
                if category == "complement_alimentaire":
                    # Les supplÃ©ments doivent avoir database
                    self.assertIn("database", product, f"{product.get('name')} sans 'database'")


class TestIntegrationScenarios(unittest.TestCase):
    """Tests d'intÃ©gration pour les scÃ©narios complets"""

    def test_scenario_patient_d_sommeil(self):
        """
        SCÃ‰NARIO : Patient D (Sommeil)
        Attendu : Doit obtenir des recommandations pour 'Sommeil'
        """
        result = match_symptoms_with_products(["Sommeil"])
        
        # Doit avoir des rÃ©sultats
        self.assertGreater(len(result), 0, "Aucune recommandation pour 'Sommeil'")
        
        # Alpha-Lactalbumin doit Ãªtre recommandÃ©
        self.assertIn("Alpha-Lactalbumin", result)
        
        # Le symptÃ´me doit Ãªtre "sommeil" (normalisÃ©)
        matched_symptoms = result["Alpha-Lactalbumin"]["matched_symptoms"]
        self.assertIn("sommeil", matched_symptoms)

    def test_scenario_patient_a_depression(self):
        """
        SCÃ‰NARIO : Patient A (DÃ©pression)
        Attendu : Doit obtenir des recommandations pour 'DÃ©pression'
        """
        result = match_symptoms_with_products(["DÃ©pression"])
        
        # Doit avoir des rÃ©sultats
        self.assertGreater(len(result), 0, "Aucune recommandation pour 'DÃ©pression'")

    def test_scenario_multiple_symptoms(self):
        """
        SCÃ‰NARIO : Plusieurs symptÃ´mes
        Attendu : Les produits matching plusieurs symptÃ´mes ont un score plus Ã©levÃ©
        """
        result = match_symptoms_with_products(["Sommeil", "DÃ©pression"])
        
        # Doit avoir des rÃ©sultats
        self.assertGreater(len(result), 0, "Aucune recommandation pour symptÃ´mes multiples")
        
        # Le premier produit (plus haut score) doit avoir score >= 1
        first_product = next(iter(result.values()))
        self.assertGreaterEqual(first_product["score"], 1)


if __name__ == '__main__':
    # Lance tous les tests et affiche le rapport
    unittest.main()

