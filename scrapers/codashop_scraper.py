"""
Scraper para codashop.com
Extrae información de precios de productos gaming
Estructura: SKU cards con información de diamantes y precios
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


class CodashopScraper:
    """Scraper para codashop.com - Extrae dinámicamente todos los items de la página"""
    
    def __init__(self, url: str = None):
        self.url = url or "https://www.codashop.com/es-pe/free-fire"
        self.seller = "Codashop"
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
                await page.wait_for_selector('div#step-sku', timeout=10000)
                
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
        Extrae los items de la estructura de Codashop.
        
        Estructura HTML:
        <div id="step-sku" class="product__purchase-step__container" ...>
            <div class="sku-card">
                <div class="sku-info-section__titles__title">
                    <span>341 Diamantes</span>
                </div>
                <div class="sku-subtitle">(310 + 31 Bonus)</div>
                <span class="price-section__price__price-container__amount">S/11,68</span>
            </div>
        </div>
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
            items = []
            
            # Buscar el div con id "step-sku"
            step_sku = soup.find('div', id='step-sku')
            if not step_sku:
                print(f"    ⚠️  No se encontró <div id='step-sku'>")
                return None
            
            # Buscar todos los sku-card
            sku_cards = step_sku.find_all('div', class_='sku-card')
            print(f"    Encontrados {len(sku_cards)} items")
            
            for card in sku_cards:
                try:
                    # Extraer el texto del subtitle (entre paréntesis)
                    subtitle_div = card.find('div', class_='sku-subtitle')
                    if not subtitle_div:
                        continue
                    
                    subtitle_text = subtitle_div.get_text(strip=True)
                    if not subtitle_text:
                        continue
                    
                    # Remover paréntesis y procesar: "(310 + 31 Bonus)" -> "310 diamantes + 31 Bonus"
                    nombre = self._normalize_item_name(subtitle_text)
                    
                    if not nombre:
                        continue
                    
                    # Extraer precio
                    price_span = card.find('span', class_='price-section__price__price-container__amount')
                    if not price_span:
                        continue
                    
                    precio = self._extract_price(price_span)
                    if precio is None:
                        continue
                    
                    items.append({
                        "nombre": nombre,
                        "precio": precio,
                        "url": self.url,
                        "disponible": "Sí"
                    })
                    
                    print(f"    ✅ {nombre} - S/{precio}")
                    
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
        Formato: S/11,68, S/19,47, etc.
        """
        try:
            price_text = price_span.get_text(strip=True)
            
            # Extraer el número (S/ 11,68 -> 11.68)
            price_match = re.search(r'S/\s*([\d,\.]+)', price_text)
            if not price_match:
                return None
            
            price_str = price_match.group(1).replace(',', '.')
            price = float(price_str)
            
            return price
            
        except Exception as e:
            return None
    
    def _normalize_item_name(self, subtitle: str) -> str:
        """
        Normaliza el nombre del item desde el subtitle.
        Ejemplos:
        - "(310 + 31 Bonus)" -> "310 diamantes + 31 Bonus"
        - "(520 + 52 Bonus)" -> "520 diamantes + 52 Bonus"
        """
        try:
            # Remover paréntesis
            nombre = re.sub(r'[()]', '', subtitle).strip()
            
            # Convertir a minúsculas la palabra "diamantes"
            # Patrón: número + espacios + "+" -> número + " diamantes +"
            nombre = re.sub(r'^(\d+)\s*\+', r'\1 diamantes +', nombre, flags=re.IGNORECASE)
            
            # Capitalizar "Bonus" si existe
            nombre = re.sub(r'\bbonus\b', 'Bonus', nombre, flags=re.IGNORECASE)
            
            # Limpiar espacios múltiples
            nombre = ' '.join(nombre.split())
            
            return nombre.strip()
            
        except Exception as e:
            return subtitle
