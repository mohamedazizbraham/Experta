

# --- PATCH COMPATIBILITÉ PYTHON 3.10+ ---
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
#Experta utilise une vieille fonction de Python (collections.Mapping)
# qui a été supprimée dans Python 3.10.Ce patch "trompe" Experta en lui faisant
# croire que la vieille fonction existe toujours.
from experta import *
from database import CATALOGUE_PRODUITS, CONTRE_INDICATIONS

class Produit(Fact):
    pass

class ContreIndication(Fact):
    pass

class BesoinClient(Fact):
    pass

class ConditionClient(Fact):
    pass

class ProduitInterdit(Fact):
    pass

class Recommandation(Fact):
    pass

class MoteurRecommandation(KnowledgeEngine):
    
    @DefFacts()
    def chargement_initial(self):
        for p in CATALOGUE_PRODUITS:
            yield Produit(nom=p['nom'], cible=p['cible'])
            
        for c in CONTRE_INDICATIONS:
            yield ContreIndication(produit=c['produit'], condition=c['condition'])

    # Règle 1 : Sécurité (Inchangée)
    @Rule(
        ContreIndication(produit=MATCH.p, condition=MATCH.c),
        ConditionClient(condition=MATCH.c)
    )
    def detecter_danger(self, p, c):
        self.declare(ProduitInterdit(produit=p))

    # Règle 2 : Recommandation 
    @Rule(
        BesoinClient(symptome=MATCH.s),
        Produit(nom=MATCH.p, cible=MATCH.s), 
        NOT(ProduitInterdit(produit=MATCH.p))
    )
    def generer_recommandation(self, p, s):
        self.declare(Recommandation(nom=p, cible=s))