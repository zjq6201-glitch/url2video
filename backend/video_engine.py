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
    """生成语音 (Edge-TTS)"""
    filename = os.path.join(TEMP_DIR, f"voice_{index}.mp3")
    try:
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural") 
        await communicate.save(filename)
        return filename
    except Exception as e:
        print(f"⚠️ Edge-TTS 生成失败 ({e})")
        
    if pyttsx3:
        try:
            engine = pyttsx3.init()
            engine.save_to_file(text, filename)
            engine.runAndWait()
            return filename
        except:
            pass
    return None

# 🔥 修改点 1：默认分辨率降为 720p (720x1280)
# 1080p 太吃内存，512MB 扛不住
def smart_resize_crop(clip, target_w=720, target_h=1280):
    """
    🔥 核心算法：智能填充裁剪
    """
    img_ratio = clip.w / clip.h
    target_ratio = target_w / target_h
    
    if img_ratio > target_ratio:
        clip = clip.resize(height=target_h)
        clip = clip.crop(x1=(clip.w - target_w) / 2, width=target_w, height=target_h)
    else:
        clip = clip.resize(width=target_w)
        clip = clip.crop(y1=(clip.h - target_h) / 2, width=target_w, height=target_h)
        
    return clip

# ==========================================
# 🎬 主渲染逻辑
# ==========================================

async def create_video(script_data, images_urls):
    print("🎬 [VideoEngine] 启动渲染引擎 (Low RAM Mode)...")

    # 1. 预下载图片
    local_images = []
    for i, url in enumerate(images_urls): 
        if i >= 6: break # 限制图片数量，省内存
        path = download_image(url, i)
        if path:
            local_images.append(path)
    
    if not local_images:
        return None

    # 2. 合成片段
    clips = []
    script_lines = script_data.get('script_lines', [])
    
    for i, line in enumerate(script_lines):
        voice_text = line['voiceover']
        audio_path = await generate_voiceover(voice_text, i)
        
        if not audio_path or not os.path.exists(audio_path):
            continue
            
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.3
            
            img_path = local_images[i % len(local_images)]
            img_clip = ImageClip(img_path)
            
            # 🔥 修改点 2：使用 720p 裁剪
            img_clip = smart_resize_crop(img_clip, 720, 1280)
            
            # Ken Burns 效果
            img_clip = img_clip.resize(lambda t: 1 + 0.04 * t)
            
            img_clip = img_clip.set_duration(duration).set_audio(audio_clip)
            img_clip = img_clip.crossfadein(0.5)
            
            clips.append(img_clip)
            
            # 🔥 强制垃圾回收：每处理完一个片段，手动释放内存
            # 虽然 Python 会自动回收，但在低配机器上最好手动触发
            del audio_clip
            del img_clip
            
        except Exception as e:
            print(f"⚠️ 场景 {i} 处理出错: {e}")

    if not clips:
        return None

    # 3. 最终渲染
    output_filename = "final_output.mp4"
    
    try:
        final_video = concatenate_videoclips(clips, method="compose", padding=-0.5)
        
        final_video.write_videofile(
            output_filename, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            
            # 🔥🔥🔥 关键修改：单线程 + 低内存预设 🔥🔥🔥
            threads=1,              # 必须改为 1！多线程会瞬间撑爆 512MB
            preset='ultrafast',     # 使用最快的预设，减少内存驻留时间
            
            # 码率控制 (720p 对应 1.5Mbps 足够清晰)
            bitrate="1500k",        
            audio_bitrate="128k",
            
            # 减少音频缓冲区大小 (默认 2000，改小能省内存)
            audio_buffersize=1000,
            
            logger=None 
        )
        
        # 显式释放内存
        final_video.close()
        for c in clips:
            c.close()

        file_size = os.path.getsize(output_filename) / 1024 / 1024
        print(f"\n🎉 渲染成功 (720p/SingleThread)！大小: {file_size:.2f} MB")
        
        return output_filename
        
    except Exception as e:
        print(f"❌ 渲染崩溃 (OOM): {e}")
        return None