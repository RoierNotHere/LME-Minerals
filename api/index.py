from http.server import BaseHTTPRequestHandler
import cloudscraper
from bs4 import BeautifulSoup
import json
import random
import time

# Cache global para evitar peticiones excesivas y bloqueos 403
# Guardamos los datos por 1 hora (3600 segundos)
cache_lme = {
    "datos": None,
    "timestamp": 0
}

class handler(BaseHTTPRequestHandler):

    def obtener_datos_lme(self):
        scraper = cloudscraper.create_scraper(
            delay=10, 
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        materiales_config = [
            {"id": "niquel", "url": "https://www.lme.com/metals/non-ferrous/lme-nickel#Summary"},
            {"id": "aluminio", "url": "https://www.lme.com/metals/non-ferrous/lme-aluminium#Overview"},
            {"id": "estano", "url": "https://www.lme.com/metals/non-ferrous/lme-tin#Summary"}
        ]
        
        resultados = {}
        
        # Headers idénticos a los que usas en Investing para mayor consistencia
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive'
        }

        try:
            for metal in materiales_config:
                # El wait aleatorio que pediste (2.5 a 3.5 segundos)
                time.sleep(random.uniform(2.5, 3.5))
                
                res = scraper.get(metal["url"], headers=headers, timeout=20)
                
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    # Selector específico de la LME
                    elemento = soup.find('span', class_='hero-metal-data__number')
                    
                    if elemento:
                        resultados[metal["id"]] = elemento.text.strip()
                    else:
                        resultados[metal["id"]] = "No encontrado"
                else:
                    resultados[metal["id"]] = f"Error {res.status_code}"
            
            return resultados

        except Exception as e:
            print(f"Error en scraping: {str(e)}")
            return None

    def do_GET(self):
        global cache_lme
        
        ahora = time.time()
        TIEMPO_CACHE = 3600  # 1 hora de vida para los datos
        
        # Lógica de Cache
        if cache_lme["datos"] and (ahora - cache_lme["timestamp"] < TIEMPO_CACHE):
            valor_final = cache_lme["datos"]
            fuente = "Caché Local"
        else:
            # Consultar nuevos datos
            nuevos_datos = self.obtener_datos_lme()
            
            if nuevos_datos:
                cache_lme["datos"] = nuevos_datos
                cache_lme["timestamp"] = ahora
                valor_final = nuevos_datos
                fuente = "LME Real-time"
            else:
                # Si falla el scraping, intentar mostrar lo que había en caché aunque sea viejo
                valor_final = cache_lme["datos"] if cache_lme["datos"] else {"error": "Servicio bloqueado"}
                fuente = "Error / Bloqueo (IP Vercel)"

        # Respuesta JSON
        payload = {
            "lme_data": valor_final,
            "info": {
                "fuente": fuente,
                "timestamp": int(ahora)
            }
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))
        return