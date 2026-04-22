"""
Configuración centralizada del proyecto de web scraping
"""
import os
from pathlib import Path
from datetime import datetime

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
SCRAPERS_DIR = PROJECT_ROOT / "scrapers"

# Crear directorio de output si no existe
OUTPUT_DIR.mkdir(exist_ok=True)

# Configuración de User-Agent para requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Configuración de timeouts
REQUEST_TIMEOUT = 10

# Sitios web a scrapear
SITES_CONFIG = {
    "pagostore": {
        "url_base": "https://pagostore.garena.com/",
        "games": {
            "free_fire": {
                "item_ids": list(range(17992, 17998)),  # 17992 a 17997
                "game_name": "Free Fire"
            }
        }
    },
    "bonox": {
        "games": {
            "free_fire": {
                "item_ids": [],  # Bonox extrae automáticamente todos los items de la página
                "game_name": "Free Fire",
                "url": "https://bonoxs.com/pe/free-fire-pe?from=store"
            },
            "mobile_legends": {
                "item_ids": [],  # Bonox extrae automáticamente todos los items de la página
                "game_name": "Mobile Legends",
                "url": "https://bonoxs.com/pe/mobile-legends-br?from=store"
            },
            "valorant": {
                "item_ids": [],  # Bonox extrae automáticamente todos los items de la página
                "game_name": "Valorant",
                "url": "https://bonoxs.com/pe/valorant-pe?from=store"
            },
            "wild_rift": {
                "item_ids": [],  # Bonox extrae automáticamente todos los items de la página
                "game_name": "League of Legends: Wild Rift",
                "url": "https://bonoxs.com/pe/wild-rift-pe?from=store"
            },
            "blood_strike": {
                "item_ids": [],  # Bonox extrae automáticamente todos los items de la página
                "game_name": "Blood Strike",
                "url": "https://bonoxs.com/pe/blood-strike-ww?from=store"
            },
            "roblox": {
                "item_ids": [],
                "game_name": "Roblox",
                "url": "https://bonoxs.com/pe/roblox-la?from=store"
            },
            "marvel_rivals": {
                "item_ids": [],
                "game_name": "Marvel Rivals",
                "url": "https://bonoxs.com/pe/marvel-rivals-ww?from=store"
            }
        }
    },
    "gamefan": {
        "base_url": "https://gamefan.la",
        "games": {
            "free_fire": {
                "game_name": "Free Fire",
                "url": "https://gamefan.la/pe/juegos/freefire"
            },
            "league_of_legends": {
                "game_name": "League of Legends",
                "url": "https://gamefan.la/pe/recargar/riot%20points"
            },
            "valorant": {
                "game_name": "Valorant",
                "url": "https://gamefan.la/pe/juegos/valorant"
            },
            "roblox": {
                "game_name": "Roblox",
                "url": "https://gamefan.la/pe/juegos/roblox"
            }
        }
    },
    "gamescenter": {
        "base_url": "https://gamescenter.pe",
        "games": {
            "free_fire": {
                "game_name": "Free Fire",
                "url": "https://gamescenter.pe/categoria-producto/free-fire-diamantes/"
            },
            "roblox": {
                "game_name": "Roblox",
                "url": [
                    "https://gamescenter.pe/categoria-producto/roblox-robux/",
                    "https://gamescenter.pe/categoria-producto/roblox-robux/page/2/"
                ]
            },
            "blood_strike": {
                "game_name": "Blood Strike",
                "url": "https://gamescenter.pe/categoria-producto/recargas/blood-strike/"
            },
            "genshin_impact": {
                "game_name": "Genshin Impact",
                "url": "https://gamescenter.pe/categoria-producto/recargas/genshin-impact/"
            },
            "wild_rift": {
                "game_name": "League of Legends: Wild Rift",
                "url": "https://gamescenter.pe/categoria-producto/recargas/league-of-legends-wild-rift/"
            }
        }
    },
    "mtcgame": {
        "base_url": "https://www.mtcgame.com",
        "games": {
            "free_fire": {
                "game_name": "Free Fire",
                "url": "https://www.mtcgame.com/garena/free-fire-garena-diamond-top-up"
            },
            "mobile_legends": {
                "game_name": "Mobile Legends",
                "url": "https://www.mtcgame.com/moonton/mobile-legends-bang-bang-diamond-top-up"
            },
            "roblox": {
                "game_name": "Roblox",
                "url": "https://www.mtcgame.com/roblox-gift-card/roblox-robux-gift-cards-global"
            },
            "valorant": {
                "game_name": "Valorant",
                "url": "https://www.mtcgame.com/riot/valorant-points-vp-gift-card-latam-store"
            },
            "league_of_legends": {
                "game_name": "League of Legends",
                "url": "https://www.mtcgame.com/riot-points-league-of-legends/latin-america-north-south"
            }
        }
    },
    "codashop": {
        "base_url": "https://www.codashop.com",
        "games": {
            "free_fire": {
                "game_name": "Free Fire",
                "url": "https://www.codashop.com/es-pe/free-fire"
            }
        }
    }
}

