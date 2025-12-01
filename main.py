import discord  # Bibliothèque Discord pour créer le bot (usage: décorateurs/embeds, multiples)
from discord import app_commands  # Commandes slash Discord (usage: décorateurs @app_commands, ~240, ~420)
from discord.ext import commands, tasks  # Extensions Discord pour commandes et tâches récurrentes (usage: bot setup ~16, tasks.loop ~93)
from dotenv import load_dotenv  # Charger les variables d'environnement depuis .env (usage: ~18)
import os  # Gestion des chemins et variables système (usage: ~19)
import random  # Génération de nombres aléatoires (usage: spawn/capture/randomstarter ~104, ~335, ~280)
import asyncio  # Programmation asynchrone (usage: avant_spawn sleep ~140)
from functools import wraps  # Wrapper pour préserver les métadonnées de fonctions (usage: track_command ~230)
from PIL import Image  # Manipulation d'images (usage: spawn image ~120, team grid ~540)
from io import BytesIO  # Gestion des flux de bytes en mémoire (usage: team image buffer ~585)
import DatabaseFunction as db  # Fonctions de base de données personnalisées (usage: nombreuses: init, queries)
import OtherCode as alt  # Fonctions utilitaires personnalisées (usage: quiz, starters ~200+)
from Classes import PokedexView, TeamView, PCView, QuizView  # Vues Discord personnalisées (Pokédex, équipe, PC, quiz) (usage: instantiation ~500, ~620)
from HistoryFunctions import HistoryManager  # Gestionnaire d'historique des commandes (usage: instance ~24, usage décorateur ~230)
from datetime import datetime, timedelta  # Gestion des dates et durées (usage: on_ready ~66, spawn ~112, before_loop ~136)
import uuid  # Génération d'identifiants uniques (usage: code capture spawn ~116)
import DisplayFunction as display  # Fonctions d'affichage centralisées (usage: spawns, captures, historique, team)
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

        
        
# Dictionnaire des starters
starters = {
    1: ("Bulbizarre", "0001"),
    2: ("Salamèche", "0004"),
    3: ("Carapuce", "0007"),
    4: ("Pikachu", "0025"),
    5: ("Germignon", "0152"),
    6: ("Héricendre", "0155"),
    7: ("Kaiminus", "0158"),
    8: ("Arcko", "0252"),
    9: ("Poussifeu", "0255"),
    10: ("Gobou", "0258"),
    11: ("Tortipouss", "0387"),
    12: ("Ouisticram", "0390"),
    13: ("Tiplouf", "0393"),
    14: ("Vipelierre", "0495"),
    15: ("Gruikui", "0498"),
    16: ("Moustillon", "0501"),
    17: ("Marisson", "0650"),
    18: ("Feunnec", "0653"),
    19: ("Grenousse", "0656")
}

