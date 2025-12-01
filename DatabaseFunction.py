import sqlite3  # Bibliothèque pour interagir avec la base de données SQLite (usage: partout)
import os  # Gestion des chemins et fichiers système (usage: définition du chemin DB)
from datetime import datetime  # Gestion de dates (usage: timestamp custom ~273)
import random  # Aléatoire pour stats des Pokémon (usage: create_pokemon_instance ~273)

# Chemin vers le dossier Back
DB_PATH = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_PATH, 'Database.sqlite')

# Fonction pour créer les tables si elles n'existent pas
def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Créer la table User
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            Id INTEGER PRIMARY KEY,
            Pseudo TEXT NOT NULL,
            StarterPokemon TEXT,
            PokemonId INTEGER REFERENCES AllPokemons(Id_Pokemon) DEFAULT NULL
        )
    """)
    
    # 2. Créer la table PC
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PC (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idUser INTEGER NOT NULL,
            ownerPseudo TEXT NOT NULL,
            idPokemons TEXT,
            BoîtesName TEXT DEFAULT '{"Boîte 1":"Boîte 1","Boîte 2":"Boîte 2","Boîte 3":"Boîte 3","Boîte 4":"Boîte 4","Boîte 5":"Boîte 5","Boîte 6":"Boîte 6","Boîte 7":"Boîte 7","Boîte 8":"Boîte 8","Boîte 9":"Boîte 9","Boîte 10":"Boîte 10","Boîte 11":"Boîte 11","Boîte 12":"Boîte 12","Boîte 13":"Boîte 13","Boîte 14":"Boîte 14","Boîte 15":"Boîte 15","Boîte 16":"Boîte 16","Boîte 17":"Boîte 17","Boîte 18":"Boîte 18","Boîte 19":"Boîte 19","Boîte 20":"Boîte 20","Boîte 21":"Boîte 21","Boîte 22":"Boîte 22","Boîte 23":"Boîte 23","Boîte 24":"Boîte 24","Boîte 25":"Boîte 25","Boîte 26":"Boîte 26","Boîte 27":"Boîte 27","Boîte 28":"Boîte 28","Boîte 29":"Boîte 29","Boîte 30":"Boîte 30","Boîte 31":"Boîte 31","Boîte 32":"Boîte 32"}',
            FOREIGN KEY (idUser) REFERENCES User(Id)
        )
    """)
    
    # 3. Créer la table Team
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Team (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idUser INTEGER NOT NULL,
            Owner TEXT NOT NULL,
            pokemonId1 INTEGER NOT NULL,
            pokemonId2 INTEGER,
            pokemonId3 INTEGER,
            pokemonId4 INTEGER,
            pokemonId5 INTEGER,
            pokemonId6 INTEGER,
            FOREIGN KEY (idUser) REFERENCES User(Id)
        )
    """)

    # 4. Créer la table Pokedex (ajoutée pour être complet)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pokedex (
            Id CHAR(4) NOT NULL PRIMARY KEY,
            Nom TEXT NOT NULL,
            Image TEXT,
            CatchRate INTEGER,
            Type1 TEXT,
            Type2 TEXT
        )
    """)
    
    # 5. Créer la table SpawnedPokemons
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SpawnedPokemons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            PokedexId INTEGER NOT NULL REFERENCES Pokedex(Id),
            spawn_time DATETIME NOT NULL,
            despawn_time DATETIME NOT NULL,
            CaptureCode TEXT NOT NULL,
            Niveau INTEGER NOT NULL DEFAULT 5
        )
    """)
    
    # 6. Créer la table CommandHistory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CommandHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            commandName TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (userId) REFERENCES User(Id)
        )
    """)
    
    # 7. Créer la table AllPokemons (instances individuelles de Pokémon capturés)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AllPokemons (
            Id_Pokemon INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Pokedex_Number INTEGER NOT NULL,
            Niveau INTEGER NOT NULL CHECK(Niveau >= 1 AND Niveau <= 100),
            Type1 TEXT NOT NULL,
            Type2 TEXT,
            PV INTEGER NOT NULL CHECK(PV > 0),
            Attaque INTEGER NOT NULL CHECK(Attaque > 0),
            Defense INTEGER NOT NULL CHECK(Defense > 0),
            Attaque_Spec INTEGER NOT NULL CHECK(Attaque_Spec > 0),
            Defense_Spec INTEGER NOT NULL CHECK(Defense_Spec > 0),
            Vitesse INTEGER NOT NULL CHECK(Vitesse > 0),
            Sexe TEXT CHECK(Sexe IN ('♂', '♀', 'Inconnu')),
            IdOwner INTEGER NOT NULL,
            OwnerName TEXT NOT NULL,
            DateCapture DATETIME DEFAULT CURRENT_TIMESTAMP,
            Location TEXT DEFAULT 'PC',
            FOREIGN KEY (IdOwner) REFERENCES User(Id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Toutes les tables (User, PC, Team, Pokedex, SpawnedPokemons, CommandHistory, AllPokemons) ont été vérifiées.")
    print("Colonnes ajoutées: Pokedex.Type1/Type2, User.PokemonId, AllPokemons.Location")

# Fonction pour ajouter un utilisateur dans la table User
def add_new_user(user_id, user_pseudo):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT OR IGNORE INTO User (Id, Pseudo) VALUES (?, ?)", (user_id, user_pseudo))
        conn.commit()
        # Le print est retiré pour éviter le spam lors du scan au démarrage
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'utilisateur : {e}")
    finally:
        conn.close()

# Fonction pour initialiser le PC du joueur
def init_player_pc(user_id, user_pseudo, starter_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Mettre à jour le StarterPokemon dans User
        cursor.execute("UPDATE User SET StarterPokemon = ? WHERE Id = ?", (starter_name, user_id))
        
        # Ajouter une entrée dans PC
        cursor.execute("""
            INSERT OR IGNORE INTO PC (idUser, ownerPseudo, idPokemons) 
            VALUES (?, ?, ?)
        """, (user_id, user_pseudo, "[]"))
        
        conn.commit()
        print(f"PC de {user_pseudo} initialisé avec {starter_name}")
    except Exception as e:
        print(f"Erreur lors de l'initialisation du PC : {e}")
    finally:
        conn.close()

# Mettre à jour le PokemonId (starter) dans User
def update_user_starter_id(user_id, pokemon_instance_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE User SET PokemonId = ? WHERE Id = ?", (pokemon_instance_id, user_id))
        conn.commit()
    except Exception as e:
        print(f"Erreur mise à jour PokemonId : {e}")
    finally:
        conn.close()

# Fonction utilitaire pour vérifier si un joueur a déjà un starter
def has_starter(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT StarterPokemon FROM User WHERE Id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result is not None and result[0] is not None


# Suppression d'une entrée du PC par id (colonne primaire)
def delete_pc_by_id(pc_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM PC WHERE id = ?", (pc_id,))
        conn.commit()
        print(f"Entrée PC id={pc_id} supprimée")
    except Exception as e:
        print(f"Erreur suppression PC id={pc_id} : {e}")
    finally:
        conn.close()

# Suppression des entrées PC pour un utilisateur spécifique
def delete_pc_by_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM PC WHERE idUser = ?", (user_id,))
        conn.commit()
        print(f"Entrées PC de l'utilisateur {user_id} supprimées")
    except Exception as e:
        print(f"Erreur suppression PC user={user_id} : {e}")
    finally:
        conn.close()

# Reset complet de la base (suppression du fichier puis recréation des tables)
def reset_database(confirm=False):
    if not confirm:
        print("Reset annulé: passez confirm=True pour exécuter.")
        return
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            print("Fichier de base supprimé.")
        init_database()
        print("Base recréée.")
    except Exception as e:
        print(f"Erreur lors du reset de la base : {e}")

# Récupérer le nom d'un Pokémon depuis la table Pokedex
def get_pokemon_name(pokedex_id_str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Nom FROM Pokedex WHERE Id = ?", (pokedex_id_str,))
        row = cursor.fetchone()
        return row[0] if row and row[0] else None
    except Exception as e:
        print(f"Erreur lors de la lecture du Pokedex ({pokedex_id_str}) : {e}")
        return None
    finally:
        conn.close()

# Récupérer les données d'un Pokémon (nom et image) depuis la table Pokedex
def get_pokemon_data(pokedex_id_str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Nom, Image FROM Pokedex WHERE Id = ?", (pokedex_id_str,))
        row = cursor.fetchone()
        if row:
            return {"nom": row[0], "image": row[1]}
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture du Pokedex ({pokedex_id_str}) : {e}")
        return None
    finally:
        conn.close()


# Récupérer les données complètes d'un Pokémon (avec types) depuis la table Pokedex
def get_pokemon_full_data(pokedex_id_str):
    """Récupère toutes les infos d'un Pokémon depuis Pokedex (pour génération)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Note: Il faudra ajouter Type1 et Type2 à la table Pokedex pour cela
        cursor.execute("SELECT Nom, Image FROM Pokedex WHERE Id = ?", (pokedex_id_str,))
        row = cursor.fetchone()
        if row:
            return {"nom": row[0], "image": row[1]}
        return None
    except Exception as e:
        print(f"Erreur lecture Pokedex complet ({pokedex_id_str}) : {e}")
        return None
    finally:
        conn.close()


# Créer un Pokémon individuel dans AllPokemons
def create_pokemon_instance(pokedex_number: int, niveau: int, sexe: str, owner_id: int, owner_name: str, location: str = "Team"):
    """
    Génère un Pokémon individuel avec ses stats dans AllPokemons
    Retourne l'Id_Pokemon créé ou None en cas d'erreur
    location: 'Team' ou 'PC'
    """
    
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Récupérer les infos depuis Pokedex (avec types maintenant)
        pokedex_str = f"{pokedex_number:04d}"
        cursor.execute("SELECT Nom, Type1, Type2 FROM Pokedex WHERE Id = ?", (pokedex_str,))
        row = cursor.fetchone()
        
        if not row:
            print(f"Pokémon #{pokedex_number} introuvable dans Pokedex")
            return None
        
        pokemon_name = row[0]
        type1 = row[1] if row[1] else "Normal"
        type2 = row[2] if row[2] else None
        
        # Générer des stats basées sur le niveau (formule simple)
        # Stats de base * (niveau / 50) + variation aléatoire
        base_multiplier = niveau / 50.0
        
        pv = max(10, int(50 * base_multiplier + random.randint(-5, 5)))
        attaque = max(5, int(45 * base_multiplier + random.randint(-3, 3)))
        defense = max(5, int(40 * base_multiplier + random.randint(-3, 3)))
        attaque_spec = max(5, int(45 * base_multiplier + random.randint(-3, 3)))
        defense_spec = max(5, int(40 * base_multiplier + random.randint(-3, 3)))
        vitesse = max(5, int(50 * base_multiplier + random.randint(-3, 3)))
        
        # Insérer dans AllPokemons
        cursor.execute("""
            INSERT INTO AllPokemons 
            (Name, Pokedex_Number, Niveau, Type1, Type2, PV, Attaque, Defense, 
             Attaque_Spec, Defense_Spec, Vitesse, Sexe, IdOwner, OwnerName, DateCapture, Location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pokemon_name, pokedex_number, niveau, type1, type2, pv, attaque, defense,
              attaque_spec, defense_spec, vitesse, sexe, owner_id, owner_name, datetime.now(), location))
        
        conn.commit()
        pokemon_instance_id = cursor.lastrowid
        print(f"Pokémon #{pokedex_number} ({pokemon_name}) créé avec Id_Pokemon={pokemon_instance_id} (Location: {location})")
        return pokemon_instance_id
        
    except Exception as e:
        print(f"Erreur création instance Pokémon : {e}")
        return None
    finally:
        conn.close()


# Récupérer un Pokémon individuel depuis AllPokemons
def get_pokemon_instance(pokemon_instance_id: int):
    """Récupère les détails d'un Pokémon individuel"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT Id_Pokemon, Name, Pokedex_Number, Niveau, Type1, Type2,
                   PV, Attaque, Defense, Attaque_Spec, Defense_Spec, Vitesse,
                   Sexe, IdOwner, OwnerName, DateCapture
            FROM AllPokemons WHERE Id_Pokemon = ?
        """, (pokemon_instance_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0], "name": row[1], "pokedex_number": row[2], "niveau": row[3],
                "type1": row[4], "type2": row[5], "pv": row[6], "attaque": row[7],
                "defense": row[8], "attaque_spec": row[9], "defense_spec": row[10],
                "vitesse": row[11], "sexe": row[12], "owner_id": row[13],
                "owner_name": row[14], "date_capture": row[15]
            }
        return None
    except Exception as e:
        print(f"Erreur récupération instance Pokémon : {e}")
        return None
    finally:
        conn.close()


# Enregistrer un Pokémon spawné dans la table SpawnedPokemons
def spawn_pokemon_in_db(pokedex_id_int, spawn_time, despawn_time, capture_code, niveau):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO SpawnedPokemons (PokedexId, spawn_time, despawn_time, CaptureCode, Niveau)
            VALUES (?, ?, ?, ?, ?)
        """, (pokedex_id_int, spawn_time, despawn_time, capture_code, niveau))
        conn.commit()
        spawn_id = cursor.lastrowid
        print(f"Pokémon #{pokedex_id_int} spawné (ID spawn: {spawn_id}, code: {capture_code})")
        return spawn_id
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du spawn : {e}")
        return None
    finally:
        conn.close()

# Récupérer un spawn par son code de capture (si pas encore expiré)
def get_spawn_by_code(capture_code):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT sp.id, sp.PokedexId, sp.spawn_time, sp.despawn_time, 
                   pd.Nom, pd.Image, pd.Id, sp.Niveau
            FROM SpawnedPokemons sp
            JOIN Pokedex pd ON sp.PokedexId = CAST(pd.Id AS INTEGER)
            WHERE sp.CaptureCode = ?
        """, (capture_code,))
        row = cursor.fetchone()
        if row:
            return {
                "spawn_id": row[0],
                "pokedex_id": row[1],
                "spawn_time": row[2],
                "despawn_time": row[3],
                "nom": row[4],
                "image": row[5],
                "pokedex_str": row[6],
                "niveau": row[7]
            }
        return None
    except Exception as e:
        print(f"Erreur récupération spawn code {capture_code} : {e}")
        return None
    finally:
        conn.close()

# Supprimer un spawn après capture
def delete_spawn(spawn_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM SpawnedPokemons WHERE id = ?", (spawn_id,))
        conn.commit()
    except Exception as e:
        print(f"Erreur suppression spawn {spawn_id} : {e}")
    finally:
        conn.close()


# Récupérer l'équipe d'un utilisateur
def get_user_team(user_id):
    """Retourne la liste des IDs Pokémon dans l'équipe (6 slots, None si vide)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT pokemonId1, pokemonId2, pokemonId3, pokemonId4, pokemonId5, pokemonId6
            FROM Team WHERE idUser = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return list(row)  # Liste de 6 éléments (peut contenir None)
        return [None, None, None, None, None, None]  # Équipe vide
    except Exception as e:
        print(f"Erreur récupération équipe : {e}")
        return [None, None, None, None, None, None]
    finally:
        conn.close()

# ---------------- Command History (DB-backed) ----------------
def add_command_history(user_id: int, command_name: str, pseudo: str = None) -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO CommandHistory (userId, commandName, pseudo, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (user_id, command_name, pseudo)
        )
        conn.commit()
    except Exception as e:
        print(f"Erreur ajout historique commande: {e}")
    finally:
        conn.close()

def get_last_command_history(user_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT commandName, timestamp, pseudo FROM CommandHistory WHERE userId = ? ORDER BY timestamp DESC, id DESC LIMIT 1",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {"command": row[0], "timestamp": row[1], "pseudo": row[2], "user_id": user_id}
    except Exception as e:
        print(f"Erreur lecture dernière commande: {e}")
        return None
    finally:
        conn.close()

def get_all_command_history(user_id: int) -> list:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT commandName, timestamp, pseudo FROM CommandHistory WHERE userId = ? ORDER BY timestamp DESC, id DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        return [{"command": r[0], "timestamp": r[1], "pseudo": r[2], "user_id": user_id} for r in rows]
    except Exception as e:
        print(f"Erreur lecture historique commandes: {e}")
        return []
    finally:
        conn.close()

def clear_command_history(user_id: int) -> None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM CommandHistory WHERE userId = ?", (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Erreur nettoyage historique commandes: {e}")
    finally:
        conn.close()


# Ajouter un Pokémon dans le premier slot libre de l'équipe
def add_pokemon_to_team(user_id, pokemon_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, Owner, pokemonId1, pokemonId2, pokemonId3, pokemonId4, pokemonId5, pokemonId6 FROM Team WHERE idUser = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            # Créer l'équipe si elle n'existe pas
            cursor.execute("SELECT Pseudo FROM User WHERE Id = ?", (user_id,))
            user_row = cursor.fetchone()
            owner = user_row[0] if user_row and user_row[0] else str(user_id)
            cursor.execute(
                "INSERT INTO Team (idUser, Owner, pokemonId1) VALUES (?, ?, ?)",
                (user_id, owner, pokemon_id)
            )
            # Mettre à jour la Location à 'Team'
            cursor.execute("UPDATE AllPokemons SET Location = 'Team' WHERE Id_Pokemon = ?", (pokemon_id,))
            conn.commit()
            return True
        
        # Trouver le premier slot libre
        slots = ["pokemonId1", "pokemonId2", "pokemonId3", "pokemonId4", "pokemonId5", "pokemonId6"]
        # row structure: (id, Owner, p1, p2, p3, p4, p5, p6)
        current_slots = row[2:]
        for i, val in enumerate(current_slots):
            if val is None:
                cursor.execute(f"UPDATE Team SET {slots[i]} = ? WHERE idUser = ?", (pokemon_id, user_id))
                # Mettre à jour la Location à 'Team'
                cursor.execute("UPDATE AllPokemons SET Location = 'Team' WHERE Id_Pokemon = ?", (pokemon_id,))
                conn.commit()
                return True
        return False  # Équipe pleine
    except Exception as e:
        print(f"Erreur ajout Pokémon à l'équipe : {e}")
        return False
    finally:
        conn.close()


def add_pokemon_to_pc(user_id, pokemon_id):
    """Ajoute un Pokémon à la liste idPokemons du PC de l'utilisateur"""
    import json
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT idPokemons FROM PC WHERE idUser = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            # Parser la liste existante
            try:
                id_list = json.loads(row[0]) if row[0] else []
            except json.JSONDecodeError:
                id_list = []
            
            # Ajouter le nouveau Pokémon
            if pokemon_id not in id_list:
                id_list.append(pokemon_id)
            
            # Sauvegarder
            cursor.execute("UPDATE PC SET idPokemons = ? WHERE idUser = ?", 
                          (json.dumps(id_list), user_id))
            conn.commit()
            return True
        else:
            print(f"PC introuvable pour user {user_id}")
            return False
    except Exception as e:
        print(f"Erreur ajout Pokémon au PC : {e}")
        return False
    finally:
        conn.close()


# ----------------- Fonctions pour l'historique des commandes -----------------

# ----------------- Pokédex helpers (pages/chapters) -----------------

def _gen_bounds(gen: int):
    bounds = {
        1: (1, 151),
        2: (152, 251),
        3: (252, 386),
        4: (387, 493),
        5: (494, 649),
        6: (650, 721),
    }
    return bounds.get(gen, (1, 151))


def get_pokedex_count_range(gen: int) -> int:
    start, end = _gen_bounds(gen)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM Pokedex
            WHERE CAST(Id AS INTEGER) BETWEEN ? AND ?
            """,
            (start, end),
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    except Exception as e:
        print(f"Erreur count Pokedex gen {gen}: {e}")
        return 0
    finally:
        conn.close()


def get_pokedex_range(gen: int, limit: int, offset: int):
    start, end = _gen_bounds(gen)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT Id, Nom, Image
            FROM Pokedex
            WHERE CAST(Id AS INTEGER) BETWEEN ? AND ?
            ORDER BY CAST(Id AS INTEGER)
            LIMIT ? OFFSET ?
            """,
            (start, end, limit, offset),
        )
        rows = cursor.fetchall()
        return [
            {"id": r[0], "nom": r[1], "image": r[2]}
            for r in rows
        ]
    except Exception as e:
        print(f"Erreur get range Pokedex gen {gen}: {e}")
        return []
    finally:
        conn.close()


def get_pokedex_search_count(gen: int, term: str) -> int:
    start, end = _gen_bounds(gen)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        like = f"%{term}%"
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM Pokedex
            WHERE CAST(Id AS INTEGER) BETWEEN ? AND ?
              AND LOWER(Nom) LIKE LOWER(?)
            """,
            (start, end, like),
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    except Exception as e:
        print(f"Erreur count recherche Pokedex gen {gen}: {e}")
        return 0
    finally:
        conn.close()


def get_pokedex_search(gen: int, term: str, limit: int, offset: int):
    start, end = _gen_bounds(gen)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        like = f"%{term}%"
        cursor.execute(
            """
            SELECT Id, Nom, Image
            FROM Pokedex
            WHERE CAST(Id AS INTEGER) BETWEEN ? AND ?
              AND LOWER(Nom) LIKE LOWER(?)
            ORDER BY CAST(Id AS INTEGER)
            LIMIT ? OFFSET ?
            """,
            (start, end, like, limit, offset),
        )
        rows = cursor.fetchall()
        return [
            {"id": r[0], "nom": r[1], "image": r[2]}
            for r in rows
        ]
    except Exception as e:
        print(f"Erreur recherche Pokedex gen {gen}: {e}")
        return []
    finally:
        conn.close()

def save_command_to_db(user_id: int, command_name: str, timestamp):
    """Enregistre une commande dans la base de données"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO CommandHistory (userId, commandName, timestamp)
            VALUES (?, ?, ?)
        """, (user_id, command_name, timestamp))
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la commande : {e}")
    finally:
        conn.close()


def get_user_command_history(user_id: int) -> list:
    """Récupère tout l'historique des commandes d'un utilisateur depuis la DB"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT commandName, timestamp 
            FROM CommandHistory 
            WHERE userId = ? 
            ORDER BY timestamp DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        return [{"command": row[0], "timestamp": row[1]} for row in rows]
    except Exception as e:
        print(f"Erreur lors de la récupération de l'historique : {e}")
        return []
    finally:
        conn.close()


def clear_user_command_history(user_id: int):
    """Supprime tout l'historique des commandes d'un utilisateur"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM CommandHistory WHERE userId = ?", (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de la suppression de l'historique : {e}")
    finally:
        conn.close()


# ----------------- PC Box helpers -----------------

def get_pc_pokemon(user_id: int, box_number: int):
    """Récupère les Pokémon d'une boîte spécifique (30 par boîte, Location='PC')
    Retourne une liste de 30 éléments (None si slot vide)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Récupérer tous les Pokémon en PC de l'utilisateur triés par DateCapture
        cursor.execute("""
            SELECT Id_Pokemon, Name, Pokedex_Number, Niveau, Sexe, Type1, Type2,
                   PV, Attaque, Defense, Attaque_Spec, Defense_Spec, Vitesse
            FROM AllPokemons
            WHERE IdOwner = ? AND Location = 'PC'
            ORDER BY DateCapture ASC
        """, (user_id,))
        all_pc = cursor.fetchall()
        
        # Calculer l'offset pour cette boîte (30 par boîte)
        offset = (box_number - 1) * 30
        box_pokemon = all_pc[offset:offset + 30]
        
        # Compléter avec None jusqu'à 30
        result = []
        for row in box_pokemon:
            result.append({
                "id_pokemon": row[0],
                "name": row[1],
                "pokedex_number": row[2],
                "niveau": row[3],
                "sexe": row[4],
                "type1": row[5],
                "type2": row[6],
                "pv": row[7],
                "attaque": row[8],
                "defense": row[9],
                "attaque_spec": row[10],
                "defense_spec": row[11],
                "vitesse": row[12]
            })
        
        while len(result) < 30:
            result.append(None)
        
        return result
    except Exception as e:
        print(f"Erreur get_pc_pokemon: {e}")
        return [None] * 30
    finally:
        conn.close()


def get_box_names(user_id: int):
    """Récupère le dictionnaire des noms de boîtes"""
    import json
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT BoîtesName FROM PC WHERE idUser = ?", (user_id,))
        row = cursor.fetchone()
        if row and row[0]:
            return json.loads(row[0])
        # Retourner les noms par défaut
        return {f"Boîte {i}": f"Boîte {i}" for i in range(1, 33)}
    except Exception as e:
        print(f"Erreur get_box_names: {e}")
        return {f"Boîte {i}": f"Boîte {i}" for i in range(1, 33)}
    finally:
        conn.close()


def update_box_name(user_id: int, box_number: int, new_name: str):
    """Met à jour le nom d'une boîte"""
    import json
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Récupérer les noms actuels
        box_names = get_box_names(user_id)
        # Mettre à jour
        box_names[f"Boîte {box_number}"] = new_name
        # Sauvegarder
        cursor.execute("UPDATE PC SET BoîtesName = ? WHERE idUser = ?", 
                      (json.dumps(box_names, ensure_ascii=False), user_id))
        conn.commit()
    except Exception as e:
        print(f"Erreur update_box_name: {e}")
    finally:
        conn.close()


def count_pc_pokemon(user_id: int) -> int:
    """Compte le nombre de Pokémon dans le PC"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM AllPokemons
            WHERE IdOwner = ? AND Location = 'PC'
        """, (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 0
    except Exception as e:
        print(f"Erreur count_pc_pokemon: {e}")
        return 0
    finally:
        conn.close()
