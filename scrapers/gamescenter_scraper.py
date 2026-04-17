"""
Scraper para gamescenter.pe
Extrae información de precios de productos gaming (WooCommerce)
Estructura: <ul class="products elementor-grid"> -> <li class="product"> items
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


class GamescenterScraper:
    """Scraper para gamescenter.pe - Extrae dinámicamente todos los items de la página"""
    
    def __init__(self, url: str = None):
        self.url = url or "https://gamescenter.pe/categoria-producto/free-fire-diamantes/"
        self.seller = "Gamescenter"
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
                    "moneda": "PEN",
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
                await page.wait_for_selector('ul.products', timeout=10000)
                
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
        Extrae los items de la estructura WooCommerce.
        
        Estructura HTML:
        <ul class="products elementor-grid columns-4">
            <li class="wcpa_has_options product type-product ... instock ...">
                <a href="..." class="woocommerce-LoopProduct-link ...">
                    <h2 class="woocommerce-loop-product__title">Producto Name</h2>
                    <span class="price">
                        <span class="woocommerce-Price-amount amount">
                            <bdi><span class="woocommerce-Price-currencySymbol">S/</span>&nbsp;18.00</bdi>
                        </span>
                    </span>
                </a>
            </li>
        </ul>
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
            items = []
            
            # Buscar el ul con clase "products"
            products_ul = soup.find('ul', class_='products')
            if not products_ul:
                print(f"    ⚠️  No se encontró <ul class='products'>")
                return None
            
            # Buscar todos los items (li.product)
            product_items = products_ul.find_all('li', class_='product')
            print(f"    Encontrados {len(product_items)} items")
            
            for li in product_items:
                try:
                    # Determinar disponibilidad
                    disponible = "Sí" if "instock" in li.get("class", []) else "No"
                    
                    # Extraer nombre
                    title_h2 = li.find('h2', class_='woocommerce-loop-product__title')
                    if not title_h2:
                        continue
                    
                    nombre = title_h2.get_text(strip=True)
                    if not nombre:
                        continue
                    
                    # Normalizar nombre (remover juego y región)
                    nombre = self._normalize_item_name(nombre)
                    
                    # Extraer precio
                    price_span = li.find('span', class_='price')
                    if not price_span:
                        continue
                    
                    precio = self._extract_price(price_span)
                    if precio is None:
                        continue
                    
                    # Extraer URL
                    link_a = li.find('a', class_='woocommerce-LoopProduct-link')
                    if not link_a or not link_a.get('href'):
                        url = self.url
                    else:
                        url = link_a.get('href')
                    
                    items.append({
                        "nombre": nombre,
                        "precio": precio,
                        "url": url,
                        "disponible": disponible
                    })
                    
                    print(f"    ✅ {nombre} - S/ {precio}")
                    
                except Exception as e:
                    print(f"    ⚠️  Error extrayendo item: {e}")
                    continue
            
            return items if items else None
            
        except Exception as e:
            print(f"    ❌ Error en extracción: {e}")
            return None
    
    def _extract_price(self, price_span) -> Optional[float]:
        """
        Extrae el precio del span.
        
        Puede estar en dos formatos:
        1. Simple: <span class="price"><span class="woocommerce-Price-amount">...S/ 18.00...</span></span>
        2. Con descuento: <span class="price"><del>...</del>...<ins>...S/ 149.00...</ins></span>
        """
        try:
            # Buscar si hay <ins> (precio con descuento)
            ins_tag = price_span.find('ins')
            if ins_tag:
                # Hay descuento, usar el precio de ins
                price_text = ins_tag.get_text(strip=True)
            else:
                # Sin descuento, usar el contenido completo
                price_text = price_span.get_text(strip=True)
            
            # Extraer el número (S/ 18.00 o similar)
            price_match = re.search(r'S/\s*([\d,\.]+)', price_text)
            if not price_match:
                return None
            
            price_str = price_match.group(1).replace(',', '.')
            price = float(price_str)
            
            return price
            
        except Exception as e:
            return None
    
    def _normalize_item_name(self, nombre: str) -> str:
        """
        Normaliza el nombre del item removiendo prefijos de juego y sufijos de región.
        
        Ejemplos:
        - "Free Fire: 520 Diamantes + 52 Bonus – Perú" → "520 Diamantes + 52 Bonus"
        - "ROBLOX: 5000 Robux + 500 Bonus" → "5000 Robux + 500 Bonus"
        - "Blood Strike - Oro Común x500" → "Oro Común x500"
        """
        try:
            # Remover prefijos de juego: "Free Fire: ", "Free Fire - ", "ROBLOX: ", "ROBLOX - ", "Blood Strike - "
            nombre = re.sub(r'^(free\s+fire|roblox|blood\s+strike)\s*[:\-–]?\s*', '', nombre, flags=re.IGNORECASE)
            
            # Remover sufijos de región y plataforma
            nombre = re.sub(r'\s*[–\-]\s*(Perú|Latinoamérica|Robux Gift Card GLOBAL)\s*$', '', nombre)
            
            # Limpiar espacios múltiples
            nombre = ' '.join(nombre.split())
            
            return nombre.strip()
            
        except Exception as e:
            return nombre
