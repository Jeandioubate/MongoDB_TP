"""
models/client.py — Fonctions de validation et construction des documents Client
"""

from datetime import datetime


def build_client(nom: str, prenom: str, email: str, telephone: str = "",
                 rue: str = "", ville: str = "", code_postal: str = "") -> dict:
    return {
        "nom":      nom.strip().upper(),
        "prenom":   prenom.strip().capitalize(),
        "email":    email.strip().lower(),
        "telephone": telephone.strip(),
        "adresse": {
            "rue":        rue.strip(),
            "ville":      ville.strip().capitalize(),
            "codePostal": code_postal.strip(),
        },
        "dateCreation": datetime.now(),
    }
