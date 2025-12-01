"""Gestionnaire de la commande /letsgo - Introduction au bot"""

import discord
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import DatabaseFunction as db
import DisplayFunction as display


async def letsgo_handler(interaction: discord.Interaction):
    """
    Introduit le bot et explique les commandes principales pour choisir un starter
    
    Args:
        interaction: Objet d'interaction Discord
    """
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    # Sécurité : on s'assure que le joueur est bien dans la table User
    db.add_new_user(user_id, user_pseudo)
    
    if db.has_starter(user_id):
        await interaction.response.send_message(
            "Tu as déjà commencé ton aventure ! Utilise ton PC ou ton équipe pour voir tes Pokémons.",
            ephemeral=True
        )
    else:
        # Message d'intro + présentation des trois possibilités
        intro = (
            f"Bonjour {interaction.user.mention} ! Bienvenue dans le monde des Pokémon.\n"
            "Pour commencer ton voyage, tu dois choisir ton premier compagnon.\n\n"
            "Choisis comment obtenir ton starter :\n"
            "• `/randomstarter` : Starter aléatoire\n"
            "• `/starterquiz` : Quiz interactif pour te guider\n"
            "• `/starterchoice` : Choisis par nom ou numéro"
        )
        embed = display.make_letsgo_intro_embed(intro)
        await interaction.response.send_message(embed=embed, ephemeral=True)