Questions = alt.Arbre("Q1 : Dans la vie, es-tu quelqu'un de plutôt énergique et impulsif ?",
                #oui
                    alt.Arbre("Q2 : Aimes-tu attirer toute l'attention sur toi ?",
                        #oui
                            alt.Arbre("Q3 : Préfères-tu utiliser la magie plutôt que tes poings ?",
                                #oui
                                    "Feunnec",
                                #non
                                    alt.Arbre("Q4 : Voudrais-tu être la mascotte aimée de tous ?",
                                        #oui
                                            "Pikachu",
                                        #non
                                            "Ouisticram"
                                    )
                            ),
                        #non
                            alt.Arbre("Q3 : La force brute est-elle la solution à tout ?",
                                #oui
                                    alt.Arbre("Q4 : Aimes-tu manger autant que te battre ?",
                                        #oui
                                            "Gruikui",
                                        #non
                                            alt.Arbre("Q5 : Es-tu un peu hyperactif et mordant ?",
                                                #oui
                                                    "Kaiminus",
                                                #non
                                                    "Poussifeu"
                                            )
                                    ),
                                #non
                                    alt.Arbre("Q4 : Te considères-tu comme 'Cool' et rapide ?",
                                        #oui
                                            alt.Arbre("Q5 : As-tu un côté un peu sombre ou ninja ?",
                                                #oui 
                                                    "Grenousse",
                                                #non
                                                    "Arcko"
                                            ),
                                        #non 
                                            alt.Arbre("Q5 : As-tu une flamme intérieure qui ne s'éteint jamais ?",
                                                #oui
                                                    "Salamèche",
                                                #non
                                                    "Héricendre"
                                            )
                                    )
                            )
                    ),        
                #non
                    alt.Arbre("Q2 : Te sens-tu plus à l'aise dans l'eau que sur terre ?",
                        #oui
                            alt.Arbre("Q3 : L'honneur et la discipline sont-ils importants pour toi ?",
                                #oui
                                    alt.Arbre("Q4 : Utilises-tu des armes (coquillages, épées) ?",
                                        #oui
                                            "Moustillon",
                                        #non
                                            "Tiplouf"
                                    ),
                                #non
                                    alt.Arbre("Q4 : Aimes-tu avoir une carapace solide ?",
                                        #oui
                                            "Carapuce",
                                        #non
                                            "Gobou"
                                    )
                            ),
                        #non
                            alt.Arbre("Q3 : Aimes-tu te prélasser au soleil ?",
                                #oui
                                    alt.Arbre("Q4 : As-tu une fleur ou une plante qui pousse sur toi ?",
                                        #oui
                                            alt.Arbre("Q5 : Es-tu le tout premier, le numéro 1 ?",
                                                #oui
                                                    "Bulbizarre",
                                                #non
                                                    "Germignon"
                                            ),
                                        #non
                                            "Vipelierre"
                                    ),
                                #non
                                    alt.Arbre("Q4 : Aimes-tu la solidité et la protection ?",
                                        #oui
                                            alt.Arbre("Q5 : Portes-tu une armure d'épines ?",
                                                #oui
                                                    "Marisson",
                                                #non
                                                    "Tortipouss"
                                            ),
                                        #non
                                            "Arcko"
                                    )
                            )
                    )
            )

########---ÉVÉNEMENTS---##################################################################################################################

def track_command(command_name: str):
    """Décorateur pour enregistrer les commandes dans l'historique"""
    def decorator(func):
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, **kwargs):
            # Enregistrer la commande dans l'historique (DB)
            history_manager.add_command(interaction.user.id, command_name, interaction.user.name)
            
            # Exécuter la commande originale
            return await func(interaction, **kwargs)
        return wrapper
    return decorator

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "Feur" or message.content == "feur":
        await message.channel.send("TA GUEULE")
    
    await bot.process_commands(message)

#ajout d'un nouvel utilisateur à la base de données lorsqu'il rejoint le serveur (table User)
@bot.event
async def on_member_join(member):
    # Ajouter le nouvel utilisateur dans la base de données
    db.add_new_user(member.id, member.name)
    
    # ID du channel d'accueil (récupéré de ton ancien code)
    Accueil_channel = bot.get_channel(ACCUEIL_CHANNEL_ID)
    if Accueil_channel:
        await Accueil_channel.send(f"Bienvenue sur le serveur {member.mention} !")





########---COMMANDES---##################################################################################################################

