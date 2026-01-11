# app.py
from logic import MoteurRecommandation, BesoinClient, ConditionClient, Recommandation
from database import CATALOGUE_COMPLET

def afficher_details_produit(nom_produit):
    """
    Fonction utilitaire pour retrouver la fiche JSON complète
    à partir du nom et afficher les détails.
    """
    # Recherche du dictionnaire correspondant dans le catalogue
    fiche = next((item for item in CATALOGUE_COMPLET if item["name"] == nom_produit), None)
    
    if fiche:
        print(f"\n   [DÉTAILS FICHE : {nom_produit}]")
        # On coupe la description pour ne pas encombrer la console
        desc = fiche.get('description', '')
        print(f"   Description : {desc[:150]}..." if len(desc) > 150 else f"   Description : {desc}")
        print(f"   Dosage : {fiche.get('dosage', 'Non spécifié')}")
        
        # Affichage des alertes interactions s'il y en a dans la section safety
        interactions = fiche.get('safety', {}).get('interactions', [])
        # On récupère les noms des agents qui ont une sévérité notée ou qui existent
        agents = [i['agent'] for i in interactions if i.get('agent')]
        
        if agents:
            print(f"   ⚠️ Interactions connues : {', '.join(agents)}")

def lancer_diagnostic(nom_user, symptomes, conditions_medicales=[]):
    engine = MoteurRecommandation()
    engine.reset() # Charge les données JSON converties en faits
    
    # Injection des faits utilisateur
    # On met les symptômes en minuscule pour correspondre au parser de logic.py
    for s in symptomes:
        engine.declare(BesoinClient(symptome=s.lower()))
        
    for c in conditions_medicales:
        engine.declare(ConditionClient(condition=c.lower()))
        
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

# --- BANC D'ESSAI (TESTS COMPLETS) ---

# 1. Test Dépression SIMPLE
# Attendu : 5-HTP et Millepertuis (car très efficaces tous les deux)
lancer_diagnostic("Patient A (Dépressif simple)", 
                  symptomes=['Dépression'])

# 2. Test Dépression sous PILULE CONTRACEPTIVE
# Attendu : 5-HTP uniquement. 
# Le Millepertuis doit être BLOQUÉ (Interaction majeure avec la pilule).
lancer_diagnostic("Patiente B (Sous Pilule)", 
                  symptomes=['Dépression'], 
                  conditions_medicales=['Contraceptifs oraux (Pilule)'])

# 3. Test Fatigue & Stress (Femme Enceinte)
# Attendu : Magnésium Bisglycinate uniquement.
# Guarana (Caféine) -> BLOQUÉ (Grossesse).
# 5-HTP / Millepertuis -> BLOQUÉS (Grossesse).
lancer_diagnostic("Patiente C (Enceinte Fatiguée)", 
                  symptomes=['Fatigue', 'Stress'], 
                  conditions_medicales=['Grossesse'])

# 4. Test Sommeil (Insomnie simple)
# Attendu : Mélatonine, Magnésium Bisglycinate (aide au sommeil), 5-HTP (précurseur).
lancer_diagnostic("Patient D (Insomnie)", 
                  symptomes=['Sommeil'])

# 5. Test Hypertension + Fatigue
# Attendu : Magnésium (OK).
# Guarana -> BLOQUÉ (Hypertension).
lancer_diagnostic("Patient E (Hypertendu)", 
                  symptomes=['Fatigue'], 
                  conditions_medicales=['Hypertension'])

# 6. Test Interactions complexes (Anticoagulants)
# Attendu : Magnésium (OK).
# Millepertuis -> BLOQUÉ (Risque thrombose).
# Mélatonine -> BLOQUÉ (Risque saignement théorique - selon database).
lancer_diagnostic("Patient F (Sous Anticoagulants)", 
                  symptomes=['Dépression', 'Sommeil'], 
                  conditions_medicales=['Anticoagulants'])