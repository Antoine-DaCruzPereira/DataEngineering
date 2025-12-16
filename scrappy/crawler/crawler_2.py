import scrapy
from scrapy.selector import Selector

class ViaAutoPaginationSpider(scrapy.Spider):
    name = 'viaauto_pagination'
    # URL de base sans paramètres
    start_urls = ['https://viaautomobile.com/voiture-occasion']

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True, 
            'args': ['--disable-blink-features=AutomationControlled']
        },
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 3, # Délai un peu plus long pour éviter le ban sur plusieurs pages
    }

    def start_requests(self):
        # On initialise le compteur de page à 1
        yield scrapy.Request(
            self.start_urls[0],
            meta={
                'playwright': True, 
                'playwright_include_page': True,
                'page_number': 1
            }
        )

    async def parse(self, response):
        page = response.meta['playwright_page']
        current_page = response.meta.get('page_number', 1)
        
        try:
            print(f"--- Traitement de la page {current_page} ---")

            # 1. Gestion cookies (seulement sur la page 1 pour gagner du temps)
            if current_page == 1:
                try:
                    await page.wait_for_selector('button:has-text("Accepter")', timeout=3000)
                    await page.click('button:has-text("Accepter")')
                except:
                    pass

            # Scroll pour charger les images
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

            content = await page.content()
            sel = Selector(text=content)

            # 2. Extraction des données (Code validé)
            vehicles = sel.css('div.item.border')
            print(f"✅ {len(vehicles)} véhicules trouvés sur la page {current_page}.")

            for car in vehicles:
                # Titre
                t1 = car.css('p[class*="h5"]::text').get()
                t2 = car.css('p[class*="mb-3"]::text').get()
                titre = f"{t1 or ''} {t2 or ''}".strip()

                # Prix (XPath chercheur d'or)
                prix = car.xpath('.//*[contains(text(), "€")]/text()').get()
                prix = prix.strip() if prix else "N/C"

                # Détails (Scan de la liste)
                details_raw = car.xpath('.//ul[contains(@class, "list-inline")]//text()').getall()
                details = " | ".join([d.strip() for d in details_raw if d.strip() and len(d.strip()) > 1])

                yield {
                    'titre': titre,
                    'prix': prix,
                    'details': details,
                    'lien': response.urljoin(car.css('a::attr(href)').get())
                }

            # 3. GESTION DE LA PAGINATION (Max 10 pages)
            if current_page < 10:
                next_page_num = current_page + 1
                
                # Méthode : Construction d'URL (Plus rapide et fiable que de chercher le bouton "Suivant")
                # L'URL standard est souvent : https://viaautomobile.com/voiture-occasion?page=2
                next_url = f"https://viaautomobile.com/voiture-occasion?page={next_page_num}"
                
                print(f"➡️ Passage à la page suivante : {next_url}")
                
                yield scrapy.Request(
                    url=next_url,
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                        'page_number': next_page_num
                    }
                )
            else:
                print("🛑 Limite de 10 pages atteinte.")

        except Exception as e:
            self.logger.error(f"Erreur sur la page {current_page} : {e}")
        finally:
            # On ferme la page pour libérer la mémoire à chaque itération
            await page.close()