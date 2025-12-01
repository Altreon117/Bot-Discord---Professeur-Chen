"""Gestionnaire de la commande /team - Affichage de l'équipe du joueur"""

import discord
import DatabaseFunction as db
import DisplayFunction as display
from Classes import TeamView


async def team_handler(interaction: discord.Interaction):
    """Affiche l'équipe actuelle du joueur avec une vue interactive"""
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    team_pokemon = db.get_user_team(user_id)
    
    file_img = display.make_team_grid_file(team_pokemon, db)
    embed = display.make_team_embed(user_pseudo)
    
    view = TeamView(user_id, team_pokemon, db)
    
    await interaction.response.send_message(embed=embed, file=file_img, view=view, ephemeral=True)
