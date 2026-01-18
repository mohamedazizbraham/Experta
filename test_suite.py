import unittest
# On importe le moteur et les faits depuis vos fichiers existants
from logic import MoteurRecommandation, BesoinClient, ConditionClient, Recommandation, ProduitInterdit, Produit

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
        recos = [f['nom'] for f in self.engine.facts.values() if isinstance(f, Recommandation)]
        interdits = [f['produit'] for f in self.engine.facts.values() if isinstance(f, ProduitInterdit)]
        
        return recos, interdits

    # ====================================================================
    # 1. UNIT TESTS (Vérification technique)
    # ====================================================================

    def test_unit_chargement_categories(self):
        """
        Vérifie que le parser lit bien les différentes catégories du dictionnaire.
        On vérifie qu'on trouve au moins un produit de chaque type.
        """
        # On récupère tous les faits 'Produit' chargés en mémoire
        tous_produits = [f['nom'] for f in self.engine.facts.values() if isinstance(f, Produit)]
        
        # Test Catégorie Sport
        self.assertTrue(any("Yoga" in p for p in tous_produits), "Erreur: Le Yoga (Sport) n'est pas chargé.")
        # Test Catégorie Herbe
        self.assertTrue(any("Millepertuis" in p for p in tous_produits), "Erreur: Le Millepertuis (Herbe) n'est pas chargé.")
        # Test Catégorie Complément
        self.assertTrue(any("Magnésium" in p for p in tous_produits), "Erreur: Le Magnésium (Complément) n'est pas chargé.")

    # ====================================================================
    # 2. INTEGRATION TESTS (Scénarios "Happy Path" - Ça marche ?)
    # ====================================================================

    def test_scenario_1_depression_simple(self):
        """
        SCÉNARIO 1 : Patient A (Dépressif simple)
        Attendu : Doit recevoir des solutions de plusieurs catégories (Chimie + Herbe).
        """
        recos, _ = self._lancer_moteur(
            symptomes=['Dépression'], 
            conditions=[]
        )
        
        # Vérification Holistique
        self.assertIn("5-HTP", recos, "Devrait recommander 5-HTP")
        self.assertIn("Millepertuis (St. John's Wort)", recos, "Devrait recommander Millepertuis")

    def test_scenario_4_insomnie_simple(self):
        """
        SCÉNARIO 4 : Patient D (Insomnie)
        Attendu : Approche holistique complète (Chimie + Sport).
        """
        recos, _ = self._lancer_moteur(
            symptomes=['Sommeil'], 
            conditions=[]
        )
        
        # On s'attend à voir du Yoga (Sport) ET de la Mélatonine (Chimie)
        self.assertIn("Mélatonine", recos)
        self.assertIn("Yoga Nidra (Méditation)", recos)

    # ====================================================================
    # 3. REGRESSION TESTS (Scénarios de Sécurité - Ça ne casse pas ?)
    # ====================================================================

    def test_scenario_2_interaction_pilule(self):
        """
        SCÉNARIO 2 : Patiente B (Sous Pilule)
        Attendu : Le Millepertuis doit être STRICTEMENT interdit.
        """
        recos, interdits = self._lancer_moteur(
            symptomes=['Dépression'], 
            conditions=['Contraceptifs oraux (Pilule)']
        )
        
        # Le 5-HTP est OK
        self.assertIn("5-HTP", recos)
        
        # Le Millepertuis est INTERDIT
        self.assertIn("Millepertuis (St. John's Wort)", interdits)
        self.assertNotIn("Millepertuis (St. John's Wort)", recos, "FAIL: Millepertuis recommandé avec la pilule !")

    def test_scenario_3_femme_enceinte(self):
        """
        SCÉNARIO 3 : Patiente C (Enceinte Fatiguée)
        Attendu : Filtrage massif. Seuls Magnésium et Yoga sont autorisés.
        """
        recos, interdits = self._lancer_moteur(
            symptomes=['Fatigue', 'Stress'], 
            conditions=['Grossesse']
        )
        
        # Ce qui est autorisé
        self.assertIn("Magnésium Bisglycinate", recos)
        self.assertIn("Yoga Nidra (Méditation)", recos)
        
        # Ce qui doit être bloqué (vérification multiple)
        produits_dangereux = ["Guarana", "5-HTP", "Millepertuis (St. John's Wort)"]
        for p in produits_dangereux:
            self.assertNotIn(p, recos, f"FAIL DE SÉCURITÉ: {p} a été recommandé à une femme enceinte.")

    def test_scenario_5_hypertension(self):
        """
        SCÉNARIO 5 : Patient E (Hypertendu)
        Attendu : Le Guarana (Stimulant) doit être bloqué.
        """
        recos, interdits = self._lancer_moteur(
            symptomes=['Fatigue'], 
            conditions=['Hypertension']
        )
        
        self.assertIn("Magnésium Bisglycinate", recos) # Alternative sûre
        self.assertNotIn("Guarana", recos, "FAIL: Guarana recommandé à un hypertendu.")

    def test_scenario_6_anticoagulants(self):
        """
        SCÉNARIO 6 : Patient F (Sous Anticoagulants)
        Attendu : Interactions croisées bloquées (Millepertuis + Mélatonine).
        """
        recos, interdits = self._lancer_moteur(
            symptomes=['Dépression', 'Sommeil'], 
            conditions=['Anticoagulants']
        )
        
        # Vérifications
        self.assertNotIn("Millepertuis (St. John's Wort)", recos)
        self.assertNotIn("Mélatonine", recos)
        self.assertIn("Yoga Nidra (Méditation)", recos) # Le sport reste autorisé

if __name__ == '__main__':
    # Lance tous les tests et affiche le rapport
    unittest.main()