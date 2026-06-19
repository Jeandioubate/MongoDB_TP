"""
models/compte.py — Construction des documents Compte et Opération
"""

from datetime import datetime
from bson import ObjectId


def build_compte(numero: str, type_compte: str, solde: float,
                 client_id: ObjectId, devise: str = "EUR") -> dict:
    return {
        "numero":       numero.strip(),
        "type":         type_compte,
        "solde":        round(solde, 2),
        "devise":       devise,
        "clientId":     client_id,
        "dateCreation": datetime.now(),
        "operations":   [],
    }


def build_depot(montant: float) -> dict:
    return {
        "_id":     ObjectId(),
        "type":    "depot",
        "montant": round(montant, 2),
        "date":    datetime.now(),
        "statut":  "valide",
    }


def build_retrait(montant: float) -> dict:
    return {
        "_id":     ObjectId(),
        "type":    "retrait",
        "montant": round(montant, 2),
        "date":    datetime.now(),
        "statut":  "valide",
    }


def build_virement(montant: float, source_id: ObjectId,
                   dest_id: ObjectId, motif: str = "") -> dict:
    return {
        "_id":           ObjectId(),
        "type":          "virement",
        "montant":       round(montant, 2),
        "date":          datetime.now(),
        "statut":        "valide",
        "compteSourceId": source_id,
        "compteDestId":   dest_id,
        "motif":         motif.strip(),
    }
