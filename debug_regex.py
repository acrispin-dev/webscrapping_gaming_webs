#!/usr/bin/env python3
"""
Debug script para verificar regex patterns
"""
import re

test_string = "Diamond 99 + 11 Bonus"

# Patrón 1
pattern1 = r'[Dd]iamond\s+(\d+)\s*\+\s*(\d+)\s*[Bb]onus'
match1 = re.search(pattern1, test_string)
print(f"Pattern 1: {pattern1}")
print(f"Test string: '{test_string}'")
print(f"Match 1: {match1}")
if match1:
    print(f"  Group 1: {match1.group(1)}")
    print(f"  Group 2: {match1.group(2)}")
print()

# Más simple
pattern2 = r'(\d+)\s*\+\s*(\d+)'
match2 = re.search(pattern2, test_string)
print(f"Pattern 2: {pattern2}")
print(f"Match 2: {match2}")
if match2:
    print(f"  Group 1: {match2.group(1)}")
    print(f"  Group 2: {match2.group(2)}")
print()

# Test con Pagostore
test_string2 = "Diamond 100 + 10 Bonus"
print(f"\nTest string 2: '{test_string2}'")
match3 = re.search(pattern1, test_string2)
print(f"Pattern 1 Match: {match3}")
if match3:
    print(f"  Group 1: {match3.group(1)}")
    print(f"  Group 2: {match3.group(2)}")
