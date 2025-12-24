from flask import Blueprint, request, Response
from database import get_collection
import csv
import io

bp = Blueprint('export', __name__)

@bp.route('/export-csv')
def exporter_csv():
    try:
        collection = get_collection()
        
        # Copie ici la logique des filtres (query) comme dans main.py
        # Pour faire simple je mets la query de base, mais tu peux copier tout le bloc if/else
        query = {"prix": {"$gt": 0}} 
        
        voitures = list(collection.find(query).sort("prix", 1))

        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['Marque', 'Titre', 'Prix', 'Année', 'Km', 'Lien'])

        for v in voitures:
            writer.writerow([
                v.get('marque', 'Inconnue'),
                v.get('titre', ''),
                v.get('prix', 0),
                v['caracteristiques'].get('annee', ''),
                v['caracteristiques'].get('kilometrage', ''),
                v.get('lien', '')
            ])

        output.seek(0)
        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=export_voitures.csv"})

    except Exception as e:
        return f"Erreur Export : {e}"