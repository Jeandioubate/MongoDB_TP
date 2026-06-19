"""
services/compte_service.py — CRUD comptes + opérations
"""

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from MongoTp.db import get_db
from MongoTp.models.compte import (
    build_compte, build_depot, build_retrait, build_virement
)


def _col():
    return get_db()["comptes"]


# ── COMPTES ──────────────────────────────────────────────────────────────────

def creer_compte(numero: str, type_compte: str, solde_initial: float,
                 client_id) -> dict:
    if isinstance(client_id, str):
        client_id = ObjectId(client_id)
    # Vérifier que le client existe
    client = get_db()["clients"].find_one({"_id": client_id})
    if not client:
        raise ValueError("Client introuvable.")
    if type_compte not in ("courant", "epargne"):
        raise ValueError("Type de compte invalide. Choisir 'courant' ou 'epargne'.")
    if solde_initial < 0:
        raise ValueError("Le solde initial ne peut pas être négatif.")
    doc = build_compte(numero, type_compte, solde_initial, client_id)
    try:
        result = _col().insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc
    except DuplicateKeyError:
        raise ValueError(f"Le numéro de compte '{numero}' existe déjà.")


def obtenir_compte(compte_id) -> dict | None:
    if isinstance(compte_id, str):
        compte_id = ObjectId(compte_id)
    return _col().find_one({"_id": compte_id})


def obtenir_compte_par_numero(numero: str) -> dict | None:
    return _col().find_one({"numero": numero})


def lister_comptes(client_id=None) -> list:
    filtre = {"clientId": ObjectId(client_id)} if client_id else {}
    return list(_col().find(filtre).sort("numero", 1))


def modifier_compte(compte_id, **champs) -> bool:
    if isinstance(compte_id, str):
        compte_id = ObjectId(compte_id)
    mise_a_jour = {}
    if champs.get("type"):
        if champs["type"] not in ("courant", "epargne"):
            raise ValueError("Type invalide.")
        mise_a_jour["type"] = champs["type"]
    if champs.get("devise"):
        mise_a_jour["devise"] = champs["devise"].strip().upper()
    if not mise_a_jour:
        return False
    result = _col().update_one({"_id": compte_id}, {"$set": mise_a_jour})
    return result.modified_count > 0


def supprimer_compte(compte_id) -> bool:
    if isinstance(compte_id, str):
        compte_id = ObjectId(compte_id)
    compte = _col().find_one({"_id": compte_id})
    if not compte:
        raise ValueError("Compte introuvable.")
    if compte.get("solde", 0) != 0:
        raise ValueError("Impossible de supprimer : le solde doit être à 0 €.")
    result = _col().delete_one({"_id": compte_id})
    return result.deleted_count > 0


# ── OPÉRATIONS ───────────────────────────────────────────────────────────────

def effectuer_depot(compte_id, montant: float) -> dict:
    if isinstance(compte_id, str):
        compte_id = ObjectId(compte_id)
    if montant <= 0:
        raise ValueError("Le montant doit être positif.")
    op = build_depot(montant)
    result = _col().update_one(
        {"_id": compte_id},
        {
            "$push": {"operations": op},
            "$inc":  {"solde": montant},
        }
    )
    if result.modified_count == 0:
        raise ValueError("Compte introuvable.")
    return op


def effectuer_retrait(compte_id, montant: float) -> dict:
    if isinstance(compte_id, str):
        compte_id = ObjectId(compte_id)
    if montant <= 0:
        raise ValueError("Le montant doit être positif.")
    compte = _col().find_one({"_id": compte_id})
    if not compte:
        raise ValueError("Compte introuvable.")
    if compte["solde"] < montant:
        raise ValueError(
            f"Solde insuffisant. Solde disponible : {compte['solde']:.2f} €"
        )
    op = build_retrait(montant)
    _col().update_one(
        {"_id": compte_id},
        {
            "$push": {"operations": op},
            "$inc":  {"solde": -montant},
        }
    )
    return op


def effectuer_virement(compte_source_id, compte_dest_id, montant: float,
                       motif: str = "") -> dict:
    if isinstance(compte_source_id, str):
        compte_source_id = ObjectId(compte_source_id)
    if isinstance(compte_dest_id, str):
        compte_dest_id = ObjectId(compte_dest_id)
    if compte_source_id == compte_dest_id:
        raise ValueError("Les comptes source et destinataire doivent être différents.")
    if montant <= 0:
        raise ValueError("Le montant doit être positif.")

    source = _col().find_one({"_id": compte_source_id})
    dest   = _col().find_one({"_id": compte_dest_id})
    if not source:
        raise ValueError("Compte source introuvable.")
    if not dest:
        raise ValueError("Compte destinataire introuvable.")
    if source["solde"] < montant:
        raise ValueError(
            f"Solde insuffisant. Solde disponible : {source['solde']:.2f} €"
        )

    op = build_virement(montant, compte_source_id, compte_dest_id, motif)

    # Débit source
    _col().update_one(
        {"_id": compte_source_id},
        {"$push": {"operations": op}, "$inc": {"solde": -montant}}
    )
    # Crédit destination
    _col().update_one(
        {"_id": compte_dest_id},
        {"$push": {"operations": op}, "$inc": {"solde": montant}}
    )
    return op


def historique_operations(compte_id, type_filtre: str = None) -> list:
    if isinstance(compte_id, str):
        compte_id = ObjectId(compte_id)
    compte = _col().find_one({"_id": compte_id})
    if not compte:
        raise ValueError("Compte introuvable.")
    ops = compte.get("operations", [])
    if type_filtre:
        ops = [o for o in ops if o["type"] == type_filtre]
    return sorted(ops, key=lambda o: o["date"], reverse=True)
