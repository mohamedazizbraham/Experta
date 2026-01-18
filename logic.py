# logic.py

# --- PYTHON 3.10+ COMPATIBILITY PATCH ---
# Experta uses an old collection mapping that was removed in Python 3.10.
# This patch redirects the old path to the new one.
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
# ----------------------------------------

from experta import *
from database import CATALOGUE_COMPLET

# --- FACTS DEFINITION (The Engine's Vocabulary) ---

class Produit(Fact):
    """Fact: Represents a product and what condition it treats."""
    pass

class ContreIndication(Fact):
    """Fact: Represents a safety restriction (e.g., 5-HTP is bad for Pregnancy)."""
    pass

class BesoinClient(Fact):
    """Fact: Represents the symptom or need the user wants to address."""
    pass

class ConditionClient(Fact):
    """Fact: Represents the user's medical status (e.g., Pregnancy, Medication)."""
    pass

class ProduitInterdit(Fact):
    """Fact: Internal marker for a product deemed dangerous for the specific user."""
    pass

class Recommandation(Fact):
    """Fact: The final validated result to be displayed."""
    pass

# --- INFERENCE ENGINE ---

class MoteurRecommandation(KnowledgeEngine):
    
    @DefFacts()
    def initial_loading(self):
        """
        SMART LOADER (Category Dictionary Compatible):
        This function runs at startup. It iterates through the categories 
        (Supplements, Herbs, Sport...) and then the products to extract 
        logical rules (Targets & Safety) from the JSON structure.
        """
        # 1. Iterate over the main categories (Dictionary keys)
        for category, product_list in CATALOGUE_COMPLET.items():
            
            # 2. Iterate over the products inside each category list
            for sheet in product_list:
                product_name = sheet['name']
                
                # --- A. Extract Targets (Therapeutic Indications) ---
                # We look into the 'database' list which contains efficacy data
                if 'database' in sheet:
                    for entry in sheet['database']:
                        target = entry.get('health_condition_or_goal', '').strip().lower()
                        if target:
                            # Declare that this product treats this target
                            yield Produit(nom=product_name, cible=target)
                
                # --- B. Extract Contraindications (Safety Rules) ---
                safety = sheet.get('safety', {})
                
                # 1. Pregnancy and Breastfeeding logic
                if 'pregnancy_lactation' in safety:
                    for precaution in safety['pregnancy_lactation']:
                        condition_text = precaution.get('condition', '').lower()
                        safety_info = precaution.get('safety_information', '').lower()
                        
                        # Detect warning keywords in French (as data is in French)
                        # We look for "éviter" (avoid) or "limiter" (limit)
                        is_risky = "éviter" in condition_text or "éviter" in safety_info or "limiter" in safety_info
                        
                        if "grossesse" in condition_text and is_risky:
                            yield ContreIndication(produit=product_name, condition="grossesse")
                        
                        if "allaitement" in condition_text and is_risky:
                            yield ContreIndication(produit=product_name, condition="allaitement")

                # 2. Drug Interactions logic
                if 'interactions' in safety:
                    for interaction in safety['interactions']:
                        agent = interaction.get('agent', '').strip().lower()
                        if agent:
                            # Create a restriction for this drug/agent
                            yield ContreIndication(produit=product_name, condition=agent)

                # 3. Specific Precautions (e.g., Hypertension, Driving)
                if 'precautions' in safety:
                    for precaution in safety['precautions']:
                        condition_pop = precaution.get('population_condition', '').strip().lower()
                        if condition_pop:
                             yield ContreIndication(produit=product_name, condition=condition_pop)

    # --- BUSINESS RULES ---

    # Rule 1: SAFETY (Block dangerous products)
    # Logic: IF Product has Contraindication 'C' AND User has Condition 'C' -> FORBIDDEN
    @Rule(
        ContreIndication(produit=MATCH.p, condition=MATCH.c),
        ConditionClient(condition=MATCH.c)
    )
    def detect_danger(self, p, c):
        # We declare an internal fact "ProduitInterdit"
        self.declare(ProduitInterdit(produit=p))
        # Optional: Print for debugging purposes
        # print(f"   [SAFETY] Exclusion of {p} due to incompatibility with: {c}")

    # Rule 2: RECOMMENDATION (Validate safe products)
    # Logic: IF User needs 'S', Product 'P' treats 'S', AND 'P' is NOT Forbidden -> RECOMMEND
    @Rule(
        BesoinClient(symptome=MATCH.s),
        Produit(nom=MATCH.p, cible=MATCH.s),
        NOT(ProduitInterdit(produit=MATCH.p))
    )
    def generate_recommendation(self, p, s):
        # We declare the final recommendation
        self.declare(Recommandation(nom=p, cible=s))