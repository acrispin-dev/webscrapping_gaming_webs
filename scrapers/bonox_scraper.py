"""
Scraper para bonoxs.com
Extrae automáticamente información de precios de Free Fire
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os
import re
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REQUEST_TIMEOUT, USER_AGENT


class BonoxScraper:
    """Scraper para bonoxs.com - Extrae dinámicamente todos los items de la página"""
    
    def __init__(self, url: str = None):
        self.base_url = url or "https://bonoxs.com/pe/free-fire-pe?from=store"
        self.seller = "Bonox"
    
    @staticmethod
    def calculate_diamond_name(total_diamonds: int) -> str:
        """
        Calcula el nombre correcto de diamantes a partir del total.
        
        Bonox ofrece: base_diamonds + 10% como bonus
        Si total = 110, entonces base = 100, bonus = 10
        Retorna: "Diamond 100 + 10 Bonus"
        """
        # El bonus es aproximadamente 10% del base
        base = int(total_diamonds / 1.1)
        bonus = total_diamonds - base
        
        return f"Diamond {base} + {bonus} Bonus"
    
    def scrape_game(self, game_name: str, item_ids: List[int] = None) -> List[Dict]:
        """Scraping para un juego específico - Extrae automáticamente de la página"""
        print(f"\n🎮 Scrapendo {game_name} desde {self.seller}...")
        
        # Intenta primero con Playwright
        items = self._scrape_all_items_playwright()
        
        if not items:
            # Fallback a requests
            items = self._scrape_all_items_requests()
        
        if items:
            print(f"📋 Total de items encontrados: {len(items)}")
        else:
            print(f"⚠️  No se pudieron extraer items")
            return []
        
        results = []
        for idx, item in enumerate(items, 1):
            try:
                # Si el item ya tiene nombre (de Mobile Legends), úsalo directamente
                if "nombre" in item and item["nombre"]:
                    item_name = item["nombre"]
                # Si solo tiene diamantes, calcula el nombre
                elif item.get("total", 0) > 0:
                    item_name = self.calculate_diamond_name(item["total"])
                else:
                    item_name = "Item"
                
                data = {
                    "seller": self.seller,
                    "juego": game_name,
                    "nombre_item": item_name,
                    "precio": f"{item['precio']:.2f}",
                    "moneda": "PEN",
                    "disponible": "Sí",
                    "url_producto": self.base_url,
                    "fecha_scrapping": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                results.append(data)
                price_display = f"{data['precio']} {data['moneda']}"
                print(f"  [{idx}/{len(items)}] {item_name}... ✅ {price_display}")
                
            except Exception as e:
                print(f"  [{idx}/{len(items)}] Error procesando item: {e}")
        
        print(f"✨ Completado: {len(results)}/{len(items)} items")
        return results
    
    def _scrape_all_items_playwright(self) -> Optional[List[Dict]]:
        """Extrae todos los items usando Playwright"""
        try:
            result = asyncio.run(self._scrape_async())
            return result
        except Exception as e:
            return None
    
    async def _scrape_async(self) -> Optional[List[Dict]]:
        """Scraping asincrónico con Playwright - mejorado"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                print("⏳ Cargando página con Playwright...")
                try:
                    await page.goto(self.base_url, wait_until="networkidle", timeout=REQUEST_TIMEOUT * 2000)
                except:
                    # Si networkidle falla, intentar con domcontentloaded
                    print("⏳ Reintentando con domcontentloaded...")
                    await page.goto(self.base_url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT * 2000)
                
                # Esperar a que se renderice el contenido
                print("⏳ Esperando renderización...")
                await page.wait_for_timeout(3000)
                
                # Tratar de scroll para disparar carga lazy
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
                
                # Obtener contenido HTML
                content = await page.content()
                print(f"✅ Página renderizada ({len(content)} bytes)")
                
                items = self._extract_items_from_html(content)
                
                return items if items else None
                
            except Exception as e:
                print(f"⚠️  Error en Playwright: {e}")
                return None
            finally:
                await browser.close()
    
    def _scrape_all_items_requests(self) -> Optional[List[Dict]]:
        """Extrae todos los items usando requests (fallback)"""
        try:
            url = self.base_url
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            items = self._extract_items_from_html(response.text)
            return items
            
        except Exception as e:
            return None
    
    def _extract_items_from_html(self, html_content: str) -> Optional[List[Dict]]:
        """
        Extrae todos los items de la estructura HTML de forma flexible.
        
        Bonox usa Next.js SSR con diferentes estructuras según el juego:
        - Free Fire: Principalmente diamantes con bonus
        - Mobile Legends: Pases, Diamantes, Combos, Bono Doble Recompensa
        - Valorant: Paquetes VP directos
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
            items = []
            seen_prices = set()  # Para evitar duplicados
            
            # ESTRATEGIA VALORANT: Buscar estructura con VP y S/
            # Si detectamos VP, asumimos que es Valorant
            if "VP" in html_content:
                valorant_items = self._extract_valorant_items(soup)
                if valorant_items:
                    print(f"    Detectada estructura Valorant")
                    return valorant_items
            
            # ESTRATEGIA BONOX STANDARD (Free Fire, Mobile Legends)
            # Buscar todos los botones que contengan precio
            buttons = soup.find_all('button')
            print(f"    Encontrados {len(buttons)} botones")
            
            for button in buttons:
                # Buscar precio en el botón
                price_divs = button.find_all('div', class_=re.compile(r'.*text-custom-bonoxsYellow.*'))
                if not price_divs:
                    continue
                
                price_text = price_divs[0].get_text(strip=True)
                price_match = re.search(r'S/\s*([\d,\.]+)', price_text)
                if not price_match:
                    continue
                
                price_str = price_match.group(1).replace(',', '.')
                try:
                    precio = float(price_str)
                except ValueError:
                    continue
                
                # Buscar nombre del item - puede ser en múltiples formatos
                item_name = None
                
                # Obtener todo el texto del botón
                button_text = button.get_text(" ", strip=True)
                # Limpiar espacios múltiples
                button_text = re.sub(r'\s+', ' ', button_text)
                
                # Formato 0: Simple "XXX Diamantes" (sin bonus explícito)
                # Buscar primero este patrón simple
                simple_diamond_match = re.search(r'^(\d+)\s+Diamantes\s*$|^(\d+)\s*$', button_text.split('S/')[0].strip())
                if not simple_diamond_match:
                    # Intentar extraer solo el número si es la primera palabra
                    first_part = button_text.split()[0] if button_text.split() else None
                    if first_part and first_part.isdigit():
                        simple_diamond_match = re.match(r'(\d+)', first_part)
                
                if simple_diamond_match:
                    total = int(simple_diamond_match.group(1) or simple_diamond_match.group(2))
                    item_name = self.calculate_diamond_name(total)
                    items.append({
                        "total": total,
                        "precio": precio,
                        "nombre": item_name
                    })
                    print(f"    ✅ {item_name} - S/ {precio}")
                    continue
                
                # Formato 1: "XXX Diamantes + YY Bonus" (con bonus explícito)
                if re.search(r'\d+\s+Diamantes.*\+\s*\d+\s+Bonus', button_text):
                    # Extraer solo la parte con diamantes
                    diamond_match = re.search(r'(\d+)\s+Diamantes\s*\+\s*(\d+)\s+Bonus', button_text)
                    if diamond_match:
                        total = int(diamond_match.group(1)) + int(diamond_match.group(2))
                        item_name = f"Diamond {diamond_match.group(1)} + {diamond_match.group(2)} Bonus"
                        items.append({
                            "total": total,
                            "precio": precio,
                            "nombre": item_name
                        })
                        print(f"    ✅ {item_name} - S/ {precio}")
                        continue
                
                # Formato 2: Combo con pase "XXX Diamantes + Pase"
                if "Diamantes" in button_text and "Pase" in button_text:
                    diamond_match = re.search(r'(\d+)\s+Diamantes\s*\+\s+Pase', button_text)
                    if diamond_match:
                        diamonds = int(diamond_match.group(1))
                        item_name = f"{diamonds} Diamantes + Pase"
                        items.append({
                            "total": 0,
                            "precio": precio,
                            "nombre": item_name
                        })
                        print(f"    ✅ {item_name} - S/ {precio}")
                        continue
                
                # Formato 3: Bono doble "XXX+XXX Diamantes"
                if re.search(r'\d+\+\d+\s+Diamantes', button_text):
                    bonus_match = re.search(r'(\d+)\+(\d+)\s+Diamantes', button_text)
                    if bonus_match:
                        part1 = int(bonus_match.group(1))
                        part2 = int(bonus_match.group(2))
                        item_name = f"{part1} + {part2} Diamantes (Bono Doble)"
                        items.append({
                            "total": 0,
                            "precio": precio,
                            "nombre": item_name
                        })
                        print(f"    ✅ {item_name} - S/ {precio}")
                        continue
                
                # Formato 4: Nombre textual (ej: "Paquete Semanal Élite", "Pase Semanal")
                # Extraer primera línea/sección que tenga texto
                # Separar por saltos de línea o "S/"
                parts = re.split(r'S/|RECOMENDADO|\n', button_text)
                if parts:
                    candidate = parts[0].strip()
                    # Limpiar de números puros y símbolos
                    if candidate and not re.match(r'^[\d\+\s\.]+$', candidate):
                        item_name = candidate
                        # Limitar a palabras razonables
                        if len(item_name) < 100 and len(item_name) > 2:
                            items.append({
                                "total": 0,
                                "precio": precio,
                                "nombre": item_name
                            })
                            print(f"    ✅ {item_name} - S/ {precio}")
                            continue
            
            if items:
                return items
            
            # Estrategia 2: Fallback - extracción por regex en el texto plano
            # Si el contenido está en JSON o en atributos HTML
            page_text = soup.get_text()
            
            # Buscar patrones "XXX Diamantes" y "S/ Y,YY"
            diamond_prices_pattern = r'(\d+)\s+Diamantes[^S]*S/\s*([\d,\.]+)'
            matches = re.findall(diamond_prices_pattern, page_text)
            
            if matches:
                print(f"    Encontrados {len(matches)} items por regex")
                for diamonds_str, price_str in matches:
                    try:
                        total = int(diamonds_str)
                        price = float(price_str.replace(',', '.'))
                        items.append({
                            "total": total,
                            "precio": price
                        })
                        print(f"    ✅ {total} Diamantes - S/ {price}")
                    except ValueError:
                        continue
            
            return items if items else None
            
        except Exception as e:
            print(f"    Error en extracción: {e}")
            return None
    
    def _extract_valorant_items(self, soup: BeautifulSoup) -> Optional[List[Dict]]:
        """
        Extrae items específicos de Valorant.
        
        Estructura Valorant:
        <button class="px-2 py-[2px] flex items-center...">
            <div class="flex flex-col w-full">
                <span class="text-[12px]">540VP</span>
                <span class="text-[#73ff9b] text-[9px]">S/ 18.00</span>
            </div>
        </button>
        """
        try:
            items = []
            
            # Buscar todos los botones
            buttons = soup.find_all('button')
            print(f"    Encontrados {len(buttons)} botones para Valorant")
            
            for button in buttons:
                # Buscar todos los spans dentro del botón
                spans = button.find_all('span')
                if len(spans) < 2:
                    continue
                
                # Primer span contiene el nombre del VP (540VP, 1035VP, etc)
                vp_text = spans[0].get_text(strip=True)
                
                # Segundo span contiene el precio (S/ 18.00)
                price_text = spans[1].get_text(strip=True)
                
                # Validar formato VP
                vp_match = re.search(r'(\d+)\s*VP', vp_text)
                if not vp_match:
                    continue
                
                # Extraer precio
                price_match = re.search(r'S/\s*([\d,\.]+)', price_text)
                if not price_match:
                    continue
                
                try:
                    price_str = price_match.group(1).replace(',', '.')
                    precio = float(price_str)
                    vp_value = int(vp_match.group(1))
                    
                    # El nombre del item es simplemente "XXXVP"
                    item_name = f"{vp_value}VP"
                    
                    items.append({
                        "total": 0,
                        "precio": precio,
                        "nombre": item_name
                    })
                    print(f"    ✅ {item_name} - S/ {precio}")
                    
                except ValueError:
                    continue
            
            return items if items else None
            
        except Exception as e:
            print(f"    Error extrayendo Valorant: {e}")
            return None


