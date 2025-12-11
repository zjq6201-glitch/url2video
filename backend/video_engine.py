import os
import requests
import asyncio
import edge_tts
import pyttsx3
from moviepy.editor import *

# 临时文件夹
TEMP_DIR = "temp_assets"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def download_image(url, index):
    """下载图片"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            filename = os.path.join(TEMP_DIR, f"image_{index}.jpg")
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f"⚠️ 图片下载失败 {url}: {e}")
    return None

def generate_voiceover_offline(text, filename):
    """【备选方案】使用系统自带的离线语音 (pyttsx3)"""
    print(f"🐢 网络不通，切换到离线语音引擎...")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if "female" in voice.name.lower() or "ziwei" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
            
    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

async def generate_voiceover(text, index):
    """尝试生成语音：优先 Edge-TTS，失败则用离线"""
    filename = os.path.join(TEMP_DIR, f"voice_{index}.mp3")
    
    # 方案 A: Edge-TTS
    try:
        print(f"🎙️ [Edge-TTS] 正在生成语音片段 {index}...")
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural") 
        await communicate.save(filename)
        return filename
    except Exception as e:
        print(f"⚠️ Edge-TTS 连接失败 ({e})")
        
    # 方案 B: 离线兜底
    try:
        generate_voiceover_offline(text, filename)
        return filename
    except Exception as e:
        print(f"❌ 离线语音也失败了: {e}")
        return None

# ================= 修改重点在这里 =================
# 1. 改为 async def
async def create_video(script_data, images_urls):
    print("🎬 正在启动视频渲染引擎...")

    # 1. 下载图片
    print(f"⬇️ 正在下载 {len(images_urls)} 张图片素材...")
    local_images = []
    for i, url in enumerate(images_urls[:8]): 
        path = download_image(url, i)
        if path:
            local_images.append(path)
    
    if not local_images:
        print("❌ 严重错误：没有下载到任何图片")
        return None

    # 2. 逐个场景处理
    clips = []
    script_lines = script_data.get('script_lines', [])

    print("🎞️ 开始合成片段...")
    
    for i, line in enumerate(script_lines):
        # A. 生成音频
        voice_text = line['voiceover']
        
        # 2. 直接使用 await，删掉了 loop.run_until_complete
        audio_path = await generate_voiceover(voice_text, i)
        
        if not audio_path or not os.path.exists(audio_path):
            print(f"⚠️ 跳过片段 {i}: 音频生成失败")
            continue
            
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.5
            
            img_path = local_images[i % len(local_images)]
            
            # 画面处理
            clip = ImageClip(img_path).set_duration(duration)
            clip = clip.resize(height=1920)
            if clip.w < 1080: clip = clip.resize(width=1080)
            clip = clip.crop(x1=clip.w/2 - 540, y1=0, width=1080, height=1920)
            clip = clip.resize(lambda t: 1 + 0.04 * t)  
            
            clip = clip.set_audio(audio_clip)
            clips.append(clip)
            print(f"   ✅ 片段 {i+1} 就绪")
            
        except Exception as e:
            print(f"⚠️ 画面处理出错: {e}")

    if not clips:
        print("❌ 没有生成的片段")
        return None

    # 3. 最终拼接
    print("🚀 正在渲染最终 MP4...")
    try:
        final_video = concatenate_videoclips(clips, method="compose")
        output_filename = "final_output.mp4"
        
        final_video.write_videofile(
            output_filename, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            threads=4,
            preset='ultrafast'
        )
        
        print(f"\n🎉 成功！视频: {os.path.abspath(output_filename)}")
        return output_filename
    except Exception as e:
        print(f"❌ 渲染失败: {e}")
        return None