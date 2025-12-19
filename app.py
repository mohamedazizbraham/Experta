
from logic import MoteurRecommandation, BesoinClient, ConditionClient, Recommandation

def lancer_diagnostic(nom_user, symptomes, conditions_medicales=[]):
    engine = MoteurRecommandation()
    engine.reset()
    
    # Injection des faits
    for s in symptomes:
        engine.declare(BesoinClient(symptome=s))
    for c in conditions_medicales:
        engine.declare(ConditionClient(condition=c))
        
    engine.run()
    
    # Affichage
    facts_list = list(engine.facts.values())
    
    print(f"\n--- RECOMMANDATION POUR : {nom_user.upper()} ---")
    print(f"Profil : {symptomes}")
    if conditions_medicales:
        print(f"/!\\ Prise en compte conditions : {conditions_medicales}")
    print("-" * 50)
    
    found = False
    recommandations_uniques = set()

    for fait in facts_list:
        if isinstance(fait, Recommandation):
            item_str = f"• {fait['nom']} (Cible : {fait['cible']})"
            
            if item_str not in recommandations_uniques:
                recommandations_uniques.add(item_str)
                print(item_str)
                found = True
    
    if not found:
        print("Aucun produit ne correspond à vos critères de sécurité.")
    
    print("-" * 50)

# --- BANC D'ESSAI ---

lancer_diagnostic("L'Étudiant", 
                  symptomes=['stress', 'fatigue'], 
                  conditions_medicales=[])

lancer_diagnostic("Femme Enceinte", 
                  symptomes=['fatigue', 'sommeil', 'stress'], 
                  conditions_medicales=['grossesse'])

lancer_diagnostic("Senior Hypertendu", 
                  symptomes=['articulation', 'fatigue'], 
                  conditions_medicales=['hypertension'])

lancer_diagnostic("Patient Cardiaque", 
                  symptomes=['immunite', 'articulation'], 
                  conditions_medicales=['anticoagulant'])