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
from scrapers.mtcgame_scraper import MTCGameScraper


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


def scrape_mtcgame() -> None:
    """Ejecuta el scraping de MTCGame - Extrae automáticamente todos los items de múltiples juegos"""
    config = SITES_CONFIG["mtcgame"]
    all_data = []
    
    for game_key, game_config in config["games"].items():
        game_name = game_config["game_name"]
        game_url = game_config["url"]
        
        # Crear scraper con URL específica del juego
        scraper = MTCGameScraper(url=game_url)
        
        # Ejecutar scraping - MTCGame extrae automáticamente todos los items
        data = scraper.scrape_game(game_name)
        
        # Acumular datos de todos los juegos
        if data:
            all_data.extend(data)
    
    # Guardar todos los datos en un solo CSV
    if all_data:
        save_to_csv(all_data, "MTCGame", "Todos")


def merge_all_csv() -> None:
    """
    Unifica todos los CSVs de los diferentes vendedores en un solo archivo
    Nombre del archivo final: GAMING_SCRAPPING_FINAL.csv
    """
    print("\n" + "=" * 60)
    print("🔗 UNIFICANDO CSVs")
    print("=" * 60)
    
    all_data = []
    seller_files = [
        "Pagostore_output_pricing.csv",
        "Bonox_output_pricing.csv",
        "Gamefan_output_pricing.csv",
        "Gamescenter_output_pricing.csv",
        "MTCGame_output_pricing.csv"
    ]
    
    # Leer cada CSV y acumular datos
    for filename in seller_files:
        filepath = OUTPUT_DIR / filename
        
        if filepath.exists():
            try:
                df = pd.read_csv(filepath, encoding="utf-8")
                all_data.append(df)
                print(f"✅ {filename}: {len(df)} items")
            except Exception as e:
                print(f"⚠️  Error leyendo {filename}: {e}")
        else:
            print(f"⚠️  {filename} no encontrado")
    
    # Combinar todos los datos
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        
        # Ordenar por vendedor y juego
        final_df = final_df.sort_values(['seller', 'juego', 'nombre_item'])
        
        # Guardar archivo final
        final_file = OUTPUT_DIR / "GAMING_SCRAPPING_FINAL.csv"
        final_df.to_csv(final_file, index=False, encoding="utf-8")
        
        print(f"\n📊 RESUMEN FINAL")
        print(f"{'─' * 60}")
        print(f"Total de items unificados: {len(final_df)}")
        print(f"\nDesglose por vendedor:")
        for seller in sorted(final_df['seller'].unique()):
            count = len(final_df[final_df['seller'] == seller])
            games = final_df[final_df['seller'] == seller]['juego'].nunique()
            print(f"  • {seller}: {count} items en {games} juego(s)")
        
        print(f"\n✅ Archivo final guardado: {final_file}")
        print(f"   Tamaño: {final_file.stat().st_size / 1024:.2f} KB")
        print(f"   Filas: {len(final_df)}")
        print(f"   Columnas: {len(final_df.columns)}")
    else:
        print("\n❌ No se encontraron archivos CSV para unificar")


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
        scrape_mtcgame()
        
        # Unificar todos los CSVs en uno solo
        merge_all_csv()
        
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
