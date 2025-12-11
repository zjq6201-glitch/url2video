import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 引入我们写好的核心逻辑
from backend.scraper import scrape_product
from backend.ai_director import generate_script
from backend.video_engine import create_video

app = FastAPI()

# 允许跨域 (防止前端报错)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 prototype 文件夹，这样才能访问 index.html 里的 css/js (如果有的话)
# 但目前我们直接读取文件返回
PROTOTYPE_DIR = "prototype"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """当用户访问 http://127.0.0.1:8000 时，显示 index.html"""
    with open(os.path.join(PROTOTYPE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/pricing.html", response_class=HTMLResponse)
async def read_pricing():
    """显示价格页"""
    with open(os.path.join(PROTOTYPE_DIR, "pricing.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/generate")
async def generate_video_endpoint(url: str = Form(...)):
    """
    核心 API：接收前端发来的 URL -> 爬虫 -> AI -> 视频 -> 返回文件
    """
    print(f"🌐 收到 Web 请求，目标: {url}")
    
    # 1. 抓取
    product_data = scrape_product(url)
    if not product_data:
        return {"status": "error", "message": "无法抓取该链接，请检查是否为 Shopify 网站"}
    
    # 2. 脚本
    script_data = generate_script(product_data)
    if not script_data:
        return {"status": "error", "message": "AI 生成脚本失败"}
    
    # 3. 视频
    # 注意：这里我们只用前5张图，防止生成太慢
    video_path = await create_video(script_data, product_data['images'])
    
    if not video_path:
        return {"status": "error", "message": "视频渲染失败"}
    
    # 4. 返回视频文件给浏览器下载
    return FileResponse(video_path, media_type="video/mp4", filename="generated_video.mp4")

if __name__ == "__main__":
    import uvicorn
    print("🟢 服务已启动！请在浏览器访问 http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)