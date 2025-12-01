import discord
import DatabaseFunction as db


async def on_message_handler(message: discord.Message, bot: discord.Client):
    """Handler pour l'événement on_message"""
    if message.author == bot.user:
        return

    if message.content == "Feur" or message.content == "feur":
        await message.channel.send("TA GUEULE")
    
    await bot.process_commands(message)


async def on_member_join_handler(member: discord.Member, accueil_channel_id: int, bot: discord.Client):
    """Gère l'arrivée d'un nouveau membre sur le serveur"""
    """Handler pour l'événement on_member_join"""
    # Ajouter le nouvel utilisateur dans la base de données
    db.add_new_user(member.id, member.name)
    
    # ID du channel d'accueil
    Accueil_channel = bot.get_channel(accueil_channel_id)
    if Accueil_channel:
        await Accueil_channel.send(f"Bienvenue sur le serveur {member.mention} !")
