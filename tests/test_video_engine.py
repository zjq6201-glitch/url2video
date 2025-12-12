#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试视频生成模块"""

import sys
import os
import io
import asyncio

# 添加项目根目录到路径，以便导入 backend 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("TEST 3: Testing Video Engine Module")
print("="*60)

from backend.video_engine import create_video

# 模拟脚本数据（简化版，只测试1-2个场景）
test_script = {
    "script_lines": [
        {
            "scene_index": 1,
            "duration": "3s",
            "visual_description": "Product image with sparkle effect",
            "voiceover": "Introducing the amazing Ritz eyeshadow."
        },
        {
            "scene_index": 2,
            "duration": "3s",
            "visual_description": "Close-up of the product",
            "voiceover": "Supercharged sparkling color that lasts all day."
        }
    ]
}

# 测试图片URL（使用之前抓取到的）
test_images = [
    "https://cdn.shopify.com/s/files/1/1338/0845/files/Ritz.jpg?v=1715359129",
    "https://cdn.shopify.com/s/files/1/1338/0845/products/123371356185-Ritz-SSShadow.jpg"
]

print(f"\n[TEST] Testing video generation:")
print(f"  - Script lines: {len(test_script['script_lines'])}")
print(f"  - Images: {len(test_images)}")

async def test_video():
    try:
        result = await create_video(test_script, test_images)
        
        if result:
            print(f"\n[SUCCESS] Video generation successful!")
            print(f"  - Output file: {result}")
            
            import os
            if os.path.exists(result):
                file_size = os.path.getsize(result) / (1024 * 1024)  # MB
                print(f"  - File size: {file_size:.2f} MB")
                print(f"  - Full path: {os.path.abspath(result)}")
            else:
                print(f"  - [WARN] File not found at: {result}")
        else:
            print("\n[FAIL] Video generation returned None")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# 运行异步测试
asyncio.run(test_video())

print("\n" + "="*60)
print("[DONE] Test 3 completed!")
print("="*60)