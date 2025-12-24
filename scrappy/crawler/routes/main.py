from flask import Blueprint, render_template, request, url_for
from database import get_collection 
from bson.objectid import ObjectId
import math

bp = Blueprint('main', __name__)

@bp.route('/')
def afficher_annonces():
    try:
        collection = get_collection() 

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
        voitures = list(collection.find(query).sort("prix", 1).skip(skip_count).limit(per_page))
        
        total_results = collection.count_documents(query)
        total_pages = math.ceil(total_results / per_page)
        
        return render_template('index.html', voitures=voitures, total=total_results, page=page, total_pages=total_pages)

    except Exception as e:
        return f"Erreur : {e}"
    
@bp.route('/voiture/<voiture_id>')
def details_voiture(voiture_id):
        try:
            collection = get_collection()
        
        # 1. On cherche LA voiture précise par son ID
            voiture = collection.find_one({"_id": ObjectId(voiture_id)})
        
            if not voiture:
                return "Voiture introuvable", 404

        # 2. SUGGESTIONS : On cherche des voitures similaires
        # (Même marque, prix +/- 20%, et pas la voiture elle-même)
            prix = voiture.get('prix', 0)
            suggestions = list(collection.find({
                "marque": voiture['marque'],
                "prix": {"$gte": prix * 0.8, "$lte": prix * 1.2},
                "_id": {"$ne": ObjectId(voiture_id)} # On exclut la voiture actuelle
            }).limit(3))

            return render_template('detail.html', v=voiture, suggestions=suggestions)

        except Exception as e:
            return f"Erreur : {e}"