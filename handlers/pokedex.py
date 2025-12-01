"""Gestionnaire de la commande /pokedex - Consultation du Pokédex par pages"""

import discord
import DatabaseFunction as db
from Classes import PokedexView


async def pokedex_handler(interaction: discord.Interaction):
    """Affiche le Pokédex du joueur avec pagination (6x5 Pokémon par page)"""
    user_id = interaction.user.id
    view = PokedexView(user_id, db, initial_gen=1, page_size=30)
    file_img = view._build_page_image()
    embed = view._build_embed()
    await interaction.response.send_message(embed=embed, file=file_img, view=view, ephemeral=True)
