import os, sys

# Ajout du dossier Back au chemin pour importer DatabaseFunction
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACK_DIR = os.path.dirname(CURRENT_DIR)  # dossier Back
if BACK_DIR not in sys.path:
    sys.path.append(BACK_DIR)

import DatabaseFunction as db

if __name__ == "__main__":
    # Sécurité : demander confirmation dans la console si lancé manuellement
    confirmation = input("Confirmer le reset complet de la base ? (oui/non): ").strip().lower()
    if confirmation == "oui":
        db.reset_database(confirm=True)
        print("Reset terminé. Tables vides recréées.")
    else:
        print("Reset annulé.")
