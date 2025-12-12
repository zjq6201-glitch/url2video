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

def generate_script(product_info):
    print("✍️ DeepSeek is writing a viral script...")
    
    # 这里的 Prompt 是核心！我们要教 AI 怎么写出爆款
    # 结构：Hook (3秒黄金开场) -> Pain (痛点) -> Solution (产品) -> CTA (号召购买)
    system_prompt = """
    You are a world-class TikTok Dropshipping Copywriter. 
    Your goal is to write a high-converting, viral video script (30-45 seconds) for a product.

    STRICT RULES:
    1. STRUCTURE:
       - [0-3s] THE HOOK: A shocking question or statement to stop scrolling immediately.
       - [3-15s] THE PROBLEM: Agitate a relatable pain point. Make the viewer feel it.
       - [15-30s] THE SOLUTION: Introduce the product as the ultimate magic fix.
       - [30-40s] THE CTA: A strong call to action (e.g., "Get yours now", "Link in bio", "50% off today").
    
    2. TONE:
       - Use Gen-Z slang (e.g., "Game changer", "Obsessed", "Literal life saver").
       - High energy, fast-paced, punchy sentences.
       - NO "Hello everyone", NO "Welcome to my video". Jump STRAIGHT into the hook.
       - Use emojis suitable for the text.

    3. FORMAT:
       - Return ONLY the raw text of the script. Do not label "Hook:" or "Body:".
       - Keep it under 150 words total.
    """

    user_prompt = f"Product Description: {product_info}\n\nWrite the script now."

    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY, 
            base_url="https://api.deepseek.com"
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False
        )
        
        script = response.choices[0].message.content.strip()
        print(f"✅ Script generated: {script[:50]}...")
        return script

    except Exception as e:
        print(f"❌ Script generation failed: {e}")
        # 如果 AI 挂了，用这个保底文案
        return "Wait, have you seen this? This product is literally a game changer! It solves your biggest problem instantly. I am actually obsessed. You need to grab this before it sells out! Link in bio! 🔥"

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