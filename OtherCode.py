import random  # Choix aléatoires (sexe starter)
from io import BytesIO  # Buffer mémoire pour images
from PIL import Image  # Manipulation des sprites starters
import discord  # Embeds et fichiers Discord
from Classes import Arbre  # Structure d'arbre pour le quiz
import DisplayFunction as display  # Fonctions d'affichage centralisées


# ----------------- Logique Quiz Starter (utilitaires) -----------------
# Ces éléments sont externalisés pour alléger main.py. La commande slash
# ne doit conserver que le décorateur et l'initialisation de la session.

quiz_sessions = {}  # user_id -> noeud courant (Arbre ou str feuille)

def build_question_embed(node: Arbre):
    return display.build_question_embed(node)

async def generate_starter_embed(starter_id: int, starters: dict, title: str):
    return await display.generate_starter_embed(starter_id, starters, title)


def normalize_starter_name(s: str) -> str:
    return (s.lower()
            .replace("é","e").replace("è","e").replace("ê","e")
            .replace("ï","i").replace("î","i")
            .replace("ç","c").strip())

def resolve_starter(choice: str, starters: dict):
    """Retourne l'id du starter à partir d'un numéro Pokédex (4, 0004) ou nom.
    Renvoie None si introuvable."""
    raw = choice.strip()
    if raw.isdigit():
        try:
            # Chercher par numéro de Pokédex, pas par ID du dictionnaire
            pokedex_num = raw.zfill(4)  # Convertir en format 0004
            for sid, (nom, code) in starters.items():
                if code == pokedex_num:
                    return sid
        except Exception:
            pass
    # Nom
    norm = normalize_starter_name(raw)
    for sid, (nom, _code) in starters.items():
        if normalize_starter_name(nom) == norm:
            return sid
    return None
