from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time

# Cache global para no saturar y evitar bloqueos
cache_lme = {
    "datos": {},
    "timestamp": 0
}

class handler(BaseHTTPRequestHandler):

    def intentar_scrape(self, materiales):
        # Lista de configuraciones para rotar identidad
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]

        scraper = cloudscraper.create_scraper(
            delay=10,
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        resultados = {}
        
        for metal in materiales:
            # Delay entre peticiones para que parezca humano
            time.sleep(random.uniform(2.0, 3.0))
            
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9',
                'Referer': 'https://www.google.com/',
                'Sec-Fetch-Mode': 'navigate'
            }

            try:
                res = scraper.get(metal["url"], headers=headers, timeout=15)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    elemento = soup.find('span', class_='hero-metal-data__number')
                    resultados[metal["id"]] = elemento.text.strip() if elemento else "No encontrado"
                else:
                    resultados[metal["id"]] = f"Error {res.status_code}"
            except Exception as e:
                resultados[metal["id"]] = f"Error: {str(e)}"
        
        return resultados

    def do_GET(self):
        global cache_lme
        
        materiales_config = [
            {"id": "niquel", "url": "https://www.lme.com/metals/non-ferrous/lme-nickel#Summary"},
            {"id": "aluminio", "url": "https://www.lme.com/metals/non-ferrous/lme-aluminium#Overview"},
            {"id": "estano", "url": "https://www.lme.com/metals/non-ferrous/lme-tin#Summary"}
        ]
        
        ahora = time.time()
        TIEMPO_CACHE = 1800  # 30 minutos
        
        # Lógica de Cache
        if cache_lme["datos"] and (ahora - cache_lme["timestamp"] < TIEMPO_CACHE):
            final_data = cache_lme["datos"]
            fuente = "cache"
        else:
            final_data = self.intentar_scrape(materiales_config)
            cache_lme["datos"] = final_data
            cache_lme["timestamp"] = ahora
            fuente = "real-time"

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        res_json = {
            "lme_data": final_data,
            "status": "online",
            "fuente": fuente,
            "timestamp": int(ahora)
        }
        
        self.wfile.write(json.dumps(res_json).encode('utf-8'))