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
        
        # LISTE NOIRE (Pour virer les jantes et chaussettes)
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
        
        # --- 1. FILTRE ANTI-POUBELLE ---
        titre_upper = titre.upper()
        for keyword in self.EXCLUDED_KEYWORDS:
            if keyword in titre_upper:
                raise DropItem(f"❌ Ignoré : {titre}")

        # --- 2. ANNÉE ---
        annee = None
        annee_match = re.search(r'(199\d|20[0-3]\d)', raw_text)
        if annee_match:
            annee = int(annee_match.group(1))

        # --- 3. KILOMÉTRAGE (CORRECTION ICI) ---
        km = None
        # Explication du Regex magique :
        # (?:^|[\D]) -> Doit commencer soit au début, soit après un caractère qui N'EST PAS un chiffre (l'espace).
        # (\d{1,3}(?:\s?\d{3})?) -> Capture 1 à 3 chiffres, suivis optionnellement d'un espace et 3 chiffres.
        # Cela force un maximum de 6 chiffres (999 999 km), donc impossible de coller l'année !
        km_match = re.search(r'(?:^|[\D])(\d{1,3}(?:\s?\d{3})?)\s*km', raw_text, re.IGNORECASE)
        
        if km_match:
            clean_km = km_match.group(1).replace(' ', '')
            if clean_km.isdigit():
                km = int(clean_km)

        # --- 4. MARQUE ---
        marque = "Inconnue"
        url_match = re.search(r'voiture-occasion/([^/]+)/', lien)
        if url_match:
            marque_brute = url_match.group(1).replace('-', ' ').capitalize()
        else:
            marque_brute = titre.split(' ')[0].strip().capitalize() if titre else "Inconnue"
        marque = self.BRAND_MAPPING.get(marque_brute, marque_brute)

        # --- 5. ENERGIE & BOITE ---
        boite = "Manuelle"
        if "auto" in raw_text.lower() or "bva" in raw_text.lower(): boite = "Automatique"
            
        energie = "Autre"
        text_low = raw_text.lower()
        if "diesel" in text_low: energie = "Diesel"
        elif "essence" in text_low: energie = "Essence"
        elif "hybrid" in text_low: energie = "Hybride"
        elif "electrique" in text_low or "électrique" in text_low: energie = "Electrique"

        prix_clean = "".join(re.findall(r'\d+', item.get('prix_brut', '')))
        
        # --- 6. SAUVEGARDE ---
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