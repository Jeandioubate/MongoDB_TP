"""
seed.py — Initialisation de la base de données avec un jeu de données initial
Usage : python -m banque.seed
"""

from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, ASCENDING
from MongoTp.config import MONGO_URI, DB_NAME


def run():
    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]
    col_clients = db["clients"]
    col_comptes = db["comptes"]

    # ── Nettoyage ──────────────────────────────────────────────────────────
    col_clients.delete_many({})
    col_comptes.delete_many({})
    print("Collections vidées")

    # ── Index ──────────────────────────────────────────────────────────────
    col_clients.create_index([("email", ASCENDING)], unique=True)
    col_comptes.create_index([("numero", ASCENDING)], unique=True)
    col_comptes.create_index([("clientId", ASCENDING)])
    col_comptes.create_index([("operations.date", ASCENDING)])
    col_comptes.create_index([("operations.type", ASCENDING)])
    print("Index créés")

    # ── Clients ────────────────────────────────────────────────────────────
    clients_data = [
        {
            "nom": "DUPONT", "prenom": "Alice",
            "email": "alice.dupont@mail.fr", "telephone": "+33612345678",
            "adresse": {"rue": "12 rue de la Paix", "ville": "Paris", "codePostal": "75001"},
            "dateCreation": datetime(2024, 1, 15),
        },
        {
            "nom": "MARTIN", "prenom": "Bruno",
            "email": "bruno.martin@mail.fr", "telephone": "+33698765432",
            "adresse": {"rue": "5 avenue Foch", "ville": "Lyon", "codePostal": "69006"},
            "dateCreation": datetime(2024, 1, 16),
        },
        {
            "nom": "LEROY", "prenom": "Claire",
            "email": "claire.leroy@mail.fr", "telephone": "+33677889900",
            "adresse": {"rue": "8 boulevard Victor Hugo", "ville": "Marseille", "codePostal": "13001"},
            "dateCreation": datetime(2024, 1, 17),
        },
    ]
    res = col_clients.insert_many(clients_data)
    id_alice, id_bruno, id_claire = res.inserted_ids
    print(f"{len(res.inserted_ids)} clients créés")

    # ── IDs comptes pré-générés (nécessaires pour les virements) ──────────
    id_cpt_alice_c  = ObjectId()
    id_cpt_alice_e  = ObjectId()
    id_cpt_bruno    = ObjectId()
    id_cpt_claire   = ObjectId()

    # ── Comptes avec opérations ────────────────────────────────────────────
    comptes_data = [

        # Alice — Compte courant
        {
            "_id":    id_cpt_alice_c,
            "numero": "FR76-3000-1001-0001",
            "type":   "courant", "solde": 2450.00, "devise": "EUR",
            "clientId": id_alice, "dateCreation": datetime(2024, 1, 20),
            "operations": [
                {"_id": ObjectId(), "type": "depot",    "montant": 3000.00, "date": datetime(2024, 1, 20), "statut": "valide"},
                {"_id": ObjectId(), "type": "retrait",  "montant":  200.00, "date": datetime(2024, 2,  5), "statut": "valide"},
                {"_id": ObjectId(), "type": "virement", "montant":  350.00, "date": datetime(2024, 3, 10), "statut": "valide",
                 "compteSourceId": id_cpt_alice_c, "compteDestId": id_cpt_bruno, "motif": "Remboursement dîner"},
            ],
        },

        # Alice — Compte épargne
        {
            "_id":    id_cpt_alice_e,
            "numero": "FR76-3000-1001-0002",
            "type":   "epargne", "solde": 8000.00, "devise": "EUR",
            "clientId": id_alice, "dateCreation": datetime(2024, 1, 25),
            "operations": [
                {"_id": ObjectId(), "type": "depot", "montant": 5000.00, "date": datetime(2024, 1, 25), "statut": "valide"},
                {"_id": ObjectId(), "type": "depot", "montant": 3000.00, "date": datetime(2024, 2, 15), "statut": "valide"},
            ],
        },

        # Bruno — Compte courant
        {
            "_id":    id_cpt_bruno,
            "numero": "FR76-3000-1002-0001",
            "type":   "courant", "solde": 1200.00, "devise": "EUR",
            "clientId": id_bruno, "dateCreation": datetime(2024, 1, 18),
            "operations": [
                {"_id": ObjectId(), "type": "depot",    "montant": 1500.00, "date": datetime(2024, 1, 18), "statut": "valide"},
                {"_id": ObjectId(), "type": "retrait",  "montant":  650.00, "date": datetime(2024, 2, 20), "statut": "valide"},
                {"_id": ObjectId(), "type": "virement", "montant":  350.00, "date": datetime(2024, 3, 10), "statut": "valide",
                 "compteSourceId": id_cpt_alice_c, "compteDestId": id_cpt_bruno, "motif": "Remboursement dîner"},
            ],
        },

        # Claire — Compte courant
        {
            "_id":    id_cpt_claire,
            "numero": "FR76-3000-1003-0001",
            "type":   "courant", "solde": 3750.00, "devise": "EUR",
            "clientId": id_claire, "dateCreation": datetime(2024, 1, 22),
            "operations": [
                {"_id": ObjectId(), "type": "depot",    "montant": 4000.00, "date": datetime(2024, 1, 22), "statut": "valide"},
                {"_id": ObjectId(), "type": "retrait",  "montant":  500.00, "date": datetime(2024, 3,  1), "statut": "valide"},
                {"_id": ObjectId(), "type": "virement", "montant":  250.00, "date": datetime(2024, 3, 15), "statut": "valide",
                 "compteSourceId": id_cpt_claire, "compteDestId": id_cpt_alice_c, "motif": "Loyer mars"},
            ],
        },
    ]

    res = col_comptes.insert_many(comptes_data)
    print(f"{len(res.inserted_ids)} comptes créés")

    print("─" * 56)
    for cpt in col_comptes.find():
        nb = len(cpt.get("operations", []))
        print(f"   {cpt['numero']} ({cpt['type']:7}) │ {cpt['solde']:>9.2f} € │ {nb} opération(s)")
    print("─" * 56)
    print("Initialisation terminée\n")
    client.close()


if __name__ == "__main__":
    run()