#/letsgo
@bot.tree.command(name="letsgo", description="Commence ton aventure Pokémon !")
@track_command("letsgo")
async def letsgo(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    # Sécurité : on s'assure que le joueur est bien dans la table User
    db.add_new_user(user_id, user_pseudo)
    
    if db.has_starter(user_id):
        await interaction.response.send_message("Tu as déjà commencé ton aventure ! Utilise ton PC ou ton équipe pour voir tes Pokémons.", ephemeral=True)
    else:
        # Message d'intro + présentation des trois possibilités
        intro = (
            f"Bonjour {interaction.user.mention} ! Bienvenue dans le monde des Pokémon.\n"
            "Pour commencer ton voyage, tu dois choisir ton premier compagnon.\n\n"
            "Choisis comment obtenir ton starter :\n"
            "• `/randomstarter` : Starter aléatoire\n"
            "• `/starterquiz` : Quiz interactif pour te guider\n"
            "• `/starterchoice` : Choisis par nom ou numéro"
        )
        embed = display.make_letsgo_intro_embed(intro)
        channel = bot.get_channel(ADVENTURE_CHANNEL_ID)
        if channel:
            await channel.send(f"{interaction.user.mention} a lancé l'aventure. Choisis une option avec les commandes slash.")
            embed.set_footer(text=f"Ton aventure commence dans le salon {channel.name}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)





#/randomstarter
@bot.tree.command(name="randomstarter", description="Obtenir un starter Pokémon aléatoire")
@track_command("randomstarter")
async def randomstarter(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_pseudo = interaction.user.name

    # 1. Vérification : Le joueur a-t-il déjà commencé l'aventure ?
    if db.has_starter(user_id):
        await interaction.response.send_message("Tu as déjà choisi un starter ! Regarde dans ton PC.", ephemeral=True)
        return
    
    # Choix aléatoire
    resultat = random.randint(1, 19)
    
    embed, fichier_image, starter_nom, pokedex_num_int, sexe, niveau = await alt.generate_starter_embed(resultat, starters, "Ton starter aléatoire !")
    
    # --- SAUVEGARDE EN BASE DE DONNÉES ---
    db.add_new_user(user_id, user_pseudo)
    db.init_player_pc(user_id, user_pseudo, starter_nom)
    
    # Créer l'instance Pokémon individuelle dans AllPokemons avec Location='Team'
    pokemon_instance_id = db.create_pokemon_instance(pokedex_num_int, niveau, sexe, user_id, user_pseudo, location="Team")
    
    # Ajouter l'Id_Pokemon à l'équipe (et non le Pokedex_Number)
    if pokemon_instance_id:
        db.add_pokemon_to_team(user_id, pokemon_instance_id)
        db.update_user_starter_id(user_id, pokemon_instance_id)
    
    channel = bot.get_channel(ADVENTURE_CHANNEL_ID)
    if channel:
        # Message public visible par tous
        await channel.send(f"{interaction.user.mention} a choisi **{starter_nom}** !")
        await interaction.response.send_message(embed=embed, file=fichier_image, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, file=fichier_image, ephemeral=True)
 
 
    
#/starterquiz
@bot.tree.command(name="starterquiz", description="Choisis ton starter Pokémon via un quiz de questions")
@track_command("starterquiz")
async def starterquiz(interaction: discord.Interaction):
    user_id = interaction.user.id
    if db.has_starter(user_id):
        await interaction.response.send_message("Tu as déjà un starter.", ephemeral=True)
        return
    alt.quiz_sessions[user_id] = Questions
    embed = alt.build_question_embed(Questions)
    view = QuizView(user_id, starters, db, Questions, alt.quiz_sessions)
    # Version entièrement éphémère (visible uniquement par l'utilisateur)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    


#/speak_about
@bot.tree.command(name="speak_about", description="Vérifie si un sujet existe dans l'arbre de questions du quiz")
@app_commands.describe(sujet="Le mot ou sujet à rechercher dans l'arbre")
@track_command("speak_about")
async def speak_about(interaction: discord.Interaction, sujet: str):
    """Parcourt l'arbre de quiz pour vérifier si un sujet existe"""
    
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




#/starterchoice
@bot.tree.command(name="starterchoice", description="Choisis ton starter via son nom ou numéro")
@app_commands.describe(choice="Nom (Bulbizarre) ou numéro (1, 0001)")
@track_command("starterchoice")
async def starterchoice(interaction: discord.Interaction, choice: str):
    user_id = interaction.user.id
    if db.has_starter(user_id):
        await interaction.response.send_message("Tu as déjà un starter.", ephemeral=True)
        return

    starter_id = alt.resolve_starter(choice, starters)
    if starter_id is None:
        await interaction.response.send_message("Starter inconnu. Fournis un nom ou numéro valide.", ephemeral=True)
        return

    embed, fichier_image, starter_nom, pokedex_num_int, sexe, niveau = await alt.generate_starter_embed(starter_id, starters, "Ton starter choisi !")
    # Sauvegarde BD
    db.add_new_user(user_id, interaction.user.name)
    db.init_player_pc(user_id, interaction.user.name, starter_nom)
    
    # Créer l'instance Pokémon individuelle avec Location='Team'
    pokemon_instance_id = db.create_pokemon_instance(pokedex_num_int, niveau, sexe, user_id, interaction.user.name, location="Team")
    
    # Ajouter l'Id_Pokemon à l'équipe
    if pokemon_instance_id:
        db.add_pokemon_to_team(user_id, pokemon_instance_id)
        db.update_user_starter_id(user_id, pokemon_instance_id)
    
    channel = bot.get_channel(ADVENTURE_CHANNEL_ID)
    if channel:
        # Message public visible par tous
        await channel.send(f"{interaction.user.mention} a choisi **{starter_nom}** !")
        await interaction.response.send_message(embed=embed, file=fichier_image, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, file=fichier_image, ephemeral=True)




#/capture
@bot.tree.command(name="capture", description="Capture un Pokémon sauvage avec son code")
@app_commands.describe(code="Le code de capture affiché lors du spawn")
@track_command("capture")
async def capture(interaction: discord.Interaction, code: str):
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    # Vérifier si le joueur a un starter
    if not db.has_starter(user_id):
        await interaction.response.send_message("Tu dois d'abord obtenir un starter avec /letsgo !", ephemeral=True)
        return
    
    # Récupérer le spawn depuis la DB
    spawn_data = db.get_spawn_by_code(code.upper())
    if not spawn_data:
        await interaction.response.send_message("Code invalide, Pokémon déjà capturé ou temps de capture dépassé.", ephemeral=True)
        return
    
    # Vérifier si le spawn est encore valide (pas expiré)
    despawn_time = datetime.fromisoformat(spawn_data["despawn_time"])
    if datetime.now() > despawn_time:
        db.delete_spawn(spawn_data["spawn_id"])
        await interaction.response.send_message("Code invalide, Pokémon déjà capturé ou temps de capture dépassé.", ephemeral=True)
        return
    
    # Récupérer le CatchRate depuis la table Pokedex
    conn = db.sqlite3.connect(db.DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT CatchRate FROM Pokedex WHERE Id = ?", (spawn_data["pokedex_str"],))
    row = cursor.fetchone()
    conn.close()
    catch_rate = row[0] if row else 45
    
    # Logique de capture : random(1-255) <= CatchRate
    roll = random.randint(1, 255)
    success = roll <= catch_rate
    
    pokemon_name = spawn_data["nom"]
    
    if success:
        # Capture réussie
        # Le spawn sera nettoyé automatiquement lorsqu'il sera expiré
        
        # Créer l'instance Pokémon capturée
        sexe = random.choice(["♂", "♀"]) 
        niveau = spawn_data["niveau"]  # Le niveau du spawn
        
        # D'abord créer avec Location='PC' par défaut
        pokemon_instance_id = db.create_pokemon_instance(
            spawn_data["pokedex_id"], 
            niveau, 
            sexe, 
            user_id, 
            user_pseudo,
            location="PC"
        )
        
        # Ajouter le Pokémon à l'équipe (Id_Pokemon, pas Pokedex_Number)
        # add_pokemon_to_team met automatiquement Location='Team' si réussi
        added = False
        if pokemon_instance_id:
            added = db.add_pokemon_to_team(user_id, pokemon_instance_id)
            # Si l'équipe est pleine, ajouter au PC
            if not added:
                db.add_pokemon_to_pc(user_id, pokemon_instance_id)
        
        embed = display.make_capture_success_embed(interaction.user.mention, pokemon_name, niveau, added, roll, catch_rate)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Annonce publique dans le channel d'aventure
        channel = bot.get_channel(ADVENTURE_CHANNEL_ID)
        if channel:
            await channel.send(f"{interaction.user.mention} a capturé le **{pokemon_name}** sauvage !")
    else:
        # Capture ratée
        embed = display.make_capture_failed_embed(pokemon_name, roll, catch_rate)
        await interaction.response.send_message(embed=embed, ephemeral=True)


#/derniere commande
@bot.tree.command(name="derniere_commande", description="Affiche ta dernière commande utilisée")
@track_command("derniere_commande")
async def derniere_commande(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    # Récupérer la dernière commande (avant celle-ci)
    all_cmds = history_manager.get_all_user_commands(user_id)
    
    if len(all_cmds) <= 1:
        await interaction.response.send_message("Aucune commande précédente trouvée.", ephemeral=True)
        return
    
    # La première est "derniere_commande", on veut la seconde
    last_cmd = all_cmds[1]
    
    embed = display.make_last_command_embed(last_cmd['command'], user_pseudo, last_cmd['timestamp'])
    
    await interaction.response.send_message(embed=embed)


#/historique
@bot.tree.command(name="historique", description="Affiche tout ton historique de commandes")
@track_command("historique")
async def historique(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    # Récupérer l'historique depuis la base de données (complet)
    history_list = history_manager.get_all_user_commands(user_id)
    
    if not history_list:
        await interaction.response.send_message("Tu n'as pas encore utilisé de commandes.", ephemeral=True)
        return
    
    # Créer l'embed avec pagination si nécessaire
    embed = display.make_history_embed(history_list, user_pseudo)
    
    await interaction.response.send_message(embed=embed)


#/vider historique
@bot.tree.command(name="vider_historique", description="Supprime tout ton historique de commandes")
@track_command("vider_historique")
async def vider_historique(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    # Supprimer de la mémoire
    history_manager.clear_user_history(user_id)
    
    # Supprimer de la base de données
    db.clear_user_command_history(user_id)
    
    embed = display.make_history_cleared_embed(user_pseudo)
    
    await interaction.response.send_message(embed=embed)



#/team
@bot.tree.command(name="team", description="Affiche ton équipe Pokémon")
@track_command("team")
async def team(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_pseudo = interaction.user.name
    
    # Récupérer l'équipe du joueur
    team_pokemon = db.get_user_team(user_id)
    
    # Construire l'image et l'embed via DisplayFunction
    file_img = display.make_team_grid_file(team_pokemon, db)
    embed = display.make_team_embed(user_pseudo)
    
    # Créer la vue avec les boutons
    view = TeamView(user_id, team_pokemon, db)
    
    await interaction.response.send_message(embed=embed, file=file_img, view=view, ephemeral=True)



#/pokedex
@bot.tree.command(name="pokedex", description="Feuilleter le Pokédex par pages (6x5)")
@track_command("pokedex")
async def pokedex(interaction: discord.Interaction):
    user_id = interaction.user.id
    view = PokedexView(user_id, db, initial_gen=1, page_size=30)
    file_img = view._build_page_image()
    embed = view._build_embed()
    await interaction.response.send_message(embed=embed, file=file_img, view=view, ephemeral=True)



#/pc
@bot.tree.command(name="pc", description="Accède à ton PC pour voir tes Pokémon stockés")
@track_command("pc")
async def pc(interaction: discord.Interaction):
    user_id = interaction.user.id
    
    # Vérifier si le joueur a un PC
    if not db.has_starter(user_id):
        await interaction.response.send_message("Tu dois d'abord obtenir un starter avec /letsgo !", ephemeral=True)
        return
    
    view = PCView(user_id, db, box_number=1)
    file_img = view._build_box_image()
    embed = view._build_embed()
    await interaction.response.send_message(embed=embed, file=file_img, view=view, ephemeral=True)




###########LAnCEMENT DU BOT##########################################################################################################

# Lancement du bot
if token:
    bot.run(token)
else:
    print("Erreur : Le token est introuvable. Vérifie le fichier .env")