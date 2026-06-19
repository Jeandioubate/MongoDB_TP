"""
services/client_service.py — CRUD clients
"""

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from MongoTp.db import get_db
from MongoTp.models.client import build_client


def _col():
    return get_db()["clients"]


def creer_client(nom, prenom, email, telephone="", rue="", ville="", code_postal=""):
    doc = build_client(nom, prenom, email, telephone, rue, ville, code_postal)
    try:
        result = _col().insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc
    except DuplicateKeyError:
        raise ValueError(f"L'email '{email}' est déjà utilisé.")


def rechercher_clients(terme: str) -> list:
    """Recherche par nom, prénom ou email (insensible à la casse)."""
    regex = {"$regex": terme, "$options": "i"}
    return list(_col().find({
        "$or": [{"nom": regex}, {"prenom": regex}, {"email": regex}]
    }))


def obtenir_client(client_id) -> dict | None:
    if isinstance(client_id, str):
        client_id = ObjectId(client_id)
    return _col().find_one({"_id": client_id})


def lister_clients() -> list:
    return list(_col().find().sort("nom", 1))


def modifier_client(client_id, **champs):
    if isinstance(client_id, str):
        client_id = ObjectId(client_id)
    mise_a_jour = {}
    mapping = {
        "nom":        lambda v: v.strip().upper(),
        "prenom":     lambda v: v.strip().capitalize(),
        "email":      lambda v: v.strip().lower(),
        "telephone":  lambda v: v.strip(),
        "adresse.rue":        lambda v: v.strip(),
        "adresse.ville":      lambda v: v.strip().capitalize(),
        "adresse.codePostal": lambda v: v.strip(),
    }
    for cle, valeur in champs.items():
        if cle in mapping and valeur:
            mise_a_jour[cle] = mapping[cle](valeur)
    if not mise_a_jour:
        return False
    result = _col().update_one({"_id": client_id}, {"$set": mise_a_jour})
    return result.modified_count > 0


def supprimer_client(client_id) -> bool:
    if isinstance(client_id, str):
        client_id = ObjectId(client_id)
    # Vérifier qu'il n'a plus de comptes
    nb_comptes = get_db()["comptes"].count_documents({"clientId": client_id})
    if nb_comptes > 0:
        raise ValueError("Impossible de supprimer : le client possède encore des comptes.")
    result = _col().delete_one({"_id": client_id})
    return result.deleted_count > 0
