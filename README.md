## Application Console TP BANQUE MongoDB

### Description
Cette application est une application console développée en Python utilisant MongoDB comme base de données. Elle permet de gérer des clients et leurs comptes bancaires et d'effectuer les principales opérations bancaires via une interface en ligne de commande.
### Fonctionnalités
**1. Gestion des clients** 

• Créer un client  
• Rechercher un client  
• Modifier un client  
• Supprimer un client  
• Lister les clients 

**2. Gestion des comptes** 

• Créer un compte  
• Consulter un compte  
• Modifier un compte  
• Supprimer un compte  
• Lister les comptes  

**3. Gestion des opérations** 

• Effectuer un dépôt  
• Effectuer un retrait  
• Effectuer un virement  
• Consulter l'historique des opérations 

### Technologies utilisées

- Python 3
- MongoDB
- PyMongo

### Prérequis
Avant d'exécuter l'application, assurez-vous d'avoir installé :

- Python 3.x
- MongoDB
- Le package Python PyMongo

**Installation de PyMongo :**

"Pip install pymongo"

### Installation
**1. Cloner le dépôt :**

Git clone <https://github.com/Jeandioubate/MongoDB_TP.git>

**2. Accéder au dossier du projet :**

cd Documents\Exo NoSQL_MongoDB\MongoTp\

**3. Démarrer MongoDB**

**4. Lancer l'application :**

python -m MongoTp.main.py

Au lancement, l'application propose de charger le jeu de données de démo (TROIS clients, QUATRE comptes, NEUF opérations). Ensuite le menu principal s'ouvre :

1. Gestion des clients → créer / rechercher / modifier / supprimer / lister
2. Gestion des comptes → créer / consulter / modifier / supprimer / lister
3. Gestion des opérations → dépôt / retrait / virement / historique filtrable

### Architecture du projet

MongoTP/

    config.py                  ← URI MongoDB
    db.py                      ← Singleton de connexion
    seed.py                    ← Jeu de données initial
    main.py                    ← Point d'entrée + menu principal
    models/
        client.py              ← Construction des documents Client
        compte.py              ← Construction des documents Compte + Opérations
    services/
        client_service.py      ← CRUD clients
        compte_service.py      ← CRUD comptes + opérations
    ui/
        utils.py               ← Affichage console coloré
        menu_clients.py        ← Menu gestion clients
        menu_comptes.py        ← Menu gestion comptes & opérations

Règles métier implémentées

- Retrait et virement refusés si solde insuffisant
- Suppression d'un client bloquée s'il possède encore des comptes
- Suppression d'un compte bloquée si le solde n'est pas à 0 €
- Email unique par client (index MongoDB unique)
- Numéro de compte unique (index MongoDB unique)
- Le virement met à jour atomiquement les deux comptes (source et destinataire)