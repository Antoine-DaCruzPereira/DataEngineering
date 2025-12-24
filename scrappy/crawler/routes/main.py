from flask import Blueprint, render_template, request, url_for
from database import get_collection 
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