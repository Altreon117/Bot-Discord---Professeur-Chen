import discord
import DatabaseFunction as db
import DisplayFunction as display


async def derniere_commande_handler(interaction: discord.Interaction, history_manager):
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    all_cmds = history_manager.get_all_user_commands(user_id)
    
    if len(all_cmds) <= 1:
        await interaction.response.send_message("Aucune commande précédente trouvée.", ephemeral=True)
        return
    
    last_cmd = all_cmds[1]
    embed = display.make_last_command_embed(last_cmd['command'], user_pseudo, last_cmd['timestamp'])
    await interaction.response.send_message(embed=embed)


async def historique_handler(interaction: discord.Interaction, history_manager):
    """Affiche l'historique complet des commandes du joueur"""
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    history_list = history_manager.get_all_user_commands(user_id)
    
    if not history_list:
        await interaction.response.send_message("Tu n'as pas encore utilisé de commandes.", ephemeral=True)
        return
    
    embed = display.make_history_embed(history_list, user_pseudo)
    await interaction.response.send_message(embed=embed)


async def vider_historique_handler(interaction: discord.Interaction, history_manager):
    """Supprime l'historique des commandes du joueur"""
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    history_manager.clear_user_history(user_id)
    db.clear_user_command_history(user_id)
    
    embed = display.make_history_cleared_embed(user_pseudo)
    await interaction.response.send_message(embed=embed)
