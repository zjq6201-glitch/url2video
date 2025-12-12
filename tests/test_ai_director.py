#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试AI脚本生成模块"""

import sys
import os
import io

# 添加项目根目录到路径，以便导入 backend 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("TEST 2: Testing AI Director Module")
print("="*60)

from backend.ai_director import generate_script

# 模拟产品数据
test_product = {
    "title": "Ritz",
    "description": "Our famous OG crème-to-powder formula delivers supercharged sparkling colour with minimal creasing, fading or fallout."
}

print(f"\n[TEST] Testing with product:")
print(f"  - Title: {test_product['title']}")
print(f"  - Description: {test_product['description']}")

try:
    result = generate_script(test_product)
    
    if result:
        print("\n[SUCCESS] Script generation successful!")
        script_lines = result.get('script_lines', [])
        print(f"  - Script lines count: {len(script_lines)}")
        
        if script_lines:
            print(f"\n  First script line preview:")
            first_line = script_lines[0]
            print(f"    Scene: {first_line.get('scene_index', 'N/A')}")
            print(f"    Duration: {first_line.get('duration', 'N/A')}")
            print(f"    Voiceover: {first_line.get('voiceover', 'N/A')[:60]}...")
            print(f"    Visual: {first_line.get('visual_description', 'N/A')[:60]}...")
    else:
        print("\n[FAIL] Script generation returned None")
        sys.exit(1)
        
except Exception as e:
    print(f"\n[ERROR] Exception occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("[DONE] Test 2 completed!")
print("="*60)