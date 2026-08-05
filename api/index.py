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
        # User-Agents modernos y consistentes
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
        ]

        scraper = cloudscraper.create_scraper(
            delay=10,
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        resultados = {}
        
        for metal in materiales:
            # Pausa aleatoria más larga (entre 5 y 20 segundos) para simular navegación humana
            tiempo_espera = random.uniform(5.0, 20.0)
            time.sleep(tiempo_espera)
            
            ua_actual = random.choice(user_agents)
            
            # Headers mejorados para imitar un navegador real completo
            headers = {
                'User-Agent': ua_actual,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-User': '?1',
                'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"'
            }

            try:
                res = scraper.get(metal["url"], headers=headers, timeout=20)
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
