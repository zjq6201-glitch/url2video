#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试网页抓取模块"""

import sys
import os
import io

# 添加项目根目录到路径，以便导入 backend 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("TEST 1: Testing Scraper Module")
print("="*60)

from backend.scraper import scrape_product

# 测试URL
test_url = "https://colourpop.com/products/ritz"
print(f"\n[TEST] Testing URL: {test_url}")

try:
    result = scrape_product(test_url)
    
    if result:
        print("\n[SUCCESS] Scraping successful!")
        print(f"  - Title: {result.get('title', 'N/A')}")
        print(f"  - Description length: {len(result.get('description', ''))}")
        print(f"  - Images count: {len(result.get('images', []))}")
        print(f"  - Source: {result.get('source', 'N/A')}")
        
        if result.get('images'):
            print(f"\n  First 3 image URLs:")
            for i, img_url in enumerate(result.get('images', [])[:3], 1):
                print(f"    {i}. {img_url[:80]}...")
    else:
        print("\n[FAIL] Scraping returned None")
        sys.exit(1)
        
except Exception as e:
    print(f"\n[ERROR] Exception occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("[DONE] Test 1 completed!")
print("="*60)