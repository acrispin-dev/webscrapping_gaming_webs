"""
Scraper para mtcgame.com
Extrae información de precios de productos gaming (grid basado en Tailwind CSS)
Estructura: <div class="grid ..."> -> <div class="bg-gradient-to-b ..."> items con <h3>, <p> price
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REQUEST_TIMEOUT, USER_AGENT


class MTCGameScraper:
    """Scraper para mtcgame.com - Extrae dinámicamente todos los items de la página"""
    
    def __init__(self, url: str = None):
        self.url = url or "https://www.mtcgame.com/garena/free-fire-garena-diamond-top-up"
        self.seller = "MTCGame"
        self.headers = {"User-Agent": USER_AGENT}
    
    def scrape_game(self, game_name: str) -> List[Dict]:
        """Scraping para un juego específico - Extrae automáticamente de la página"""
        print(f"\n🎮 Scrapendo {game_name} desde {self.seller}...")
        
        # Usar Playwright para renderizar JavaScript
        items = self._scrape_with_playwright()
        
        if not items:
            print(f"⚠️  No se pudieron extraer items")
            return []
        
        print(f"📋 Total de items encontrados: {len(items)}")
        
        results = []
        for idx, item in enumerate(items, 1):
            try:
                item_name = item.get("nombre", "Item")
                price = item.get("precio")
                url = item.get("url", self.url)
                disponible = item.get("disponible", "Sí")
                
                data = {
                    "seller": self.seller,
                    "juego": game_name,
                    "nombre_item": item_name,
                    "precio": f"{price:.2f}",
                    "moneda": "USD",
                    "disponible": disponible,
                    "url_producto": url,
                    "fecha_scrapping": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                results.append(data)
                price_display = f"{data['precio']} {data['moneda']}"
                print(f"  [{idx}/{len(items)}] {item_name}... ✅ {price_display}")
                
            except Exception as e:
                print(f"  [{idx}/{len(items)}] Error procesando item: {e}")
        
        print(f"✨ Completado: {len(results)}/{len(items)} items")
        return results
    
    def _scrape_with_playwright(self) -> Optional[List[Dict]]:
        """Extrae todos los items usando Playwright"""
        try:
            result = asyncio.run(self._scrape_async())
            return result
        except Exception as e:
            print(f"    ❌ Error con Playwright: {e}")
            return None
    
    async def _scrape_async(self) -> Optional[List[Dict]]:
        """Scraping asincrónico con Playwright"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            try:
                page = await browser.new_page()
                page.set_default_timeout(30000)
                
                print(f"    ⏳ Cargando página con Playwright...")
                await page.goto(self.url, wait_until="domcontentloaded")
                
                print(f"    ⏳ Esperando renderización...")
                # Esperar a que se carguen los productos
                await page.wait_for_selector('div.grid', timeout=10000)
                
                # Obtener el HTML renderizado
                html_content = await page.content()
                print(f"    ✅ Página renderizada ({len(html_content)} bytes)")
                
                # Parsear y extraer items
                items = self._extract_items_from_html(html_content)
                
                return items
                
            finally:
                await browser.close()
    
    def _extract_items_from_html(self, html_content: str) -> Optional[List[Dict]]:
        """
        Extrae los items de la estructura de grid de Tailwind CSS.
        
        Estructura HTML:
        <div class="grid grid-cols-2 sm:grid-cols-3 ...">
            <div class="bg-gradient-to-b from-mtc-deep-dark to-gray-900 ...">
                <a href="/garena/free-fire-garena-diamond-top-up/free-fire-100-diamonds-top-up">
                    <img ...>
                </a>
                <div class="bg-mtc-deep-dark px-4 py-4 ...">
                    <a href="...">
                        <h3 class="text-white font-bold ...">Free Fire 100 Diamonds Top Up</h3>
                    </a>
                    <div class="mb-4 bg-gradient-to-r ...">
                        <p class="text-sm ... text-green-400">$1</p>
                    </div>
                    <div class="flex gap-2">
                        <button>...</button>
                        <button>...</button>
                    </div>
                </div>
            </div>
        </div>
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
            items = []
            
            # Buscar el div con clase "grid"
            products_grid = soup.find('div', class_='grid')
            if not products_grid:
                print(f"    ⚠️  No se encontró <div class='grid'>")
                return None
            
            # Buscar todos los items (div con bg-gradient-to-b)
            product_items = products_grid.find_all('div', class_='bg-gradient-to-b')
            print(f"    Encontrados {len(product_items)} items")
            
            for div in product_items:
                try:
                    # Extraer nombre del h3
                    title_h3 = div.find('h3', class_='text-white')
                    if not title_h3:
                        continue
                    
                    nombre = title_h3.get_text(strip=True)
                    if not nombre:
                        continue
                    
                    # Normalizar nombre (remover "Free Fire" del inicio y "Top Up" del final)
                    nombre = self._normalize_item_name(nombre)
                    
                    # Extraer precio
                    price_p = div.find('p', class_='text-green-400')
                    if not price_p:
                        continue
                    
                    precio = self._extract_price(price_p)
                    if precio is None:
                        continue
                    
                    # Extraer URL - buscar el primer enlace que tenga href
                    link_a = div.find('a', href=True)
                    if not link_a or not link_a.get('href'):
                        # Construir URL completa
                        url = self.url
                    else:
                        href = link_a.get('href')
                        # Si es URL relativa, construir URL completa
                        if href.startswith('/'):
                            url = f"https://www.mtcgame.com{href}"
                        else:
                            url = href
                    
                    items.append({
                        "nombre": nombre,
                        "precio": precio,
                        "url": url,
                        "disponible": "Sí"  # MTCGame no muestra disponibilidad claramente
                    })
                    
                    print(f"    ✅ {nombre} - ${precio}")
                    
                except Exception as e:
                    print(f"    ⚠️  Error extrayendo item: {e}")
                    continue
            
            return items if items else None
            
        except Exception as e:
            print(f"    ❌ Error en extracción: {e}")
            return None
    
    def _extract_price(self, price_p) -> Optional[float]:
        """
        Extrae el precio del párrafo.
        Formato: $1, $2, $5, $10, $20, $2.05, $9.63, etc.
        """
        try:
            price_text = price_p.get_text(strip=True)
            
            # Extraer el número ($ 1, $2.05, etc)
            price_match = re.search(r'\$\s*([\d,\.]+)', price_text)
            if not price_match:
                return None
            
            price_str = price_match.group(1).replace(',', '.')
            price = float(price_str)
            
            return price
            
        except Exception as e:
            return None
    
    def _normalize_item_name(self, nombre: str) -> str:
        """
        Normaliza el nombre del item removiendo prefijos de juego y "Top Up" del final.
        
        Ejemplos:
        - "Free Fire 100 Diamonds Top Up" → "100 Diamonds"
        - "Free Fire Weekly Membership Top-Up (Global)" → "Weekly Membership (Global)"
        - "Mobile Legends - Diamond 1234 Top-Up" → "Diamond 1234"
        - "Mobile Legends - Twilight Pass Top Up" → "Twilight Pass"
        """
        try:
            # Remover "Free Fire" o "Mobile Legends - " del inicio
            nombre = re.sub(r'^(free\s+fire|mobile\s+legends)\s*[–\-]?\s*', '', nombre, flags=re.IGNORECASE)
            
            # Remover "Top Up" o "Top-Up" del final
            nombre = re.sub(r'\s+top[\-\s]*up\s*$', '', nombre, flags=re.IGNORECASE)
            
            # Limpiar espacios múltiples
            nombre = ' '.join(nombre.split())
            
            return nombre.strip()
            
        except Exception as e:
            return nombre
