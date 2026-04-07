from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Configuración del scraper
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        url = "https://www.lme.com/metals/non-ferrous/lme-nickel#Summary"
        
        try:
            res = scraper.get(url, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                elemento = soup.find('span', class_='hero-metal-data__number')
                
                if elemento:
                    precio = elemento.text.strip()
                    payload = {
                        "niquel": precio,
                        "fuente": "LME",
                        "status": "success"
                    }
                    status_code = 200
                else:
                    payload = {"error": "Selector no encontrado"}
                    status_code = 404
            else:
                payload = {"error": f"Error LME: {res.status_code}"}
                status_code = 500
                
        except Exception as e:
            payload = {"error": str(e)}
            status_code = 500

        # Respuesta de la API
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return