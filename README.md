# 🎮 PokeTrainer - Bot Discord Pokémon

Bot Discord Pokémon complet : spawns aléatoires, captures, quiz starter, Pokédex paginé, équipe 3x2 avec détails, et PC (boîtes, renommage, navigation). Architecture optimisée avec affichages centralisés et interactions modernes.

## ✨ Fonctionnalités

### 🌟 Spawns & Captures
- **Spawns aléatoires** : apparitions de Pokémon sauvages avec timer (30 min) et code de capture unique
- **Système de capture** : réussite/échec basé sur taux et tirage aléatoire
- **Ajout automatique** : à l'équipe (si place) ou au PC

### 🎯 Quiz Starter
- **Choix guidé** : arbre de décision interactif pour sélectionner ton starter
- **Option aléatoire** : starter surprise
- **Affichage complet** : sprite, stats, confirmation

### 📖 Pokédex
- **Pagination par génération** : Gen 1 à 6 (151 à 721 Pokémon)
- **Recherche** : trouve un Pokémon par nom
- **Grille 6×5** : grandes vignettes avec sprites et numéros Pokédex
- **Navigation fluide** : boutons Précédent/Suivant, sélection de génération

### 👥 Équipe
- **Vue en grille 3×2** : tous les membres de ton équipe
- **Détails complets** : stats (PV, Attaque, Défense, Att. Spé, Déf. Spé, Vitesse), type, niveau, sexe
- **Navigation** : clique sur un slot pour voir les détails

### 💾 PC (Boîtes)
- **32 boîtes** : 30 slots par boîte (960 Pokémon max)
- **Affichage 6×5** : vue claire de chaque boîte
- **Renommage** : personnalise tes boîtes
- **Navigation** : goto, précédent, suivant
- **Détails par slot** : stats complètes et sprite agrandi

### 📊 Historique
- **Suivi des commandes** : historique par utilisateur
- **Affichage** : 10 dernières commandes avec timestamps
- **Nettoyage** : vide ton historique

## 🏗️ Architecture du projet

```
PokeTrainer/
├── Back/                           # Backend Python
│   ├── main.py                     # Commandes Discord (bot entry point)
│   ├── Classes.py                  # Views/Buttons/Modals (interactions Discord)
│   ├── DisplayFunction.py          # Centralisation des affichages (embeds + images)
│   ├── DatabaseFunction.py         # Accès DB (SQLite), requêtes, helpers
│   ├── OtherCode.py                # Utilitaires quiz et starters
│   ├── PokeKey.env                 # Clés/secrets (DISCORD_TOKEN) ⚠️ À ne pas commit
│   ├── Database.sqlite             # Base de données SQLite
│   └── sqlite commands/            # Scripts SQL et utilitaires DB
│       ├── reset_database.py       # Script de reset complet de la DB
│       ├── Pokedex_creation.sqlite3-query  # Données Pokédex (INSERT + UPDATE)
│       ├── initiation des boites.sqlite3-query
│       ├── reset starter.sqlite3-query
│       └── things.sqlite3-query
│
├── PokeSprites/                    # Sprites des Pokémon (Poke0001.png à Poke0721.png)
├── DresseurSprites/                # Sprites des dresseurs
├── Icons/                          # Icônes UI
│
├── README.md                       # Documentation (ce fichier)
└── .gitignore                      # Fichiers ignorés par Git
```

### 📦 Modules principaux

| Fichier | Rôle | Dépendances |
|---------|------|-------------|
| **main.py** | Commandes slash (/spawn, /capture, /team, etc.) | discord.py, DatabaseFunction, DisplayFunction |
| **Classes.py** | Composants interactifs (Views, Buttons, Modals) | discord.py, DisplayFunction, DatabaseFunction |
| **DisplayFunction.py** | Génération d'embeds et d'images (centralisé) | discord, PIL (Image, ImageDraw, ImageFont) |
| **DatabaseFunction.py** | Accès et gestion SQLite (CRUD, requêtes) | sqlite3 |
| **OtherCode.py** | Quiz starters, arbre de décision | discord.py, DisplayFunction |

