from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Lista de User-Agents actualizados para rotar y evitar detección
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

        # Creamos el scraper con una configuración de cifrado más robusta
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

        # Configuramos encabezados que imitan a un humano real
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        materiales_config = [
            {"id": "niquel", "url": "https://www.lme.com/metals/non-ferrous/lme-nickel#Summary"},
            {"id": "aluminio", "url": "https://www.lme.com/metals/non-ferrous/lme-aluminium#Overview"},
            {"id": "estano", "url": "https://www.lme.com/metals/non-ferrous/lme-tin#Summary"}
        ]
        
        resultados = {}
        status_code = 200

        try:
            for metal in materiales_config:
                # Realizamos la petición con los headers reforzados
                res = scraper.get(metal["url"], headers=headers, timeout=20)
                
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # Intentamos encontrar el precio
                    elemento = soup.find('span', class_='hero-metal-data__number')
                    
                    if elemento:
                        resultados[metal["id"]] = elemento.text.strip()
                    else:
                        resultados[metal["id"]] = "Selector no hallado"
                else:
                    # Guardamos el error específico para debuggear
                    resultados[metal["id"]] = f"Error {res.status_code}"
            
            payload = {
                "lme_data": resultados,
                "status": "success" if any("Error" not in str(v) for v in resultados.values()) else "failed"
            }
            
        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        # Respuesta para Vercel
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return