"""
main.py — Point d'entrée de l'application bancaire console
Usage : python -m banque.main
"""

import sys
from MongoTp.db import get_db, close_db
from MongoTp.ui.utils import menu, BOLD, CYAN, RESET, GREEN, GREY
from MongoTp.ui import menu_clients, menu_comptes


BANNER = f"""
{BOLD}{CYAN}
#€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€
#€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€

  BIENVENUE A LA BANQUE YMO_GROUP

#€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€
#€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€
{RESET}{GREEN}         Application de gestion bancaire — v1.0{RESET}
"""


def main():
    print(BANNER)

    # Connexion
    try:
        db = get_db()
        db.command("ping")
        print(f"  {GREEN}✔ Connexion MongoDB établie{RESET}\n")
    except Exception as e:
        print(f"\n  ✘ Impossible de se connecter à MongoDB : {e}")
        print(f"  Vérifiez que MongoDB est démarré et que l'URI est correct dans config.py\n")
        sys.exit(1)

    # Demander si on souhaite réinitialiser les données
    rep = input(f"  {BOLD}Initialiser le jeu de données de démo ? (oui/non){RESET} : ").strip().lower()
    if rep == "oui":
        from MongoTp.seed import run as seed_run
        seed_run()

    # Menu principal
    while True:
        choix = menu("MENU PRINCIPAL", [
            ("clients",    "Gestion des clients"),
            ("comptes",    "Gestion des comptes"),
            ("operations", "Gestion des opérations"),
        ])
        if choix == "0":
            print(f"\n  {GREY}Au revoir !{RESET}\n")
            break
        elif choix == "1":
            menu_clients.run()
        elif choix == "2":
            menu_comptes.run_comptes()
        elif choix == "3":
            menu_comptes.run_operations()

    close_db()


if __name__ == "__main__":
    main()
