import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载环境变量
load_dotenv()

# 2. 初始化 DeepSeek 客户端
# 注意：DeepSeek 完美兼容 OpenAI 库，只需修改 base_url
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def clean_json_output(content):
    """
    有时候 AI 会返回 ```json ... ``` 格式，我们需要把 markdown 符号去掉
    才能被 json.loads 解析
    """
    # 修复点：给正则表达式加上了引号 r'...'
    # 去掉开头的 ```json
    content = re.sub(r'^```json\s*', '', content)
    # 去掉开头的 ```
    content = re.sub(r'^```\s*', '', content)
    # 去掉结尾的 ```
    content = re.sub(r'```$', '', content)
    return content.strip()

def generate_script(product_data):
    title = product_data.get('title', 'Unknown Product')
    description = product_data.get('description', '')[:800]

    print(f"🧠 AI 导演 (DeepSeek) 正在构思脚本: {title}...")

    # --- 核心提示词 ---
    system_prompt = """
    You are an expert short-video director for TikTok and Reels.
    Your task is to convert product information into a high-converting, viral video script (30-45 seconds).

    ### SCRIPT STRUCTURE (Strictly follow this flow):
    1. HOOK (0-3s): Visually striking or controversial statement to stop scrolling.
    2. PAIN POINT (3-10s): The problem the viewer is facing.
    3. SOLUTION (10-25s): How this product solves it (Key Features).
    4. CTA (25-30s): Strong Call to Action (e.g., "Link in bio", "Get yours now").

    ### OUTPUT FORMAT:
    You must output valid JSON only. Do not add conversational text.
    The JSON structure must be:
    {
      "script_lines": [
        {
          "scene_index": 1,
          "duration": "3s",
          "visual_description": "Detailed visual description for AI video generator...", 
          "voiceover": "The spoken words..."
        }
      ]
    }
    """

    user_prompt = f"""
    Product Name: {title}
    Product Description: {description}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={ "type": "json_object" } 
        )
        
        script_raw = response.choices[0].message.content
        
        # 清洗数据
        script_clean = clean_json_output(script_raw)
        
        # 解析 JSON
        script_json = json.loads(script_clean)
        
        print("✅ 脚本创作完成！")
        return script_json

    except Exception as e:
        print(f"❌ AI 生成失败: {e}")
        # 打印原始返回以便调试
        if 'script_raw' in locals():
            print(f"调试-原始返回: {script_raw}")
        return None

# --- 单独测试入口 ---
if __name__ == "__main__":
    # 模拟数据 (Ritz 眼影)
    test_product = {
        "title": "ColourPop Ritz Super Shock Shadow",
        "description": "Our famous OG crème-to-powder formula delivers supercharged sparkling colour with minimal creasing, fading or fallout."
    }
    
    script = generate_script(test_product)
    
    if script:
        print("\n🎬 --- DeepSeek 导演生成的脚本 ---")
        for line in script.get('script_lines', []):
            print(f"[{line['duration']}]")
            print(f"   👁️ 画面: {line['visual_description']}")
            print(f"   🗣️ 旁白: {line['voiceover']}")
            print("-" * 30)