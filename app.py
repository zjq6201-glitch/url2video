import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 引入我们写好的核心逻辑
from backend.scraper import scrape_product
from backend.ai_director import generate_script
from backend.video_engine import create_video
# 🔥 新增：引入数据库模块
import backend.db as db

# 加载环境变量
load_dotenv()

app = FastAPI()

# 允许跨域 (防止前端报错)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 原型文件夹路径
PROTOTYPE_DIR = "prototype"

# ==========================================
# 1. 页面路由 (Page Routes)
# ==========================================

# 解决 favicon.ico 404 问题
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    # 如果根目录下有 favicon.ico 就返回，没有就返回 204 (No Content) 让浏览器闭嘴
    if os.path.exists("favicon.ico"):
        return FileResponse("favicon.ico")
    return Response(status_code=204)

@app.get("/", response_class=FileResponse)
async def read_root():
    """当用户访问首页时"""
    return FileResponse(os.path.join(PROTOTYPE_DIR, "index.html"))

@app.get("/pricing.html", response_class=FileResponse)
async def read_pricing():
    """显示价格页"""
    return FileResponse(os.path.join(PROTOTYPE_DIR, "pricing.html"))

@app.get("/success.html", response_class=FileResponse)
async def read_success():
    """显示支付成功页"""
    return FileResponse(os.path.join(PROTOTYPE_DIR, "success.html"))

# ==========================================
# 2. 核心 API (Core API)
# ==========================================

@app.post("/api/generate")
async def generate_video_endpoint(
    url: str = Form(...), 
    user_id: str = Form(...) # 🔥 新增：必须接收 user_id 来扣费
):
    """
    核心流程：
    1. 检查积分 -> 2. 爬虫 -> 3. AI脚本 -> 4. 渲染视频 -> 5. 上传云端 -> 6. 扣费存历史
    """
    print(f"🌐 收到请求 | 用户: {user_id} | 链接: {url}")
    
    # --- 第1步：💰 检查积分 (Gatekeeping) ---
    credits = db.get_or_create_user(user_id)
    if credits <= 0:
        # 返回 402 Payment Required 状态码
        return JSONResponse(
            status_code=402, 
            content={"status": "error", "message": "您的积分不足！请先充值。"}
        )
    print(f"✅ 积分检查通过，剩余: {credits}")
    
    # --- 第2步：🕷️ 抓取 ---
    product_data = scrape_product(url)
    if not product_data:
        return JSONResponse(status_code=400, content={"status": "error", "message": "无法抓取该链接，请检查是否为 Shopify/Amazon 网站"})
    
    # --- 第3步：✍️ AI 脚本 ---
    script_data = generate_script(product_data)
    if not script_data:
        return JSONResponse(status_code=500, content={"status": "error", "message": "AI 脚本生成失败"})
    
    # --- 第4步：🎬 渲染视频 ---
    # 这里我们只用前 6 张图，防止生成太慢
    video_path = await create_video(script_data, product_data['images'])
    
    if not video_path:
        return JSONResponse(status_code=500, content={"status": "error", "message": "视频渲染失败"})
    
    # --- 第5步：☁️ 上传到 Supabase (关键步骤) ---
    # 将本地生成的视频上传到云端存储桶
    cloud_url = db.upload_video_to_storage(video_path, user_id)
    
    # 如果上传失败（比如没配 Supabase Key），做个降级处理
    if not cloud_url:
        print("⚠️ 上传云端失败，降级为直接返回文件流（本次不保存历史）")
        # 直接返回文件流，保证用户能拿到视频，但不扣费或保存历史可能不合适，这里视情况而定
        # 为了 MVP 体验，我们选择直接返回文件
        return FileResponse(video_path, media_type="video/mp4", filename="generated_video.mp4")

    # --- 第6步：📝 扣费并保存历史 ---
    db.deduct_credit(user_id)
    db.save_history(user_id, url, cloud_url, script_data)
    
    # --- 第7步：✅ 返回 JSON 给前端 ---
    # 前端拿到 video_url 后，会创建一个下载链接
    return JSONResponse(content={
        "status": "success", 
        "video_url": cloud_url,
        "remaining_credits": credits - 1
    })

if __name__ == "__main__":
    import uvicorn
    print("🟢 服务已启动！请在浏览器访问 http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)