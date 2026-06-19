"""
ui/menu_comptes.py — Menu de gestion des comptes et opérations
"""

from MongoTp.ui.utils import (
    titre, succes, erreur, info, saisir, saisir_montant,
    saisir_choix, menu, afficher_compte, afficher_operation,
    separateur, BOLD, RESET, GREY
)
from MongoTp.services import client_service as cli_svc
from MongoTp.services import compte_service as cpt_svc


# ── Helpers ────────────────────────────────────────────────────────────────

def _choisir_client():
    terme = saisir("Rechercher le client (nom, prénom ou email)")
    resultats = cli_svc.rechercher_clients(terme)
    if not resultats:
        info("Aucun client trouvé.")
        return None
    separateur()
    for i, c in enumerate(resultats, 1):
        from MongoTp.ui.utils import afficher_client
        print(f"  {i}. ", end="")
        afficher_client(c, compact=True)
    separateur()
    try:
        idx = int(saisir("Numéro du client")) - 1
        return resultats[idx]
    except (ValueError, IndexError):
        erreur("Sélection invalide.")
        return None


def _choisir_compte(prompt_client: bool = True):
    if prompt_client:
        client = _choisir_client()
        if not client:
            return None, None
        comptes = cpt_svc.lister_comptes(client_id=str(client["_id"]))
    else:
        comptes = cpt_svc.lister_comptes()
        client  = None

    if not comptes:
        info("Aucun compte trouvé pour ce client.")
        return None, None

    separateur()
    for i, cpt in enumerate(comptes, 1):
        print(f"  {i}. ", end="")
        afficher_compte(cpt, compact=True)
    separateur()
    try:
        idx = int(saisir("Numéro du compte")) - 1
        cpt = comptes[idx]
        if client is None:
            client = cli_svc.obtenir_client(cpt["clientId"])
        return cpt, client
    except (ValueError, IndexError):
        erreur("Sélection invalide.")
        return None, None


# ── Gestion des comptes ────────────────────────────────────────────────────

def creer():
    titre("Créer un compte")
    client = _choisir_client()
    if not client:
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    info(f"Client sélectionné : {client['prenom']} {client['nom']}")
    try:
        numero     = saisir("Numéro de compte (ex: FR76-3000-1004-0001)")
        type_cpt   = saisir_choix("Type (courant/epargne)", ["courant", "epargne"])
        solde_init = saisir_montant("Solde initial (€)")
        cpt = cpt_svc.creer_compte(numero, type_cpt, solde_init, client["_id"])
        succes(f"Compte créé avec succès (ID : {cpt['_id']})")
        afficher_compte(cpt, client)
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def consulter():
    titre("Consulter un compte")
    cpt, client = _choisir_compte()
    if cpt:
        afficher_compte(cpt, client)
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def modifier():
    titre("Modifier un compte")
    cpt, client = _choisir_compte()
    if not cpt:
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    afficher_compte(cpt, client)
    info("Laissez vide pour conserver la valeur actuelle.")
    champs = {
        "type":   saisir("Nouveau type (courant/epargne)", obligatoire=False),
        "devise": saisir("Nouvelle devise (EUR, USD…)", obligatoire=False),
    }
    try:
        if cpt_svc.modifier_compte(cpt["_id"], **champs):
            succes("Compte modifié avec succès.")
        else:
            info("Aucune modification apportée.")
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def supprimer():
    titre("Supprimer un compte")
    cpt, client = _choisir_compte()
    if not cpt:
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    afficher_compte(cpt, client)
    confirm = saisir("Confirmer la suppression ? (oui/non)")
    if confirm.lower() != "oui":
        info("Suppression annulée.")
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    try:
        cpt_svc.supprimer_compte(cpt["_id"])
        succes("Compte supprimé avec succès.")
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def lister():
    titre("Lister les comptes")
    choix = saisir_choix("Afficher (tous/client)", ["tous", "client"])
    if choix == "client":
        client = _choisir_client()
        if not client:
            input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
            return
        comptes = cpt_svc.lister_comptes(client_id=str(client["_id"]))
        info(f"Comptes de {client['prenom']} {client['nom']} :")
    else:
        comptes = cpt_svc.lister_comptes()
        info(f"{len(comptes)} compte(s) au total :")

    if not comptes:
        info("Aucun compte trouvé.")
    else:
        separateur()
        for cpt in comptes:
            cl = None if choix == "client" else cli_svc.obtenir_client(cpt["clientId"])
            afficher_compte(cpt, cl, compact=True)
        separateur()
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


