#!/usr/bin/env python3
"""Test script to verify category_type is working correctly."""

from logic import match_symptoms_with_products
from service import decide

print("=" * 60)
print("Testing match_symptoms_with_products...")
print("=" * 60)

result = match_symptoms_with_products(['Sommeil'])
items = list(result.items())[:3]
for name, item in items:
    cat_type = item.get('category_type', 'N/A')
    score = item.get('score', 'N/A')
    print(f"✓ {name}: category_type={cat_type}, score={score}")

print("\n" + "=" * 60)
print("Testing service.decide...")
print("=" * 60)

result = decide(['Sommeil', 'Dépression'])
recommendations = result.get('recommendations', [])
print(f"Total recommendations: {len(recommendations)}")

# Group by category type
by_type = {}
for rec in recommendations:
    cat_type = rec.get('category_type', 'recommendation')
    if cat_type not in by_type:
        by_type[cat_type] = []
    by_type[cat_type].append(rec['produit'])

for cat_type, products in by_type.items():
    print(f"\n{cat_type}s: {len(products)} items")
    for prod in products[:2]:
        print(f"  - {prod}")
    if len(products) > 2:
        print(f"  ... and {len(products) - 2} more")
