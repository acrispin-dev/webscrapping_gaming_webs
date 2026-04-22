# 🚀 Flujo Automatizado de Scraping + Normalización

## Descripción General

El `main.py` ha sido actualizado para incluir la normalización de items Free Fire **automáticamente** después de:
1. Ejecutar todos los scrapers
2. Generar CSVs individuales por vendedor
3. Unificar en GAMING_SCRAPPING_FINAL.csv

Ahora **no necesitas ejecutar scripts separados**. Un solo comando hace todo:

```bash
python main.py
```

## Flujo de Ejecución

```
┌─────────────────────────────────────┐
│ 1. SCRAPING                         │
├─────────────────────────────────────┤
│ • Pagostore → Pagostore_output.csv  │
│ • Bonox → Bonox_output.csv          │
│ • Gamefan → Gamefan_output.csv      │
│ • Gamescenter → Gamescenter_out.csv │
│ • MTCGame → MTCGame_output.csv      │
│ • Codashop → Codashop_output.csv    │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ 2. UNIFICACIÓN                      │
├─────────────────────────────────────┤
│ Merge todos los CSVs → GAMING_SCRA  │
│ PPING_FINAL.csv (248 items)         │
└─────────────────────────────────────┘
          ↓
┌─────────────────────────────────────┐
│ 3. NORMALIZACIÓN (NUEVO)            │
├─────────────────────────────────────┤
│ Normaliza Free Fire items en:        │
│ • Todos los CSVs individuales       │
│ • GAMING_SCRAPPING_FINAL.csv        │
│                                     │
│ Reglas aplicadas:                   │
│ • Diamond X + Y Bonus (Pagostore)  │
│ • Diamantes X + Y Bonus (Gamefan)  │
│ • X Diamonds → Diamantes + bonus    │
│ • Ajuste de números terminados en 9 │
└─────────────────────────────────────┘
```

## Cambios Realizados a main.py

### 1. Nuevo Import
```python
from config import SITES_CONFIG, CSV_COLUMNS, get_output_filename, OUTPUT_DIR, normalize_freefire_item_name
```

### 2. Nueva Función `normalize_all_csv()`
- Normaliza todos los CSVs individuales de Free Fire
- Normaliza el archivo final GAMING_SCRAPPING_FINAL.csv
- Reporta número total de items normalizados

### 3. Integración en main()
```python
# Unificar todos los CSVs en uno solo
merge_all_csv()

# Normalizar items de Free Fire (NUEVO)
normalize_all_csv()
```

## Resultado Final

Cuando ejecutes `python main.py`, obtendrás:

```
======================================================
🕷️  GAMING PRICE SCRAPER - Control de Precios Gaming
======================================================
⏰ Fecha/Hora: 2026-04-22 13:29:21
📁 Directorio de salida: output

🔗 UNIFICANDO CSVs
======================================================
✅ Pagostore_output_pricing.csv: 6 items
✅ Bonox_output_pricing.csv: 91 items
... (otros vendedores)

📊 RESUMEN FINAL
────────────────────────────────────────────────────
Total de items unificados: 248
Desglose por vendedor:
  • Bonox: 91 items en 7 juego(s)
  • Codashop: 5 items en 1 juego(s)
  ... (otros vendedores)

✅ Archivo final guardado: GAMING_SCRAPPING_FINAL.csv
   Tamaño: 33.90 KB
   Filas: 248
   Columnas: 8

🔄 NORMALIZANDO ITEMS DE FREE FIRE
======================================================
✅ Pagostore_output_pricing.csv: 6 items normalizados
✅ Bonox_output_pricing.csv: 12 items normalizados
✅ Gamefan_output_pricing.csv: 8 items normalizados
✅ Gamescenter_output_pricing.csv: 15 items normalizados
✅ MTCGame_output_pricing.csv: 5 items normalizados
✅ Codashop_output_pricing.csv: 5 items normalizados
✅ GAMING_SCRAPPING_FINAL.csv: 51 items normalizados

📊 Total de items normalizados: 51
======================================================

✨ ¡Scraping completado exitosamente!
======================================================
```

## Ejemplo de Normalización Aplicada

### Antes (en raw CSV):
```
MTCGame,Free Fire,100 Diamonds,1.0,USD,...
Gamefan,Free Fire,310 diamantes,11.48,PEN,...
Bonox,Free Fire,Diamond 99 + 11 Bonus,3.51,PEN,...
```

### Después (normalizado):
```
MTCGame,Free Fire,Diamantes 100 + 10 Bonus,1.0,USD,...
Gamefan,Free Fire,Diamantes 310 + 31 Bonus,11.48,PEN,...
Bonox,Free Fire,Diamantes 100 + 10 Bonus,3.51,PEN,...
```

## Scripts Auxiliares (Opcionales)

Aunque todo está automatizado en main.py, puedes usar estos scripts si necesitas:

- `normalize_free_fire.py` - Normaliza solo los CSVs sin scrapear
- `merge_csvs_quick.py` - Unifica los CSVs sin scrapear
- `report_normalization.py` - Genera reporte de conformidad

## Ventajas de la Integración

✅ **Un solo comando**: `python main.py`
✅ **Automatización completa**: Scraping → Unificación → Normalización
✅ **Consistencia**: Todos los items Free Fire usan el mismo formato
✅ **Sin pasos manuales**: No necesitas ejecutar scripts separados
✅ **Auditabilidad**: Ve exactamente cuántos items fueron normalizados

## Ejecución Recomendada

```powershell
# Con UTF-8 para mejor visualización de caracteres especiales
$env:PYTHONIOENCODING='utf-8'
python main.py
```
