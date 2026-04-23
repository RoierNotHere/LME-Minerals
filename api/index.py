from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time  # Necesario para el delay

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Rotación de User-Agents para variar la identidad del navegador
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
        ]

        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

        materiales_config = [
            {"id": "niquel", "url": "https://www.lme.com/metals/non-ferrous/lme-nickel#Summary"},
            {"id": "aluminio", "url": "https://www.lme.com/metals/non-ferrous/lme-aluminium#Overview"},
            {"id": "estano", "url": "https://www.lme.com/metals/non-ferrous/lme-tin#Summary"}
        ]
        
        resultados = {}
        status_code = 200

        try:
            for metal in materiales_config:
                # --- El "Wait" aleatorio ---
                # Esto hace que el script espere un tiempo al azar entre 2.5 y 3.5 seg
                tiempo_espera = random.uniform(2.5, 3.5)
                time.sleep(tiempo_espera)
                
                # Configuración de headers dinámica
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Referer': 'https://www.google.com/',
                    'Connection': 'keep-alive'
                }

                res = scraper.get(metal["url"], headers=headers, timeout=20)
                
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    elemento = soup.find('span', class_='hero-metal-data__number')
                    
                    if elemento:
                        resultados[metal["id"]] = elemento.text.strip()
                    else:
                        resultados[metal["id"]] = "Dato no encontrado"
                else:
                    resultados[metal["id"]] = f"Error {res.status_code}"
            
            payload = {
                "lme_data": resultados,
                "status": "success"
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