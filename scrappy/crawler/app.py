from flask import Flask, render_template, request, url_for
import pymongo
import math
import json

app = Flask(__name__)

# Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "auto_data"
COLLECTION_NAME = "paruvendu"

@app.route('/')
def afficher_annonces():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        page = request.args.get('page', 1, type=int)
        per_page = 20
        marque_filter = request.args.get('marque')
        prix_max = request.args.get('prix_max')
        km_max = request.args.get('km_max')
        annee_min = request.args.get('annee_min')
        query = {"prix": {"$gt": 0}}

        if marque_filter:
            query["marque"] = {"$regex": marque_filter, "$options": "i"}
        if prix_max and prix_max.isdigit():
            query["prix"] = {"$gt": 0, "$lte": int(prix_max)}
        if km_max and km_max.isdigit():
            query["caracteristiques.kilometrage"] = {"$lte": int(km_max)}
        if annee_min and annee_min.isdigit():
            query["caracteristiques.annee"] = {"$gte": int(annee_min)}
        skip_count = (page - 1) * per_page
        voitures = list(collection.find(query)
                        .sort("prix", 1)
                        .skip(skip_count)
                        .limit(per_page))
        total_results = collection.count_documents(query)
        total_pages = math.ceil(total_results / per_page)

        client.close()
        
        return render_template(
            'index.html', 
            voitures=voitures, 
            total=total_results, 
            page=page, 
            total_pages=total_pages
        )

    except Exception as e:
        return f"Erreur : {e}"



@app.route('/statistiques')
def afficher_statistiques():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        pipeline = [
            {"$match": {"prix": {"$gt": 0}, "marque": {"$ne": "Inconnue"}}},
            
            {"$group": {
                "_id": "$marque",             
                "count": {"$sum": 1},         
                "avgPrice": {"$avg": "$prix"},
                "avgKm": {"$avg": "$caracteristiques.kilometrage"} 
            }},
        
            {"$sort": {"count": -1}},
            
            {"$limit": 20}
        ]
        stats_data = list(collection.aggregate(pipeline))
        labels_marques = [item["_id"] for item in stats_data]
        data_counts = [item["count"] for item in stats_data]
        data_prices = [int(item["avgPrice"]) for item in stats_data]

        client.close()
        return render_template(
            'stats.html', 
            labels_marques=labels_marques,
            data_counts=data_counts,
            data_prices=data_prices
        )

    except Exception as e:
        return f"Erreur lors du calcul des statistiques : {e}"
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)