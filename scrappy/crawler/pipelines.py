import pymongo
import re

class MongoPipeline:
    def __init__(self):
        # CONNEXION DOCKER : On utilise le nom du service "mongo"
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["auto_data"]
        self.collection = self.db["paruvendu"]

    def process_item(self, item, spider):
        # --- 1. Nettoyage des données ---
        raw_text = item.get('infos_brutes', '')
        titre = item.get('titre', '')
        lien = item.get('lien', '')
        
        # Extraction Prix (on garde que les chiffres)
        prix_clean = "".join(re.findall(r'\d+', item.get('prix_brut', '')))
        
        # Extraction Kilométrage
        km_match = re.search(r'(\d[\d\s]*)\s*km', raw_text, re.IGNORECASE)
        km = int(km_match.group(1).replace(' ', '')) if km_match else None
        
        # Extraction Année
        annee_match = re.search(r'(19|20)\d{2}', raw_text)
        annee = int(annee_match.group(0)) if annee_match else None
        
        # Classification Boite
        boite = "Manuelle"
        if "auto" in raw_text.lower() or "bva" in raw_text.lower():
            boite = "Automatique"
            
        # Classification Énergie
        energie = "Autre"
        text_low = raw_text.lower()
        if "diesel" in text_low: energie = "Diesel"
        elif "essence" in text_low: energie = "Essence"
        elif "hybrid" in text_low: energie = "Hybride"
        elif "electrique" in text_low: energie = "Electrique"

        # --- 2. Création de l'objet final ---
        document = {
            'titre': titre,
            'prix': int(prix_clean) if prix_clean else 0,
            'caracteristiques': {
                'annee': annee,
                'kilometrage': km,
                'boite': boite,
                'energie': energie
            },
            'lien': lien
        }
        
        # --- 3. Envoi vers MongoDB (Upsert) ---
        self.collection.update_one(
            {'lien': lien},
            {'$set': document},
            upsert=True
        )
        
        print(f"✅ Sauvegardé : {titre[:30]}... ({annee})")
        return item

    def close_spider(self, spider):
        self.client.close()