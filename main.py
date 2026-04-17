"""
Script principal para ejecutar el web scraping de tiendas gaming
Coordina la ejecución de todos los scrapers y genera archivos CSV con los resultados
"""
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Importar configuración
from config import SITES_CONFIG, CSV_COLUMNS, get_output_filename, OUTPUT_DIR

# Importar scrapers
from scrapers.pagostore_scraper import PagostoreScraper
from scrapers.bonox_scraper import BonoxScraper
from scrapers.gamefan_scraper import GamefanScraper
from scrapers.gamescenter_scraper import GamescenterScraper


def save_to_csv(data: list, seller: str, game: str) -> None:
    """
    Guarda los datos en un archivo CSV
    
    Args:
        data: Lista de diccionarios con los datos a guardar
        seller: Nombre del vendedor
        game: Nombre del juego
    """
    if not data:
        print(f"⚠️  No hay datos para guardar ({seller} - {game})")
        return
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Asegurar que todas las columnas estén presentes en el orden correcto
    df = df.reindex(columns=CSV_COLUMNS, fill_value="N/A")
    
    # Generar nombre del archivo
    filename = get_output_filename(seller, game)
    filepath = OUTPUT_DIR / filename
    
    # Guardar CSV
    df.to_csv(filepath, index=False, encoding="utf-8")
    
    print(f"💾 Archivo guardado: {filepath}")
    print(f"   Registros: {len(df)}")


def scrape_pagostore() -> None:
    """Ejecuta el scraping de Pagostore"""
    scraper = PagostoreScraper()
    config = SITES_CONFIG["pagostore"]
    
    for game_key, game_config in config["games"].items():
        game_name = game_config["game_name"]
        item_ids = game_config["item_ids"]
        
        # Ejecutar scraping
        data = scraper.scrape_game(game_name, item_ids)
        
        # Guardar en CSV
        if data:
            save_to_csv(data, scraper.seller, game_name)


def scrape_bonox() -> None:
    """Ejecuta el scraping de Bonox - Extrae automáticamente todos los items de múltiples juegos"""
    config = SITES_CONFIG["bonox"]
    all_data = []
    
    for game_key, game_config in config["games"].items():
        game_name = game_config["game_name"]
        game_url = game_config["url"]
        
        # Crear scraper con URL específica del juego
        scraper = BonoxScraper(url=game_url)
        
        # Ejecutar scraping - Bonox extrae automáticamente todos los items
        data = scraper.scrape_game(game_name)
        
        # Acumular datos de todos los juegos
        if data:
            all_data.extend(data)
    
    # Guardar todos los datos en un solo CSV
    if all_data:
        save_to_csv(all_data, "Bonox", "Todos")


def scrape_gamefan() -> None:
    """Ejecuta el scraping de Gamefan - Extrae automáticamente todos los items de múltiples juegos"""
    config = SITES_CONFIG["gamefan"]
    all_data = []
    
    for game_key, game_config in config["games"].items():
        game_name = game_config["game_name"]
        game_url = game_config["url"]
        
        # Crear scraper con URL específica del juego
        scraper = GamefanScraper(base_url=config["base_url"], url=game_url)
        
        # Ejecutar scraping - Gamefan extrae automáticamente todos los items
        data = scraper.scrape_game(game_name)
        
        # Acumular datos de todos los juegos
        if data:
            all_data.extend(data)
    
    # Guardar todos los datos en un solo CSV
    if all_data:
        save_to_csv(all_data, "Gamefan", "Todos")


def scrape_gamescenter() -> None:
    """Ejecuta el scraping de Gamescenter - Extrae automáticamente todos los items de múltiples juegos"""
    config = SITES_CONFIG["gamescenter"]
    all_data = []
    
    for game_key, game_config in config["games"].items():
        game_name = game_config["game_name"]
        game_url = game_config["url"]
        
        # Crear scraper con URL específica del juego
        scraper = GamescenterScraper(url=game_url)
        
        # Ejecutar scraping - Gamescenter extrae automáticamente todos los items
        data = scraper.scrape_game(game_name)
        
        # Acumular datos de todos los juegos
        if data:
            all_data.extend(data)
    
    # Guardar todos los datos en un solo CSV
    if all_data:
        save_to_csv(all_data, "Gamescenter", "Todos")


def main():
    """Función principal que coordina todo el scraping"""
    print("=" * 60)
    print("🕷️  GAMING PRICE SCRAPER - Control de Precios Gaming")
    print("=" * 60)
    print(f"⏰ Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Directorio de salida: {OUTPUT_DIR}")
    print()
    
    try:
        # Ejecutar scrapers
        scrape_pagostore()
        scrape_bonox()
        scrape_gamefan()
        scrape_gamescenter()
        
        print()
        print("=" * 60)
        print("✨ ¡Scraping completado exitosamente!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error durante el scraping: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
