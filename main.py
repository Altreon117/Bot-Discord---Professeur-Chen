import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import random
import asyncio
from functools import wraps
from PIL import Image
from io import BytesIO
import DatabaseFunction as db
import OtherCode as alt
from Classes import PokedexView, TeamView, PCView, QuizView
from HistoryFunctions import HistoryManager
from datetime import datetime, timedelta
import uuid
import DisplayFunction as display
from handlers.starters import (
    randomstarter_handler,
    starterquiz_handler,
    starterchoice_handler,
)
from handlers.capture import capture_handler
from handlers.history import (
    derniere_commande_handler,
    historique_handler,
    vider_historique_handler,
)
from handlers.team import team_handler
from handlers.pokedex import pokedex_handler
from handlers.pc import pc_handler
from handlers.letsgo import letsgo_handler
from handlers.speak_about import speak_about_handler
from handlers.events import (
    on_message_handler,
    on_member_join_handler,
)
from handlers.decorators import track_command as create_track_command
from data.game_data import starters, Questions

ADVENTURE_CHANNEL_ID = 1441094127881031681 
ACCUEIL_CHANNEL_ID = 1441058736071245946
GENERAL_CHANNEL_ID = 1441421738406842420



#######--- PARAMETRAGE DU BOT ---########################################################################################################

# Chargement du token
load_dotenv(dotenv_path="Back/PokeKey.env")
token = os.getenv("DISCORD_TOKEN") # MON TRESOR JE VOUS LE LAISSE SI VOUS VOULEZ. TROUVEZ LE !! JE L'AI LAISSEZ QUELQUE PART DANS CE MONDE !!! 

# Configuration des intents
intents = discord.Intents.default()
intents.message_content = True # Permet de lire le contenu des messages
intents.members = True # Permet de lire les membres du serveur
bot = commands.Bot(command_prefix="/", intents=intents)

# Gestionnaire d'historique des commandes
history_manager = HistoryManager()



