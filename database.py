# database.py

CATALOGUE_PRODUITS = [
    # --- ENERGIE & IMMUNITÉ ---
    {"nom": "Vitamine C Acerola", "cible": "fatigue"},
    {"nom": "Vitamine C Acerola", "cible": "immunite"},
    {"nom": "Ginseng Rouge", "cible": "fatigue"},
    {"nom": "Ginseng Rouge", "cible": "libido"},
    {"nom": "Guarana", "cible": "fatigue"},
    {"nom": "Gelée Royale", "cible": "fatigue"},
    {"nom": "Spiruline", "cible": "carence"},
    
    # --- STRESS & SOMMEIL ---
    {"nom": "Magnesium Bisglycinate", "cible": "stress"},
    {"nom": "Magnesium Bisglycinate", "cible": "fatigue"},
    {"nom": "Melatonine Spray", "cible": "sommeil"},
    {"nom": "Valeriane Bio", "cible": "stress"},
    {"nom": "Valeriane Bio", "cible": "sommeil"},
    {"nom": "Ashwagandha", "cible": "stress"},
    
    # --- DIGESTION ---
    {"nom": "Charbon Actif", "cible": "ballonnement"},
    {"nom": "Probiotiques Complets", "cible": "digestion"},
    {"nom": "Probiotiques Complets", "cible": "immunite"},
    
    # --- ARTICULATIONS & OS ---
    {"nom": "Curcuma Piperine", "cible": "articulation"},
    {"nom": "Collagene Marin", "cible": "articulation"},
    {"nom": "Collagene Marin", "cible": "peau"},
    {"nom": "Vitamine D3", "cible": "os"},
    {"nom": "Vitamine D3", "cible": "immunite"},
]

# Les contre-indications restent identiques
CONTRE_INDICATIONS = [
    {"produit": "Melatonine Spray", "condition": "grossesse"},
    {"produit": "Ginseng Rouge", "condition": "grossesse"},
    {"produit": "Guarana", "condition": "grossesse"},
    {"produit": "Ashwagandha", "condition": "grossesse"},
    {"produit": "Guarana", "condition": "hypertension"},
    {"produit": "Ginseng Rouge", "condition": "hypertension"},
    {"produit": "Curcuma Piperine", "condition": "anticoagulant"},
    {"produit": "Ginseng Rouge", "condition": "anticoagulant"},
    {"produit": "Gelée Royale", "condition": "diabete"},
]