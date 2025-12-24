import pymongo

# Configuration centralisée
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "auto_data"
COLLECTION_NAME = "paruvendu"

def get_collection():
    """Fonction  pour récupérer la collection/Database"""
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]