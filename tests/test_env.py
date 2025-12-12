#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速环境检查脚本"""

import sys
import os
import io

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("[ENV CHECK] Checking environment...")

# 1. Python 版本
print(f"[OK] Python version: {sys.version}")

# 2. 检查核心依赖
dependencies = {
    'requests': 'requests',
    'beautifulsoup4': 'bs4',
    'openai': 'openai',
    'moviepy': 'moviepy',
    'edge_tts': 'edge_tts',
    'dotenv': 'dotenv',
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn'
}

missing = []
for name, module in dependencies.items():
    try:
        __import__(module)
        print(f"[OK] {name}")
    except ImportError:
        print(f"[FAIL] {name} - not installed")
        missing.append(name)

if missing:
    print(f"\n[WARN] Missing dependencies: {', '.join(missing)}")
    print("Run: pip install -r requirements.txt")
else:
    print("\n[OK] All dependencies installed!")

# 3. 检查环境变量
import os
from dotenv import load_dotenv
load_dotenv()

env_vars = {
    'SCRAPERAPI_KEY': 'ScraperAPI key',
    'DEEPSEEK_API_KEY': 'DeepSeek API key'
}

print("\n[ENV VARS] Checking environment variables:")
for key, desc in env_vars.items():
    value = os.getenv(key)
    if value:
        # 只显示前4个字符，保护隐私
        masked = value[:4] + '...' if len(value) > 4 else '***'
        print(f"[OK] {key}: {masked}")
    else:
        print(f"[FAIL] {key}: not set ({desc})")

print("\n" + "="*50)
print("[DONE] Environment check completed!")