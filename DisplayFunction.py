import discord  # Construction d'embeds et fichiers Discord (usage: helpers d'affichage)
from io import BytesIO  # Buffer mémoire pour images
from PIL import Image, ImageDraw, ImageFont  # Manipulation d'images et polices
from datetime import datetime  # Formatage/affichage des dates
import random  # Choix aléatoires (quiz, etc.)


# ---------- rognage horaire ----------

def trim_timestamp(ts: str) -> str:
    if not ts:
        return ""
    return ts.split(".")[0] if "." in ts else ts


# ---------- Spawns ----------

def make_spawn_file_and_embed(pokemon_name: str, pokedex_str: str, niveau: int, sexe: str, despawn_time: datetime, capture_code: str):
    """Construit le fichier image + embed pour un spawn de Pokémon."""
    image_path = f"PokeSprites/Poke{pokedex_str}.png"
    try:
        img = Image.open(image_path)
        width, height = img.size
        img_cropped = img.crop((0, 0, width // 2, height))
        img_resized = img_cropped.resize((img_cropped.width * 2, img_cropped.height * 2), Image.Resampling.NEAREST)
        img_bytes = BytesIO()
        img_resized.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        file_obj = discord.File(img_bytes, filename=f"Poke{pokedex_str}.png")
    except Exception as e:
        print(f"Erreur image spawn: {e}")
        return None, None

    expiration_str = despawn_time.strftime("%H:%M")
    duree_minutes = 30
    embed = discord.Embed(
        title=f"Un {pokemon_name} sauvage apparaît !",
        description=(
            f"Un {pokemon_name} sauvage est apparu ! Pokédex #{pokedex_str}\n"
            f"Temps pour le capturer: {duree_minutes} min (jusqu'à {expiration_str})."
        ),
        color=discord.Color.green()
    )
    embed.add_field(name="Niveau", value=f"Niv. {niveau}", inline=True)
    embed.add_field(name="Sexe", value=sexe, inline=True)
    embed.set_image(url=f"attachment://Poke{pokedex_str}.png")
    embed.set_footer(text=f"Code de capture : {capture_code} • Utilise /capture pour essayer !")
    return file_obj, embed


# ---------- Letsgo ----------

def make_letsgo_intro_embed(intro: str):
    embed = discord.Embed(title="Commence ton aventure !", description=intro, color=discord.Color.blue())
    embed.set_footer(text="Utilise l'une des commandes slash ci-dessus")
    return embed


# ---------- Capture ----------

def make_capture_success_embed(user_mention: str, pokemon_name: str, niveau: int, added: bool, roll: int, catch_rate: int):
    embed = discord.Embed(
        title="Capture réussie !",
        description=f"Félicitations {user_mention} ! Tu as capturé **{pokemon_name}** (Niv. {niveau}) !",
        color=discord.Color.gold()
    )
    if not added:
        embed.add_field(name="⚠️ Équipe pleine", value="Le Pokémon a été envoyé au PC.", inline=False)
    embed.set_footer(text=f"Roll: {roll}/{catch_rate}")
    return embed


def make_capture_failed_embed(pokemon_name: str, roll: int, catch_rate: int):
    embed = discord.Embed(
        title="Capture ratée...",
        description=f"**{pokemon_name}** s'est échappé ! Réessaye avant qu'il ne disparaisse.",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Roll: {roll}/{catch_rate}")
    return embed


# ---------- Historique ----------

def make_last_command_embed(command_name: str, user_pseudo: str, timestamp_str: str):
    ts = trim_timestamp(timestamp_str)
    embed = discord.Embed(
        title="🕒 Dernière commande",
        description=f"**/{command_name}**\nUtilisateur: **{user_pseudo}**",
        color=discord.Color.yellow()
    )
    embed.add_field(name="Date", value=ts, inline=False)
    return embed


def make_history_embed(history_list: list, user_pseudo: str):
    embed = discord.Embed(
        title="📜 Historique des commandes",
        description=f"Utilisateur: **{user_pseudo}**\nTotal: **{len(history_list)}** commande(s)",
        color=discord.Color.yellow()
    )
    display_count = min(10, len(history_list))
    for i, cmd in enumerate(history_list[:display_count]):
        ts = trim_timestamp(cmd.get('timestamp', ''))
        embed.add_field(name=f"{i+1}. /{cmd.get('command','')}", value=f"📅 {ts}", inline=False)
    if len(history_list) > 10:
        embed.set_footer(text=f"Affichage des 10 dernières sur {len(history_list)} commandes")
    return embed


def make_history_cleared_embed(user_pseudo: str):
    return discord.Embed(
        title="🗑️ Historique vidé",
        description=f"Utilisateur: **{user_pseudo}**\nTon historique de commandes a été complètement supprimé.",
        color=discord.Color.yellow()
    )


# ---------- Team ----------

def make_team_grid_file(team_pokemon: list, db_module):
    """Construit l'image 3x2 de l'équipe et retourne un discord.File nommé team.png"""
    pokemon_width, pokemon_height = 200, 200
    grid_image = Image.new('RGBA', (pokemon_width * 3, pokemon_height * 2), (255, 255, 255, 0))

    for idx, pokemon_id in enumerate(team_pokemon):
        col = idx % 3
        row = idx // 3
        x = col * pokemon_width
        y = row * pokemon_height

        if pokemon_id is None:
            image_path = "PokeSprites/Poke0000.png"
        else:
            pokemon_instance = db_module.get_pokemon_instance(pokemon_id)
            if pokemon_instance:
                pokedex_number = pokemon_instance["pokedex_number"]
                pokedex_str = f"{pokedex_number:04d}"
                pokemon_data = db_module.get_pokemon_data(pokedex_str)
                if pokemon_data and pokemon_data.get("image"):
                    image_path = f"PokeSprites/{pokemon_data['image']}"
                else:
                    image_path = "PokeSprites/Poke0000.png"
            else:
                image_path = "PokeSprites/Poke0000.png"

        try:
            poke_img = Image.open(image_path)
            width, height = poke_img.size
            poke_cropped = poke_img.crop((0, 0, width // 2, height))
            poke_resized = poke_cropped.resize((pokemon_width, pokemon_height), Image.Resampling.NEAREST)
            grid_image.paste(poke_resized, (x, y))
        except Exception as e:
            print(f"Erreur chargement image team slot {idx}: {e}")
            try:
                fallback = Image.open("PokeSprites/Poke0000.png")
                width, height = fallback.size
                fallback_cropped = fallback.crop((0, 0, width // 2, height))
                fallback_resized = fallback_cropped.resize((pokemon_width, pokemon_height), Image.Resampling.NEAREST)
                grid_image.paste(fallback_resized, (x, y))
            except Exception:
                pass

    img_bytes = BytesIO()
    grid_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return discord.File(img_bytes, filename="team.png")


def make_team_embed(user_pseudo: str):
    embed = discord.Embed(title=f"ÉQUIPE DE {user_pseudo}", color=discord.Color.blue())
    embed.set_image(url="attachment://team.png")
    embed.set_footer(text="Clique sur un bouton pour voir les détails d'un Pokémon")
    return embed


# ---------- Team Details ----------

def make_team_slot_detail_embed(current_title: str, slot_index: int, pokemon_instance: dict, image_path: str):
    pokemon_nom = pokemon_instance["name"]
    pokedex_number = pokemon_instance["pokedex_number"]
    niveau = pokemon_instance["niveau"]
    sexe = pokemon_instance["sexe"]
    pv = pokemon_instance["pv"]
    attaque = pokemon_instance["attaque"]
    defense = pokemon_instance["defense"]
    attaque_spec = pokemon_instance["attaque_spec"]
    defense_spec = pokemon_instance["defense_spec"]
    vitesse = pokemon_instance["vitesse"]
    type1 = pokemon_instance["type1"]
    type2 = pokemon_instance["type2"]

    types_str = f"{type1}" + (f"/{type2}" if type2 else "")
    new_embed = discord.Embed(
        title=current_title,
        description=(
            f"**Slot {slot_index + 1} - {pokemon_nom}** {sexe}\n"
            f"**Pokédex:** #{pokedex_number:04d} | **Type:** {types_str} | **Niveau:** {niveau}"
        ),
        color=discord.Color.blue()
    )
    new_embed.add_field(name="💚 PV", value=str(pv), inline=True)
    new_embed.add_field(name="⚔️ Attaque", value=str(attaque), inline=True)
    new_embed.add_field(name="🛡️ Défense", value=str(defense), inline=True)
    new_embed.add_field(name="✨ Att. Spé", value=str(attaque_spec), inline=True)
    new_embed.add_field(name="🔰 Déf. Spé", value=str(defense_spec), inline=True)
    new_embed.add_field(name="⚡ Vitesse", value=str(vitesse), inline=True)

    try:
        img = Image.open(image_path)
        width, height = img.size
        img_cropped = img.crop((0, 0, width // 2, height))
        new_size = (img_cropped.width * 2, img_cropped.height * 2)
        img_resized = img_cropped.resize(new_size, Image.Resampling.NEAREST)
        img_bytes = BytesIO()
        img_resized.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        file_detail = discord.File(img_bytes, filename="detail_current.png")
        new_embed.set_thumbnail(url="attachment://detail_current.png")
    except Exception:
        file_detail = None
    new_embed.set_footer(text="Clique sur un autre bouton pour voir un autre Pokémon")
    return new_embed, file_detail

# ---------- Quiz ----------

def build_question_embed(node) -> discord.Embed:
    return discord.Embed(title="Quiz Starter", description=getattr(node, "racine", str(node)), color=discord.Color.red())

async def generate_starter_embed(starter_id: int, starters: dict, title: str):
    starter_nom, pokedex_num_str = starters[starter_id]
    sexe = random.choice(["♂", "♀"])  # noqa: F821 (random imported indirectly by caller)
    niveau = 5
    fichier_image = None
    try:
        image_path = f"PokeSprites/Poke{pokedex_num_str}.png"
        img = Image.open(image_path)
        width, height = img.size
        img_cropped = img.crop((0, 0, width // 2, height))
        new_size = (img_cropped.width * 2, img_cropped.height * 2)
        img_resized = img_cropped.resize(new_size, Image.Resampling.NEAREST)
        img_bytes = BytesIO()
        img_resized.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        fichier_image = discord.File(img_bytes, filename=f"Poke{pokedex_num_str}.png")
    except Exception as e:
        print(f"Erreur image quiz: {e}")

    embed = discord.Embed(
        title=title,
        description=f"Félicitations ! **{starter_nom}** rejoint ton équipe.",
        color=discord.Color.red()
    )
    embed.add_field(name="Niveau", value=f"Niv. {niveau}", inline=True)
    embed.add_field(name="Sexe", value=sexe, inline=True)
    if fichier_image:
        embed.set_image(url=f"attachment://Poke{pokedex_num_str}.png")
    embed.set_footer(text=f"Pokédex #{pokedex_num_str} | Ajouté à l'équipe")
    return embed, fichier_image, starter_nom, int(pokedex_num_str), sexe, niveau


def make_quiz_confirmed_embed(starter_nom: str, niveau: int, sexe: str, pokedex_num_int: int):
    embed = discord.Embed(
        title="Starter confirmé !",
        description=f"**{starter_nom}** rejoint officiellement ton équipe.",
        color=discord.Color.red()
    )
    embed.add_field(name="Niveau", value=f"Niv. {niveau}", inline=True)
    embed.add_field(name="Sexe", value=sexe, inline=True)
    embed.set_footer(text=f"Pokédex #{pokedex_num_int:04d} | Ajouté à l'équipe")
    return embed


# ---------- Pokédex ----------

def make_pokedex_page_image(db_module, gen: int, page: int, page_size: int, search_term: str | None):
    cols, rows = 6, 5 # Grille 6x5
    tile_w, tile_h = 540, 540 # Taille d'une case
    label_h = 70 # Espace pour le nom du Pokémon
    header_h = 120 # Espace pour le titre

    offset = page * page_size
    if search_term:
        entries = db_module.get_pokedex_search(gen, search_term, limit=page_size, offset=offset)
    else:
        entries = db_module.get_pokedex_range(gen, limit=page_size, offset=offset)

    W, H = cols * tile_w, rows * tile_h + header_h
    canvas = Image.new('RGBA', (W, H), (70, 70, 70, 255))
    draw = ImageDraw.Draw(canvas)

    # Titre
    try:
        title_font = ImageFont.truetype("arial.ttf", 80)
    except Exception:
        try:
            title_font = ImageFont.truetype("Arial.ttf", 80)
        except Exception:
            title_font = ImageFont.load_default()
    title_text = "POKÉDEX"
    try:
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        text_w = bbox[2] - bbox[0]
    except Exception:
        text_w = len(title_text) * 40
    title_x = (W - text_w) // 2
    draw.text((title_x, 20), title_text, fill=(220, 220, 220, 255), font=title_font)

    for idx in range(rows * cols):
        col = idx % cols
        row = idx // cols
        x0 = col * tile_w
        y0 = row * tile_h + header_h
        sprite_box = (x0 + 20, y0 + 20, x0 + tile_w - 20, y0 + tile_h - label_h - 20)
        label_y = y0 + tile_h - label_h
        draw.rectangle((sprite_box[0], sprite_box[1], sprite_box[2], y0 + tile_h - label_h), fill=(45, 45, 45, 255))

        if idx < len(entries):
            e = entries[idx]
            poke_id_str = e["id"]
            nom = e["nom"]
            img_file = e["image"] or f"Poke{poke_id_str}.png"
            img_path = f"PokeSprites/{img_file}"
            try:
                img = Image.open(img_path)
            except Exception:
                img = Image.open("PokeSprites/Poke0000.png")
            w, h = img.size
            img = img.crop((0, 0, w // 2, h))
            avail_w = sprite_box[2] - sprite_box[0]
            avail_h = sprite_box[3] - sprite_box[1]
            scale = min(avail_w / img.width, avail_h / img.height)
            new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
            img = img.resize(new_size, Image.Resampling.NEAREST)
            paste_x = sprite_box[0] + (avail_w - new_size[0]) // 2
            paste_y = sprite_box[1] + (avail_h - new_size[1]) // 2
            canvas.paste(img, (paste_x, paste_y))
            draw.rectangle((x0 + 20, label_y, x0 + tile_w - 20, y0 + tile_h - 20), fill=(55, 55, 55, 255))
            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except Exception:
                try:
                    font = ImageFont.truetype("Arial.ttf", 32)
                except Exception:
                    font = ImageFont.load_default()
            draw.text((x0 + 30, label_y + 18), f"#{int(poke_id_str):04d} {nom}", fill=(220, 220, 220, 255), font=font)
        else:
            draw.rectangle((x0 + 20, y0 + 20, x0 + tile_w - 20, y0 + tile_h - 20), outline=(80, 80, 80, 255), fill=(50, 50, 50, 255))

    img_bytes = BytesIO()
    canvas.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return discord.File(img_bytes, filename="pokedex_page.png")


def make_pokedex_embed(gen: int, page: int, page_count: int, search_term: str | None):
    subtitle = f"Page {page + 1}/{page_count}"
    if search_term:
        subtitle += f" • Filtre: {search_term}"
    embed = discord.Embed(title=f"Pokédex - Gen {gen}", description=subtitle, color=discord.Color.blue())
    embed.set_image(url="attachment://pokedex_page.png")
    return embed


# ---------- PC ----------

def make_pc_box_image(db_module, user_id: int, box_number: int):
    cols, rows = 6, 5
    tile_w, tile_h = 540, 540
    label_h = 70
    header_h = 120

    box_pokemon = db_module.get_pc_pokemon(user_id, box_number)
    W, H = cols * tile_w, rows * tile_h + header_h
    canvas = Image.new('RGBA', (W, H), (70, 70, 70, 255))
    draw = ImageDraw.Draw(canvas)

    box_names = db_module.get_box_names(user_id)
    box_title = box_names.get(f"Boîte {box_number}", f"Boîte {box_number}")

    try:
        title_font = ImageFont.truetype("arial.ttf", 80)
    except Exception:
        try:
            title_font = ImageFont.truetype("Arial.ttf", 80)
        except Exception:
            title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), box_title, font=title_font)
        text_w = bbox[2] - bbox[0]
    except Exception:
        text_w = len(box_title) * 40
    title_x = (W - text_w) // 2
    draw.text((title_x, 20), box_title, fill=(220, 220, 220, 255), font=title_font)

    for idx in range(30):
        col = idx % cols
        row = idx // cols
        x0 = col * tile_w
        y0 = row * tile_h + header_h
        sprite_box = (x0 + 20, y0 + 20, x0 + tile_w - 20, y0 + tile_h - label_h - 20)
        label_y = y0 + tile_h - label_h
        draw.rectangle((sprite_box[0], sprite_box[1], sprite_box[2], y0 + tile_h - label_h), fill=(45, 45, 45, 255))

        pokemon = box_pokemon[idx]
        if pokemon:
            pokedex_str = f"{pokemon['pokedex_number']:04d}"
            pokemon_data = db_module.get_pokemon_data(pokedex_str)
            img_file = pokemon_data["image"] if pokemon_data else f"Poke{pokedex_str}.png"
            img_path = f"PokeSprites/{img_file}"
            try:
                img = Image.open(img_path)
            except Exception:
                img = Image.open("PokeSprites/Poke0000.png")
            w, h = img.size
            img = img.crop((0, 0, w // 2, h))
            avail_w = sprite_box[2] - sprite_box[0]
            avail_h = sprite_box[3] - sprite_box[1]
            scale = min(avail_w / img.width, avail_h / img.height)
            new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
            img = img.resize(new_size, Image.Resampling.NEAREST)
            paste_x = sprite_box[0] + (avail_w - new_size[0]) // 2
            paste_y = sprite_box[1] + (avail_h - new_size[1]) // 2
            canvas.paste(img, (paste_x, paste_y))

            draw.rectangle((x0 + 20, label_y, x0 + tile_w - 20, y0 + tile_h - 20), fill=(55, 55, 55, 255))
            try:
                font = ImageFont.truetype("arial.ttf", 28)
            except Exception:
                try:
                    font = ImageFont.truetype("Arial.ttf", 28)
                except Exception:
                    font = ImageFont.load_default()
            nom = pokemon['name']
            niveau = pokemon['niveau']
            draw.text((x0 + 30, label_y + 18), f"{nom} Niv.{niveau}", fill=(220, 220, 220, 255), font=font)
        else:
            draw.rectangle((x0 + 20, y0 + 20, x0 + tile_w - 20, y0 + tile_h - 20), fill=(50, 50, 50, 255))

    img_bytes = BytesIO()
    canvas.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return discord.File(img_bytes, filename=f"pc_box{box_number}.png")


def make_pc_embed(db_module, user_id: int, box_number: int, max_boxes: int):
    box_names = db_module.get_box_names(user_id)
    box_title = box_names.get(f"Boîte {box_number}", f"Boîte {box_number}")
    total_pc = db_module.count_pc_pokemon(user_id)
    embed = discord.Embed(
        title=f"PC - {box_title}",
        description=f"Boîte {box_number}/{max_boxes} • Total PC: {total_pc} Pokémon",
        color=discord.Color.dark_blue()
    )
    embed.set_image(url=f"attachment://pc_box{box_number}.png")
    embed.set_footer(text="Clique sur un bouton pour voir les détails d'un Pokémon")
    return embed


# ---------- PC Case Details ----------

def make_pc_slot_detail_embed(pokemon: dict, slot: int):
    """Construit l'embed + fichier image pour les détails d'un slot PC"""
    types_str = f"{pokemon['type1']}" + (f"/{pokemon['type2']}" if pokemon['type2'] else "")
    detail_embed = discord.Embed(
        title=f"PC - Slot {slot}",
        description=f"**{pokemon['name']}** {pokemon['sexe']}\n"
                   f"**Pokédex:** #{pokemon['pokedex_number']:04d} | **Type:** {types_str} | **Niveau:** {pokemon['niveau']}",
        color=discord.Color.dark_blue()
    )
    
    detail_embed.add_field(name="💚 PV", value=str(pokemon['pv']), inline=True)
    detail_embed.add_field(name="⚔️ Attaque", value=str(pokemon['attaque']), inline=True)
    detail_embed.add_field(name="🛡️ Défense", value=str(pokemon['defense']), inline=True)
    detail_embed.add_field(name="✨ Att. Spé", value=str(pokemon['attaque_spec']), inline=True)
    detail_embed.add_field(name="🔰 Déf. Spé", value=str(pokemon['defense_spec']), inline=True)
    detail_embed.add_field(name="⚡ Vitesse", value=str(pokemon['vitesse']), inline=True)
    
    # Image du Pokémon
    pokedex_str = f"{pokemon['pokedex_number']:04d}"
    image_path = f"PokeSprites/Poke{pokedex_str}.png"
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        img_cropped = img.crop((0, 0, width // 2, height))
        new_size = (img_cropped.width * 2, img_cropped.height * 2)
        img_resized = img_cropped.resize(new_size, Image.Resampling.NEAREST)
        img_bytes = BytesIO()
        img_resized.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        detail_embed.set_thumbnail(url=f"attachment://detail_pc_{pokemon['id_pokemon']}.png")
        file_detail = discord.File(img_bytes, filename=f"detail_pc_{pokemon['id_pokemon']}.png")
        return detail_embed, file_detail
    except Exception as e:
        print(f"Erreur affichage détails PC: {e}")
        return detail_embed, None