# Configuración de CSV
CSV_COLUMNS = ["seller", "juego", "nombre_item", "precio", "moneda", 
               "disponible", "url_producto", "fecha_scrapping"]

def get_output_filename(seller: str, game: str = None) -> str:
    """Genera nombre de archivo CSV"""
    return f"{seller}_output_pricing.csv"


def normalize_freefire_item_name(nombre_item: str, seller: str = None) -> str:
    """
    Normaliza los nombres de items de Free Fire para todos los vendedores.
    
    Reglas:
    1. Si NO contiene "diamante" o "diamond" (pases, membresías, etc.), devuelve el nombre tal cual
    2. Si contiene "diamante/diamond", normaliza a formato "Diamantes {base} + {bonus} Bonus"
    3. Si termina en 9, aumenta 1 y reduce bonus en 1
    
    Args:
        nombre_item: Nombre del item a normalizar
        seller: Nombre del vendedor (opcional, para lógica específica por vendor)
    
    Returns:
        Nombre normalizado del item
    """
    import re
    
    # Si no contiene "diamante" ni "diamond", devolver tal cual
    if 'diamante' not in nombre_item.lower() and 'diamond' not in nombre_item.lower():
        return nombre_item
    
    base = None
    bonus = None
    
    # Patrón 1: "Diamond X + Y Bonus" (Pagostore, Bonox con formato completo)
    match = re.search(r'[Dd]iamond\s+(\d+)\s*\+\s*(\d+)\s*[Bb]onus', nombre_item)
    if match:
        base = int(match.group(1))
        bonus = int(match.group(2))
    
    # Patrón 2: "X diamantes + Y Bonus" (Gamescenter)
    if base is None:
        match = re.search(r'(\d+)\s+diamantes?\s*\+\s*(\d+)\s*[Bb]onus', nombre_item, re.IGNORECASE)
        if match:
            base = int(match.group(1))
            bonus = int(match.group(2))
    
    # Patrón 3: "Diamond X Y Bonus" (sin +)
    if base is None:
        match = re.search(r'[Dd]iamond\s+(\d+)\s+(\d+)\s*[Bb]onus', nombre_item)
        if match:
            base = int(match.group(1))
            bonus = int(match.group(2))
    
    # Patrón 4: "X diamantes + Y Bonus" (variable)
    if base is None:
        match = re.search(r'(\d+)\s+diamantes?\s+(\d+)\s*[Bb]onus', nombre_item, re.IGNORECASE)
        if match:
            base = int(match.group(1))
            bonus = int(match.group(2))
    
    # Patrón 5: Solo número (ej: "100 diamantes" de Gamefan)
    if base is None:
        match = re.search(r'^(\d+)\s*diamantes', nombre_item, re.IGNORECASE)
        if match:
            base = int(match.group(1))
            bonus = int(base * 0.1)
    
    # Patrón 6: "X Diamonds" sin bonus (ej: "100 Diamonds" de MTCGame)
    if base is None:
        match = re.search(r'^(\d+)\s*[Dd]iamonds?$', nombre_item)
        if match:
            base = int(match.group(1))
            bonus = int(base * 0.1)
    
    # Si extrajimos base y bonus, normalizar
    if base is not None and bonus is not None:
        # Aplicar regla: si termina en 9, aumentar base y restar bonus
        if base % 10 == 9:
            base += 1
            bonus = max(0, bonus - 1)
        
        return f"Diamantes {base} + {bonus} Bonus"
    
    # Si no coincide ningún patrón, devolver tal cual
    return nombre_item
