"""
ui/utils.py — Utilitaires d'affichage console
"""

# ── Couleurs ANSI ─────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GREY   = "\033[90m"
WHITE  = "\033[97m"
BLUE   = "\033[94m"


def titre(texte: str):
    largeur = 56
    print(f"\n{BOLD}{CYAN}{'═' * largeur}{RESET}")
    print(f"{BOLD}{CYAN}  {texte.upper()}{RESET}")
    print(f"{BOLD}{CYAN}{'═' * largeur}{RESET}\n")


def separateur():
    print(f"{GREY}{'─' * 56}{RESET}")


def succes(msg: str):
    print(f"\n{GREEN}✔  {msg}{RESET}")


def erreur(msg: str):
    print(f"\n{RED}✘  {msg}{RESET}")


def info(msg: str):
    print(f"{YELLOW}ℹ  {msg}{RESET}")


def saisir(prompt: str, obligatoire: bool = True) -> str:
    while True:
        valeur = input(f"  {BOLD}{prompt}{RESET} : ").strip()
        if valeur or not obligatoire:
            return valeur
        erreur("Ce champ est obligatoire.")


def saisir_montant(prompt: str) -> float:
    while True:
        try:
            valeur = float(input(f"  {BOLD}{prompt}{RESET} : ").replace(",", "."))
            if valeur > 0:
                return valeur
            erreur("Le montant doit être positif.")
        except ValueError:
            erreur("Veuillez saisir un nombre valide.")


def saisir_choix(prompt: str, options: list[str]) -> str:
    while True:
        val = input(f"  {BOLD}{prompt}{RESET} : ").strip().lower()
        if val in options:
            return val
        erreur(f"Choix invalide. Options : {', '.join(options)}")


def menu(titre_menu: str, options: list[tuple[str, str]]) -> str:
    """Affiche un menu numéroté et retourne le choix saisi."""
    print(f"\n{BOLD}{BLUE}  {titre_menu}{RESET}")
    separateur()
    for i, (_, label) in enumerate(options, 1):
        print(f"  {CYAN}{i}{RESET}. {label}")
    print(f"  {CYAN}0{RESET}. {RED}Retour / Quitter{RESET}")
    separateur()
    valides = [str(i) for i in range(len(options) + 1)]
    while True:
        choix = input(f"  {BOLD}Votre choix{RESET} : ").strip()
        if choix in valides:
            return choix
        erreur("Choix invalide.")


def afficher_client(c: dict, compact: bool = False):
    if compact:
        print(f"  {BOLD}{c.get('prenom','')} {c.get('nom','')}{RESET}"
              f"  {GREY}│{RESET}  {c.get('email','')}  "
              f"  {GREY}│{RESET}  {c.get('telephone','')}")
    else:
        separateur()
        print(f"  {BOLD}Nom      :{RESET} {c.get('prenom','')} {c.get('nom','')}")
        print(f"  {BOLD}Email    :{RESET} {c.get('email','')}")
        print(f"  {BOLD}Tél.     :{RESET} {c.get('telephone','')}")
        adr = c.get("adresse", {})
        print(f"  {BOLD}Adresse  :{RESET} {adr.get('rue','')} — "
              f"{adr.get('codePostal','')} {adr.get('ville','')}")
        print(f"  {BOLD}ID       :{RESET} {GREY}{c['_id']}{RESET}")
        separateur()


def afficher_compte(cpt: dict, client: dict = None, compact: bool = False):
    if compact:
        print(f"  {BOLD}{cpt.get('numero','')}{RESET}"
              f"  {GREY}│{RESET}  {cpt.get('type',''):8}"
              f"  {GREY}│{RESET}  {BOLD}{cpt.get('solde', 0):>10.2f} €{RESET}"
              + (f"  {GREY}│ {client.get('prenom','')} {client.get('nom','')}{RESET}"
                 if client else ""))
    else:
        separateur()
        print(f"  {BOLD}Numéro   :{RESET} {cpt.get('numero','')}")
        print(f"  {BOLD}Type     :{RESET} {cpt.get('type','')}")
        print(f"  {BOLD}Solde    :{RESET} {BOLD}{GREEN}{cpt.get('solde', 0):.2f} €{RESET}")
        print(f"  {BOLD}Devise   :{RESET} {cpt.get('devise','EUR')}")
        if client:
            print(f"  {BOLD}Client   :{RESET} {client.get('prenom','')} {client.get('nom','')}")
        nb_ops = len(cpt.get("operations", []))
        print(f"  {BOLD}Opérations:{RESET} {nb_ops}")
        print(f"  {BOLD}ID       :{RESET} {GREY}{cpt['_id']}{RESET}")
        separateur()


def afficher_operation(op: dict):
    TYPE_COLOR = {"depot": GREEN, "retrait": RED, "virement": YELLOW}
    TYPE_LABEL = {"depot": "Dépôt    ", "retrait": "Retrait  ", "virement": "Virement "}
    couleur = TYPE_COLOR.get(op["type"], WHITE)
    label   = TYPE_LABEL.get(op["type"], op["type"])
    date    = op["date"].strftime("%d/%m/%Y %H:%M") if op.get("date") else "—"
    montant = f"{op.get('montant', 0):.2f} €"
    ligne   = (f"  {couleur}{label}{RESET}"
               f"  {GREY}{date}{RESET}"
               f"  {BOLD}{montant:>12}{RESET}")
    if op["type"] == "virement" and op.get("motif"):
        ligne += f"  {GREY}({op['motif']}){RESET}"
    print(ligne)
