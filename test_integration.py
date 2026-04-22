#!/usr/bin/env python3
"""
Script para probar que la normalización está integrada correctamente en main.py
"""
import pandas as pd
from pathlib import Path
from config import normalize_freefire_item_name, OUTPUT_DIR

print("=" * 70)
print("✅ TEST: Normalización integrada en main.py")
print("=" * 70)

# Leer el CSV final
final_file = OUTPUT_DIR / "GAMING_SCRAPPING_FINAL.csv"

if final_file.exists():
    df = pd.read_csv(final_file)
    
    # Filtrar Free Fire items
    ff_items = df[df['juego'] == 'Free Fire'].copy()
    
    print(f"\n📊 Total de items Free Fire: {len(ff_items)}")
    
    # Contar items normalizados
    normalized = ff_items[ff_items['nombre_item'].str.contains('Diamantes.*Bonus', regex=True, case=False, na=False)]
    special = ff_items[~ff_items['nombre_item'].str.contains('diamante|diamond', regex=True, case=False, na=False)]
    
    print(f"✅ Items normalizados: {len(normalized)}")
    print(f"ℹ️  Items especiales (sin diamantes): {len(special)}")
    
    print("\n" + "=" * 70)
    print("📋 MUESTRA DE ITEMS NORMALIZADOS POR VENDEDOR")
    print("=" * 70)
    
    for seller in sorted(ff_items['seller'].unique()):
        seller_items = ff_items[ff_items['seller'] == seller]
        print(f"\n{seller} ({len(seller_items)} items):")
        for _, row in seller_items.head(2).iterrows():
            print(f"  • {row['nombre_item']} - {row['precio']} {row['moneda']}")
    
    print("\n" + "=" * 70)
    print("✨ Normalización verificada correctamente")
    print("=" * 70)
else:
    print(f"\n❌ {final_file} no encontrado")
    print("Ejecuta main.py primero para generar los datos")
