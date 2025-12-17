import pymongo
import re

class MongoPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["auto_data"]
        self.collection = self.db["paruvendu"]

        # Mapping pour corriger les marques bizarres si besoin
        self.BRAND_MAPPING = {
            "Ds": "Citroën",
            "Vw": "Volkswagen"
        }

    def process_item(self, item, spider):
        raw_text = item.get('infos_brutes', '')
        titre = item.get('titre', '')
        lien = item.get('lien', '')
        
        # --- 1. MARQUE ---
        marque = "Inconnue"
        
        url_match = re.search(r'voiture-occasion/([^/]+)/', lien)
        
        if url_match:
            # On trouve la marque dans l'URL (ex: "land-rover", "peugeot")
            marque_brute = url_match.group(1).replace('-', ' ').capitalize()
        else:
            # Si l'URL est bizarre, on revient à l'ancienne méthode (premier mot du titre)
            marque_brute = titre.split(' ')[0].strip().capitalize() if titre else "Inconnue"

        # On applique le mapping final (ex: si l'URL dit "Ds", on met "Citroën")
        marque = self.BRAND_MAPPING.get(marque_brute, marque_brute)

        # --- 2. KILOMÉTRAGE ---
        km = None
        km_match = re.search(r'(\d{1,3}(?:[\s]\d{3})*)\s*km', raw_text, re.IGNORECASE)
        if km_match:
            clean_km = km_match.group(1).replace(' ', '')
            if clean_km.isdigit():
                km = int(clean_km)

        # --- 3. ANNÉE ---
        annee = None
        annee_match = re.search(r'(199\d|20[0-2]\d)', raw_text)
        if annee_match:
            annee = int(annee_match.group(1))
            if km and abs(km - annee) < 100:
                annee = None

        # --- 4. CARACTÉRISTIQUES ---
        boite = "Manuelle"
        if "auto" in raw_text.lower() or "bva" in raw_text.lower():
            boite = "Automatique"
            
        energie = "Autre"
        text_low = raw_text.lower()
        if "diesel" in text_low: energie = "Diesel"
        elif "essence" in text_low: energie = "Essence"
        elif "hybrid" in text_low: energie = "Hybride"
        elif "electrique" in text_low or "électrique" in text_low: energie = "Electrique"

        prix_clean = "".join(re.findall(r'\d+', item.get('prix_brut', '')))
        
        # --- 5. SAUVEGARDE ---
        document = {
            'titre': titre,
            'marque': marque, # Maintenant ce sera "Peugeot" même si le titre est "208"
            'prix': int(prix_clean) if prix_clean else 0,
            'caracteristiques': {
                'annee': annee,
                'kilometrage': km,
                'boite': boite,
                'energie': energie
            },
            'lien': lien
        }
        
        self.collection.update_one(
            {'lien': lien}, {'$set': document}, upsert=True
        )
        
        print(f"✅ {marque} | {titre[:15]}... | {km} km")
        return item

    def close_spider(self, spider):
        self.client.close()