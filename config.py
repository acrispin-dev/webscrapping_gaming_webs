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
                "url": "https://gamescenter.pe/categoria-producto/roblox-robux/"
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
