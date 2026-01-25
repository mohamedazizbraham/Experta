"""app.py

Interface console de démonstration.

Compatible avec `database.py` qui charge automatiquement les JSON depuis `data/`.
"""

from logic import MoteurRecommandation, BesoinClient, ConditionClient, Recommandation
from database import CATALOGUE_COMPLET


def _norm(s: str) -> str:
    return (s or "").strip().casefold()


_CATEGORY_LABELS = {
    "complement_alimentaire": "Compléments alimentaires",
    "sport_et_pratique": "Pratiques / Activités",
    "regime_alimentaire": "Régimes / Diètes",
}

def afficher_details_produit(nom_produit):
    """
    Fonction utilitaire pour retrouver la fiche JSON complète
    à partir du nom et afficher les détails.
    Adaptée pour parcourir le dictionnaire de catégories.
    """
    fiche_trouvee = None
    categorie_trouvee = ""
    nom_norm = _norm(nom_produit)
    
    # On parcourt chaque clé (catégorie) et valeur (liste de produits) du dictionnaire
    for cat, liste_produits in CATALOGUE_COMPLET.items():
        for item in liste_produits:
            if _norm(item.get("name", "")) == nom_norm:
                fiche_trouvee = item
                categorie_trouvee = cat
                break
        if fiche_trouvee:
            break
    # -------------------------------------------------------------
    
    if fiche_trouvee:
        # On affiche aussi la catégorie pour info
        label_cat = _CATEGORY_LABELS.get(categorie_trouvee, categorie_trouvee.replace('_', ' ').title())
        print(f"\n   [DÉTAILS FICHE : {fiche_trouvee.get('name', nom_produit)}] ({label_cat})")
        
        # On coupe la description pour ne pas encombrer la console
        desc = fiche_trouvee.get('description', '')
        print(f"   Description : {desc[:150]}..." if len(desc) > 150 else f"   Description : {desc}")
        
        # Affichage Dosage / Pratique selon le contexte
        if "sport" in categorie_trouvee:
            label_dosage = "Pratique"
        elif "regime" in categorie_trouvee:
            label_dosage = "Régime"
        else:
            label_dosage = "Dosage"
        print(f"   {label_dosage} : {fiche_trouvee.get('dosage', 'Non spécifié') or 'Non spécifié'}")
        
        # Affichage des alertes interactions s'il y en a dans la section safety
        interactions = fiche_trouvee.get('safety', {}).get('interactions', [])
        # On récupère les noms des agents qui ont une sévérité notée ou qui existent
        agents = [i.get('agent') for i in interactions if i.get('agent')]
        
        if agents:
            print(f"   ⚠️ Interactions connues : {', '.join(agents)}")

def lancer_diagnostic(nom_user, symptomes, conditions_medicales=None):
    if conditions_medicales is None:
        conditions_medicales = []
    engine = MoteurRecommandation()
    engine.reset() # Charge les données JSON converties en faits par logic.py
    
    # Injection des faits utilisateur
    # On met les symptômes en minuscule pour correspondre au parser de logic.py
    for s in symptomes:
        engine.declare(BesoinClient(symptome=(s or "").lower()))
        
    for c in conditions_medicales:
        engine.declare(ConditionClient(condition=(c or "").lower()))
        
    engine.run()
    
    # Affichage des résultats
    print(f"\n{'='*60}")
    print(f"PATIENT : {nom_user.upper()}")
    print(f"Besoin : {symptomes}")
    if conditions_medicales:
        print(f"/!\\ Conditions Médicales : {conditions_medicales}")
    print(f"{'-'*60}")
    
    facts_list = list(engine.facts.values())
    found = False
    deja_affiche = set()

    for fait in facts_list:
        if isinstance(fait, Recommandation):
            unique_key = fait['nom']
            # Petit système pour ne pas afficher 2 fois le même produit si il répond à 2 besoins
            if unique_key not in deja_affiche:
                print(f"✅ RECOMMANDATION : {fait['nom']} (Cible : {fait['cible']})")
                afficher_details_produit(fait['nom'])
                deja_affiche.add(unique_key)
                found = True
    
    if not found:
        print("❌ Aucune recommandation trouvée (ou tous les produits compatibles sont bloqués par sécurité).")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # --- BANC D'ESSAI (TESTS COMPLETS) ---
    # NB: Les produits disponibles dépendent des JSON présents dans `data/`.

    lancer_diagnostic(
        "Patient A (Dépressif simple)",
        symptomes=["Dépression"],
    )

    lancer_diagnostic(
        "Patiente B (Sous Pilule)",
        symptomes=["Dépression"],
        conditions_medicales=["Contraceptifs oraux (Pilule)"],
    )

    lancer_diagnostic(
        "Patiente C (Enceinte Fatiguée)",
        symptomes=["Fatigue", "Stress"],
        conditions_medicales=["Grossesse"],
    )

    lancer_diagnostic(
        "Patient D (Sommeil)",
        symptomes=["Sommeil"],
    )

    lancer_diagnostic(
        "Patient E (Hypertendu)",
        symptomes=["Fatigue"],
        conditions_medicales=["Hypertension"],
    )

    lancer_diagnostic(
        "Patient F (Sous Anticoagulants)",
        symptomes=["Dépression", "Sommeil"],
        conditions_medicales=["Anticoagulants"],
    )