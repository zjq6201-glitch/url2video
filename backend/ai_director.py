import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==========================================
# 🛠️ 修复点 1：正确获取环境变量
# ==========================================
api_key = os.getenv("DEEPSEEK_API_KEY")

# 初始化 DeepSeek
client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com"
)

def clean_json_output(content):
    """清洗 AI 返回的 JSON 字符串"""
    if not content: return "{}"
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'^```\s*', '', content)
    content = re.sub(r'```$', '', content)
    return content.strip()

def generate_script(product_info):
    print("✍️ DeepSeek is writing a structured script...")
    
    # 检查 Key 是否存在
    if not api_key:
        print("❌ 错误：未找到 DEEPSEEK_API_KEY 环境变量！")
        return get_fallback_script()

    system_prompt = """
    You are a professional TikTok video director.
    Your job is to create a structured video script JSON for a product.

    INPUT: Product Title & Description
    OUTPUT: A strictly valid JSON object.

    JSON STRUCTURE RULES:
    {
      "script_lines": [
        {
          "duration": 5,
          "visual_description": "Close up shot of the product texture",
          "voiceover": "Stop scrolling! You need to see this."
        }
      ]
    }

    CONTENT RULES:
    1. Total duration: 30-45 seconds.
    2. Tone: Viral, High Energy, Gen-Z Slang, Urgent.
    3. Structure: Hook -> Pain Point -> Solution -> CTA.
    4. NO markdown, NO explanations, ONLY JSON.
    """

    user_prompt = f"Product Info: {product_info}\n\nGenerate the JSON script now."

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
            temperature=0.7 
        )
        
        raw_content = response.choices[0].message.content.strip()
        print(f"🤖 AI Raw Output: {raw_content[:50]}...")
        
        clean_content = clean_json_output(raw_content)
        script_data = json.loads(clean_content)
        
        if "script_lines" not in script_data:
            print("⚠️ AI JSON 缺少 script_lines，使用兜底脚本...")
            return get_fallback_script()

        print("✅ Script JSON generated successfully!")
        return script_data

    except Exception as e:
        print(f"❌ Script generation error: {e}")
        # ==========================================
        # 🛠️ 修复点 2：出错时返回字典，而不是字符串
        # ==========================================
        return get_fallback_script()

def get_fallback_script():
    """当 AI 失败时，返回一个格式正确的保底 JSON"""
    return {
        "script_lines": [
            {
                "duration": 5,
                "visual_description": "Show the product clearly on screen",
                "voiceover": "Wait, stop scrolling! You literally need to see this product right now."
            },
            {
                "duration": 5,
                "visual_description": "Show product features",
                "voiceover": "It is honestly a game changer and solves your biggest problem instantly."
            },
            {
                "duration": 5,
                "visual_description": "Call to action text overlay",
                "voiceover": "Click the link in bio to grab yours before it sells out!"
            }
        ]
    }

# --- 测试入口 ---
if __name__ == "__main__":
    test_prod = {'title': 'Test Lipstick', 'description': 'Red and shiny'}
    res = generate_script(test_prod)
    print(json.dumps(res, indent=2))