# database.py

CATALOGUE_COMPLET = [
    {
        "name": "5-HTP",
        "description": "5-HTP est le précurseur de la sérotonine, un neurotransmetteur impliqué dans la régulation de nombreux processus corporels tels que l'humeur, le sommeil et l'appétit. 5-HTP peut augmenter les niveaux de sérotonine dans le cerveau, ce qui peut réduire les symptômes de la dépression et diminuer l'appétit.",
        "overview": [
            {
                "question": "Qu’est-ce que le 5-HTP?",
                "answer": "5-HTP est un acide aminé et un précurseur du neurotransmetteur sérotonine. Il est produit dans le corps à partir de l'acide aminé essentiel tryptophan, et il peut être supplémenté directement. Les plantes sont une source riche en 5-HTP, et les graines de Griffonia simplicifolia sont souvent utilisées pour l'extraction et la production commerciale de 5-HTP. [4]"
            },
            {
                "question": "Quels sont les principaux bénéfices du 5-HTP?",
                "answer": "5-HTP est très fiable pour augmenter les niveaux de sérotonine dans les neurones présynaptiques du cerveau et est en fait utilisé comme substance test pour aider à déterminer la puissance d'autres substances augmentant la sérotonine. [5] La plupart des recherches ont étudié le 5-HTP pour son rôle potentiel dans le traitement de la dépression. Cela repose sur la théorie sérotoninergique de la dépression - la théorie controversée selon laquelle la dépression résulterait d'un faible taux de sérotonine dans le cerveau. [6] Bien que certaines études soient prometteuses, le corpus de preuves reste globalement faible. La majorité de ces recherches a été menée dans les années 1970 et 1980 avec une qualité méthodologique médiocre. [1] [7] Le 5-HTP peut réduire les symptômes de la dépression comparé à un placebo lorsqu'il est pris seul ou en complément d'un traitement standard. [1] De plus, deux études à court terme (de 6 à 8semaines) ont rapporté que le 5-HTP réduisait les symptômes de la dépression à un degré similaire à celui des antidépresseurs SSRI fluoxetine et fluvoxamine. [8] [9] Bien que cela soit encourageant, des recherches de meilleure qualité sont nécessaires pour confirmer ces effets. Le 5-HTP pourrait également jouer un rôle dans la régulation de l'appétit. Chez les personnes en surpoids ou obèses, les chercheurs ont observé une perte de poids due à une réduction de l'apport calorique et à une augmentation de la satiété, c’est-à-dire la sensation de plénitude, pendant la supplémentation en 5-HTP. [2] [3] [10] Le 5-HTP a également été étudié pour ses effets sur la prévention de la migraine ou des céphalées de tension, [11] [12] [13] la fibromyalgie, [14] [15] et la maladie de Parkinson. [16] [17] Actuellement, les recherches sont mitigées et largement inconclusives."
            },
            {
                "question": "Quels sont les principaux inconvénients du 5-HTP?",
                "answer": "5-HTP peut provoquer des effets secondaires légers qui peuvent s'améliorer avec le temps. Ceux-ci comprennent des nausées, des douleurs abdominales et de la diarrhée, et plus rarement de la fatigue, de l'insomnie et des maux de tête. L'administration intraveineuse de 5-HTP a été rapportée comme causant de la confusion, de l'anxiété et une altération de la mémoire. [18] [1] À fortes doses (100-200mg par kg de poids corporel), le 5-HTP a été associé à un syndrome sérotoninergique chez les animaux de laboratoire, une condition sévère due à des niveaux élevés de sérotonine dans le corps. [1] Chez les rongeurs, le risque de syndrome sérotoninergique était accru lorsque le 5-HTP était combiné avec des SSRI (médicaments antidépresseurs couramment utilisés). Aucun rapport de toxicité n'a été observé à des doses normales, et il convient de noter que le syndrome sérotoninergique lié à la supplémentation en 5-HTP n'a pas été observé chez l'homme. [1] En 1989 et 1990, plus de 1500 cas de syndrome d’éosinophilie myalgique (EMS) (un syndrome rare avec des symptômes de douleurs musculaires sévères et de fatigue) ont conduit à plus de 30 décès signalés chez des personnes prenant des suppléments de tryptophan, précurseur direct du 5-HTP. De plus, quelques cas d’EMS ont été rapportés avec la supplémentation en 5-HTP. Il a été déterminé que l’EMS était probablement dû à un contaminant toxique présent dans les suppléments, et aucun cas confirmé n’a été enregistré ces dernières années. Néanmoins, cela a entraîné une forte diminution de l’utilisation et de la recherche sur les suppléments de tryptophan et de 5-HTP. Pour éviter le risque d’EMS, il est important que les suppléments de 5-HTP soient purifiés et testés pour les contaminants. [1] [19]"
            },
            {
                "question": "Comment le 5-HTP agit-il?",
                "answer": "5-HTP agit comme précurseur direct du neurotransmetteur sérotonine. Le 5-HTP traverse facilement la barrière hémato-encéphalique, ce qui peut entraîner une augmentation des niveaux de sérotonine dans les neurones présynaptiques du cerveau. Cela peut jouer un rôle dans la régulation de l'humeur, du sommeil, de l'appétit, de la mémoire et de divers autres processus. [4] Cependant, il est également important de noter que la relation entre les niveaux de sérotonine et la dépression n'est pas aussi claire que le pensent beaucoup de personnes. Le corpus actuel de preuves ne montre pas de façon constante que des niveaux plus faibles de sérotonine sont associés à la dépression ou en sont la cause. [6]"
            }
        ],
        "dosage": "Le 5-HTP est généralement pris par voie orale sous forme de gélule. Il peut être pris une fois par jour ou en doses fractionnées (c’est-à-dire que la dose quotidienne totale est répartie en deux ou trois prises). Pour la dépression, la plupart des études ont utilisé des doses comprises entre 200mg et 300mg par jour pendant jusqu’à 1an. [1] Pour la perte de poids ou la régulation de l’appétit, le 5-HTP a été utilisé à des doses comprises entre 750mg et 900mg par jour pendant jusqu’à 6semaines. [2] [3] ⚠️ Avertissement: risque de syndrome sérotoninergique",
        "safety": {
            "summary": [
                "La prise de 100mg ou moins de 5-HTP semble bien tolérée. Des doses plus élevées (200-300mg) peuvent entraîner des effets indésirables gastro-intestinaux.",
                "Théoriquement, le 5-HTP peut provoquer des effets sérotoninergiques additifs lorsqu’il est utilisé avec d’autres agents sérotoninergiques.",
                "Le 5-HTP intraveineux doit être évité afin de prévenir les toxicités liées à une surdose telles que la confusion, les troubles de la mémoire et l’anxiété.",
                "Le 5-HTP n’a pas été étudié pendant la grossesse ou l’allaitement. Son éviction est donc justifiée."
            ],
            "side_effects": {
                "summary": "Les effets secondaires gastro-intestinaux du 5-HTP surviennent à des doses plus élevées (200-300mg), possiblement dus à une augmentation de la motilité intestinale résultant de la conversion du 5-HTP en sérotonine. Étant donné que la demi-vie du 5-HTP est courte (environ 4heures) et que la concentration maximale est atteinte en 1-2heures, afin de réduire les effets indésirables il est recommandé d’administrer le 5-HTP en doses plus petites et fractionnées (p.ex., 100mg 2-3 fois par jour). [1] [27] Des effets indésirables neuropsychologiques tels que la confusion, les troubles de la mémoire et l’anxiété ont été rapportés avec des doses intraveineuses de 200-300mg de 5-HTP et très rarement avec des doses orales élevées. [1] [25] De très rares cas (rapports de cas uniques) ont également décrit une gastro-entérite et un scléroderme chez des personnes prenant du 5-HTP. [27] [33]",
                "table": [
                    {
                        "effect": "Nausée [1] [27]",
                        "details": "Voie: orale Dose: 200-300 milligrammes Remarques: Prendre 100milligrammes de 5-HTP 2-3 fois par jour, plutôt qu’en une seule prise, peut prévenir cet effet indésirable."
                    }
                ]
            },
            "interactions": [
                {
                    "agent": "Médicaments sérotoninergiques",
                    "effect": "Théoriquement, la prise de 5-HTP avec d’autres médicaments sérotoninergiques peut augmenter le risque d’effets sérotoninergiques additifs et éventuellement accroître le risque de syndrome sérotoninergique. [27] Cependant, cela n’a pas été signalé dans la recherche clinique. [25] [28] [29]",
                    "evidence": "Théorique",
                    "severity": "Inconnu"
                },
                {
                    "agent": "Carbidopa",
                    "effect": "",
                    "evidence": "",
                    "severity": ""
                },
                {
                    "agent": "Suppléments sérotoninergiques",
                    "effect": "",
                    "evidence": "",
                    "severity": ""
                }
            ],
            "pregnancy_lactation": [
                {
                    "condition": "Grossesse: éviter",
                    "safety_information": "Le supplément 5-HTP n’a pas été étudié pendant la grossesse. L’évitement est justifié."
                },
                {
                    "condition": "Allaitement: éviter",
                    "safety_information": "Le supplément 5-HTP n’a pas été étudié pendant l’allaitement. L’évitement est justifié."
                }
            ],
            "precautions": [
                {
                    "population_condition": "Affections gastro-intestinales",
                    "details": "Des doses élevées de 5-HTP (200-300mg) peuvent provoquer des troubles gastro-intestinaux et doivent être utilisées avec prudence, notamment chez les personnes présentant des affections gastro-intestinales préexistantes. [1] [27]"
                }
            ],
            "anti_doping": {
                "label": "Non interdit",
                "text": "Selon la liste 2025 des substances interdites du WADA, le 5-HTP n'est pas interdit."
            }
        },
        "database": [
            {
                "health_condition_or_goal": "Dépression",
                "outcomes": [
                    {
                        "outcome": "Symptômes de la dépression",
                        "grade": "B",
                        "effect": "Amélioration modérée",
                        "evidence": "2 études Participants: 123",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 123
                    }
                ]
            },
            {
                "health_condition_or_goal": "Obésité",
                "outcomes": [
                    {
                        "outcome": "Appétit",
                        "grade": "B",
                        "effect": "Diminution modérée",
                        "evidence": "2 études Participants: 39",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 39
                    },
                    {
                        "outcome": "Poids",
                        "grade": "",
                        "effect": "",
                        "evidence": "2 études participants : 39",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 39
                    }
                ]
            },
            {
                "health_condition_or_goal": "Terreurs nocturnes",
                "outcomes": [
                    {
                        "outcome": "Fréquence des terreurs nocturnes",
                        "grade": "",
                        "effect": "",
                        "evidence": "1 étude participants : 45",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 45
                    }
                ]
            },
            {
                "health_condition_or_goal": "Diabète de type 2",
                "outcomes": [
                    {
                        "outcome": "Appétit",
                        "grade": "C",
                        "effect": "Diminution modérée",
                        "evidence": "1 étude participants : 25",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 25
                    },
                    {
                        "outcome": "Poids",
                        "grade": "",
                        "effect": "",
                        "evidence": "1 Participants à l'étude : 25",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 25
                    }
                ]
            },
            {
                "health_condition_or_goal": "Trouble panique",
                "outcomes": [
                    {
                        "outcome": "Cortisol",
                        "grade": "",
                        "effect": "",
                        "evidence": "1 Participants à l'étude : 48",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 48
                    }
                ]
            },
            {
                "health_condition_or_goal": "Maladie de Parkinson",
                "outcomes": [
                    {
                        "outcome": "Apathie",
                        "grade": "D",
                        "effect": "Aucun effet",
                        "evidence": "1 Participants à l'étude : 25",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 25
                    },
                    {
                        "outcome": "Symptômes de dépression",
                        "grade": "",
                        "effect": "",
                        "evidence": "1 Participants à l'étude : 25",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 25
                    }
                ]
            },
            {
                "health_condition_or_goal": "Perte de poids et maintien",
                "outcomes": [
                    {
                        "outcome": "Appétit",
                        "grade": "C",
                        "effect": "Diminution modérée",
                        "evidence": "1 Participants à l'étude : 20",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 20
                    },
                    {
                        "outcome": "Poids",
                        "grade": "",
                        "effect": "",
                        "evidence": "1 Participants à l'étude : 20",
                        "studies": [
                            {
                                "title": "Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/23380314"
                            },
                            {
                                "title": "A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine.",
                                "url": "https://pubmed.ncbi.nlm.nih.gov/1909444"
                            }
                        ],
                        "participants": 20
                    }
                ]
            }
        ],
        "faq": [
            {
                "question": "Le 5-HTP affecte-t-il le sommeil ?",
                "answer": "Le 5-HTP, précurseur de la sérotonine et, par conséquent, de la mélatonine, fait l'objet de recherches limitées et non concluantes concernant ses effets sur le sommeil, et certaines études suggèrent qu'il ne pourrait pas améliorer le sommeil et pourrait même réduire la durée du sommeil chez les personnes âgées. Bien qu'il ait été rapporté qu'il réduisait les épisodes de terreurs nocturnes chez les enfants, cette observation n'est pas étayée par une étude contrôlée par placebo."
            },
            {
                "question": "La supplémentation en tryptophane est-elle une alternative appropriée au 5-HTP ?",
                "answer": "Le tryptophane peut être converti en 5-HTP dans l'organisme, mais la supplémentation directe en 5-HTP est plus efficace pour augmenter les niveaux de sérotonine car elle contourne une étape de conversion limitante. De plus, le tryptophane entre en concurrence avec d'autres acides aminés pour pénétrer le cerveau, alors que le 5-HTP peut traverser la barrière hémato-encéphalique plus facilement."
            },
            {
                "question": "Quels sont les autres noms du 5-HTP?",
                "answer": "Notez que le 5-HTP est également connu sous le nom de: 5-HTP ne doit pas être confondu avec: - 5-hydroxytryptophan - L-5-Hydroxytryptophan - L-5HTP - Oxitriptan - 5-Hydroxytryptamine (Sérotonine ou 5-HT) - Tryptophane"
            }
        ],
        "references": [
            {
                "text": "Weight - Ceci F, Cangiano C, Cairella M, Cascino A, Del Ben M, Muscaritoli M, Sibilia L, Rossi Fanelli F The effects of oral 5-hydroxytryptophan administration on feeding behavior in obese adult female subjects J Neural Transm. (1989)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/2468734"
            },
            {
                "text": "Weight - Cangiano C, Ceci F, Cascino A, Del Ben M, Laviano A, Muscaritoli M, Antonucci F, Rossi-Fanelli F Eating behavior and adherence to dietary prescriptions in obese adult subjects treated with 5-hydroxytryptophan Am J Clin Nutr. (1992 Nov)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/1384305"
            },
            {
                "text": "Sleep Terror Frequency - Bruni O, Ferri R, Miano S, Verrillo E L -5-Hydroxytryptophan treatment of sleep terrors in children Eur J Pediatr. (2004 Jul)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/15146330"
            },
            {
                "text": "Appetite - Cangiano C, Laviano A, Del Ben M, Preziosa I, Angelico F, Cascino A, Rossi-Fanelli F Effects of oral 5-hydroxy-tryptophan on energy intake and macronutrient selection in non-insulin dependent diabetic patients Int J Obes Relat Metab Disord. (1998 Jul)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/9705024"
            },
            {
                "text": "Cortisol - Schruers K, van Diest R, Nicolson N, Griez E L-5-hydroxytryptophan induced increase in salivary cortisol in panic disorder patients and healthy volunteers Psychopharmacology (Berl). (2002 Jun)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/12073163"
            },
            {
                "text": "Depression Symptoms - Jangid P, Malik P, Singh P, Sharma M, Gulia AK Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode. Asian J Psychiatr. (2013-Feb)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/23380314"
            },
            {
                "text": "Depression Symptoms - Pöldinger W, Calanchini B, Schwarz W A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine. Psychopathology. (1991)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/1909444"
            },
            {
                "text": "Depression Symptoms - Meloni M, Puligheddu M, Carta M, Cannas A, Figorilli M, Defazio G Efficacy and safety of 5-hydroxytryptophan on depression and apathy in Parkinson's disease: a preliminary finding. Eur J Neurol. (2020 May)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/32067288"
            }
        ],
        "database_references": [
            {
                "text": "Weight - Ceci F, Cangiano C, Cairella M, Cascino A, Del Ben M, Muscaritoli M, Sibilia L, Rossi Fanelli F The effects of oral 5-hydroxytryptophan administration on feeding behavior in obese adult female subjects J Neural Transm. (1989)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/2468734"
            },
            {
                "text": "Weight - Cangiano C, Ceci F, Cascino A, Del Ben M, Laviano A, Muscaritoli M, Antonucci F, Rossi-Fanelli F Eating behavior and adherence to dietary prescriptions in obese adult subjects treated with 5-hydroxytryptophan Am J Clin Nutr. (1992 Nov)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/1384305"
            },
            {
                "text": "Sleep Terror Frequency - Bruni O, Ferri R, Miano S, Verrillo E L -5-Hydroxytryptophan treatment of sleep terrors in children Eur J Pediatr. (2004 Jul)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/15146330"
            },
            {
                "text": "Appetite - Cangiano C, Laviano A, Del Ben M, Preziosa I, Angelico F, Cascino A, Rossi-Fanelli F Effects of oral 5-hydroxy-tryptophan on energy intake and macronutrient selection in non-insulin dependent diabetic patients Int J Obes Relat Metab Disord. (1998 Jul)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/9705024"
            },
            {
                "text": "Cortisol - Schruers K, van Diest R, Nicolson N, Griez E L-5-hydroxytryptophan induced increase in salivary cortisol in panic disorder patients and healthy volunteers Psychopharmacology (Berl). (2002 Jun)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/12073163"
            },
            {
                "text": "Depression Symptoms - Jangid P, Malik P, Singh P, Sharma M, Gulia AK Comparative study of efficacy of l-5-hydroxytryptophan and fluoxetine in patients presenting with first depressive episode. Asian J Psychiatr. (2013-Feb)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/23380314"
            },
            {
                "text": "Depression Symptoms - Pöldinger W, Calanchini B, Schwarz W A functional-dimensional approach to depression: serotonin deficiency as a target syndrome in a comparison of 5-hydroxytryptophan and fluvoxamine. Psychopathology. (1991)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/1909444"
            },
            {
                "text": "Depression Symptoms - Meloni M, Puligheddu M, Carta M, Cannas A, Figorilli M, Defazio G Efficacy and safety of 5-hydroxytryptophan on depression and apathy in Parkinson's disease: a preliminary finding. Eur J Neurol. (2020 May)",
                "link": "https://pubmed.ncbi.nlm.nih.gov/32067288"
            }
        ]
    },
    {
        "name": "Magnésium Bisglycinate",
        "description": "Forme chélatée de magnésium liée à la glycine, offrant une biodisponibilité supérieure et une excellente tolérance digestive. Essentiel pour la relaxation musculaire et nerveuse.",
        "overview": [
            {
                "question": "Qu’est-ce que le Magnésium Bisglycinate?",
                "answer": "C'est un minéral essentiel lié à deux molécules de glycine. Cette structure protège le magnésium de l'acidité gastrique et facilite son absorption intestinale sans effet laxatif notable."
            },
            {
                "question": "Quels sont les bénéfices?",
                "answer": "Il aide à réduire la fatigue, soutient le système nerveux, réduit les crampes musculaires et améliore la qualité du sommeil en régulant les neurotransmetteurs."
            }
        ],
        "dosage": "300mg à 400mg par jour, de préférence le soir au repas ou au coucher.",
        "safety": {
            "summary": [
                "Excellente tolérance digestive contrairement à l'oxyde de magnésium.",
                "Sûr pour la plupart des adultes."
            ],
            "side_effects": {
                "summary": "Très rares. Possibles troubles digestifs légers chez les personnes très sensibles.",
                "table": []
            },
            "interactions": [
                {
                    "agent": "Antibiotiques (Tétracyclines)",
                    "effect": "Peut réduire l'absorption de l'antibiotique. Espacer de 2h.",
                    "evidence": "Clinique",
                    "severity": "Modéré"
                },
                {
                    "agent": "Bisphosphonates",
                    "effect": "Réduit l'absorption.",
                    "evidence": "Clinique",
                    "severity": "Modéré"
                }
            ],
            "pregnancy_lactation": [
                {
                    "condition": "Grossesse: autorisé",
                    "safety_information": "Souvent recommandé pour les crampes. Respecter les doses."
                },
                {
                    "condition": "Allaitement: autorisé",
                    "safety_information": "Compatible avec l'allaitement."
                }
            ],
            "precautions": [
                {
                    "population_condition": "Insuffisance rénale sévère",
                    "details": "Contre-indiqué sans avis médical."
                }
            ],
            "anti_doping": {
                "label": "Non interdit",
                "text": "Autorisé."
            }
        },
        "database": [
            {
                "health_condition_or_goal": "Stress",
                "outcomes": [
                    {
                        "outcome": "Niveau de cortisol",
                        "grade": "A",
                        "effect": "Réduction significative",
                        "evidence": "3 études",
                        "studies": [],
                        "participants": 200
                    }
                ]
            },
            {
                "health_condition_or_goal": "Fatigue",
                "outcomes": [
                    {
                        "outcome": "Énergie perçue",
                        "grade": "A",
                        "effect": "Amélioration",
                        "evidence": "Plusieurs études cliniques",
                        "studies": [],
                        "participants": 150
                    }
                ]
            },
            {
                "health_condition_or_goal": "Crampes musculaires",
                "outcomes": [
                    {
                        "outcome": "Fréquence des crampes",
                        "grade": "B",
                        "effect": "Diminution",
                        "evidence": "Données observationnelles",
                        "studies": [],
                        "participants": 80
                    }
                ]
            },
            {
                "health_condition_or_goal": "Sommeil",
                "outcomes": [
                    {
                        "outcome": "Qualité du sommeil",
                        "grade": "B",
                        "effect": "Amélioration",
                        "evidence": "Études mixtes",
                        "studies": [],
                        "participants": 100
                    }
                ]
            }
        ],
        "faq": [
            {
                "question": "Donne-t-il la diarrhée?",
                "answer": "Non, la forme bisglycinate est connue pour ne pas avoir d'effet laxatif notable contrairement à l'oxyde de magnésium."
            }
        ],
        "references": [],
        "database_references": []
    },
    {
        "name": "Mélatonine",
        "description": "Hormone naturelle produite par la glande pinéale qui signale au corps qu'il est temps de dormir. Utilisée pour réduire le temps d'endormissement et les effets du décalage horaire.",
        "overview": [
            {
                "question": "Est-ce addictif?",
                "answer": "Non, contrairement aux somnifères classiques (benzodiazépines), il n'y a pas d'accoutumance physique majeure démontrée à ce jour."
            }
        ],
        "dosage": "1mg à 2mg, 30 minutes avant le coucher.",
        "safety": {
            "summary": [
                "Peut causer une somnolence diurne si pris trop tard ou à trop forte dose."
            ],
            "side_effects": {
                "summary": "Somnolence, maux de tête, vertiges légers.",
                "table": []
            },
            "interactions": [
                {
                    "agent": "Anticoagulants",
                    "effect": "Peut augmenter le risque de saignement (théorique).",
                    "evidence": "Faible",
                    "severity": "Modéré"
                },
                {
                    "agent": "Sédatifs",
                    "effect": "Augmente l'effet sédatif.",
                    "evidence": "Forte",
                    "severity": "Modéré"
                }
            ],
            "pregnancy_lactation": [
                {
                    "condition": "Grossesse: éviter",
                    "safety_information": "Manque de données, principe de précaution."
                },
                {
                    "condition": "Allaitement: éviter",
                    "safety_information": "Passe dans le lait maternel."
                }
            ],
            "precautions": [
                {
                    "population_condition": "Conduite de véhicules",
                    "details": "Peut causer une somnolence."
                }
            ],
            "anti_doping": {
                "label": "Non interdit",
                "text": "Autorisé."
            }
        },
        "database": [
            {
                "health_condition_or_goal": "Sommeil",
                "outcomes": [
                    {
                        "outcome": "Temps d'endormissement",
                        "grade": "A",
                        "effect": "Réduction",
                        "evidence": "Méta-analyse",
                        "studies": [],
                        "participants": 500
                    }
                ]
            },
            {
                "health_condition_or_goal": "Jet lag",
                "outcomes": [
                    {
                        "outcome": "Symptômes du décalage horaire",
                        "grade": "A",
                        "effect": "Amélioration",
                        "evidence": "Méta-analyse Cochrane",
                        "studies": [],
                        "participants": 300
                    }
                ]
            }
        ],
        "faq": [],
        "references": [],
        "database_references": []
    },
    {
        "name": "Millepertuis (St. John's Wort)",
        "description": "Plante médicinale utilisée traditionnellement pour les troubles de l'humeur. Son efficacité est comparable à certains antidépresseurs, mais elle présente de nombreuses interactions médicamenteuses.",
        "overview": [
            {
                "question": "Comment agit le Millepertuis?",
                "answer": "L'hyperforine, son principe actif, inhibe la recapture de la sérotonine, dopamine et noradrénaline."
            }
        ],
        "dosage": "300mg d'extrait standardisé, 3 fois par jour. Effets ressentis après 2 à 4 semaines.",
        "safety": {
            "summary": [
                "Attention : Puissant inducteur enzymatique (CYP3A4).",
                "Rend inefficaces de nombreux médicaments vitaux."
            ],
            "side_effects": {
                "summary": "Photosensibilisation (sensibilité au soleil), troubles digestifs, sécheresse buccale.",
                "table": [
                    {
                        "effect": "Photosensibilité",
                        "details": "Éviter l'exposition prolongée au soleil."
                    }
                ]
            },
            "interactions": [
                {
                    "agent": "Contraceptifs oraux (Pilule)",
                    "effect": "Diminue l'efficacité contraceptive. Risque de grossesse.",
                    "evidence": "Forte",
                    "severity": "Majeur"
                },
                {
                    "agent": "Anticoagulants",
                    "effect": "Réduit l'effet anticoagulant (risque de thrombose).",
                    "evidence": "Forte",
                    "severity": "Majeur"
                },
                {
                    "agent": "Antidépresseurs",
                    "effect": "Risque de syndrome sérotoninergique.",
                    "evidence": "Forte",
                    "severity": "Majeur"
                },
                {
                    "agent": "Immunosuppresseurs",
                    "effect": "Risque de rejet de greffe.",
                    "evidence": "Forte",
                    "severity": "Majeur"
                }
            ],
            "pregnancy_lactation": [
                {
                    "condition": "Grossesse: éviter",
                    "safety_information": "Données insuffisantes et risque d'interactions."
                },
                {
                    "condition": "Allaitement: éviter",
                    "safety_information": "Passe dans le lait maternel."
                }
            ],
            "precautions": [
                {
                    "population_condition": "Troubles bipolaires",
                    "details": "Risque de virage maniaque."
                }
            ],
            "anti_doping": {
                "label": "Non interdit",
                "text": "Autorisé."
            }
        },
        "database": [
            {
                "health_condition_or_goal": "Dépression",
                "outcomes": [
                    {
                        "outcome": "Score Hamilton Depression",
                        "grade": "A",
                        "effect": "Amélioration comparable aux ISRS",
                        "evidence": "Multiples méta-analyses",
                        "studies": [],
                        "participants": 1000
                    }
                ]
            },
            {
                "health_condition_or_goal": "Anxiété",
                "outcomes": [
                    {
                        "outcome": "Symptômes anxieux",
                        "grade": "B",
                        "effect": "Réduction modérée",
                        "evidence": "Études cliniques",
                        "studies": [],
                        "participants": 150
                    }
                ]
            }
        ],
        "faq": [
            {
                "question": "Puis-je le prendre avec ma pilule?",
                "answer": "NON. Il annule l'effet de la pilule contraceptive."
            }
        ],
        "references": [],
        "database_references": []
    },
    {
        "name": "Guarana",
        "description": "Graine amazonienne contenant une forte concentration de caféine (guaranine) à libération lente. Utilisée pour la vigilance, l'énergie et le métabolisme.",
        "overview": [
            {
                "question": "Différence avec le café?",
                "answer": "La caféine du guarana est liée aux tanins, ce qui procure une énergie plus stable et durable sans le pic d'excitation immédiat du café."
            }
        ],
        "dosage": "Dépend de la teneur en caféine. Généralement 500mg à 1000mg de poudre. Ne pas dépasser 400mg de caféine totale/jour.",
        "safety": {
            "summary": [
                "Stimulant du système nerveux central.",
                "Peut causer nervosité et insomnie."
            ],
            "side_effects": {
                "summary": "Palpitations, insomnie, agitation, irritation gastrique.",
                "table": [
                    {
                        "effect": "Insomnie",
                        "details": "Ne pas prendre après 16h."
                    }
                ]
            },
            "interactions": [
                {
                    "agent": "Stimulants",
                    "effect": "Effet cumulatif (tachycardie).",
                    "evidence": "Clinique",
                    "severity": "Modéré"
                },
                {
                    "agent": "Éphédrine",
                    "effect": "Risque cardiovasculaire élevé.",
                    "evidence": "Forte",
                    "severity": "Majeur"
                }
            ],
            "pregnancy_lactation": [
                {
                    "condition": "Grossesse: éviter",
                    "safety_information": "Limiter la caféine (<200mg/jour). Risque de fausse couche à haute dose."
                },
                {
                    "condition": "Allaitement: à limiter",
                    "safety_information": "La caféine passe dans le lait et peut exciter le bébé."
                }
            ],
            "precautions": [
                {
                    "population_condition": "Hypertension",
                    "details": "Peut augmenter la tension artérielle."
                },
                {
                    "population_condition": "Troubles cardiaques",
                    "details": "Éviter."
                }
            ],
            "anti_doping": {
                "label": "Surveillé",
                "text": "La caféine est dans le programme de surveillance WADA (pas interdite, mais surveillée)."
            }
        },
        "database": [
            {
                "health_condition_or_goal": "Fatigue",
                "outcomes": [
                    {
                        "outcome": "Vigilance",
                        "grade": "A",
                        "effect": "Augmentation immédiate",
                        "evidence": "Consensus EFSA",
                        "studies": [],
                        "participants": 0
                    }
                ]
            },
            {
                "health_condition_or_goal": "Perte de poids",
                "outcomes": [
                    {
                        "outcome": "Métabolisme basal",
                        "grade": "B",
                        "effect": "Légère augmentation",
                        "evidence": "Études métaboliques",
                        "studies": [],
                        "participants": 50
                    }
                ]
            },
            {
                "health_condition_or_goal": "Concentration",
                "outcomes": [
                    {
                        "outcome": "Focus mental",
                        "grade": "B",
                        "effect": "Amélioration",
                        "evidence": "Études cognitives",
                        "studies": [],
                        "participants": 60
                    }
                ]
            }
        ],
        "faq": [],
        "references": [],
        "database_references": []
    }
]