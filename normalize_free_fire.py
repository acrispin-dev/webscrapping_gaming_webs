#!/usr/bin/env python3
"""
Script para normalizar los nombres de items de Free Fire en todos los CSVs
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUT_DIR, normalize_freefire_item_name

print("=" * 70)
print("🔄 NORMALIZANDO NAMES DE FREE FIRE EN TODOS LOS CSVs")
print("=" * 70)

seller_files = [
    "Pagostore_output_pricing.csv",
    "Bonox_output_pricing.csv",
    "Gamefan_output_pricing.csv",
    "Gamescenter_output_pricing.csv",
    "MTCGame_output_pricing.csv",
    "Codashop_output_pricing.csv"
]

for filename in seller_files:
    filepath = OUTPUT_DIR / filename
    
    if not filepath.exists():
        print(f"\n⚠️  {filename} no encontrado, saltando...")
        continue
    
    try:
        # Leer CSV
        df = pd.read_csv(filepath, encoding="utf-8")
        
        # Extraer seller del nombre del archivo
        seller = filename.replace("_output_pricing.csv", "")
        
        print(f"\n📄 Procesando {filename}...")
        print(f"   Total de filas: {len(df)}")
        
        # Normalizar solo items de Free Fire
        df_modified = df.copy()
        
        # Aplicar normalización a items de Free Fire
        mask = df_modified['juego'] == 'Free Fire'
        if mask.any():
            print(f"   Items de Free Fire encontrados: {mask.sum()}")
            
            # Normalizar nombres
            df_modified.loc[mask, 'nombre_item'] = df_modified.loc[mask, 'nombre_item'].apply(
                lambda x: normalize_freefire_item_name(x, seller)
            )
            
            # Mostrar cambios
            changed = (df.loc[mask, 'nombre_item'] != df_modified.loc[mask, 'nombre_item']).sum()
            if changed > 0:
                print(f"   ✅ {changed} items normalizados")
                
                # Mostrar ejemplos de antes y después
                print(f"\n   Ejemplos de normalización:")
                for idx in df_modified[mask].index[:3]:
                    before = df.loc[idx, 'nombre_item']
                    after = df_modified.loc[idx, 'nombre_item']
                    if before != after:
                        print(f"     • '{before}' → '{after}'")
            else:
                print(f"   ℹ️  Todos los items ya están normalizados")
        else:
            print(f"   ℹ️  No hay items de Free Fire en este archivo")
        
        # Guardar CSV actualizado
        df_modified.to_csv(filepath, index=False, encoding="utf-8")
        print(f"   💾 CSV actualizado correctamente")
        
    except Exception as e:
        print(f"   ❌ Error procesando {filename}: {e}")

print(f"\n" + "=" * 70)
print("✨ Normalización completada")
print("=" * 70)
