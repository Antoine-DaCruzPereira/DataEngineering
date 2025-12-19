import scrapy
import re

class ParuVenduSpider(scrapy.Spider):
    name = "paruvendu"
    PAGE_MAX = 25
    start_urls = ['https://www.paruvendu.fr/auto-moto/listefo/default/default?p=1']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': False,
        'ITEM_PIPELINES': {
            'pipelines.MongoPipeline': 300,
        }
    }

    def parse(self, response):
        annonces = response.css('div.blocAnnonce')
        self.logger.info(f"--- PAGE SCANNÉE : {len(annonces)} annonces trouvées ---")

        for annonce in annonces:
            titre = annonce.css('h3::text').get(default='').strip()
            prix_brut = annonce.xpath('.//div[contains(text(), "€")]/text()').get(default='')
            text_elements = annonce.css('*::text').getall()
            infos_brutes = " ".join([t.strip() for t in text_elements if t.strip()])
            
            lien = response.urljoin(annonce.css('a::attr(href)').get())

            yield {
                'titre': titre,
                'prix_brut': prix_brut,
                'infos_brutes': infos_brutes,
                'lien': lien
            }

        # Pagination
        page_match = re.search(r'p=(\d+)', response.url)
        current_page = int(page_match.group(1)) if page_match else 1
        next_page = current_page + 1
        
        if next_page <= self.PAGE_MAX:
            next_url = f'https://www.paruvendu.fr/auto-moto/listefo/default/default?p={next_page}'
            yield scrapy.Request(next_url, callback=self.parse)