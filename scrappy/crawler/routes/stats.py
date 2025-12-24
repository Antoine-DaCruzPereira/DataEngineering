from flask import Blueprint, render_template
from database import get_collection

bp = Blueprint('stats', __name__)

@bp.route('/statistiques')
def afficher_statistiques():
    try:
        collection = get_collection()
        
        # Pipeline d'agrégation (Code inchangé)
        pipeline = [
            {"$match": {"prix": {"$gt": 0}, "marque": {"$ne": "Inconnue"}}},
            {"$group": {
                "_id": "$marque",
                "count": {"$sum": 1},
                "avgPrice": {"$avg": "$prix"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 15}
        ]
        stats_data = list(collection.aggregate(pipeline))
        
        labels_marques = [item["_id"] for item in stats_data]
        data_counts = [item["count"] for item in stats_data]
        data_prices = [int(item["avgPrice"]) for item in stats_data]

        return render_template('stats.html', labels_marques=labels_marques, data_counts=data_counts, data_prices=data_prices)

    except Exception as e:
        return f"Erreur Stats : {e}"