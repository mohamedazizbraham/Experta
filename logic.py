# logic.py

# --- PYTHON 3.10+ COMPATIBILITY PATCH ---
# Experta uses an old collection mapping that was removed in Python 3.10.
# This patch redirects the old path to the new one.
import collections
import collections.abc

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
# ----------------------------------------

from experta import *
from database import CATALOGUE_COMPLET
from typing import List, Dict, Tuple

# --- HEALTH CONDITION EXTRACTION (Clear & Reusable) ---

def extract_health_conditions_from_supplements() -> Dict[str, List[str]]:
    """
    Extract all health_condition_or_goal from supplement database entries.
    
    Returns:
        Dict[str, List[str]]: Mapping of product name to list of health conditions
        
    Example:
        {
            "Alpha-Lactalbumin": ["Santé du sommeil"],
            "5-HTP": ["Dépression", "Anxiété", "Sommeil"],
            ...
        }
    """
    product_conditions: Dict[str, List[str]] = {}
    
    # Iterate through all categories in the catalogue
    for category, product_list in CATALOGUE_COMPLET.items():
        for sheet in product_list:
            product_name = sheet.get('name', '').strip()
            
            if not product_name:
                continue
            
            conditions = []
            
            # Extract from 'database' list (contains efficacy data with health_condition_or_goal)
            if 'database' in sheet and isinstance(sheet['database'], list):
                for entry in sheet['database']:
                    health_condition = entry.get('health_condition_or_goal', '').strip()
                    if health_condition and health_condition not in conditions:
                        conditions.append(health_condition)
            
            # Store only if conditions were found
            if conditions:
                product_conditions[product_name] = conditions
    
    return product_conditions


def normalize_health_condition(condition: str) -> str:
    """
    Normalize a health condition by extracting the main keyword.
    
    Args:
        condition: Raw health condition string (e.g., "Santé du sommeil")
        
    Returns:
        str: Normalized condition (e.g., "sommeil")
        
    Examples:
        normalize_health_condition("Santé du sommeil") -> "sommeil"
        normalize_health_condition("Sommeil") -> "sommeil"
        normalize_health_condition("Santé cardiovasculaire générale") -> "cardiovasculaire"
    """
    # Stop words to remove (articles, prepositions, qualifiers)
    stop_words = {"santé", "de", "du", "de", "la", "le", "et", "ou", "bien-être", "générale", "général"}
    
    # Convert to lowercase and split
    words = condition.lower().split()
    
    # Filter out stop words
    filtered = [w for w in words if w not in stop_words and w]
    
    # Return the first significant word (usually the main condition)
    # We use first instead of last to get "cardiovasculaire" from "cardiovasculaire générale"
    return filtered[0] if filtered else condition.lower()


def match_symptoms_with_products(patient_symptoms: List[str]) -> Dict[str, Dict]:
    """
    Match patient symptoms with products that can treat them.
    This function performs exact matching between patient symptoms and product health conditions.
    
    Args:
        patient_symptoms: List of patient symptoms (e.g., ["Sommeil", "Fatigue"])
        
    Returns:
        Dict[str, Dict]: Dictionary of matched products with details
        {
            "Alpha-Lactalbumin": {
                "matched_symptoms": ["sommeil"],
                "raw_conditions": ["Santé du sommeil"],
                "score": 1
            },
            "5-HTP": {
                "matched_symptoms": ["dépression", "sommeil"],
                "raw_conditions": ["Dépression", "Anxiété", "Sommeil"],
                "score": 2
            }
        }
    """
    # Extract all health conditions from supplements
    product_conditions = extract_health_conditions_from_supplements()
    
    # Normalize patient symptoms (remove empty strings, convert to lowercase)
    normalized_symptoms = {normalize_health_condition(s) for s in patient_symptoms if s.strip()}
    
    matched_products: Dict[str, Dict] = {}
    
    # Iterate through each product and check if its conditions match patient symptoms
    for product_name, raw_conditions in product_conditions.items():
        
        # Normalize each condition and check for matches
        matched_symptoms = set()
        
        for raw_condition in raw_conditions:
            normalized_condition = normalize_health_condition(raw_condition)
            
            # Check if this normalized condition matches any patient symptom
            if normalized_condition in normalized_symptoms:
                matched_symptoms.add(normalized_condition)
        
        # Only include products that have at least one matching symptom
        if matched_symptoms:
            matched_products[product_name] = {
                "matched_symptoms": sorted(list(matched_symptoms)),
                "raw_conditions": raw_conditions,
                "score": len(matched_symptoms)  # Number of matched symptoms
            }
    
    # Sort by score (highest first) and then by product name
    sorted_products = dict(
        sorted(
            matched_products.items(),
            key=lambda x: (-x[1]["score"], x[0])
        )
    )
    
    return sorted_products


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
        # --- A. Extract & Load Health Conditions from Supplements ---
        # Use the dedicated function to extract all health conditions
        product_conditions = extract_health_conditions_from_supplements()
        
        for product_name, conditions in product_conditions.items():
            for condition in conditions:
                # Normalize the condition (e.g., "Santé du sommeil" -> "sommeil")
                normalized_condition = normalize_health_condition(condition)
                # Declare that this product treats this normalized condition
                yield Produit(nom=product_name, cible=normalized_condition)
        
        # --- B. Extract Contraindications (Safety Rules) ---
        # 1. Iterate over the main categories (Dictionary keys)
        for category, product_list in CATALOGUE_COMPLET.items():
            
            # 2. Iterate over the products inside each category list
            for sheet in product_list:
                product_name = sheet['name']
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