"""Gestionnaire de la commande /speak_about - Recherche dans l'arbre de questions"""

import discord
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import OtherCode as alt
from data.game_data import Questions


async def speak_about_handler(interaction: discord.Interaction, sujet: str):
    """
    Vérifie si un sujet existe dans l'arbre de questions du quiz starter
    
    Args:
        interaction: Objet d'interaction Discord
        sujet: Le mot ou sujet à rechercher dans l'arbre
    """
    
    def search_in_tree(node, search_term: str) -> bool:
        """Recherche récursive dans l'arbre"""
        if node is None:
            return False
        
        # Si c'est une feuille (string = nom de Pokémon)
        if isinstance(node, str):
            # Normaliser pour comparaison insensible à la casse
            pokemon_lower = node.lower()
            search_lower = search_term.lower()
            return search_lower in pokemon_lower
        
        # Si c'est un Arbre, vérifier la racine (question)
        if isinstance(node, alt.Arbre):
            # Normaliser pour comparaison insensible à la casse
            question_lower = node.racine.lower()
            search_lower = search_term.lower()
            
            # Vérifier si le terme est dans la question
            if search_lower in question_lower:
                return True
            
            # Rechercher récursivement dans les branches
            left_found = search_in_tree(node.feuilleGauche, search_term)
            right_found = search_in_tree(node.feuilleDroite, search_term)
            
            return left_found or right_found
        
        return False
    
    # Rechercher dans l'arbre Questions
    found = search_in_tree(Questions, sujet)
    
    # Créer l'embed de réponse
    if found:
        embed = discord.Embed(
            title="✅ Sujet trouvé",
            description=f"**Oui**, le sujet \"**{sujet}**\" existe dans l'arbre de questions du quiz starter.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="❌ Sujet non trouvé",
            description=f"**Non**, le sujet \"**{sujet}**\" n'existe pas dans l'arbre de questions du quiz starter.",
            color=discord.Color.red()
        )
    
    embed.set_footer(text=f"Recherche effectuée par {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)
