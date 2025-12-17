import scrapy
import re

class ParuVenduMultiPageSpider(scrapy.Spider):
    name = "paruvendu_multi"
    
    # Configuration
    PAGE_MAX = 20
    # Point de départ (page 1)
    start_urls = ['https://www.paruvendu.fr/auto-moto/listefo/default/default?p=1']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2, # Pause de 2s entre chaque page pour ne pas être banni
        'COOKIES_ENABLED': False,
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def parse(self, response):
        # 1. Extraction des données
        annonces = response.css('div.blocAnnonce')
        
        # On récupère le numéro de page
        page_actuelle = re.search(r'p=(\d+)', response.url)
        num_page = page_actuelle.group(1) if page_actuelle else "1"
        
        self.logger.info(f" Scraping de la PAGE {num_page} - {len(annonces)} annonces trouvées")

        for annonce in annonces:
            titre = annonce.css('h3::text').get(default='').strip()
            
            # Nettoyage 
            prix_brut = annonce.xpath('.//div[contains(text(), "€")]/text()').get(default='')
            prix_propre = "".join(re.findall(r'\d+', prix_brut))

            infos_brutes = annonce.css('div *::text').getall()
            infos_propres = []
            for item in infos_brutes:
                text = item.strip()
                if text and "{" not in text and len(text) < 50:
                    if text not in ["Annonce à la une", "Particulier", "Voir l'annonce", "Crédit", "Garantie"]:
                        infos_propres.append(text)
            
            description_finale = " - ".join(infos_propres)

            yield {
                'page': int(num_page), # Utile pour vérifier que la pagination marche
                'titre': titre,
                'prix': int(prix_propre) if prix_propre else None,
                'details': description_finale,
                'vendeur': 'Pro' if annonce.css('.logo-pro') else 'Particulier',
                'lien': response.urljoin(annonce.css('a::attr(href)').get())
            }

        # 2. GESTION DE LA PAGINATION AUTOMATIQUE
    
        current_p = int(num_page)
        next_p = current_p + 1
        
        if next_p <= self.PAGE_MAX:
            next_url = f'https://www.paruvendu.fr/auto-moto/listefo/default/default?p={next_p}'
            
            self.logger.info(f" Passage à la page suivante : {next_url}")
            yield scrapy.Request(next_url, callback=self.parse)