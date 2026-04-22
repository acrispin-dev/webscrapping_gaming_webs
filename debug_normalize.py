#!/usr/bin/env python3
"""
Debug script para verificar la función de normalización
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import normalize_freefire_item_name

test_cases = [
    "Diamond 99 + 11 Bonus",
    "Diamond 100 + 10 Bonus",
    "Diamond 1579 + 159 Bonus",
    "100 diamantes",
]

for test in test_cases:
    result = normalize_freefire_item_name(test)
    print(f"Input:  '{test}'")
    print(f"Output: '{result}'")
    print()
