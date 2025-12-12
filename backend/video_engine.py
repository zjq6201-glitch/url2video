import os
import requests
import asyncio
import edge_tts
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
from moviepy.editor import *

# 临时文件夹配置
TEMP_DIR = "temp_assets"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# ==========================================
# 🛠️ 工具函数
# ==========================================

def download_image(url, index):
    """下载图片并保存到临时目录"""
    try:
        # 伪装浏览器头，防止某些 CDN 拒绝访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            filename = os.path.join(TEMP_DIR, f"image_{index}.jpg")
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f"⚠️ 图片下载失败 {url}: {e}")
    return None

async def generate_voiceover(text, index):
    """
    生成语音：
    1. 优先使用 Edge-TTS (效果最好的免费 AI 语音)
    2. 失败则尝试 pyttsx3 (机械音兜底)
    """
    filename = os.path.join(TEMP_DIR, f"voice_{index}.mp3")
    
    # 方案 A: Edge-TTS (推荐)
    try:
        # 选用了 'en-US-AriaNeural'，这是一个非常自然的女声
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural") 
        await communicate.save(filename)
        return filename
    except Exception as e:
        print(f"⚠️ Edge-TTS 生成失败 ({e})，尝试切换备用方案...")
        
    # 方案 B: 离线引擎 (仅作最后的救命稻草)
    if pyttsx3:
        try:
            engine = pyttsx3.init()
            engine.save_to_file(text, filename)
            engine.runAndWait()
            return filename
        except Exception as e:
            print(f"❌ 离线语音也失败: {e}")
    
    return None

def smart_resize_crop(clip, target_w=1080, target_h=1920):
    """
    🔥 核心算法：智能填充裁剪
    确保图片填满屏幕，且画面居中，不变形
    """
    # 1. 计算宽高比
    img_ratio = clip.w / clip.h
    target_ratio = target_w / target_h
    
    # 2. 决定是基于宽度放大，还是基于高度放大
    if img_ratio > target_ratio:
        # 图片比屏幕“胖” (横图)：高度对齐，宽度两边裁掉
        # 先把高度拉到 1920
        clip = clip.resize(height=target_h)
        # 再居中裁剪宽度
        clip = clip.crop(x1=(clip.w - target_w) / 2, width=target_w, height=target_h)
    else:
        # 图片比屏幕“瘦” (长图)：宽度对齐，高度上下裁掉
        # 先把宽度拉到 1080
        clip = clip.resize(width=target_w)
        # 再居中裁剪高度
        clip = clip.crop(y1=(clip.h - target_h) / 2, width=target_w, height=target_h)
        
    return clip

# ==========================================
# 🎬 主渲染逻辑
# ==========================================

async def create_video(script_data, images_urls):
    print("🎬 [VideoEngine] 启动渲染引擎...")

    # 1. 预下载图片
    print(f"⬇️ 正在下载素材 ({len(images_urls)} 张)...")
    local_images = []
    for i, url in enumerate(images_urls): 
        # 最多只下载 8 张，多了视频太长没人看
        if i >= 8: break 
        path = download_image(url, i)
        if path:
            local_images.append(path)
    
    if not local_images:
        print("❌ 严重错误：没有下载到任何有效图片")
        return None

    # 2. 合成片段
    clips = []
    script_lines = script_data.get('script_lines', [])
    
    # 如果脚本太长，图片不够用，就循环使用图片
    print("🎞️ 开始处理场景...")
    
    for i, line in enumerate(script_lines):
        # --- A. 音频处理 ---
        voice_text = line['voiceover']
        audio_path = await generate_voiceover(voice_text, i)
        
        if not audio_path or not os.path.exists(audio_path):
            print(f"⚠️ 跳过场景 {i}: 音频缺失")
            continue
            
        try:
            # 加载音频
            audio_clip = AudioFileClip(audio_path)
            # 每一段多留 0.3 秒，让转场更自然
            duration = audio_clip.duration + 0.3
            
            # --- B. 画面处理 (Smart Crop) ---
            # 循环选取图片
            img_path = local_images[i % len(local_images)]
            
            # 加载图片
            img_clip = ImageClip(img_path)
            
            # 🌟 调用智能裁剪算法
            img_clip = smart_resize_crop(img_clip, 1080, 1920)
            
            # ✨ 添加 Ken Burns 效果 (缓慢放大 1.0 -> 1.05)
            # 这会让静态图看起来像是在“推镜头”
            img_clip = img_clip.resize(lambda t: 1 + 0.04 * t)
            
            # 设置时长和音频
            img_clip = img_clip.set_duration(duration).set_audio(audio_clip)
            
            # 设置淡入淡出 (防止画面跳变太生硬)
            img_clip = img_clip.crossfadein(0.5)
            
            clips.append(img_clip)
            print(f"   ✅ 场景 {i+1} 合成完毕 ({duration:.1f}s)")
            
        except Exception as e:
            print(f"⚠️ 场景 {i} 处理出错: {e}")

    if not clips:
        print("❌ 最终没有生成任何有效片段")
        return None

    # 3. 最终渲染
    print("🚀 正在编码最终 MP4 (这可能需要几十秒)...")
    output_filename = "final_output.mp4"
    
    try:
        # 使用 compose 方法合并，支持 crossfade 过渡效果
        final_video = concatenate_videoclips(clips, method="compose", padding=-0.5)
        
        # 写入文件
        # 🔥 优化参数：大幅压缩文件体积，防止超过 Supabase 50MB 限制
        final_video.write_videofile(
            output_filename, 
            fps=24,                 # 电影感帧率
            codec="libx264",        # H.264 编码 (兼容性最好)
            audio_codec="aac",      # 音频编码
            threads=4,              # 多线程
            
            # 🔥 关键修改点 🔥
            preset='medium',        # 改为 medium (ultrafast 生成的文件巨大，medium 压缩率更高)
            bitrate="2500k",        # 限制视频码率为 2.5Mbps (TikTok 标准)，确保文件在 10MB 左右
            audio_bitrate="128k",   # 限制音频码率
            
            logger=None             # 保持静默，防止日志爆炸
        )
        
        file_size = os.path.getsize(output_filename) / 1024 / 1024
        print(f"\n🎉 视频渲染成功！文件大小: {file_size:.2f} MB")
        
        # 双重保险：如果压缩后还是超过 45MB，打印警告
        if file_size > 45:
            print("⚠️ 警告：视频仍然过大，可能会导致 Supabase 上传失败")
            
        return output_filename
        
    except Exception as e:
        print(f"❌ 渲染阶段崩溃: {e}")
        return None