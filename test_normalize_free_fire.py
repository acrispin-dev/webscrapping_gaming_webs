#!/usr/bin/env python3
"""
Test para verificar la función de normalización de Free Fire
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import normalize_freefire_item_name

print("=" * 70)
print("✅ TEST: Normalización de Free Fire Items")
print("=" * 70)

test_cases = [
    # (input, expected_output, description)
    ("Diamond 99 + 11 Bonus", "Diamantes 100 + 10 Bonus", "Bonox: termina en 9, debe ajustar"),
    ("Diamond 199 + 21 Bonus", "Diamantes 200 + 20 Bonus", "Bonox: termina en 9, debe ajustar"),
    ("Diamond 100 + 10 Bonus", "Diamantes 100 + 10 Bonus", "Pagostore: no termina en 9"),
    ("Diamond 1579 + 159 Bonus", "Diamantes 1580 + 158 Bonus", "Bonox: termina en 9, debe ajustar"),
    ("100 diamantes", "Diamantes 100 + 10 Bonus", "Gamefan: agregar 10% bonus"),
    ("310 diamantes", "Diamantes 310 + 31 Bonus", "Gamefan: agregar 10% bonus"),
    ("520 diamantes", "Diamantes 520 + 52 Bonus", "Gamefan: agregar 10% bonus"),
    ("1060 diamantes", "Diamantes 1060 + 106 Bonus", "Gamefan: agregar 10% bonus"),
    ("2180 diamantes", "Diamantes 2180 + 218 Bonus", "Gamefan: agregar 10% bonus"),
    ("5600 diamantes", "Diamantes 5600 + 560 Bonus", "Gamefan: agregar 10% bonus"),
    ("310 diamantes + 31 Bonus", "Diamantes 310 + 31 Bonus", "Gamescenter: ya con bonus"),
    ("520 Diamantes + 52 Bonus", "Diamantes 520 + 52 Bonus", "Gamescenter: ya con bonus"),
    ("310 diamantes + 31 Bonus", "Diamantes 310 + 31 Bonus", "Codashop: ya normalizado"),
    ("Tarjeta Semanal", "Tarjeta Semanal", "Bonox: pase, no tiene diamante"),
    ("Paquete Mensual Épico", "Paquete Mensual Épico", "Bonox: paquete, no tiene diamante"),
    ("100 Diamonds", "Diamantes 100 + 10 Bonus", "MTCGame: agregar 10% bonus"),
    ("210 Diamonds", "Diamantes 210 + 21 Bonus", "MTCGame: agregar 10% bonus"),
    ("530 Diamonds", "Diamantes 530 + 53 Bonus", "MTCGame: agregar 10% bonus"),
    ("1080 Diamonds", "Diamantes 1080 + 108 Bonus", "MTCGame: agregar 10% bonus"),
    ("2200 Diamonds", "Diamantes 2200 + 220 Bonus", "MTCGame: agregar 10% bonus"),
]

all_passed = True

for input_val, expected, description in test_cases:
    result = normalize_freefire_item_name(input_val)
    passed = result == expected
    status = "✅" if passed else "❌"
    
    print(f"\n{status} {description}")
    print(f"   Input:    '{input_val}'")
    print(f"   Expected: '{expected}'")
    print(f"   Got:      '{result}'")
    
    if not passed:
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print("✨ Todos los tests pasaron correctamente!")
else:
    print("⚠️  Algunos tests fallaron")
print("=" * 70)
