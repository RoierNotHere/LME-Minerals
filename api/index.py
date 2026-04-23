from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time

# Cache para no quemar la IP
cache_metal = {
    "precio": None,
    "timestamp": 0
}

class handler(BaseHTTPRequestHandler):

    def intentar_scrape(self, url):
        # Lista de configuraciones de navegador para rotar
        configs = [
            {'browser': 'chrome', 'platform': 'windows', 'desktop': True},
            {'browser': 'firefox', 'platform': 'windows', 'desktop': True},
            {'browser': 'chrome', 'platform': 'darwin', 'desktop': True}
        ]
        
        # Headers variados: algunos sitios bloquean si ven siempre el mismo
        headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Referer': 'https://www.google.com/'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Fetch-Mode': 'navigate'
            },
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'Accept': '*/*',
                'Connection': 'keep-alive'
            }
        ]

        scraper = cloudscraper.create_scraper(
            delay=10,
            browser=random.choice(configs)
        )
        
        # El wait que pediste antes de la petición
        time.sleep(random.uniform(2.5, 3.5))
        
        res = scraper.get(url, headers=random.choice(headers_list), timeout=15)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            elemento = soup.find('span', class_='hero-metal-data__number')
            return elemento.text.strip() if elemento else "Tag no encontrado"
        
        return f"Error_{res.status_code}"

    def do_GET(self):
        global cache_metal
        
        # Solo probamos con Níquel para asegurar que no nos de timeout en Vercel
        url_target = "https://www.lme.com/metals/non-ferrous/lme-nickel#Summary"
        ahora = time.time()
        
        # Si tenemos algo en caché de menos de 30 min, lo usamos
        if cache_metal["precio"] and (ahora - cache_metal["timestamp"] < 1800):
            valor = cache_metal["precio"]
            status = "cache"
        else:
            valor = self.intentar_scrape(url_target)
            if "Error" not in valor and valor != "Tag no encontrado":
                cache_metal["precio"] = valor
                cache_metal["timestamp"] = ahora
                status = "success"
            else:
                status = "failed_or_blocked"

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        res_json = {
            "mineral": "Niquel",
            "precio": valor,
            "status": status,
            "timestamp": int(ahora)
        }
        
        self.wfile.write(json.dumps(res_json).encode('utf-8'))