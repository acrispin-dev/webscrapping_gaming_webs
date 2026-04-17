#!/usr/bin/env python3
"""
Script rápido para unificar todos los CSVs sin ejecutar los scrapers
"""
import sys
import os
from pathlib import Path
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import OUTPUT_DIR

print("=" * 70)
print("🔗 UNIFICANDO CSVs - GAMING_SCRAPPING_FINAL")
print("=" * 70)

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
    
    print(f"\n" + "=" * 70)
    print(f"📊 RESUMEN FINAL")
    print("=" * 70)
    print(f"\nTotal de items unificados: {len(final_df)}")
    print(f"\nDesglose por vendedor:")
    
    for seller in sorted(final_df['seller'].unique()):
        seller_data = final_df[final_df['seller'] == seller]
        count = len(seller_data)
        games = seller_data['juego'].nunique()
        print(f"  • {seller}: {count} items en {games} juego(s)")
    
    print(f"\n✅ Archivo final guardado: {final_file}")
    print(f"   Tamaño: {final_file.stat().st_size / 1024:.2f} KB")
    print(f"   Filas: {len(final_df)}")
    print(f"   Columnas: {len(final_df.columns)}")
    
    # Mostrar primeros 5 items
    print(f"\n📋 Primeros 5 items del archivo unificado:")
    for idx, (_, row) in enumerate(final_df.head(5).iterrows(), 1):
        print(f"   {idx}. [{row['seller']}] {row['juego']}: {row['nombre_item']} - {row['precio']} {row['moneda']}")
else:
    print("\n❌ No se encontraron archivos CSV para unificar")
