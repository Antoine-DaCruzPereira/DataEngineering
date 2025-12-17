import pymongo
import pandas as pd # Si tu as pandas, sinon juste print

# Connexion (Depuis le Mac -> Localhost)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["auto_data"]
collection = db["paruvendu"]

# 1. Compter les documents
total = collection.count_documents({})
print(f"📊 Il y a {total} voitures en base.")

# 2. Lire les 5 voitures les plus chères
# (Tri décroissant sur le prix : -1)
cursor = collection.find().sort("prix", -1).limit(5)

print("\n🏆 Top 5 des voitures les plus chères :")
for voiture in cursor:
    print(f"- {voiture['titre']} : {voiture['prix']} € ({voiture['caracteristiques']['annee']})")

# 3. Exemple de requête précise (Data Engineering)
query = {
    "caracteristiques.boite": "Automatique",
    "prix": {"$lt": 20000} # Moins de 20 000€
}
nb_auto_pas_cher = collection.count_documents(query)
print(f"\n🚗 Il y a {nb_auto_pas_cher} voitures automatiques à moins de 20k€.")