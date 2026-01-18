# database.py

CATALOGUE_COMPLET = {
    "complement_alimentaire": [
        # --- 5-HTP ---
        {
            "name": "5-HTP",
            "description": "5-HTP est le précurseur de la sérotonine, un neurotransmetteur impliqué dans la régulation de nombreux processus corporels tels que l'humeur, le sommeil et l'appétit.",
            "overview": [
                {
                    "question": "Qu’est-ce que le 5-HTP?",
                    "answer": "5-HTP est un acide aminé et un précurseur du neurotransmetteur sérotonine..."
                },
                {
                    "question": "Quels sont les principaux bénéfices du 5-HTP?",
                    "answer": "5-HTP est très fiable pour augmenter les niveaux de sérotonine..."
                },
                {
                    "question": "Quels sont les principaux inconvénients du 5-HTP?",
                    "answer": "5-HTP peut provoquer des effets secondaires légers..."
                },
                {
                    "question": "Comment le 5-HTP agit-il?",
                    "answer": "5-HTP agit comme précurseur direct du neurotransmetteur sérotonine..."
                }
            ],
            "dosage": "200mg à 300mg par jour.",
            "safety": {
                "summary": ["La prise de 100mg ou moins semble bien tolérée."],
                "side_effects": {
                    "summary": "Effets gastro-intestinaux possibles.",
                    "table": [{"effect": "Nausée", "details": "Voie orale, 200-300mg."}]
                },
                "interactions": [
                    {"agent": "Médicaments sérotoninergiques", "severity": "Inconnu"},
                    {"agent": "Carbidopa", "severity": ""},
                    {"agent": "Suppléments sérotoninergiques", "severity": ""}
                ],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: éviter", "safety_information": "Évitement justifié."},
                    {"condition": "Allaitement: éviter", "safety_information": "Évitement justifié."}
                ],
                "precautions": [{"population_condition": "Affections gastro-intestinales", "details": "Prudence."}],
                "anti_doping": {"label": "Non interdit", "text": "Autorisé."}
            },
            "database": [
                {"health_condition_or_goal": "Dépression", "outcomes": [{"outcome": "Symptômes", "grade": "B", "effect": "Amélioration"}]},
                {"health_condition_or_goal": "Obésité", "outcomes": [{"outcome": "Appétit", "grade": "B", "effect": "Diminution"}]},
                {"health_condition_or_goal": "Terreurs nocturnes", "outcomes": [{"outcome": "Fréquence", "grade": "", "effect": ""}]},
                {"health_condition_or_goal": "Diabète de type 2", "outcomes": [{"outcome": "Appétit", "grade": "C", "effect": "Diminution"}]},
                {"health_condition_or_goal": "Trouble panique", "outcomes": [{"outcome": "Cortisol", "grade": "", "effect": ""}]},
                {"health_condition_or_goal": "Maladie de Parkinson", "outcomes": [{"outcome": "Apathie", "grade": "D", "effect": "Aucun effet"}]},
                {"health_condition_or_goal": "Perte de poids et maintien", "outcomes": [{"outcome": "Appétit", "grade": "C", "effect": "Diminution"}]}
            ],
            "faq": [{"question": "Le 5-HTP affecte-t-il le sommeil ?", "answer": "Recherches limitées."}],
            "references": [],
            "database_references": []
        },
        # --- MAGNESIUM ---
        {
            "name": "Magnésium Bisglycinate",
            "description": "Forme chélatée de magnésium liée à la glycine, offrant une biodisponibilité supérieure.",
            "overview": [{"question": "Bénéfices?", "answer": "Réduit fatigue et crampes."}],
            "dosage": "300mg à 400mg par jour.",
            "safety": {
                "summary": ["Sûr pour la plupart des adultes."],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: autorisé", "safety_information": "Souvent recommandé."},
                    {"condition": "Allaitement: autorisé", "safety_information": "Compatible."}
                ],
                "interactions": [{"agent": "Antibiotiques", "severity": "Modéré"}],
                "precautions": [{"population_condition": "Insuffisance rénale sévère", "details": "Contre-indiqué."}]
            },
            "database": [
                {"health_condition_or_goal": "Stress", "outcomes": [{"outcome": "Cortisol", "grade": "A"}]},
                {"health_condition_or_goal": "Fatigue", "outcomes": [{"outcome": "Énergie", "grade": "A"}]},
                {"health_condition_or_goal": "Crampes musculaires", "outcomes": [{"outcome": "Fréquence", "grade": "B"}]},
                {"health_condition_or_goal": "Sommeil", "outcomes": [{"outcome": "Qualité", "grade": "B"}]}
            ],
            "faq": [], "references": [], "database_references": []
        },
        # --- MELATONINE ---
        {
            "name": "Mélatonine",
            "description": "Hormone naturelle du sommeil.",
            "overview": [{"question": "Addictif?", "answer": "Non."}],
            "dosage": "1mg à 2mg avant le coucher.",
            "safety": {
                "summary": ["Somnolence diurne possible."],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: éviter", "safety_information": "Manque de données."},
                    {"condition": "Allaitement: éviter", "safety_information": "Passe dans le lait."}
                ],
                "interactions": [{"agent": "Sédatifs", "severity": "Modéré"}],
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
                    {"agent": "Antidépresseurs", "severity": "Majeur"}
                ],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: éviter", "safety_information": "Risque."},
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
                "interactions": [{"agent": "Stimulants", "severity": "Modéré"}],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: éviter", "safety_information": "Limiter caféine."},
                    {"condition": "Allaitement: à limiter", "safety_information": "Excitant."}
                ],
                "precautions": [{"population_condition": "Hypertension", "details": "Augmente tension."}]
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
        # --- YOGA (Exemple pour compléter la demande) ---
        {
            "name": "Yoga Nidra (Méditation)",
            "description": "Technique de relaxation profonde aussi appelée 'sommeil yogique'. Idéal pour réduire le stress sans ingestion de produits.",
            "overview": [{"question": "C'est quoi?", "answer": "Une méditation guidée allongée."}],
            "dosage": "Séances de 20 à 30 minutes, 1 fois par jour.",
            "safety": {
                "summary": ["Aucun effet secondaire connu."],
                "pregnancy_lactation": [
                    {"condition": "Grossesse: autorisé", "safety_information": "Excellent."},
                    {"condition": "Allaitement: autorisé", "safety_information": "Excellent."}
                ],
                "interactions": [],
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