import os
import time
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# 初始化 Supabase 客户端
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("⚠️ 警告：Supabase 配置缺失，数据库功能将不可用！")
    supabase = None
else:
    supabase: Client = create_client(url, key)

def get_or_create_user(user_id):
    """获取用户积分，如果用户不存在（第一次来），就自动创建并送5分"""
    if not supabase: return 5 # 本地兜底
    
    try:
        # 1. 尝试查询
        res = supabase.table('user_credits').select("*").eq('user_id', user_id).execute()
        
        if res.data:
            return res.data[0]['credits']
        else:
            # 2. 如果没查到，说明是新用户，插入一条记录（送5分）
            print(f"🆕 新用户 {user_id}，正在初始化积分...")
            supabase.table('user_credits').insert({
                "user_id": user_id, 
                "credits": 5 
            }).execute()
            return 5
            
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return 0

def deduct_credit(user_id):
    """扣除 1 个积分"""
    if not supabase: return
    try:
        # RPC (远程存储过程) 是更安全的方法，但这里为了简单，我们先查再改
        # 1. 获取当前积分
        current = get_or_create_user(user_id)
        if current > 0:
            # 2. 更新积分 -1
            supabase.table('user_credits').update({"credits": current - 1}).eq('user_id', user_id).execute()
            print(f"💰 用户 {user_id} 积分扣除成功，剩余: {current - 1}")
    except Exception as e:
        print(f"❌ 扣费失败: {e}")

def upload_video_to_storage(local_path, user_id):
    """把本地生成的 MP4 上传到 Supabase Storage，并返回公开下载链接"""
    if not supabase: return None
    
    try:
        file_name = f"{user_id}_{int(time.time())}.mp4"
        bucket_name = "videos" # 刚才你在 Supabase 建的桶名字
        
        print(f"☁️ 正在上传视频到 Supabase: {file_name}")
        
        with open(local_path, 'rb') as f:
            supabase.storage.from_(bucket_name).upload(
                file=file_name,
                file=f,
                file_options={"content-type": "video/mp4"}
            )
            
        # 获取公开链接
        project_url = os.getenv("SUPABASE_URL")
        # 构造标准的 Supabase Storage 公开链接
        public_url = f"{project_url}/storage/v1/object/public/{bucket_name}/{file_name}"
        
        print(f"✅ 上传成功！云端链接: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ 上传视频失败: {e}")
        return None

def save_history(user_id, source_url, video_url, script_content):
    """保存生成记录到历史表"""
    if not supabase: return
    try:
        supabase.table('video_history').insert({
            "user_id": user_id,
            "source_url": source_url,
            "video_url": video_url,
            "script_content": str(script_content) # 转字符串防止 json 报错
        }).execute()
        print("📝 历史记录已保存")
    except Exception as e:
        print(f"❌ 保存历史失败: {e}")