"""Décorateur pour l'enregistrement des commandes dans la base de données"""

from functools import wraps
import discord


def track_command(command_name: str, history_manager):
    """Décorateur qui enregistre automatiquement l'usage d'une commande dans l'historique"""
    def decorator(func):
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, **kwargs):
            # Enregistrer la commande dans l'historique
            history_manager.add_command(interaction.user.id, command_name, interaction.user.name)
            
            # Exécuter la commande originale
            return await func(interaction, **kwargs)
        return wrapper
    return decorator
