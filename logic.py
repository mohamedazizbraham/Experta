# logic.py

# --- PATCH COMPATIBILITÉ PYTHON 3.10+ ---
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
# ----------------------------------------

from experta import *
from database import CATALOGUE_COMPLET

# --- DÉFINITION DES FAITS (Le vocabulaire du moteur) ---

class Produit(Fact):
    """Fait : Un produit et ce qu'il traite (ex: 5-HTP -> Dépression)"""
    pass

class ContreIndication(Fact):
    """Fait : Une restriction de sécurité (ex: 5-HTP -> Grossesse)"""
    pass

class BesoinClient(Fact):
    """Fait : Ce que l'utilisateur veut soigner (Symptôme)"""
    pass

class ConditionClient(Fact):
    """Fait : L'état de santé de l'utilisateur (Grossesse, Médicaments...)"""
    pass

class ProduitInterdit(Fact):
    """Fait : Produit marqué comme dangereux pour cet utilisateur spécifique"""
    pass

class Recommandation(Fact):
    """Fait : Le résultat final validé"""
    pass

# --- LE MOTEUR D'INFÉRENCE ---

class MoteurRecommandation(KnowledgeEngine):
    
    @DefFacts()
    def chargement_initial(self):
        """
        CHARGEUR INTELLIGENT :
        Il lit le CATALOGUE_COMPLET (format JSON/Document) et extrait uniquement
        les informations nécessaires pour le raisonnement logique.
        """
        for fiche in CATALOGUE_COMPLET:
            nom_produit = fiche['name']
            
            # 1. Extraction des Cibles (Indication thérapeutique)
            # On regarde dans la liste "database" du JSON qui contient les preuves d'efficacité
            if 'database' in fiche:
                for entry in fiche['database']:
                    # On récupère la condition (ex: "Dépression", "Obésité")
                    # .lower() permet de rendre la recherche insensible à la casse
                    cible = entry.get('health_condition_or_goal', '').strip().lower()
                    if cible:
                        yield Produit(nom=nom_produit, cible=cible)
            
            # 2. Extraction des Contre-indications (Sécurité)
            # On regarde dans l'objet "safety"
            safety = fiche.get('safety', {})
            
            # A. Traitement des cas Grossesse et Allaitement
            # Dans le JSON, c'est sous "pregnancy_lactation"
            if 'pregnancy_lactation' in safety:
                for precaution in safety['pregnancy_lactation']:
                    condition_text = precaution.get('condition', '').lower()
                    safety_info = precaution.get('safety_information', '').lower()
                    
                    # On cherche des mots clés comme "éviter" ou "risque"
                    is_risky = "éviter" in condition_text or "éviter" in safety_info
                    
                    if "grossesse" in condition_text and is_risky:
                        yield ContreIndication(produit=nom_produit, condition="grossesse")
                    
                    if "allaitement" in condition_text and is_risky:
                        yield ContreIndication(produit=nom_produit, condition="allaitement")

            # B. Traitement des Interactions Médicamenteuses
            # Dans le JSON, c'est sous "interactions"
            if 'interactions' in safety:
                for interaction in safety['interactions']:
                    agent = interaction.get('agent', '').strip().lower()
                    # Si un agent est listé (ex: "médicaments sérotoninergiques"), c'est une contre-indication
                    if agent:
                        yield ContreIndication(produit=nom_produit, condition=agent)

    # --- RÈGLES MÉTIER ---

    # Règle 1 : SÉCURITÉ (Bloquer les produits dangereux)
    # Si le produit a une contre-indication X et que le client a la condition X -> INTERDIT
    @Rule(
        ContreIndication(produit=MATCH.p, condition=MATCH.c),
        ConditionClient(condition=MATCH.c)
    )
    def detecter_danger(self, p, c):
        # On déclare le fait interne "ProduitInterdit"
        self.declare(ProduitInterdit(produit=p))
        # (Optionnel) On pourrait printer ici pour le debug :
        # print(f"   [SÉCURITÉ] Exclusion de {p} car incompatibilité avec : {c}")

    # Règle 2 : RECOMMANDATION (Valider les produits sûrs)
    # Si le client a un besoin S, qu'un produit P traite S, et que P n'est PAS interdit -> RECOMMANDER
    @Rule(
        BesoinClient(symptome=MATCH.s),
        Produit(nom=MATCH.p, cible=MATCH.s),
        NOT(ProduitInterdit(produit=MATCH.p))
    )
    def generer_recommandation(self, p, s):
        self.declare(Recommandation(nom=p, cible=s))