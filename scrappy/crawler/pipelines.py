import pymongo
import re
from scrapy.exceptions import DropItem

class MongoPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["auto_data"]
        self.collection = self.db["paruvendu"]

        self.BRAND_MAPPING = {
            "Ds": "Citroën", "DS": "Citroën", "Vw": "Volkswagen", "Land Rover": "Land Rover"
        }

        self.EXCLUDED_KEYWORDS = [
            "TRACTEUR", "CAMION", "REMORQUE", "CARAVANE", "MOTO", "SCOOTER", "QUAD", "BUGGY", "VAN",
            "JANTE", "PNEU", "ROUE", "CASQUE", "CHAINE", "CHAUSSETTE", "PIECE", "MOTEUR", 
            "BOITE DE VITESSE", "PORTE", "CAPOT", "PARE-CHOC", "SIÈGE", "VOLANT", "BATTERIE",
            "VITICOLE", "AGRICOLE", "MATERIEL", "LOCATION", "RECHERCHE", "ACHAT", "LOUE", "SERVICE","CHARIOT"
        ]

    def process_item(self, item, spider):
        raw_text = item.get('infos_brutes', '')
        titre = item.get('titre', '')
        lien = item.get('lien', '')
        

        titre_upper = titre.upper()
        for keyword in self.EXCLUDED_KEYWORDS:
            if keyword in titre_upper:
                raise DropItem(f"❌ Ignoré : {titre}")

        annee = None
        annee_match = re.search(r'(199\d|20[0-3]\d)', raw_text)
        if annee_match:
            annee = int(annee_match.group(1))

  
        km = None
        km_match = re.search(r'(?:^|[\D])(\d{1,3}(?:\s?\d{3})?)\s*km', raw_text, re.IGNORECASE)
        
        if km_match:
            clean_km = km_match.group(1).replace(' ', '')
            if clean_km.isdigit():
                km = int(clean_km)

        marque = "Inconnue"
        url_match = re.search(r'voiture-occasion/([^/]+)/', lien)
        if url_match:
            marque_brute = url_match.group(1).replace('-', ' ').capitalize()
        else:
            marque_brute = titre.split(' ')[0].strip().capitalize() if titre else "Inconnue"
        marque = self.BRAND_MAPPING.get(marque_brute, marque_brute)
        boite = "Manuelle"
        if "auto" in raw_text.lower() or "bva" in raw_text.lower(): boite = "Automatique"
            
        energie = "Autre"
        text_low = raw_text.lower()
        if "diesel" in text_low: energie = "Diesel"
        elif "essence" in text_low: energie = "Essence"
        elif "hybrid" in text_low: energie = "Hybride"
        elif "electrique" in text_low or "électrique" in text_low: energie = "Electrique"

        prix_clean = "".join(re.findall(r'\d+', item.get('prix_brut', '')))
        document = {
            'titre': titre,
            'marque': marque,
            'prix': int(prix_clean) if prix_clean else 0,
            'caracteristiques': {
                'annee': annee,
                'kilometrage': km,
                'boite': boite,
                'energie': energie
            },
            'lien': lien
        }
        
        self.collection.update_one({'lien': lien}, {'$set': document}, upsert=True)
        return item

    def close_spider(self, spider):
        self.client.close()