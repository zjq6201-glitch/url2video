from backend.scraper import scrape_product
from backend.ai_director import generate_script
from backend.video_engine import create_video
import sys
import asyncio

async def main():
    # 1. 获取用户输入
    # 如果命令行没参数，就用默认链接
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # 默认测试链接
        url = "https://colourpop.com/products/ritz"

    print("🚀 Url2Video 引擎启动...")
    print(f"🔗 目标链接: {url}")

    # --- 第一步：抓取 ---
    product_data = scrape_product(url)
    if not product_data:
        print("❌ 终止：无法抓取产品数据")
        return

    # --- 第二步：写脚本 ---
    script_data = generate_script(product_data)
    if not script_data:
        print("❌ 终止：AI 脚本生成失败")
        return

    # --- 第三步：生成视频 ---
    print("\n🎬 剧本已就绪，正在转交视频渲染引擎...")
    await create_video(script_data, product_data['images']) # 这里加 await

if __name__ == "__main__":
    asyncio.run(main())