# Documentation du Crawler ParuVendu

Ce projet consiste à recupérer des données sur un site  en utilisant **Scrapy**. On procède donc à une récuperation automatique des annonces automobiles sur le site ParuVendu, de nettoyer les données, et de les stocker dans une base de données **MongoDB** et ensuite de les afficher en utilisant **Streamlit**.

##  Structure des fichiers de Scraping

Voici le rôle détaillé de chaque fichier présent dans le dossier `scrappy/crawler/`.

### 1. `paruvendu_spider.py`
C'est le cœur du projet. Ce script est responsable de la navigation sur le site web.

* **Rôle :** Il envoie les requêtes HTTP au site ParuVendu. Il récupère le HTML brut (Titre, Prix, Description, Lien).
* **Pagination :** Il détecte automatiquement le lien "Page suivante" pour parcourir toutes les pages de résultats.
* **Configuration :** Il définit le `USER_AGENT` pour imiter un navigateur et éviter d'être bloqué.

### 2. `pipelines.py` 
C'est ici que la donnée brute est transformée en donnée propre et exploitable. Une fois que le spider a trouvé une annonce, il l'envoie ici.

* **Filtrage :** Il rejette les annonces indésirables grâce à une liste (`EXCLUDED_KEYWORDS`) : tracteurs, jantes, pneus, locations, etc.

* **Extraction Intelligente :**
    * **Rôle :** Il utilise regex pour determiner les informations suivantes :
        * **Année** 
        * **Kilométrage :** (Nettoie et convertit le kilométrage en nombre entier.)
        * **Prix** 
* **Normalisation :** Donne et index les marques (ex: "Vw" devient "Volkswagen") et détecte le type de boîte de vitesse et l'énergie.
* **Stockage :** Se connecte à **MongoDB** et sauvegarde l'annonce.

### 3. `database.py`
Ce fichier sert de point central pour la configuration de la base de données.

### 4. `docker-compose.yml`
Ce fichier permet de lancer tout l'environnement en une seule commande.

* **Rôle :** Il crée et gère deux codes ci-dessus qui fonctionnent ensemble :
    1.  **MongoDB :** La base de données qui tourne dans un conteneur .
    2.  **Crawler :** Le code Python qui s'exécute.

Il relie les deux  pour qu'ils puissent communiquer.


## Comment lancer le projet

1.  Assurez-vous d'avoir **Docker** installé.
2.  Placez-vous dans le dossier racine du projet.
3.  Lancez la commande :

```bash
docker-compose up --build
```

Lien du site : http://127.0.0.1:8501/

