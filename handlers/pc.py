"""Gestionnaire de la commande /pc - Gestion du PC (stockage Pokémon)"""

import discord
import DatabaseFunction as db
from Classes import PCView


async def pc_handler(interaction: discord.Interaction):
    """Affiche le PC du joueur avec tous les Pokémon stockés"""
    user_id = interaction.user.id
    
    if not db.has_starter(user_id):
        await interaction.response.send_message("Tu dois d'abord obtenir un starter avec /letsgo !", ephemeral=True)
        return
    
    view = PCView(user_id, db, box_number=1)
    file_img = view._build_box_image()
    embed = view._build_embed()
    await interaction.response.send_message(embed=embed, file=file_img, view=view, ephemeral=True)
