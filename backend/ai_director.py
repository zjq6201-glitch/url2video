import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 DeepSeek (兼容 OpenAI 格式)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def clean_json_output(content):
    """
    清洗 AI 返回的 JSON 字符串
    防止 AI 加了 ```json ... ``` 包裹导致解析失败
    """
    if not content: return "{}"
    # 去掉 markdown 代码块标记
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'^```\s*', '', content)
    content = re.sub(r'```$', '', content)
    return content.strip()

def generate_script(product_info):
    print("✍️ DeepSeek is writing a structured script...")
    
    # 🔥 核心修改：要求 AI 返回 JSON 格式
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
        },
        {
          "duration": 4,
          "visual_description": "Person using the product happily",
          "voiceover": "This literally changed my life."
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
        print(f"🤖 AI Raw Output (First 50 chars): {raw_content[:50]}...")
        
        # 🧹 清洗并解析 JSON
        clean_content = clean_json_output(raw_content)
        script_data = json.loads(clean_content)
        
        # 🛡️ 双重保险：确保有 script_lines 键
        if "script_lines" not in script_data:
            # 如果 AI 返回了 JSON 但格式不对，尝试修复
            print("⚠️ AI JSON 缺少 script_lines，尝试自动修复...")
            return {
                "script_lines": [
                    {
                        "duration": 5, 
                        "visual_description": "Product showcase", 
                        "voiceover": str(raw_content)[:100] # 降级处理
                    }
                ]
            }

        print("✅ Script JSON generated successfully!")
        return script_data

    except json.JSONDecodeError:
        print(f"❌ JSON Parsing Failed. Raw output: {raw_content}")
        # 兜底逻辑：如果 JSON 解析彻底失败，手动构造一个简单的结构
        return {
            "script_lines": [
                {
                    "duration": 5,
                    "visual_description": "Show product image",
                    "voiceover": "Check out this amazing product! It is a total game changer. Link in bio!"
                }
            ]
        }
    except Exception as e:
        print(f"❌ Script generation error: {e}")
        return None

# --- 测试入口 ---
if __name__ == "__main__":
    # 本地测试数据
    test_prod = {'title': 'Test Lipstick', 'description': 'Red and shiny'}
    res = generate_script(test_prod)
    print(json.dumps(res, indent=2))