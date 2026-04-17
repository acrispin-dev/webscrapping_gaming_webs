"""
Scraper para gamefan.la
Extrae información de precios de Diamond packages para Free Fire
Estructura en dos pasos: primero extrae links, luego accede a cada uno para obtener precio
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REQUEST_TIMEOUT, USER_AGENT


class GamefanScraper:
    """Scraper para gamefan.la - Extrae dinámicamente todos los items de la página"""
    
    def __init__(self, base_url: str = "https://gamefan.la", url: str = None):
        self.base_url = base_url
        self.url = url or "https://gamefan.la/pe/juegos/freefire"
        self.seller = "Gamefan"
        self.headers = {"User-Agent": USER_AGENT}
    
    def scrape_game(self, game_name: str) -> List[Dict]:
        """Scraping para un juego específico - Extrae automáticamente de la página"""
        print(f"\n🎮 Scrapendo {game_name} desde {self.seller}...")
        
        # Paso 1: Obtener la página principal y extraer los links de productos
        items_links = self._get_product_links()
        
        if not items_links:
            print(f"⚠️  No se pudieron extraer links de productos")
            return []
        
        print(f"📋 Productos encontrados: {len(items_links)}")
        
        # Paso 2: Para cada link, acceder y obtener el precio
        results = []
        for idx, item in enumerate(items_links, 1):
            try:
                item_name = item["nombre"]
                item_url = item["url"]
                
                # Acceder a la página del producto para obtener el precio
                price = self._get_product_price(item_url)
                
                if price is None:
                    print(f"  [{idx}/{len(items_links)}] {item_name}... ⚠️  No se pudo obtener precio")
                    continue
                
                data = {
                    "seller": self.seller,
                    "juego": game_name,
                    "nombre_item": item_name,
                    "precio": f"{price:.2f}",
                    "moneda": "PEN",
                    "disponible": "Sí",
                    "url_producto": item_url,
                    "fecha_scrapping": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                results.append(data)
                price_display = f"{data['precio']} {data['moneda']}"
                print(f"  [{idx}/{len(items_links)}] {item_name}... ✅ {price_display}")
                
            except Exception as e:
                print(f"  [{idx}/{len(items_links)}] Error procesando item: {e}")
        
        print(f"✨ Completado: {len(results)}/{len(items_links)} items")
        return results
    
    def _get_product_links(self) -> Optional[List[Dict]]:
        """
        Extrae los links de productos de la página principal.
        
        Estructura HTML:
        <div class="col-md-3 col-xs-6 nopadding">
            <h2 class="caption">
                <small>Garena</small><br>
                100 diamantes<br>
            </h2>
            <a href="/pe/comprar/100+diamantes" class="purchase btn btn-warning">COMPRAR</a>
        </div>
        """
        try:
            print("    ⏳ Cargando página principal...")
            response = requests.get(self.url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "lxml")
            items = []
            
            # Buscar todos los divs con clase "col-md-X col-xs-6 nopadding" (flexible con col-md-3, col-md-4, etc.)
            product_divs = soup.find_all('div', class_=re.compile(r'col-md-\d+.*col-xs-6.*nopadding'))
            print(f"    Encontrados {len(product_divs)} productos")
            
            for div in product_divs:
                try:
                    # Buscar el h2 con la clase caption
                    h2 = div.find('h2', class_='caption')
                    if not h2:
                        continue
                    
                    # Extraer el nombre del producto
                    # El h2 tiene estructura: <small>SELLER</small><br>PRODUCT_NAME<br>
                    # Eliminar primero los tags <small> que contienen el vendedor
                    for small_tag in h2.find_all('small'):
                        small_tag.decompose()
                    
                    h2_text = h2.get_text(strip=True)
                    # Limpiar espacios múltiples y saltos de línea
                    product_name = re.sub(r'\s+', ' ', h2_text).strip()
                    
                    if not product_name:
                        continue
                    
                    # Buscar el link "a" con clase "purchase"
                    link = div.find('a', class_='purchase')
                    if not link or not link.get('href'):
                        continue
                    
                    href = link.get('href')
                    
                    # Construir URL completa
                    full_url = self.base_url + href if href.startswith('/') else href
                    
                    items.append({
                        "nombre": product_name,
                        "url": full_url,
                        "href": href
                    })
                    
                except Exception as e:
                    print(f"    ⚠️  Error extrayendo producto: {e}")
                    continue
            
            return items if items else None
            
        except Exception as e:
            print(f"    ❌ Error cargando página: {e}")
            return None
    
    def _get_product_price(self, product_url: str) -> Optional[float]:
        """
        Accede a la página del producto y extrae el precio.
        
        Estructura HTML en página de producto:
        <h2 class="big">S./ 3.80</h2>
        """
        try:
            # Aumentar timeout para evitar problemas de conexión
            response = requests.get(product_url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "lxml")
            
            # Buscar el h2 con clase "big"
            price_h2 = soup.find('h2', class_='big')
            if not price_h2:
                return None
            
            price_text = price_h2.get_text(strip=True)
            
            # Extraer el precio (ej: "S./ 3.80" o "S/ 3.80")
            price_match = re.search(r'S\.?\s*/?(\s*)?([\d,\.]+)', price_text)
            if not price_match:
                return None
            
            price_str = price_match.group(2).replace(',', '.')
            price = float(price_str)
            
            return price
            
        except requests.Timeout:
            print(f"        ⚠️  Timeout en {product_url}")
            return None
        except Exception as e:
            return None
