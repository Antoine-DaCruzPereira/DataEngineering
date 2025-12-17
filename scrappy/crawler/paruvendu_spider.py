import scrapy
import re

class ParuVenduSpider(scrapy.Spider):
    name = "paruvendu"
    PAGE_MAX = 5
    start_urls = ['https://www.paruvendu.fr/auto-moto/listefo/default/default?p=1']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': False,
        # C'EST ICI QUE ÇA SE JOUE :
        # On dit au spider d'aller chercher la classe MongoPipeline dans le fichier pipelines.py
        'ITEM_PIPELINES': {
            'pipelines.MongoPipeline': 300,
        }
    }

    def parse(self, response):
        annonces = response.css('div.blocAnnonce')
        self.logger.info(f"--- PAGE SCANNÉE : {len(annonces)} annonces trouvées ---")

        for annonce in annonces:
            # On envoie les données BRUTES au pipeline
            yield {
                'titre': annonce.css('h3::text').get(default='').strip(),
                'prix_brut': annonce.xpath('.//div[contains(text(), "€")]/text()').get(default=''),
                'infos_brutes': " ".join(annonce.css('div[class*="text-"] ::text').getall()),
                'lien': response.urljoin(annonce.css('a::attr(href)').get())
            }

        # Pagination
        page_match = re.search(r'p=(\d+)', response.url)
        current_page = int(page_match.group(1)) if page_match else 1
        next_page = current_page + 1
        
        if next_page <= self.PAGE_MAX:
            next_url = f'https://www.paruvendu.fr/auto-moto/listefo/default/default?p={next_page}'
            yield scrapy.Request(next_url, callback=self.parse)