import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Configuración exclusiva para Níquel en LME
URL_LME = "https://www.lme.com/metals/non-ferrous/lme-nickel#Summary"
FILE_JSON = "precios.json"

def extraer_niquel():
    # Creamos el scraper configurado para simular un navegador real
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Consultando LME Nickel...")
        response = scraper.get(URL_LME, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscamos el precio con la clase que identificamos
            elemento = soup.find('span', class_='hero-metal-data__number')
            
            if elemento:
                precio = elemento.text.strip()
                
                # Estructura del JSON
                datos = {
                    "niquel": {
                        "precio": precio,
                        "moneda": "USD",
                        "unidad": "ton",
                        "actualizado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "fuente": "LME"
                    }
                }
                
                # --- LÍNEA CORREGIDA ---
                with open(FILE_JSON, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
                
                print(f"✅ Éxito: Níquel a {precio}. Archivo {FILE_JSON} generado.")
            else:
                print("❌ No se encontró el elemento del precio en el HTML.")
        else:
            print(f"❌ Error de acceso (Status: {response.status_code})")
            
    except Exception as e:
        print(f"❗ Error crítico: {str(e)}")

if __name__ == "__main__":
    extraer_niquel()