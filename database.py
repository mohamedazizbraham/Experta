# database.py

CATALOGUE_COMPLET = {
    "complement_alimentaire": [
        # --- 5-HTP ---
        {
            "name": "5-HTP",
            "description": "5-HTP est le précurseur de la sérotonine, un neurotransmetteur impliqué dans la régulation de nombreux processus corporels tels que l'humeur, le sommeil et l'appétit.",
            "overview": [
                {"question": "Qu’est-ce que le 5-HTP?", "answer": "Acide aminé précurseur de la sérotonine."},
                {"question": "Bénéfices?", "answer": "Augmente la sérotonine (humeur, sommeil)."}
            ],
            "dosage": "200mg à 300mg par jour.",
            "safety": {
                "summary": ["Bien toléré à faible dose."],
                "side_effects": {"summary": "Nausées possibles.", "table": [{"effect": "Nausée", "details": "Voie orale"}]},
                "interactions": [
                    {"agent": "Médicaments sérotoninergiques", "severity": "Inconnu"},
                    {"agent": "Antidépresseurs", "severity": "Majeur"}
                ],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: éviter", "safety_information": "Évitement justifié."},
                    {"condition": "Allaitement: éviter", "safety_information": "Évitement justifié."}
                ],
                "precautions": [{"population_condition": "Affections gastro-intestinales", "details": "Prudence."}],
                "anti_doping": {"label": "Non interdit", "text": "Autorisé."}
            },
            "database": [
                {"health_condition_or_goal": "Dépression", "outcomes": [{"outcome": "Symptômes", "grade": "B"}]},
                {"health_condition_or_goal": "Obésité", "outcomes": [{"outcome": "Appétit", "grade": "B"}]},
                {"health_condition_or_goal": "Sommeil", "outcomes": [{"outcome": "Temps d'endormissement", "grade": "C"}]}
            ],
            "faq": [], "references": [], "database_references": []
        },
        # --- MAGNESIUM ---
        {
            "name": "Magnésium Bisglycinate",
            "description": "Forme chélatée de magnésium liée à la glycine, offrant une biodisponibilité supérieure.",
            "overview": [{"question": "Bénéfices?", "answer": "Réduit fatigue et crampes."}],
            "dosage": "300mg à 400mg par jour.",
            "safety": {
                "summary": ["Sûr pour la plupart des adultes."],
                "interactions": [
                    {"agent": "Antibiotiques", "severity": "Modéré"},
                    {"agent": "Bisphosphonates", "severity": "Modéré"}
                ],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: autorisé", "safety_information": "Souvent recommandé."},
                    {"condition": "Allaitement: autorisé", "safety_information": "Compatible."}
                ],
                "precautions": [{"population_condition": "Insuffisance rénale sévère", "details": "Contre-indiqué."}]
            },
            "database": [
                {"health_condition_or_goal": "Stress", "outcomes": [{"outcome": "Cortisol", "grade": "A"}]},
                {"health_condition_or_goal": "Fatigue", "outcomes": [{"outcome": "Énergie", "grade": "A"}]},
                {"health_condition_or_goal": "Sommeil", "outcomes": [{"outcome": "Qualité", "grade": "B"}]},
                {"health_condition_or_goal": "Crampes musculaires", "outcomes": [{"outcome": "Fréquence", "grade": "B"}]}
            ],
            "faq": [], "references": [], "database_references": []
        },
        # --- MELATONINE (CORRIGÉE) ---
        {
            "name": "Mélatonine",
            "description": "Hormone naturelle du sommeil.",
            "overview": [{"question": "Addictif?", "answer": "Non."}],
            "dosage": "1mg à 2mg avant le coucher.",
            "safety": {
                "summary": ["Somnolence diurne possible."],
                "interactions": [
                    # C'EST CETTE LIGNE QUI MANQUAIT :
                    {"agent": "Anticoagulants", "severity": "Modéré", "effect": "Risque théorique de saignement"},
                    {"agent": "Sédatifs", "severity": "Modéré"}
                ],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: éviter", "safety_information": "Manque de données."},
                    {"condition": "Allaitement: éviter", "safety_information": "Passe dans le lait."}
                ],
                "precautions": [{"population_condition": "Conduite de véhicules", "details": "Somnolence."}]
            },
            "database": [
                {"health_condition_or_goal": "Sommeil", "outcomes": [{"outcome": "Endormissement", "grade": "A"}]},
                {"health_condition_or_goal": "Jet lag", "outcomes": [{"outcome": "Symptômes", "grade": "A"}]}
            ],
            "faq": [], "references": [], "database_references": []
        }
    ],

    "herbe_naturelle": [
        # --- MILLEPERTUIS ---
        {
            "name": "Millepertuis (St. John's Wort)",
            "description": "Plante médicinale pour les troubles de l'humeur.",
            "overview": [{"question": "Action?", "answer": "Inhibe recapture sérotonine."}],
            "dosage": "300mg 3 fois par jour.",
            "safety": {
                "summary": ["Attention : Puissant inducteur enzymatique."],
                "interactions": [
                    {"agent": "Contraceptifs oraux (Pilule)", "severity": "Majeur"},
                    {"agent": "Anticoagulants", "severity": "Majeur"},
                    {"agent": "Antidépresseurs", "severity": "Majeur"},
                    {"agent": "Immunosuppresseurs", "severity": "Majeur"}
                ],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: éviter", "safety_information": "Risque interactions."},
                    {"condition": "Allaitement: éviter", "safety_information": "Risque."}
                ],
                "precautions": [{"population_condition": "Troubles bipolaires", "details": "Risque manie."}]
            },
            "database": [
                {"health_condition_or_goal": "Dépression", "outcomes": [{"outcome": "Humeur", "grade": "A"}]},
                {"health_condition_or_goal": "Anxiété", "outcomes": [{"outcome": "Symptômes", "grade": "B"}]}
            ],
            "faq": [], "references": [], "database_references": []
        },
        # --- GUARANA ---
        {
            "name": "Guarana",
            "description": "Graine riche en caféine à libération lente.",
            "overview": [{"question": "Différence café?", "answer": "Diffusion lente."}],
            "dosage": "Ne pas dépasser 400mg caféine/jour.",
            "safety": {
                "summary": ["Stimulant."],
                "interactions": [
                    {"agent": "Stimulants", "severity": "Modéré"},
                    {"agent": "Éphédrine", "severity": "Majeur"}
                ],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: éviter", "safety_information": "Limiter caféine."},
                    {"condition": "Allaitement: à limiter", "safety_information": "Excitant."}
                ],
                "precautions": [
                    {"population_condition": "Hypertension", "details": "Augmente tension."},
                    {"population_condition": "Troubles cardiaques", "details": "Éviter."}
                ]
            },
            "database": [
                {"health_condition_or_goal": "Fatigue", "outcomes": [{"outcome": "Vigilance", "grade": "A"}]},
                {"health_condition_or_goal": "Perte de poids", "outcomes": [{"outcome": "Métabolisme", "grade": "B"}]},
                {"health_condition_or_goal": "Concentration", "outcomes": [{"outcome": "Focus", "grade": "B"}]}
            ],
            "faq": [], "references": [], "database_references": []
        }
    ],

    "sport_et_pratique": [
        # --- YOGA ---
        {
            "name": "Yoga Nidra (Méditation)",
            "description": "Technique de relaxation profonde aussi appelée 'sommeil yogique'. Idéal pour réduire le stress sans ingestion de produits.",
            "overview": [{"question": "C'est quoi?", "answer": "Une méditation guidée allongée."}],
            "dosage": "Séances de 20 à 30 minutes, 1 fois par jour.",
            "safety": {
                "summary": ["Aucun effet secondaire connu."],
                "interactions": [],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: autorisé", "safety_information": "Excellent."},
                    {"condition": "Allaitement: autorisé", "safety_information": "Excellent."}
                ],
                "precautions": []
            },
            "database": [
                {"health_condition_or_goal": "Stress", "outcomes": [{"outcome": "Relaxation", "grade": "A"}]},
                {"health_condition_or_goal": "Sommeil", "outcomes": [{"outcome": "Qualité", "grade": "A"}]},
                {"health_condition_or_goal": "Anxiété", "outcomes": [{"outcome": "Apaisement", "grade": "B"}]}
            ],
            "faq": [], "references": [], "database_references": []
        }
    ]
}