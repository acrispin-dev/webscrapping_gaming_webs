#!/usr/bin/env python3
"""
Script para generar reporte de normalización de Free Fire items
"""
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("output")
csv_file = OUTPUT_DIR / "GAMING_SCRAPPING_FINAL.csv"

# Leer CSV
df = pd.read_csv(csv_file)

# Filtrar Free Fire
ff_items = df[df['juego'] == 'Free Fire'].copy()

print("=" * 80)
print("📊 REPORTE DE NORMALIZACIÓN DE FREE FIRE ITEMS")
print("=" * 80)
print(f"\n✅ Total de items de Free Fire: {len(ff_items)}")
print()

# Items normalizados
normalized = ff_items[ff_items['nombre_item'].str.contains('Diamantes.*Bonus', regex=True, case=False, na=False)]
print(f"✅ Items normalizados (Diamantes X + Y Bonus): {len(normalized)}")

# Items que NO deben normalizarse (pases, membresías, etc.)
non_diamonds = ff_items[~ff_items['nombre_item'].str.contains('diamante|diamond', regex=True, case=False, na=False)]
print(f"ℹ️  Items especiales (sin diamantes - pases/membresías): {len(non_diamonds)}")

# Items no normalizados que DEBERÍAN serlo
needs_normalization = ff_items[
    (~ff_items['nombre_item'].str.contains('Diamantes.*Bonus', regex=True, case=False, na=False)) &
    (ff_items['nombre_item'].str.contains('diamante|diamond', regex=True, case=False, na=False))
]
print(f"⚠️  Items que DEBERÍAN normalizarse: {len(needs_normalization)}")

print("\n" + "=" * 80)
print("📋 RESUMEN POR VENDEDOR")
print("=" * 80)

for seller in ff_items['seller'].unique():
    seller_items = ff_items[ff_items['seller'] == seller]
    normalized_seller = seller_items[seller_items['nombre_item'].str.contains('Diamantes.*Bonus', regex=True, case=False, na=False)]
    
    compliance = (len(normalized_seller) / len(seller_items) * 100) if len(seller_items) > 0 else 0
    status = "✅" if compliance == 100 else "⚠️" if compliance >= 75 else "❌"
    
    print(f"\n{status} {seller}: {len(normalized_seller)}/{len(seller_items)} items normalizados ({compliance:.0f}%)")
    
    if len(needs_normalization) > 0:
        needs = needs_normalization[needs_normalization['seller'] == seller]
        if len(needs) > 0:
            print(f"   Items pendientes:")
            for _, row in needs.iterrows():
                print(f"   • {row['nombre_item']}")

print("\n" + "=" * 80)
print("✨ Normalización completada")
print("=" * 80)
