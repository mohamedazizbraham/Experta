# logic.py

# --- PYTHON 3.10+ COMPATIBILITY PATCH ---
# Experta uses an old collection mapping that was removed in Python 3.10.
# This patch redirects the old path to the new one.
import collections
import collections.abc
import re
import unicodedata

if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
# ----------------------------------------

from experta import *
from database import CATALOGUE_COMPLET, _is_risky_pregnancy_text, get_product_category_type
from typing import Any, Dict, List, Optional, Tuple


GRADE_SCORES = {
    "A": 4,
    "B": 3,
    "C": 2,
    "D": 1,
}

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
        condition: Raw health condition string (e.g., "Sante du sommeil")

    Returns:
        str: Normalized condition (e.g., "sommeil")

    Examples:
        normalize_health_condition("Sante du sommeil") -> "sommeil"
        normalize_health_condition("Sommeil") -> "sommeil"
        normalize_health_condition("Sante cardiovasculaire generale") -> "cardiovasculaire"
    """
    raw = condition or ""

    # Handle common mojibake seen in legacy data/docs, e.g. "Santé" -> "Santé".
    # Run up to 2 times to also recover double-encoded payloads.
    for _ in range(2):
        if not any(ch in raw for ch in ("Ã", "Â", "â")):
            break
        try:
            repaired = raw.encode("latin-1").decode("utf-8")
        except Exception:
            break
        if repaired == raw:
            break
        raw = repaired

    # Fold accents and punctuation so matching works with UI labels such as
    # "Ameliorer mon sommeil", "Reduire mon stress", etc.
    folded = unicodedata.normalize("NFKD", raw)
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    words = [w for w in re.split(r"[^a-z0-9]+", folded.lower()) if w]

    # Generic words to ignore:
    # - articles / glue words
    # - high-level action words often found in goal labels
    stop_words = {
        "sante", "de", "du", "la", "le", "les", "des", "et", "ou", "generale", "general",
        "mon", "ma", "mes", "notre", "nos",
        "ameliorer", "ameliore", "amelioration",
        "reduire", "diminuer", "gerer", "augmenter", "optimiser", "favoriser",
        "maintenir", "soutenir", "booster",
    }

    filtered = [w for w in words if w not in stop_words]

    # Keep first significant token to preserve prior behavior:
    # "sante cardiovasculaire generale" -> "cardiovasculaire".
    if filtered:
        return filtered[0]
    if words:
        return words[0]
    return ""


def normalize_grade(grade: str) -> str:
    """Normalize a grade to A/B/C/D, or return empty string when unknown."""
    grade_norm = (grade or "").strip().upper()
    return grade_norm if grade_norm in GRADE_SCORES else ""


def grade_to_score(grade: str) -> int:
    """Convert a grade to a numeric score used for ranking."""
    return GRADE_SCORES.get(normalize_grade(grade), 0)


def infer_grade_from_outcome_count(outcome_count: int) -> str:
    """Infer a deterministic grade when no explicit grade is present."""
    if outcome_count >= 6:
        return "A"
    if outcome_count >= 4:
        return "B"
    if outcome_count >= 2:
        return "C"
    return "D"


def _get_product_sheet(product_name: str) -> Optional[Dict[str, Any]]:
    product_name_norm = (product_name or "").strip().casefold()
    if not product_name_norm:
        return None

    for _category, product_list in CATALOGUE_COMPLET.items():
        for sheet in product_list:
            if (sheet.get("name") or "").strip().casefold() == product_name_norm:
                return sheet
    return None


def _is_nonempty_outcome(outcome: Dict[str, Any]) -> bool:
    if not isinstance(outcome, dict):
        return False

    for value in outcome.values():
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, (int, float)) and value > 0:
            return True
        if isinstance(value, list) and value:
            return True
        if isinstance(value, dict) and value:
            return True
    return False


def extract_relevant_database_entries(product_name: str, matched_conditions: List[str]) -> List[Dict[str, Any]]:
    """Return the product database entries relevant to the matched conditions."""
    sheet = _get_product_sheet(product_name)
    if not sheet:
        return []

    matched_condition_set = {
        normalize_health_condition(condition)
        for condition in matched_conditions
        if (condition or "").strip()
    }
    if not matched_condition_set:
        return []

    relevant_entries: List[Dict[str, Any]] = []
    for entry in sheet.get("database", []) or []:
        if not isinstance(entry, dict):
            continue
        health_condition = normalize_health_condition(entry.get("health_condition_or_goal", ""))
        if health_condition in matched_condition_set:
            relevant_entries.append(entry)
    return relevant_entries


def extract_relevant_outcomes(product_name: str, matched_conditions: List[str]) -> List[Dict[str, Any]]:
    """Return all outcomes attached to the matched database entries for a product."""
    relevant_outcomes: List[Dict[str, Any]] = []
    for entry in extract_relevant_database_entries(product_name, matched_conditions):
        for outcome in entry.get("outcomes", []) or []:
            if isinstance(outcome, dict):
                relevant_outcomes.append(outcome)
    return relevant_outcomes


def calculate_recommendation_grade(product_name: str, matched_conditions: List[str]) -> Dict[str, Any]:
    """
    Compute ranking grade metadata for a product using only currently matched conditions.

    Explicit grades win. If none exists on relevant outcomes, infer a grade from the
    number of relevant non-empty outcomes.
    """
    relevant_entries = extract_relevant_database_entries(product_name, matched_conditions)
    if not relevant_entries:
        return {
            "grade": "",
            "grade_score": 0,
            "grade_source": "none",
        }

    relevant_outcomes = extract_relevant_outcomes(product_name, matched_conditions)
    explicit_grades = [
        normalize_grade(outcome.get("grade", ""))
        for outcome in relevant_outcomes
        if normalize_grade(outcome.get("grade", ""))
    ]

    if explicit_grades:
        best_grade = max(explicit_grades, key=grade_to_score)
        return {
            "grade": best_grade,
            "grade_score": grade_to_score(best_grade),
            "grade_source": "explicit",
        }

    nonempty_outcome_count = sum(1 for outcome in relevant_outcomes if _is_nonempty_outcome(outcome))
    inferred_grade = infer_grade_from_outcome_count(nonempty_outcome_count)
    return {
        "grade": inferred_grade,
        "grade_score": grade_to_score(inferred_grade),
        "grade_source": "inferred",
    }


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
                "score": 1,
                "category_type": "recommendation"
            },
            "5-HTP": {
                "matched_symptoms": ["dépression", "sommeil"],
                "raw_conditions": ["Dépression", "Anxiété", "Sommeil"],
                "score": 2,
                "category_type": "recommendation"
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
            category_type = get_product_category_type(product_name) or "recommendation"
            matched_products[product_name] = {
                "matched_symptoms": sorted(list(matched_symptoms)),
                "raw_conditions": raw_conditions,
                "score": len(matched_symptoms),  # Number of matched symptoms
                "category_type": category_type
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
                        combined = f"{condition_text} {safety_info}"
                        is_risky = _is_risky_pregnancy_text(combined)
                        
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