#Initialisation du bot
@bot.event
async def on_ready():
    # 1. Initialiser les tables de la base de données
    db.init_database()
    
    # 2. Enregistrer TOUS les membres actuels du serveur dans la table User
    print("Analyse des membres du serveur...")
    total_membres = 0
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                db.add_new_user(member.id, member.name)
                total_membres += 1
    print(f"{total_membres} utilisateurs vérifiés/ajoutés dans la base de données.")
    
    # 3. Synchroniser les commandes slash
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commande(s) slash synchronisée(s)")
    except Exception as e:
        print(f"Erreur lors de la synchronisation : {e}")
    
    # Démarrer le spawn périodique de Pokémon
    if not spawn_pokemon.is_running():
        maintenant = datetime.now()
        # Calculer la prochaine heure pile (ex: si 14h37 -> 15h00)
        prochaine_heure_pile = (maintenant + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        delai_secondes = (prochaine_heure_pile - maintenant).total_seconds()
        
        # Démarrer la tâche avec un délai jusqu'à la prochaine heure pile
        spawn_pokemon.start()
        heure_spawn = prochaine_heure_pile.strftime("%H:%M")
        print(f"Spawn périodique de Pokémon démarré - Premier spawn à {heure_spawn}, puis toutes les heures pile")
        
        print("Le bot est en LIGNE !")
        
        
        
##########---TÂCHES PÉRIODIQUES---########################################################################################################


## spawn de Pokémon sauvage toutes les heures pile
@tasks.loop(hours=1)
async def spawn_pokemon():
    channel = bot.get_channel(ADVENTURE_CHANNEL_ID)
    if not channel:
        return
    
    # Pokémon Gen 1 : IDs de 0001 à 0151
    pokedex_num = random.randint(1, 151)
    pokedex_str = f"{pokedex_num:04d}"
    pokemon_data = db.get_pokemon_data(pokedex_str)
    if not pokemon_data:
        print(f"Pokémon #{pokedex_str} introuvable dans Pokedex")
        return
    
    pokemon_name = pokemon_data["nom"]
    image_filename = pokemon_data["image"]
    image_path = f"PokeSprites/{image_filename}"
    sexe = random.choice(["♂", "♀"])
    niveau = random.randint(1, 100)
    
    # Générer spawn_time, despawn_time (30min après), et capture_code unique
    spawn_time = datetime.now()
    despawn_time = spawn_time + timedelta(minutes=30)
    capture_code = uuid.uuid4().hex[:12].upper()  # Code unique 12 caractères
    
    # Enregistrer dans la base de données
    spawn_id = db.spawn_pokemon_in_db(pokedex_num, spawn_time, despawn_time, capture_code, niveau)
    
    fichier, embed = display.make_spawn_file_and_embed(pokemon_name, pokedex_str, niveau, sexe, despawn_time, capture_code)
    if not fichier or not embed:
        return
    await channel.send(content="@everyone", embed=embed, file=fichier, allowed_mentions=discord.AllowedMentions(everyone=True))

@spawn_pokemon.before_loop
async def avant_spawn():
    await bot.wait_until_ready()
    maintenant = datetime.now()
    # Calculer la prochaine heure pile
    prochaine_heure_pile = (maintenant + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    delai_secondes = (prochaine_heure_pile - maintenant).total_seconds()
    # Attendre jusqu'à la prochaine heure pile
    await asyncio.sleep(delai_secondes)


########---ÉVÉNEMENTS---##################################################################################################################


# Wrapper pour track_command qui injecte history_manager
def track_command(command_name: str):
    return create_track_command(command_name, history_manager)

@bot.event
async def on_message(message):
    await on_message_handler(message, bot)
    if message.author == bot.user:
        return

    if message.content == "Feur" or message.content == "feur":
        await message.channel.send("TA GUEULE")
    
    await bot.process_commands(message)

#ajout d'un nouvel utilisateur à la base de données lorsqu'il rejoint le serveur (table User)
@bot.event
async def on_member_join(member):
    await on_member_join_handler(member, ACCUEIL_CHANNEL_ID, bot)


########---COMMANDES---##################################################################################################################

#/letsgo
@bot.tree.command(name="letsgo", description="Commence ton aventure Pokémon !")
@track_command("letsgo")
async def letsgo(interaction: discord.Interaction):
    await letsgo_handler(interaction)


#/randomstarter
@bot.tree.command(name="randomstarter", description="Obtenir un starter Pokémon aléatoire")
@track_command("randomstarter")
async def randomstarter(interaction: discord.Interaction):
    await randomstarter_handler(interaction, starters, bot, ADVENTURE_CHANNEL_ID)
 
 
#/starterquiz
@bot.tree.command(name="starterquiz", description="Choisis ton starter Pokémon via un quiz de questions")
@track_command("starterquiz")
async def starterquiz(interaction: discord.Interaction):
    await starterquiz_handler(interaction, starters, Questions, alt.quiz_sessions)
    

#/speak_about
@bot.tree.command(name="speak_about", description="Vérifie si un sujet existe dans l'arbre de questions du quiz")
@app_commands.describe(sujet="Le mot ou sujet à rechercher dans l'arbre")
@track_command("speak_about")
async def speak_about(interaction: discord.Interaction, sujet: str):
    await speak_about_handler(interaction, sujet)


#/starterchoice
@bot.tree.command(name="starterchoice", description="Choisis ton starter via son nom ou numéro")
@app_commands.describe(choice="Nom (Bulbizarre) ou numéro (1, 0001)")
@track_command("starterchoice")
async def starterchoice(interaction: discord.Interaction, choice: str):
    await starterchoice_handler(interaction, choice, starters, bot, ADVENTURE_CHANNEL_ID)


#/capture
@bot.tree.command(name="capture", description="Capture un Pokémon sauvage avec son code")
@app_commands.describe(code="Le code de capture affiché lors du spawn")
@track_command("capture")
async def capture(interaction: discord.Interaction, code: str):
    await capture_handler(interaction, code, bot, ADVENTURE_CHANNEL_ID)


#/derniere commande
@bot.tree.command(name="derniere_commande", description="Affiche ta dernière commande utilisée")
@track_command("derniere_commande")
async def derniere_commande(interaction: discord.Interaction):
    await derniere_commande_handler(interaction, history_manager)


#/historique
@bot.tree.command(name="historique", description="Affiche tout ton historique de commandes")
@track_command("historique")
async def historique(interaction: discord.Interaction):
    await historique_handler(interaction, history_manager)


#/vider historique
@bot.tree.command(name="vider_historique", description="Supprime tout ton historique de commandes")
@track_command("vider_historique")
async def vider_historique(interaction: discord.Interaction):
    await vider_historique_handler(interaction, history_manager)


#/team
@bot.tree.command(name="team", description="Affiche ton équipe Pokémon")
@track_command("team")
async def team(interaction: discord.Interaction):
    await team_handler(interaction)


#/pokedex
@bot.tree.command(name="pokedex", description="Feuilleter le Pokédex par pages (6x5)")
@track_command("pokedex")
async def pokedex(interaction: discord.Interaction):
    await pokedex_handler(interaction)


#/pc
@bot.tree.command(name="pc", description="Accède à ton PC pour voir tes Pokémon stockés")
@track_command("pc")
async def pc(interaction: discord.Interaction):
    await pc_handler(interaction)


###########LAnCEMENT DU BOT##########################################################################################################

# Lancement du bot
if token:
    bot.run(token)
else:
    print("Erreur : Le token est introuvable. Vérifie le fichier .env")