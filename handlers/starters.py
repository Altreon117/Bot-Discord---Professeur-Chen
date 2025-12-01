"""Gestionnaires des commandes de choix de starter (randomstarter, starterquiz, starterchoice)"""

import discord
import random
import DatabaseFunction as db
import OtherCode as alt
from Classes import QuizView


async def randomstarter_handler(interaction: discord.Interaction, starters: dict, bot: discord.Client, adventure_channel_id: int):
    """Attribue un starter aléatoire au joueur"""
    user_id = interaction.user.id
    user_pseudo = interaction.user.name

    if db.has_starter(user_id):
        await interaction.response.send_message("Tu as déjà un starter.", ephemeral=True)
        return

    resultat = random.randint(1, 19)
    embed, fichier_image, starter_nom, pokedex_num_int, sexe, niveau = await alt.generate_starter_embed(resultat, starters, "Ton starter aléatoire !")

    # Sauvegarde BD
    db.add_new_user(user_id, user_pseudo)
    db.init_player_pc(user_id, user_pseudo, starter_nom)

    pokemon_instance_id = db.create_pokemon_instance(pokedex_num_int, niveau, sexe, user_id, user_pseudo, location="Team")
    if pokemon_instance_id:
        db.add_pokemon_to_team(user_id, pokemon_instance_id)
        db.update_user_starter_id(user_id, pokemon_instance_id)

    channel = bot.get_channel(adventure_channel_id)
    if channel:
        await channel.send(f"{interaction.user.mention} a choisi **{starter_nom}** !")
    await interaction.response.send_message(embed=embed, file=fichier_image, ephemeral=True)


async def starterquiz_handler(interaction: discord.Interaction, starters: dict, Questions, quiz_sessions: dict):
    """Lance le quiz interactif pour déterminer le starter idéal du joueur"""
    user_id = interaction.user.id
    if db.has_starter(user_id):
        await interaction.response.send_message("Tu as déjà un starter.", ephemeral=True)
        return
    quiz_sessions[user_id] = Questions
    embed = alt.build_question_embed(Questions)
    view = QuizView(user_id, starters, db, Questions, quiz_sessions)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def starterchoice_handler(interaction: discord.Interaction, choice: str, starters: dict, bot: discord.Client, adventure_channel_id: int):
    """Permet au joueur de choisir manuellement son starter par nom ou numéro Pokédex"""
    user_id = interaction.user.id
    user_pseudo = interaction.user.name

    if db.has_starter(user_id):
        await interaction.response.send_message("Tu as déjà un starter.", ephemeral=True)
        return

    starter_id = alt.resolve_starter(choice, starters)
    if starter_id is None:
        await interaction.response.send_message("Starter inconnu. Fournis un nom ou numéro valide.", ephemeral=True)
        return

    embed, fichier_image, starter_nom, pokedex_num_int, sexe, niveau = await alt.generate_starter_embed(starter_id, starters, "Ton starter choisi !")

    # Sauvegarde BD
    db.add_new_user(user_id, user_pseudo)
    db.init_player_pc(user_id, user_pseudo, starter_nom)

    pokemon_instance_id = db.create_pokemon_instance(pokedex_num_int, niveau, sexe, user_id, user_pseudo, location="Team")
    if pokemon_instance_id:
        db.add_pokemon_to_team(user_id, pokemon_instance_id)
        db.update_user_starter_id(user_id, pokemon_instance_id)

    channel = bot.get_channel(adventure_channel_id)
    if channel:
        await channel.send(f"{interaction.user.mention} a choisi **{starter_nom}** !")
    await interaction.response.send_message(embed=embed, file=fichier_image, ephemeral=True)
