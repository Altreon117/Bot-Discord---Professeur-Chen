"""Gestionnaire de la commande /capture - Capture des Pokémon sauvages spawnés"""

import discord
import random
from datetime import datetime
import DatabaseFunction as db
import DisplayFunction as display


async def capture_handler(interaction: discord.Interaction, code: str, bot: discord.Client, adventure_channel_id: int):
    """Tente de capturer un Pokémon spawn avec le code fourni"""
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    if not db.has_starter(user_id):
        await interaction.response.send_message("Tu dois d'abord obtenir un starter avec /letsgo !", ephemeral=True)
        return
    
    spawn_data = db.get_spawn_by_code(code.upper())
    if not spawn_data:
        await interaction.response.send_message("Code invalide, Pokémon déjà capturé ou temps de capture dépassé.", ephemeral=True)
        return
    
    despawn_time = datetime.fromisoformat(spawn_data["despawn_time"])
    if datetime.now() > despawn_time:
        db.delete_spawn(spawn_data["spawn_id"])
        await interaction.response.send_message("Code invalide, Pokémon déjà capturé ou temps de capture dépassé.", ephemeral=True)
        return
    
    conn = db.sqlite3.connect(db.DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT CatchRate FROM Pokedex WHERE Id = ?", (spawn_data["pokedex_str"],))
    row = cursor.fetchone()
    conn.close()
    catch_rate = row[0] if row else 45
    
    roll = random.randint(1, 255)
    success = roll <= catch_rate
    pokemon_name = spawn_data["nom"]
    
    if success:
        sexe = random.choice(["♂", "♀"]) 
        niveau = spawn_data["niveau"]
        
        pokemon_instance_id = db.create_pokemon_instance(
            spawn_data["pokedex_id"], 
            niveau, 
            sexe, 
            user_id, 
            user_pseudo,
            location="PC"
        )
        
        added = False
        if pokemon_instance_id:
            added = db.add_pokemon_to_team(user_id, pokemon_instance_id)
            if not added:
                db.add_pokemon_to_pc(user_id, pokemon_instance_id)
        
        embed = display.make_capture_success_embed(interaction.user.mention, pokemon_name, niveau, added, roll, catch_rate)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        channel = bot.get_channel(adventure_channel_id)
        if channel:
            await channel.send(f"{interaction.user.mention} a capturé le **{pokemon_name}** sauvage !")
    else:
        embed = display.make_capture_failed_embed(pokemon_name, roll, catch_rate)
        await interaction.response.send_message(embed=embed, ephemeral=True)
