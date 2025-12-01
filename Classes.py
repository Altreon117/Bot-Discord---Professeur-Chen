import discord  # Composants UI Discord (Views, Buttons) (usage: nombreuses classes)
from discord import app_commands  # Intégration des commandes/app_commands (usage: interactions)
from datetime import datetime  # Horodatage pour vues/images (usage: construction embeds/images)
import random  # Choix aléatoires (quiz/affichages) (usage: quiz)
from io import BytesIO  # Buffer mémoire pour images générées (usage: génération PNG)
from PIL import Image, ImageDraw, ImageFont  # Manipulation/texte des images (sprites/compositions) (usage: création images)
import DisplayFunction as display  # Fonctions d'affichage centralisées


# ================== ARBRE ( Arbre binaire (pas complet )) ==================

class Arbre:
    def __init__(self, racine, feuilleGauche=None, feuilleDroite=None):
        self.racine = racine
        self.feuilleGauche = feuilleGauche
        self.feuilleDroite = feuilleDroite

    def feuille(self):
        return self.feuilleGauche is None and self.feuilleDroite is None
    
    def is_leaf(self):
        """Vérifie si le nœud est une feuille (chaîne de caractères)"""
        return isinstance(self, str)


# ================== QUIZ VIEW (Starter Quiz) ==================

