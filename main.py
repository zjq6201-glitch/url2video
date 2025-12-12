from backend.scraper import scrape_product
from backend.ai_director import generate_script
from backend.video_engine import create_video
import sys
import asyncio
import io

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    # 1. 获取用户输入
    # 如果命令行没参数，就用默认链接
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # 默认测试链接
        url = "https://colourpop.com/products/ritz"

    print("[START] Url2Video engine starting...")
    print(f"[URL] Target: {url}")

    # --- 第一步：抓取 ---
    print("\n[STEP 1] Scraping product data...")
    product_data = scrape_product(url)
    if not product_data:
        print("[ERROR] Failed to scrape product data")
        return

    # --- 第二步：写脚本 ---
    print("\n[STEP 2] Generating AI script...")
    script_data = generate_script(product_data)
    if not script_data:
        print("[ERROR] AI script generation failed")
        return

    # --- 第三步：生成视频 ---
    print("\n[STEP 3] Starting video rendering engine...")
    video_path = await create_video(script_data, product_data['images'])
    
    if video_path:
        print(f"\n[SUCCESS] Video generated successfully!")
        print(f"[OUTPUT] File: {video_path}")
    else:
        print("\n[ERROR] Video generation failed")

if __name__ == "__main__":
    asyncio.run(main())