### 🗄️ Structure de la base de données

**Tables principales :**
- `User` : utilisateurs (Id, Pseudo, StarterPokemon, PokemonId)
- `Team` : équipes de 6 Pokémon (idUser, Owner, pokemonId1-6)
- `PC` : stockage PC (idUser, ownerPseudo, idPokemons JSON, BoîtesName JSON)
- `AllPokemons` : instances individuelles (Id_Pokemon, Name, Pokedex_Number, stats, Sexe, IdOwner, DateCapture, Location)
- `Pokedex` : référence Pokémon (Id, Nom, Image, CatchRate, Type1, Type2)
- `SpawnedPokemons` : spawns actifs (PokedexId, spawn_time, despawn_time, CaptureCode, Niveau)
- `CommandHistory` : historique des commandes (userId, commandName, timestamp)

## 🚀 Installation

### Prérequis
- Python 3.10+
- discord.py 2.0+
- Pillow (PIL)
- sqlite3 (inclus avec Python)

### Étapes

1. **Clone le projet**
```bash
git clone https://github.com/ton-repo/PokeTrainer.git
cd PokeTrainer
```

2. **Installe les dépendances**
```bash
pip install discord.py pillow python-dotenv
```

3. **Configure le token Discord**
Crée un fichier `Back/PokeKey.env` :
```env
DISCORD_TOKEN=ton_token_discord_ici
```

4. **Initialise la base de données**
```bash
cd Back
python -c "import DatabaseFunction as db; db.init_database()"
```

5. **Importe les données Pokédex** (voir section ci-dessous)

6. **Lance le bot**
```bash
python Back/main.py
```

## 🔄 Reset de la base de données

### Quand faire un reset ?
- Après avoir modifié la structure des tables dans `DatabaseFunction.py`
- Pour repartir de zéro (tests, développement)
- En cas de corruption de la base

### Procédure complète

1. **Lance le script de reset**
```bash
python 'Back/sqlite commands/reset_database.py'
```
Tape `oui` pour confirmer.

2. **Réimporte les données Pokédex**

Le fichier `Pokedex_creation.sqlite3-query` contient deux blocs essentiels :

**Bloc 1 : INSERT (lignes 3-912)** - Insère tous les Pokémon (Gen 1 à 6)
- Gen 1 (lignes 3-156) : 151 Pokémon avec INSERT INTO (Id, Nom)
- Gen 2-6 (lignes 327-912) : Pokémon suivants avec INSERT INTO (Id, Nom, Image)

**Bloc 2 : UPDATE (lignes 158-317)** - Ajoute CatchRate et Image pour Gen 1
- Met à jour les taux de capture (CatchRate)
- Ajoute les noms de fichiers images (Image = 'Poke' || Id || '.png')

**Méthode 1 : Via Python (recommandée)**
```python
# Exécute depuis le dossier racine PokeTrainer/
import sqlite3
conn = sqlite3.connect('Back/Database.sqlite')
cursor = conn.cursor()

# Lis et exécute le fichier SQL complet
with open('Back/sqlite commands/Pokedex_creation.sqlite3-query', 'r', encoding='utf-8') as f:
    sql_script = f.read()
    cursor.executescript(sql_script)

conn.commit()
conn.close()
print("Pokédex importé avec succès!")
```

**Méthode 2 : Via sqlite3 CLI**
```bash
# Depuis le dossier racine PokeTrainer/
sqlite3 Back/Database.sqlite < "Back/sqlite commands/Pokedex_creation.sqlite3-query"
```

