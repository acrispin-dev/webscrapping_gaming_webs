"""
Scraper para pagostore.garena.com
Extrae información de precios de Free Fire y otros juegos
Usa Playwright cuando es posible, fallback a requests + patrones heurísticos
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os
import re
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REQUEST_TIMEOUT


# Precios conocidos para Free Fire Diamonds (basados en observaciones previas)
# Estos son FALLBACK si no se puede extraer del sitio
KNOWN_PRICES = {
    17992: {"name": "Diamond 100 + 10 Bonus", "precio": "3.50", "moneda": "PEN"},
    17993: {"name": "Diamond 310 + 31 Bonus", "precio": "10.00", "moneda": "PEN"},
    17994: {"name": "Diamond 520 + 52 Bonus", "precio": "16.50", "moneda": "PEN"},
    17995: {"name": "Diamond 1060 + 106 Bonus", "precio": "33.00", "moneda": "PEN"},
    17996: {"name": "Diamond 2180 + 218 Bonus", "precio": "66.00", "moneda": "PEN"},
    17997: {"name": "Diamond 5600 + 560 Bonus", "precio": "165.00", "moneda": "PEN"},
}


class PagostoreScraper:
    """Scraper para extraer datos de Pagostore Garena"""
    
    def __init__(self):
        self.base_url = "https://pagostore.garena.com/"
        self.seller = "Pagostore"
        self.use_known_prices = False  # Cambiar a True si queremos usar precios conocidos
        
    def scrape_item(self, item_id: int, game_name: str) -> Optional[Dict]:
        """
        Extrae información de un item específico
        
        Args:
            item_id: ID del item a scrapear
            game_name: Nombre del juego
            
        Returns:
            Diccionario con la información del item o None si hay error
        """
        try:
            # Si queremos usar precios conocidos (para testing)
            if self.use_known_prices and item_id in KNOWN_PRICES:
                known = KNOWN_PRICES[item_id]
                url = f"{self.base_url}?item={item_id}"
                return {
                    "seller": self.seller,
                    "juego": game_name,
                    "item_id": item_id,
                    "nombre_item": known["name"],
                    "precio": known["precio"],
                    "moneda": known["moneda"],
                    "disponible": "Sí",
                    "url_producto": url,
                    "fecha_scrapping": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # Intenta con Playwright primero
            try:
                data = asyncio.run(self._scrape_with_playwright(item_id, game_name))
                if data:
                    return data
            except Exception as e:
                print(f"    (Playwright falló: {str(e)[:30]}...)", end=" ")
            
            # Fallback a requests
            data = self._scrape_with_requests(item_id, game_name)
            return data
            
        except Exception as e:
            print(f"❌ Error general: {e}")
            return None
    
    async def _scrape_with_playwright(self, item_id: int, game_name: str) -> Optional[Dict]:
        """Scraping con Playwright"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                url = f"{self.base_url}?item={item_id}"
                await page.goto(url, wait_until="networkidle", timeout=REQUEST_TIMEOUT * 1000)
                
                # Obtener contenido HTML
                content = await page.content()
                soup = BeautifulSoup(content, "lxml")
                
                # Extraer datos
                item_name = self._extract_item_name(soup, item_id)
                price_info = self._extract_price(soup, item_id, content)
                
                if not price_info:
                    return None
                
                data = {
                    "seller": self.seller,
                    "juego": game_name,
                    "item_id": item_id,
                    "nombre_item": item_name,
                    "precio": price_info["precio"],
                    "moneda": price_info["moneda"],
                    "disponible": "Sí",
                    "url_producto": url,
                    "fecha_scrapping": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                return data
                
            finally:
                await browser.close()
    
    def _scrape_with_requests(self, item_id: int, game_name: str) -> Optional[Dict]:
        """Scraping fallback con requests"""
        try:
            import requests
            
            url = f"{self.base_url}?item={item_id}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Extraer datos
            item_name = self._extract_item_name(soup, item_id)
            price_info = self._extract_price(soup, item_id, response.text)
            
            if not price_info:
                return None
            
            data = {
                "seller": self.seller,
                "juego": game_name,
                "item_id": item_id,
                "nombre_item": item_name,
                "precio": price_info["precio"],
                "moneda": price_info["moneda"],
                "disponible": "Sí",
                "url_producto": url,
                "fecha_scrapping": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return data
            
        except Exception as e:
            return None
    
    def _extract_item_name(self, soup: BeautifulSoup, item_id: int) -> str:
        """Extrae el nombre del item incluyendo bonus desde el HTML de forma robusta"""
        try:
            page_text = soup.get_text()
            
            # Patrones más específicos para extraer "Diamond XXX + YY Bonus"
            patterns = [
                # Busca: Diamond 100 + 10 Bonus, Diamond 310 + 31 Bonus, etc.
                r'(Diamond\s+(\d+)\s*\+\s*(\d+)\s*Bonus)',
                # Busca variaciones sin espacios regulares
                r'(Diamond\s*(\d+).*?\+.*?(\d+).*?Bonus)',
                # Busca solo Diamond con números
                r'(Diamond\s+(\d+(?:\s*\+\s*\d+)?)[^<]*?)',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    full_match = match.group(1).strip()
                    # Limpiar y formatear
                    full_match = re.sub(r'\s+', ' ', full_match)  # normalizar espacios
                    
                    # Si no termina con "Bonus", agregarlo
                    if not full_match.lower().endswith('bonus'):
                        full_match = full_match + ' Bonus'
                    
                    return full_match
            
            # Estrategia 2: Si encontramos un número de diamonds, intentar extraerlo
            diamond_matches = re.findall(r'Diamond\s*(\d+)', page_text, re.IGNORECASE)
            if diamond_matches:
                # Tomar el primer match
                diamond_count = diamond_matches[0]
                # Intentar buscar el bonus correspondiente cercano
                near_text = page_text[page_text.find(f'Diamond {diamond_count}'):
                                      page_text.find(f'Diamond {diamond_count}') + 200]
                
                bonus_match = re.search(r'\+\s*(\d+)', near_text)
                if bonus_match:
                    bonus_count = bonus_match.group(1)
                    return f"Diamond {diamond_count} + {bonus_count} Bonus"
                else:
                    return f"Diamond {diamond_count}"
            
            # Fallback: usar precios conocidos
            if item_id in KNOWN_PRICES:
                return KNOWN_PRICES[item_id]["name"]
            
            return f"Producto {item_id}"
            
        except Exception as e:
            # Fallback final
            if item_id in KNOWN_PRICES:
                return KNOWN_PRICES[item_id]["name"]
            return f"Producto {item_id}"
    
    def _extract_price(self, soup: BeautifulSoup, item_id: int, page_content: str) -> Optional[Dict[str, str]]:
        """Extrae el precio con múltiples estrategias - Mejorado para mayor precisión"""
        try:
            # Estrategia 1: Buscar en el HTML renderizado (Playwright) primero
            # ya que tendremos el contenido completo con precios dinámicos
            if isinstance(soup, BeautifulSoup):
                # Buscar en spans que contengan "PEN" con formato XXX,XX
                # Estos spans tienen clases como "items-center [text-decoration:inherit] inline-flex"
                price_pattern = r'PEN\s+(\d+[.,]\d+)'
                matches = re.findall(price_pattern, soup.get_text())
                
                if matches:
                    # Si hay múltiples precios, tomar el menor (mejor precio)
                    prices_float = []
                    for match in matches:
                        try:
                            price_float = float(match.replace(',', '.'))
                            if 0.5 < price_float < 500:  # Rango válido
                                prices_float.append((price_float, match))
                        except:
                            continue
                    
                    if prices_float:
                        # Ordenar por precio y tomar el menor
                        prices_float.sort(key=lambda x: x[0])
                        best_price = prices_float[0][1]
                        return {
                            "precio": best_price.replace(',', '.'),
                            "moneda": "PEN"
                        }
            
            # Estrategia 2: Buscar en page_content (para requests fallback)
            if page_content:
                page_text = page_content
                
                # Patrón mejorado: busca "PEN XX,XX" en el contexto HTML
                # Esto es más robusto que buscar solo en el texto extraído
                pattern_pen = r'PEN\s+(\d+[.,]\d+)'
                matches = re.findall(pattern_pen, page_text)
                
                if matches:
                    prices_float = []
                    for match in matches:
                        try:
                            price_float = float(match.replace(',', '.'))
                            if 0.5 < price_float < 500:
                                prices_float.append((price_float, match))
                        except:
                            continue
                    
                    if prices_float:
                        prices_float.sort(key=lambda x: x[0])
                        best_price = prices_float[0][1]
                        return {
                            "precio": best_price.replace(',', '.'),
                            "moneda": "PEN"
                        }
            
            # Estrategia 3: Usar precios conocidos como último recurso
            if item_id in KNOWN_PRICES:
                known = KNOWN_PRICES[item_id]
                print(f"    (usando precio conocido: {known['precio']} {known['moneda']})", end=" ")
                return {
                    "precio": known["precio"],
                    "moneda": known["moneda"]
                }
            
            return None
            
        except Exception as e:
            print(f"    (error extrayendo precio: {str(e)[:20]})", end=" ")
            return None
    
    def scrape_game(self, game_name: str, item_ids: List[int]) -> List[Dict]:
        """
        Scrapea todos los items de un juego
        
        Args:
            game_name: Nombre del juego
            item_ids: Lista de IDs de items a scrapear
            
        Returns:
            Lista de diccionarios con los datos de los items
        """
        print(f"\n🎮 Scrapendo {game_name} desde Pagostore...")
        print(f"📋 Total de items a scrapear: {len(item_ids)}")
        
        results = []
        for idx, item_id in enumerate(item_ids, 1):
            print(f"  [{idx}/{len(item_ids)}] Item {item_id}...", end=" ", flush=True)
            data = self.scrape_item(item_id, game_name)
            
            if data:
                results.append(data)
                print(f"✅ {data['nombre_item']}: {data['precio']} {data['moneda']}")
            else:
                print("⏭️ ")
            
            # Pequeño delay
            if idx < len(item_ids):
                time.sleep(0.5)
        
        print(f"✨ Completado: {len(results)}/{len(item_ids)} items")
        return results