# ── Gestion des opérations ────────────────────────────────────────────────

def depot():
    titre("Effectuer un dépôt")
    cpt, client = _choisir_compte()
    if not cpt:
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    afficher_compte(cpt, client)
    try:
        montant = saisir_montant("Montant du dépôt (€)")
        op = cpt_svc.effectuer_depot(cpt["_id"], montant)
        cpt_maj = cpt_svc.obtenir_compte(cpt["_id"])
        succes(f"Dépôt de {montant:.2f} € effectué. Nouveau solde : {cpt_maj['solde']:.2f} €")
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def retrait():
    titre("Effectuer un retrait")
    cpt, client = _choisir_compte()
    if not cpt:
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    afficher_compte(cpt, client)
    try:
        montant = saisir_montant("Montant du retrait (€)")
        cpt_svc.effectuer_retrait(cpt["_id"], montant)
        cpt_maj = cpt_svc.obtenir_compte(cpt["_id"])
        succes(f"Retrait de {montant:.2f} € effectué. Nouveau solde : {cpt_maj['solde']:.2f} €")
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def virement():
    titre("Effectuer un virement")
    info("Sélectionner le compte SOURCE")
    cpt_source, client_source = _choisir_compte()
    if not cpt_source:
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    afficher_compte(cpt_source, client_source)

    info("Sélectionner le compte DESTINATAIRE")
    cpt_dest, client_dest = _choisir_compte(prompt_client=True)
    if not cpt_dest:
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return
    afficher_compte(cpt_dest, client_dest)

    try:
        montant = saisir_montant("Montant du virement (€)")
        motif   = saisir("Motif (optionnel)", obligatoire=False)
        cpt_svc.effectuer_virement(cpt_source["_id"], cpt_dest["_id"], montant, motif)
        src_maj  = cpt_svc.obtenir_compte(cpt_source["_id"])
        succes(
            f"Virement de {montant:.2f} € effectué.\n"
            f"  Nouveau solde source : {src_maj['solde']:.2f} €"
        )
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


def historique():
    titre("Historique des opérations")
    cpt, client = _choisir_compte()
    if not cpt:
        input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")
        return

    filtre = saisir_choix("Filtre (tous/depot/retrait/virement)",
                          ["tous", "depot", "retrait", "virement"])
    type_filtre = None if filtre == "tous" else filtre

    try:
        ops = cpt_svc.historique_operations(cpt["_id"], type_filtre)
        info(f"Compte : {cpt['numero']}  — Solde : {cpt['solde']:.2f} €")
        if not ops:
            info("Aucune opération trouvée.")
        else:
            separateur()
            print(f"  {BOLD}{'TYPE':<12}{'DATE':>18}{'MONTANT':>14}{RESET}")
            separateur()
            for op in ops:
                afficher_operation(op)
            separateur()
            info(f"{len(ops)} opération(s) affichée(s).")
    except ValueError as e:
        erreur(str(e))
    input(f"\n  {GREY}Appuyez sur Entrée pour continuer...{RESET}")


# ── Menus ──────────────────────────────────────────────────────────────────

def run_comptes():
    while True:
        choix = menu("GESTION DES COMPTES", [
            ("creer",     "Créer un compte"),
            ("consulter", "Consulter un compte"),
            ("modifier",  "Modifier un compte"),
            ("supprimer", "Supprimer un compte"),
            ("lister",    "Lister les comptes"),
        ])
        if choix == "0":
            break
        actions = {"1": creer, "2": consulter, "3": modifier,
                   "4": supprimer, "5": lister}
        actions.get(choix, lambda: None)()


def run_operations():
    while True:
        choix = menu("GESTION DES OPÉRATIONS", [
            ("depot",      "Effectuer un dépôt"),
            ("retrait",    "Effectuer un retrait"),
            ("virement",   "Effectuer un virement"),
            ("historique", "Consulter l'historique des opérations"),
        ])
        if choix == "0":
            break
        actions = {"1": depot, "2": retrait, "3": virement, "4": historique}
        actions.get(choix, lambda: None)()