3. **Vérifie l'importation**
```python
import sqlite3
conn = sqlite3.connect('Back/Database.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM Pokedex")
count = cursor.fetchone()[0]
print(f"Nombre de Pokémon dans le Pokédex : {count}")
# Devrait afficher : Nombre de Pokémon dans le Pokédex : 721

cursor.execute("SELECT Id, Nom, Image, CatchRate FROM Pokedex WHERE Id IN ('0001', '0025', '0152', '0721')")
print(cursor.fetchall())
# Devrait afficher des données complètes avec Image et CatchRate
conn.close()
```

### ⚠️ Important après un reset
- **Tous les utilisateurs** seront supprimés
- **Toutes les équipes** seront perdues
- **Tout le PC** sera vidé
- **L'historique** sera effacé
- **Les spawns actifs** seront supprimés
- **Seules les structures de tables** seront recréées

## 📝 Commandes Discord

| Commande | Description |
|----------|-------------|
| `/letsgo` | Commence ton aventure, initialise ton profil |
| `/spawn` | Fait apparaître un Pokémon sauvage (30 min de durée) |
| `/capture <code>` | Capture un Pokémon spawné avec son code |
| `/team` | Affiche ton équipe en grille 3×2 avec détails |
| `/pokedex [generation]` | Ouvre le Pokédex paginé (par défaut Gen 1) |
| `/pc [boite]` | Affiche une boîte PC (par défaut Boîte 1) |
| `/derniere_commande` | Affiche ta dernière commande exécutée |
| `/historique` | Affiche les 10 dernières commandes |
| `/vider_historique` | Supprime tout ton historique |

## 🎨 Affichages & Design

- **Embeds Discord** : titres colorés, champs organisés, footers informatifs
- **Images générées** : sprites Pokémon agrandis (x2), grilles composées (PIL)
- **Interactions modernes** : Views avec Buttons, Modals pour saisies, navigation fluide
- **Couleurs cohérentes** : vert (spawns), or (captures réussies), rouge (échecs), bleu (équipe/pokédex)

## 🔧 Développement

### Architecture de séparation
- **DisplayFunction.py** : toute la génération d'embeds et d'images (pure functions, stateless)
- **Classes.py** : toutes les interactions Discord (Views, Buttons, Modals, callbacks)
- **DatabaseFunction.py** : tous les accès DB (requêtes, CRUD, helpers)
- **main.py** : commandes slash (thin controllers, délèguent à DisplayFunction et DatabaseFunction)

### Bonnes pratiques
- ✅ Pas de génération d'embeds dans `Classes.py` → tout dans `DisplayFunction.py`
- ✅ Pas de SQL inline dans `main.py` → tout dans `DatabaseFunction.py`
- ✅ Views = interaction seulement (boutons, modals, callbacks)
- ✅ Fonctions display = affichage seulement (embeds, images, fichiers)
- ✅ Commits explicites, branches par fonctionnalité

### Branches recommandées
- `principal` : version stable, prête à déployer
- `developpement` : intégration avant bascule sur principal
- `fonction/*` : une branche par feature (ex: `fonction/apparitions`, `fonction/pc-details`)
- `correctif/*` : corrections urgentes depuis principal

## 🐛 Dépannage

**Erreur : "Module discord not found"**
```bash
pip install discord.py
```

**Erreur : "Module PIL not found"**
```bash
pip install pillow
```

**Erreur : "No such file: PokeSprites/Poke0001.png"**
- Vérifie que le dossier `PokeSprites/` contient les sprites `Poke0001.png` à `Poke0721.png`

**Bot ne répond pas**
- Vérifie le token dans `Back/PokeKey.env`
- Vérifie les permissions du bot sur Discord (Send Messages, Embed Links, Attach Files)
- Vérifie que les intents sont activés (Message Content Intent)

**Base corrompue**
- Fais un reset complet (voir section "Reset de la base de données")

## 📄 Licence

Ce projet est un bot Discord éducatif. Pokémon est une marque déposée de Nintendo/Game Freak/Creatures Inc.

## 🤝 Contribution

Les contributions sont les bienvenues ! Ouvre une issue ou une PR pour proposer des améliorations.

---

**Développé avec ❤️ par l'équipe PokeTrainer**
