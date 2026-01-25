import unittest
# On importe le moteur et les faits depuis vos fichiers existants
from logic import MoteurRecommandation, BesoinClient, ConditionClient, Recommandation, ProduitInterdit, Produit
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

class TestSystemeExpert(unittest.TestCase):

    def setUp(self):
        """
        S'exécute avant CHAQUE test.
        Initialise un moteur vierge pour garantir l'indépendance des tests.
        """
        self.engine = MoteurRecommandation()
        self.engine.reset()

    def _lancer_moteur(self, symptomes, conditions):
        """
        Fonction utilitaire pour éviter de répéter le code d'injection des faits.
        Retourne :
          - recos : Liste des noms des produits recommandés
          - interdits : Liste des noms des produits bloqués (sécurité)
        """
        for s in symptomes:
            self.engine.declare(BesoinClient(symptome=s.lower()))
        for c in conditions:
            self.engine.declare(ConditionClient(condition=c.lower()))
        
        self.engine.run()
        
        # Extraction des résultats
        matches = [(f["nom"], f["cible"]) for f in self.engine.facts.values() if isinstance(f, Recommandation)]
        recos = [p for (p, _c) in matches]
        interdits = [f["produit"] for f in self.engine.facts.values() if isinstance(f, ProduitInterdit)]

        return recos, interdits, matches

    # ====================================================================
    # 1. UNIT TESTS (Vérification technique)
    # ====================================================================

    def test_unit_chargement_categories(self):
        """
        Vérifie que le catalogue issu de data/ est bien chargé.
        On vérifie qu'on trouve au moins un produit de chaque catégorie.
        """
        # Clés attendues (mappées depuis data/)
        self.assertIn("complement_alimentaire", CATALOGUE_COMPLET)
        self.assertIn("sport_et_pratique", CATALOGUE_COMPLET)
        self.assertIn("regime_alimentaire", CATALOGUE_COMPLET)

        self.assertGreater(len(CATALOGUE_COMPLET["complement_alimentaire"]), 0)
        self.assertGreater(len(CATALOGUE_COMPLET["sport_et_pratique"]), 0)
        self.assertGreater(len(CATALOGUE_COMPLET["regime_alimentaire"]), 0)

        # On récupère tous les faits 'Produit' chargés en mémoire
        tous_produits = [f["nom"] for f in self.engine.facts.values() if isinstance(f, Produit)]

        # Un produit par catégorie (noms réels dans data/)
        self.assertTrue(any(_norm(p) == _norm("Yoga") for p in tous_produits), "Erreur: Yoga (Sport) n'est pas chargé.")
        self.assertTrue(any(_norm(p) == _norm("Mélatonine") for p in tous_produits), "Erreur: Mélatonine (Complément) n'est pas chargée.")
        self.assertTrue(any(_norm(p) == _norm("Diète méditerranéenne") for p in tous_produits), "Erreur: Diète méditerranéenne (Régime) n'est pas chargée.")

    # ====================================================================
    # 2. INTEGRATION TESTS (Scénarios "Happy Path" - Ça marche ?)
    # ====================================================================

    def test_scenario_1_depression_simple(self):
        """
        SCÉNARIO 1 : Patient A (Dépressif simple)
        Attendu : Doit recevoir des solutions de plusieurs catégories (Complément + Pratique).
        """
        recos, interdits, matches = self._lancer_moteur(
            symptomes=['Dépression'], 
            conditions=[]
        )

        # Vérification: cibles et catégories
        self.assertIn("5-HTP", recos, "Devrait recommander 5-HTP")
        self.assertIn("Yoga", recos, "Devrait recommander Yoga")
        self.assertNotIn("5-HTP", interdits)
        self.assertNotIn("Yoga", interdits)

        # Vérifie que les recommandations ont la bonne cible
        cible = _norm("Dépression")
        for p, c in matches:
            if p in ("5-HTP", "Yoga"):
                self.assertEqual(_norm(c), cible)

        self.assertEqual(_category_of_product("5-HTP"), "complement_alimentaire")
        self.assertEqual(_category_of_product("Yoga"), "sport_et_pratique")

    def test_scenario_2_cardiovasculaire_diete(self):
        """
        SCÉNARIO 2 : Santé cardiovasculaire
        Attendu : Recommande la diète méditerranéenne.
        """
        recos, _interdits, matches = self._lancer_moteur(
            symptomes=['Santé cardiovasculaire générale'],
            conditions=[]
        )

        self.assertIn("Diète méditerranéenne", recos)
        self.assertEqual(_category_of_product("Diète méditerranéenne"), "regime_alimentaire")

        cible = _norm("Santé cardiovasculaire générale")
        for p, c in matches:
            if p == "Diète méditerranéenne":
                self.assertEqual(_norm(c), cible)

    # ====================================================================
    # 3. REGRESSION TESTS (Scénarios de Sécurité - Ça ne casse pas ?)
    # ====================================================================

    def test_scenario_3_grossesse_filtre(self):
        """
        SCÉNARIO 3 : Grossesse
        Attendu : Les produits marqués "éviter" pendant la grossesse sont bloqués.
        Yoga reste autorisé.
        """
        recos, interdits, _matches = self._lancer_moteur(
            symptomes=['Dépression'],
            conditions=['Grossesse']
        )

        # Yoga reste OK
        self.assertIn("Yoga", recos)

        # Produits à éviter pendant la grossesse (d'après data/)
        self.assertIn("5-HTP", interdits)
        self.assertIn("Mélatonine", interdits)
        self.assertNotIn("5-HTP", recos, "FAIL: 5-HTP recommandé pendant la grossesse")
        self.assertNotIn("Mélatonine", recos, "FAIL: Mélatonine recommandée pendant la grossesse")

    def test_scenario_4_interaction_warfarin(self):
        """
        SCÉNARIO 4 : Interaction médicamenteuse
        Attendu : Mélatonine est bloquée si l'utilisateur prend Warfarin.
        """
        recos, interdits, _matches = self._lancer_moteur(
            symptomes=['Hypertension artérielle'],
            conditions=['Warfarin']
        )

        self.assertIn("Mélatonine", interdits)
        self.assertNotIn("Mélatonine", recos, "FAIL: Mélatonine recommandée malgré Warfarin")

if __name__ == '__main__':
    # Lance tous les tests et affiche le rapport
    unittest.main()