class QuizView(discord.ui.View):
    def __init__(self, user_id: int, starters: dict, db_module, tree_root, quiz_sessions: dict, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.starters = starters
        self.db = db_module
        self.tree_root = tree_root
        self.quiz_sessions = quiz_sessions

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    async def _advance(self, interaction: discord.Interaction, choose_left: bool):
        current = self.quiz_sessions.get(self.user_id)
        if current is None:
            await interaction.response.edit_message(content="Session expirée.", view=None)
            return
        
        from OtherCode import build_question_embed, generate_starter_embed  # Utilitaires quiz (embeds/génération)
        
        if isinstance(current, str):
            await interaction.response.send_message("Le quiz est déjà terminé.", ephemeral=True)
            return
        next_node = current.feuilleGauche if choose_left else current.feuilleDroite
        if next_node is None:
            await interaction.response.send_message("Pas de branche ici.", ephemeral=True)
            return
        self.quiz_sessions[self.user_id] = next_node
        if isinstance(next_node, str):
            starter_nom = next_node
            # Trouver l'ID du starter à partir du nom
            starter_id = None
            for sid, (nom, _) in self.starters.items():
                if nom == starter_nom:
                    starter_id = sid
                    break
            if starter_id is None:
                await interaction.response.send_message(f"Pokémon '{starter_nom}' introuvable.", ephemeral=True)
                return
            embed, file_img, starter_nom, pokedex_num_int, sexe, niveau = await generate_starter_embed(starter_id, self.starters, "Résultat du Quiz")
            # Adapter le texte car le starter n'est pas encore confirmé
            embed.description = f"Résultat proposé : **{starter_nom}**. Appuie sur Valider pour le choisir definitivement."
            embed.set_footer(text=f"Pokédex #{pokedex_num_int:04d} | En attente de validation")
            # Stocker résultat en attente
            self.pending_starter = {
                "starter_nom": starter_nom,
                "pokedex_num_int": pokedex_num_int,
                "sexe": sexe,
                "niveau": niveau
            }
            
            # Désactiver les boutons Oui/Non et ajouter le bouton Recommencer et Valider
            for child in self.children:
                if isinstance(child, discord.ui.Button) and child.label in ["Oui", "Non"]:
                    child.disabled = True
            
            # Ajouter bouton Recommencer
            restart_button = discord.ui.Button(label="Recommencer", style=discord.ButtonStyle.primary, emoji="🔄")
            async def restart_callback(inter: discord.Interaction):
                if inter.user.id != self.user_id:
                    await inter.response.send_message("Ce n'est pas ton quiz.", ephemeral=True)
                    return
                self.quiz_sessions[self.user_id] = self.tree_root
                new_view = QuizView(self.user_id, self.starters, self.db, self.tree_root, self.quiz_sessions)
                restart_embed = build_question_embed(self.tree_root)
                await inter.response.edit_message(embed=restart_embed, view=new_view, attachments=[])
            restart_button.callback = restart_callback
            self.add_item(restart_button)

            # Ajouter bouton Valider
            validate_button = discord.ui.Button(label="Valider", style=discord.ButtonStyle.success, emoji="✅")
            async def validate_callback(inter: discord.Interaction):
                if inter.user.id != self.user_id:
                    await inter.response.send_message("Ce n'est pas ton quiz.", ephemeral=True)
                    return
                if hasattr(self, "pending_starter"):
                    data = self.pending_starter
                    user_pseudo = inter.user.name
                    # Effectuer maintenant les insertions DB
                    self.db.add_new_user(self.user_id, user_pseudo)
                    self.db.init_player_pc(self.user_id, user_pseudo, data["starter_nom"])
                    
                    # Créer l'instance Pokémon individuelle avec Location='Team'
                    pokemon_instance_id = self.db.create_pokemon_instance(
                        data["pokedex_num_int"], 
                        data["niveau"], 
                        data["sexe"], 
                        self.user_id, 
                        user_pseudo,
                        location="Team"
                    )
                    
                    # Ajouter à l'équipe
                    if pokemon_instance_id:
                        self.db.add_pokemon_to_team(self.user_id, pokemon_instance_id)
                        self.db.update_user_starter_id(self.user_id, pokemon_instance_id)
                    
                    # Mettre à jour l'embed pour refléter confirmation
                    confirmed_embed = display.make_quiz_confirmed_embed(
                        data['starter_nom'], data['niveau'], data['sexe'], data['pokedex_num_int']
                    )
                    
                    # Désactiver TOUS les boutons (Oui, Non, Recommencer, Valider)
                    for child in self.children:
                        if isinstance(child, discord.ui.Button):
                            child.disabled = True
                    
                    await inter.response.edit_message(embed=confirmed_embed, view=self, attachments=[])
                    
                    # Envoyer message public visible par tous
                    await inter.followup.send(f"{inter.user.mention} a choisi **{data['starter_nom']}** !", ephemeral=False)
                    del self.pending_starter
                else:
                    await inter.response.send_message("Aucun starter en attente.", ephemeral=True)
            validate_button.callback = validate_callback
            self.add_item(validate_button)
            
            if file_img:
                await interaction.response.edit_message(embed=embed, attachments=[file_img], view=self)
            else:
                await interaction.response.edit_message(embed=embed, view=self)
            self.quiz_sessions.pop(self.user_id, None)
        else:
            embed = build_question_embed(next_node)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Oui", style=discord.ButtonStyle.success)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._advance(interaction, choose_left=True)

    @discord.ui.button(label="Non", style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._advance(interaction, choose_left=False)


# ================== POKEDEX VIEW ==================

class PokedexView(discord.ui.View):
    def __init__(self, user_id: int, db_module, initial_gen: int = 1, page_size: int = 30):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.db = db_module
        self.gen = initial_gen
        self.page_size = page_size
        self.page = 0
        self.search_term: str | None = None

        # Désactiver temporairement les générations non disponibles (2-6) (pas le temps et flemme de renommer  ~600 images)
        try:
            counts = {g: self.db.get_pokedex_count_range(g) for g in range(1, 7)}
            # Enable if count > 0 else disable
            self.gen1.disabled = counts.get(1, 0) == 0
            self.gen2.disabled = counts.get(2, 0) == 0
            self.gen3.disabled = counts.get(3, 0) == 0
            self.gen4.disabled = counts.get(4, 0) == 0
            self.gen5.disabled = counts.get(5, 0) == 0
            self.gen6.disabled = counts.get(6, 0) == 0
        except Exception:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    def _page_count(self) -> int:
        if self.search_term:
            total = self.db.get_pokedex_search_count(self.gen, self.search_term)
        else:
            total = self.db.get_pokedex_count_range(self.gen)
        return max(1, (total + self.page_size - 1) // self.page_size)

    def _bounds(self):
        return self.page * self.page_size, self.page_size

    def _build_page_image(self):
        return display.make_pokedex_page_image(self.db, self.gen, self.page, self.page_size, self.search_term)

    def _build_embed(self):
        pc = self._page_count()
        return display.make_pokedex_embed(self.gen, self.page, pc, self.search_term)

    async def _refresh(self, interaction: discord.Interaction):
        pc = self._page_count()
        self.page = max(0, min(self.page, pc - 1))
        embed = self._build_embed()
        file_img = self._build_page_image()
        await interaction.response.edit_message(embed=embed, attachments=[file_img], view=self)

    @discord.ui.button(label="Gen1", style=discord.ButtonStyle.primary)
    async def gen1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.gen = 1
        self.page = 0
        await self._refresh(interaction)

    @discord.ui.button(label="Gen2", style=discord.ButtonStyle.secondary)
    async def gen2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.gen = 2
        self.page = 0
        await self._refresh(interaction)

    @discord.ui.button(label="Gen3", style=discord.ButtonStyle.secondary)
    async def gen3(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.gen = 3
        self.page = 0
        await self._refresh(interaction)

    @discord.ui.button(label="Gen4", style=discord.ButtonStyle.secondary)
    async def gen4(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.gen = 4
        self.page = 0
        await self._refresh(interaction)

    @discord.ui.button(label="Gen5", style=discord.ButtonStyle.secondary)
    async def gen5(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.gen = 5
        self.page = 0
        await self._refresh(interaction)

    @discord.ui.button(label="Gen6", style=discord.ButtonStyle.secondary)
    async def gen6(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.gen = 6
        self.page = 0
        await self._refresh(interaction)

    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.secondary, row=2)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        await self._refresh(interaction)

    @discord.ui.button(label="Suivant ➡️", style=discord.ButtonStyle.secondary, row=2)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = self.page + 1
        await self._refresh(interaction)

    @discord.ui.button(label="🔎 Rechercher", style=discord.ButtonStyle.primary, row=0)
    async def open_search(self, interaction: discord.Interaction, button: discord.ui.Button):
        class SearchModal(discord.ui.Modal, title="Rechercher dans le Pokédex"):
            term: str = ""
            def __init__(self, parent_view: 'PokedexView'):
                super().__init__()
                self.parent_view = parent_view
                self.input = discord.ui.TextInput(label="Nom contient", placeholder="ex: pika", required=True, max_length=32)
                self.add_item(self.input)

            async def on_submit(self, inter: discord.Interaction):
                self.parent_view.search_term = str(self.input.value).strip()
                self.parent_view.page = 0
                await self.parent_view._refresh(inter)

        await interaction.response.send_modal(SearchModal(self))

    @discord.ui.button(label="Effacer filtre", style=discord.ButtonStyle.secondary, row=0)
    async def clear_filter(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.search_term = None
        self.page = 0
        await self._refresh(interaction)


# ================== TEAM VIEW ==================

class TeamView(discord.ui.View):
    def __init__(self, user_id: int, team_pokemon: list, db_module, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.team_pokemon = team_pokemon
        self.db = db_module
        
        # Créer 6 boutons pour les 6 slots
        for i in range(6):
            pokemon_id = team_pokemon[i]
            # Déterminer le style et le label
            if pokemon_id is None:
                button = discord.ui.Button(
                    label=f"Slot {i+1}",
                    style=discord.ButtonStyle.secondary,
                    disabled=True,
                    row=i // 3  # 2 lignes de 3 boutons
                )
            else:
                button = discord.ui.Button(
                    label=f"#{i+1}",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"team_slot_{i}",
                    row=i // 3
                )
                button.callback = self.create_callback(i)
            self.add_item(button)
    
    def create_callback(self, slot_index: int):
        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Ce n'est pas ton équipe.", ephemeral=True)
                return
            
            pokemon_id = self.team_pokemon[slot_index]
            if pokemon_id is None:
                await interaction.response.send_message("Ce slot est vide.", ephemeral=True)
                return
            
            # Récupérer les données de l'instance Pokémon depuis AllPokemons
            pokemon_instance = self.db.get_pokemon_instance(pokemon_id)
            
            if not pokemon_instance:
                await interaction.response.send_message("Pokémon introuvable.", ephemeral=True)
                return
            
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
            
            # Charger l'image depuis Pokedex
            pokedex_str = f"{pokedex_number:04d}"
            pokemon_data = self.db.get_pokemon_data(pokedex_str)
            image_filename = pokemon_data["image"] if pokemon_data else "Poke0000.png"
            image_path = f"PokeSprites/{image_filename}"
            
            # Modifier l'embed existant pour ajouter les détails
            current_embed = interaction.message.embeds[0]
            
            # Créer un nouvel embed avec les infos complètes
            new_embed, file_detail = display.make_team_slot_detail_embed(
                current_embed.title, slot_index, pokemon_instance, image_path
            )
            # Garder l'image de l'équipe
            if current_embed.image:
                new_embed.set_image(url=current_embed.image.url)
            # Éditer le message avec le nouvel embed et la nouvelle miniature
            original_attachments = [att for att in interaction.message.attachments if att.filename.startswith("team_")]
            if file_detail:
                await interaction.response.edit_message(embed=new_embed, attachments=original_attachments + [file_detail], view=self)
            else:
                await interaction.response.edit_message(embed=new_embed, attachments=original_attachments, view=self)
        
        return button_callback
    
    async def on_timeout(self):
        # Désactiver tous les boutons après timeout
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


# ================== PC VIEW (Box Storage) ==================

class PCView(discord.ui.View):
    def __init__(self, user_id: int, db_module, box_number: int = 1, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.db = db_module
        self.box_number = box_number
        self.max_boxes = 32
        self.showing_details = False
        self.selected_slot = None
        
        # Désactiver les boutons si on est à la première/dernière boîte
        if self.box_number <= 1:
            self.prev_box.disabled = True
        if self.box_number >= self.max_boxes:
            self.next_box.disabled = True
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    def _build_box_image(self):
        """Crée une image 6x5 des Pokémon de la boîte actuelle"""
        return display.make_pc_box_image(self.db, self.user_id, self.box_number)
    
    def _build_embed(self):
        return display.make_pc_embed(self.db, self.user_id, self.box_number, self.max_boxes)
    
    async def _refresh(self, interaction: discord.Interaction):
        # Mettre à jour les boutons prev/next
        self.prev_box.disabled = (self.box_number <= 1)
        self.next_box.disabled = (self.box_number >= self.max_boxes)
        
        embed = self._build_embed()
        file_img = self._build_box_image()
        await interaction.response.edit_message(embed=embed, attachments=[file_img], view=self)
    
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary, row=0)
    async def prev_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.box_number = max(1, self.box_number - 1)
        await self._refresh(interaction)
    
    @discord.ui.button(label="Renommer", style=discord.ButtonStyle.primary, row=0)
    async def rename_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        class RenameModal(discord.ui.Modal, title="Renommer la boîte"):
            def __init__(self, parent_view: 'PCView'):
                super().__init__()
                self.parent_view = parent_view
                box_names = parent_view.db.get_box_names(parent_view.user_id)
                current_name = box_names.get(f"Boîte {parent_view.box_number}", f"Boîte {parent_view.box_number}")
                
                self.input = discord.ui.TextInput(
                    label="Nouveau nom", 
                    placeholder=current_name, 
                    default=current_name,
                    required=True, 
                    max_length=30
                )
                self.add_item(self.input)
            
            async def on_submit(self, inter: discord.Interaction):
                new_name = str(self.input.value).strip()
                self.parent_view.db.update_box_name(self.parent_view.user_id, self.parent_view.box_number, new_name)
                await self.parent_view._refresh(inter)
        
        await interaction.response.send_modal(RenameModal(self))
    
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary, row=0)
    async def next_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.box_number = min(self.max_boxes, self.box_number + 1)
        await self._refresh(interaction)
    
    @discord.ui.button(label="Boîte ?", style=discord.ButtonStyle.primary, row=0)
    async def goto_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        class GotoModal(discord.ui.Modal, title="Aller à la boîte"):
            def __init__(self, parent_view: 'PCView'):
                super().__init__()
                self.parent_view = parent_view
                self.input = discord.ui.TextInput(
                    label="Numéro de boîte (1-32)", 
                    placeholder="1",
                    required=True,
                    max_length=2
                )
                self.add_item(self.input)
            
            async def on_submit(self, inter: discord.Interaction):
                try:
                    num = int(self.input.value)
                    if 1 <= num <= 32:
                        self.parent_view.box_number = num
                        await self.parent_view._refresh(inter)
                    else:
                        await inter.response.send_message("Numéro de boîte invalide (1-32).", ephemeral=True)
                except ValueError:
                    await inter.response.send_message("Veuillez entrer un nombre valide.", ephemeral=True)
        
        await interaction.response.send_modal(GotoModal(self))
    
    @discord.ui.button(label="🔍 Voir détails", style=discord.ButtonStyle.success, row=1)
    async def view_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        class SlotModal(discord.ui.Modal, title="Voir les détails d'un Pokémon"):
            def __init__(self, parent_view: 'PCView'):
                super().__init__()
                self.parent_view = parent_view
                self.input = discord.ui.TextInput(
                    label="Numéro du slot (1-30)", 
                    placeholder="1",
                    required=True,
                    max_length=2
                )
                self.add_item(self.input)
            
            async def on_submit(self, inter: discord.Interaction):
                try:
                    slot = int(self.input.value)
                    if 1 <= slot <= 30:
                        box_pokemon = self.parent_view.db.get_pc_pokemon(self.parent_view.user_id, self.parent_view.box_number)
                        pokemon = box_pokemon[slot - 1]
                        
                        if pokemon is None:
                            await inter.response.send_message("Ce slot est vide.", ephemeral=True)
                            return
                        
                        # Afficher les détails
                        detail_embed, file_detail = display.make_pc_slot_detail_embed(pokemon, slot)
                        if file_detail:
                            await inter.response.send_message(embed=detail_embed, file=file_detail, ephemeral=True)
                        else:
                            await inter.response.send_message(embed=detail_embed, ephemeral=True)
                    else:
                        await inter.response.send_message("Numéro de slot invalide (1-30).", ephemeral=True)
                except ValueError:
                    await inter.response.send_message("Veuillez entrer un nombre valide.", ephemeral=True)
        
        await interaction.response.send_modal(SlotModal(self))
