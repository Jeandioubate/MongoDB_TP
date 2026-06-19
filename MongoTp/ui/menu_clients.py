"""
ui/menu_clients.py — Menu de gestion des clients
"""

from MongoTp.ui.utils import (
    titre, succes, erreur, info, saisir, menu,
    afficher_client, separateur, BOLD, RESET, GREY
)
from MongoTp.services import client_service as svc


def creer():
    titre("Créer un client")
    try:
        nom        = saisir("Nom")
        prenom     = saisir("Prénom")
        email      = saisir("Email")
        telephone  = saisir("Téléphone", obligatoire=False)
        print(f"\n  {BOLD}Adresse (optionnel){RESET}")
        rue        = saisir("Rue", obligatoire=False)
        ville      = saisir("Ville", obligatoire=False)
        code_postal = saisir("Code postal", obligatoire=False)
        client = svc.creer_client(nom, prenom, email, telephone, rue, ville, code_postal)
        succes(f"Client créé avec succès (ID : {client['_id']})")
        afficher_client(client)
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def rechercher():
    titre("Rechercher un client")
    terme = saisir("Nom, prénom ou email")
    resultats = svc.rechercher_clients(terme)
    if not resultats:
        info("Aucun client trouvé.")
    else:
        info(f"{len(resultats)} résultat(s) :")
        separateur()
        for c in resultats:
            afficher_client(c, compact=True)
        separateur()
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def modifier():
    titre("Modifier un client")
    terme = saisir("Rechercher le client (nom, prénom ou email)")
    resultats = svc.rechercher_clients(terme)
    if not resultats:
        info("Aucun client trouvé.")
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return

    separateur()
    for i, c in enumerate(resultats, 1):
        print(f"  {i}. ", end="")
        afficher_client(c, compact=True)
    separateur()

    try:
        idx = int(saisir("Numéro du client à modifier")) - 1
        client = resultats[idx]
    except (ValueError, IndexError):
        erreur("Sélection invalide.")
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return

    afficher_client(client)
    info("Laissez vide pour conserver la valeur actuelle.")
    champs = {
        "nom":               saisir("Nouveau nom", obligatoire=False),
        "prenom":            saisir("Nouveau prénom", obligatoire=False),
        "email":             saisir("Nouvel email", obligatoire=False),
        "telephone":         saisir("Nouveau téléphone", obligatoire=False),
        "adresse.rue":       saisir("Nouvelle rue", obligatoire=False),
        "adresse.ville":     saisir("Nouvelle ville", obligatoire=False),
        "adresse.codePostal": saisir("Nouveau code postal", obligatoire=False),
    }
    try:
        if svc.modifier_client(client["_id"], **champs):
            succes("Client modifié avec succès.")
        else:
            info("Aucune modification apportée.")
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def supprimer():
    titre("Supprimer un client")
    terme = saisir("Rechercher le client (nom, prénom ou email)")
    resultats = svc.rechercher_clients(terme)
    if not resultats:
        info("Aucun client trouvé.")
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return

    separateur()
    for i, c in enumerate(resultats, 1):
        print(f"  {i}. ", end="")
        afficher_client(c, compact=True)
    separateur()

    try:
        idx = int(saisir("Numéro du client à supprimer")) - 1
        client = resultats[idx]
    except (ValueError, IndexError):
        erreur("Sélection invalide.")
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return

    afficher_client(client)
    confirm = saisir(f"Confirmer la suppression ? (oui/non)")
    if confirm.lower() != "oui":
        info("Suppression annulée.")
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    try:
        svc.supprimer_client(client["_id"])
        succes("Client supprimé avec succès.")
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def lister():
    titre("Liste des clients")
    clients = svc.lister_clients()
    if not clients:
        info("Aucun client enregistré.")
    else:
        info(f"{len(clients)} client(s) :")
        separateur()
        for c in clients:
            afficher_client(c, compact=True)
        separateur()
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def run():
    while True:
        choix = menu("GESTION DES CLIENTS", [
            ("creer",     "Créer un client"),
            ("rechercher","Rechercher un client"),
            ("modifier",  "Modifier un client"),
            ("supprimer", "Supprimer un client"),
            ("lister",    "Lister les clients"),
        ])
        if choix == "0":
            break
        actions = {"1": creer, "2": rechercher, "3": modifier,
                   "4": supprimer, "5": lister}
        actions.get(choix, lambda: None)()
