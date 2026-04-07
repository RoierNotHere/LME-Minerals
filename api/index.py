from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        # Lista de materiales con sus respectivos links
        materiales_config = [
            {"id": "niquel", "url": "https://www.lme.com/metals/non-ferrous/lme-nickel#Summary"},
            {"id": "aluminio", "url": "https://www.lme.com/metals/non-ferrous/lme-aluminium#Overview"},
            {"id": "estano", "url": "https://www.lme.com/metals/non-ferrous/lme-tin#Summary"}
        ]
        
        resultados = {}
        status_code = 200

        try:
            for metal in materiales_config:
                res = scraper.get(metal["url"], timeout=15)
                
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # El selector CSS que confirmamos que funciona
                    elemento = soup.find('span', class_='hero-metal-data__number')
                    
                    if elemento:
                        resultados[metal["id"]] = elemento.text.strip()
                    else:
                        resultados[metal["id"]] = "No encontrado"
                else:
                    resultados[metal["id"]] = f"Error {res.status_code}"
            
            # Formato JSON final
            payload = {
                "lme_data": resultados,
                "status": "success"
            }
            
        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        # Respuesta de la API para Vercel
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        # Habilitamos CORS por si quieres consultar la API desde otro dominio
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return