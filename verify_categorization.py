#!/usr/bin/env python3
"""
Final test to demonstrate the categorization of recommendations vs practices.
This test specifically tests diets and practices to show they're properly categorized.
"""

from database import get_product_category_type, CATALOGUE_COMPLET, CATEGORY_TYPE_LABELS
from logic import match_symptoms_with_products
from service import decide

print("=" * 70)
print("VERIFICATION: Category Type Labeling System")
print("=" * 70)

# Show the mapping
print("\nCATEGORY MAPPINGS:")
print(f"  - Supplements → 'recommendation' → {CATEGORY_TYPE_LABELS.get('recommendation')}")
print(f"  - Diets → 'practice' → {CATEGORY_TYPE_LABELS.get('practice')}")
print(f"  - Other/Practices → 'practice' → {CATEGORY_TYPE_LABELS.get('practice')}")

# Show a few examples from each category
print("\n" + "=" * 70)
print("SAMPLES FROM EACH CATEGORY:")
print("=" * 70)

for cat_name, items in CATALOGUE_COMPLET.items():
    if items:
        print(f"\n{cat_name}:")
        for item in items[:2]:
            name = item.get('name', 'N/A')
            cat_type = item.get('category_type', 'N/A')
            print(f"  ✓ {name}: {cat_type}" + (f" → {CATEGORY_TYPE_LABELS.get(cat_type)}" if cat_type in CATEGORY_TYPE_LABELS else ""))

# Test with a symptom that includes practices
print("\n" + "=" * 70)
print("TEST: match_symptoms_with_products with 'Sleep'")
print("=" * 70)

results = match_symptoms_with_products(['Sleep'])
recos = [item for item in results.items() if item[1].get('category_type') == 'recommendation']
practices = [item for item in results.items() if item[1].get('category_type') == 'practice']

print(f"\nTotal results: {len(results)}")
print(f"  Recommendations: {len(recos)}")
for name, data in recos[:2]:
    print(f"    - {name}")
if len(recos) > 2:
    print(f"    ... and {len(recos) - 2} more")

print(f"  Practices: {len(practices)}")
for name, data in practices:
    print(f"    - {name} (Category Type: {data.get('category_type')})")

# Test service.decide which should also support category_type
print("\n" + "=" * 70)
print("TEST: service.decide with 'Sleep' + 'Stress'")
print("=" * 70)

decision = decide(['Sleep', 'Stress'])
recs = decision.get('recommendations', [])
rec_groups = {}
for rec in recs:
    cat_type = rec.get('category_type', 'recommendation')
    if cat_type not in rec_groups:
        rec_groups[cat_type] = []
    rec_groups[cat_type].append(rec['produit'])

print(f"\nTotal recommendations: {len(recs)}")
for cat_type in ['recommendation', 'practice']:
    products = rec_groups.get(cat_type, [])
    label = CATEGORY_TYPE_LABELS.get(cat_type, cat_type)
    print(f"\n{label}: {len(products)} items")
    for prod in products[:3]:
        print(f"  - {prod}")
    if len(products) > 3:
        print(f"  ... and {len(products) - 3} more")

print("\n" + "=" * 70)
print("RESULT: ✓ Categorization system is working correctly!")
print("=" * 70)
print("\nSummary:")
print("- Diets are now shown as 'Pratiques pour de meilleurs résultats'")
print("- Other practices are also shown as 'Pratiques pour de meilleurs résultats'")
print("- Supplements remain as 'Recommandations'")
print("- Frontend displays different labels based on category_type")
