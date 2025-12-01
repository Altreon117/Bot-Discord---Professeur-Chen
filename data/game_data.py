"""Données de jeu statiques - dictionnaire des starters et arbre de questions du quiz"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import OtherCode as alt


# Dictionnaire des starters - 19 starters Gen 1-6
# Format: id -> (nom, pokedex_number)
starters = {
    1: ("Bulbizarre", "0001"),
    2: ("Salamèche", "0004"),
    3: ("Carapuce", "0007"),
    4: ("Pikachu", "0025"),
    5: ("Germignon", "0152"),
    6: ("Héricendre", "0155"),
    7: ("Kaiminus", "0158"),
    8: ("Arcko", "0252"),
    9: ("Poussifeu", "0255"),
    10: ("Gobou", "0258"),
    11: ("Tortipouss", "0387"),
    12: ("Ouisticram", "0390"),
    13: ("Tiplouf", "0393"),
    14: ("Vipelierre", "0495"),
    15: ("Gruikui", "0498"),
    16: ("Moustillon", "0501"),
    17: ("Marisson", "0650"),
    18: ("Feunnec", "0653"),
    19: ("Grenousse", "0656")
}


# Arbre de questions pour le quiz starter
# Structure: alt.Arbre(question, branche_oui, branche_non)
Questions = alt.Arbre("Q1 : Dans la vie, es-tu quelqu'un de plutôt énergique et impulsif ?",
                #oui
                    alt.Arbre("Q2 : Aimes-tu attirer toute l'attention sur toi ?",
                        #oui
                            alt.Arbre("Q3 : Préfères-tu utiliser la magie plutôt que tes poings ?",
                                #oui
                                    "Feunnec",
                                #non
                                    alt.Arbre("Q4 : Voudrais-tu être la mascotte aimée de tous ?",
                                        #oui
                                            "Pikachu",
                                        #non
                                            "Ouisticram"
                                    )
                            ),
                        #non
                            alt.Arbre("Q3 : La force brute est-elle la solution à tout ?",
                                #oui
                                    alt.Arbre("Q4 : Aimes-tu manger autant que te battre ?",
                                        #oui
                                            "Gruikui",
                                        #non
                                            alt.Arbre("Q5 : Es-tu un peu hyperactif et mordant ?",
                                                #oui
                                                    "Kaiminus",
                                                #non
                                                    "Poussifeu"
                                            )
                                    ),
                                #non
                                    alt.Arbre("Q4 : Te considères-tu comme 'Cool' et rapide ?",
                                        #oui
                                            alt.Arbre("Q5 : As-tu un côté un peu sombre ou ninja ?",
                                                #oui 
                                                    "Grenousse",
                                                #non
                                                    "Arcko"
                                            ),
                                        #non 
                                            alt.Arbre("Q5 : As-tu une flamme intérieure qui ne s'éteint jamais ?",
                                                #oui
                                                    "Salamèche",
                                                #non
                                                    "Héricendre"
                                            )
                                    )
                            )
                    ),        
                #non
                    alt.Arbre("Q2 : Te sens-tu plus à l'aise dans l'eau que sur terre ?",
                        #oui
                            alt.Arbre("Q3 : L'honneur et la discipline sont-ils importants pour toi ?",
                                #oui
                                    alt.Arbre("Q4 : Utilises-tu des armes (coquillages, épées) ?",
                                        #oui
                                            "Moustillon",
                                        #non
                                            "Tiplouf"
                                    ),
                                #non
                                    alt.Arbre("Q4 : Aimes-tu avoir une carapace solide ?",
                                        #oui
                                            "Carapuce",
                                        #non
                                            "Gobou"
                                    )
                            ),
                        #non
                            alt.Arbre("Q3 : Aimes-tu te prélasser au soleil ?",
                                #oui
                                    alt.Arbre("Q4 : As-tu une fleur ou une plante qui pousse sur toi ?",
                                        #oui
                                            alt.Arbre("Q5 : Es-tu le tout premier, le numéro 1 ?",
                                                #oui
                                                    "Bulbizarre",
                                                #non
                                                    "Germignon"
                                            ),
                                        #non
                                            "Vipelierre"
                                    ),
                                #non
                                    alt.Arbre("Q4 : Aimes-tu la solidité et la protection ?",
                                        #oui
                                            alt.Arbre("Q5 : Portes-tu une armure d'épines ?",
                                                #oui
                                                    "Marisson",
                                                #non
                                                    "Tortipouss"
                                            ),
                                        #non
                                            "Arcko"
                                    )
                            )
                    )
            )
