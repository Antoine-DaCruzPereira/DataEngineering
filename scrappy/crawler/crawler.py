import scrapy
from scrapy.selector import Selector

class ViaAutoFinalV2Spider(scrapy.Spider):
    name = 'viaauto_final_v2'
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
        'DOWNLOAD_DELAY': 2,
    }

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls[0],
            meta={'playwright': True, 'playwright_include_page': True}
        )

    async def parse(self, response):
        page = response.meta['playwright_page']
        
        try:
            # Gestion cookies et chargement
            try:
                await page.wait_for_selector('button:has-text("Accepter")', timeout=3000)
                await page.click('button:has-text("Accepter")')
            except:
                pass

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

            content = await page.content()
            sel = Selector(text=content)

            # On utilise le sélecteur qui a marché : div.item.border
            vehicles = sel.css('div.item.border')
            
            print(f"✅ {len(vehicles)} véhicules trouvés.")

            for car in vehicles:
                # 1. TITRE (Méthode CSS validée)
                t1 = car.css('p[class*="h5"]::text').get()
                t2 = car.css('p[class*="mb-3"]::text').get()
                titre = f"{t1 or ''} {t2 or ''}".strip()

                # 2. PRIX (Méthode XPath "Chercheur d'Or")
                # On cherche n'importe quel texte contenant "€" dans la carte
                # C'est beaucoup plus fiable que de deviner la classe "badge"
                prix = car.xpath('.//*[contains(text(), "€")]/text()').get()
                if prix:
                    prix = prix.strip()
                else:
                    prix = "N/C"

                # 3. DETAILS (Méthode XPath "Scanner")
                # On cherche la liste (ul) qui contient "list-inline" et on prend TOUT le texte dedans
                # Cela évite les problèmes si le texte est dans un <li> ou un <span> ou un <div>
                details_raw = car.xpath('.//ul[contains(@class, "list-inline")]//text()').getall()
                
                # Nettoyage : on enlève les vides et on recolle avec " | "
                details = " | ".join([d.strip() for d in details_raw if d.strip() and len(d.strip()) > 1])

                yield {
                    'titre': titre,
                    'prix': prix,
                    'details': details,
                    'lien': response.urljoin(car.css('a::attr(href)').get())
                }

        except Exception as e:
            self.logger.error(f"Erreur : {e}")
        finally:
            await page.close()