import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urlencode

# ==========================================
# 🔑 配置 ScraperAPI (你的终极武器)
# ==========================================
SCRAPERAPI_KEY = '67882d33fd16a8d8a668f37d984cf7c2'

def get_scraperapi_url(url):
    """
    将目标 URL 包装成 ScraperAPI 的请求格式
    强制使用美国节点 (country_code=us) 解决地域跳转问题
    """
    payload = {
        'api_key': SCRAPERAPI_KEY,
        'url': url,
        'country_code': 'us', # 关键：强制美国 IP
        'keep_headers': 'true'
    }
    return 'http://api.scraperapi.com/?' + urlencode(payload)

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def scrape_shopify_json(url):
    """策略A: 通过 ScraperAPI 访问 Shopify JSON"""
    try:
        json_url = url.split('?')[0]
        if not json_url.endswith('.json'):
            json_url += '.json'
            
        # 包装 URL
        target_url = get_scraperapi_url(json_url)
        print(f"⚡ [ScraperAPI] 正在请求 JSON: {json_url}")
        
        resp = requests.get(target_url, timeout=60) # API请求可能稍微慢点，超时设长一点
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                product = data.get('product')
                if not product: return None
                
                print("✅ JSON 接口调用成功！")
                return {
                    'title': product.get('title'),
                    'description': clean_html(product.get('body_html', ''))[:500],
                    'images': [img['src'] for img in product.get('images', [])],
                    'source': 'shopify_json'
                }
            except:
                print("⚠️ 返回的不是有效 JSON")
        else:
            print(f"⚠️ JSON 请求状态码: {resp.status_code}")
            
    except Exception as e:
        print(f"⚠️ JSON 报错: {e}")
    
    return None

def scrape_html_fallback(url):
    """策略B: 通过 ScraperAPI 访问 HTML"""
    print(f"🐢 [ScraperAPI] 切换到 HTML 抓取模式...")
    
    # 包装 URL
    target_url = get_scraperapi_url(url)
    
    try:
        resp = requests.get(target_url, timeout=60)
        
        if resp.status_code != 200:
            print(f"❌ HTML 失败: {resp.status_code}")
            # 打印一点点内容看看是不是报错信息
            print(f"调试信息: {resp.text[:100]}")
            return None
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 提取 Open Graph
        title = soup.find('meta', property='og:title')
        desc = soup.find('meta', property='og:description')
        
        # 提取图片
        images = []
        og_img = soup.find('meta', property='og:image')
        if og_img: images.append(og_img['content'])
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            if ('products/' in src or '1024x1024' in src or 'cdn.shopify.com' in src):
                if src.startswith('//'): src = 'https:' + src
                if src not in images:
                    images.append(src)
        
        if title:
            print(f"✅ HTML 解析成功: {title['content']}")
            return {
                'title': title['content'],
                'description': desc['content'] if desc else '',
                'images': images[:10],
                'source': 'html_fallback'
            }
        else:
            print("❌ 未找到标题 meta 标签")
            
    except Exception as e:
        print(f"❌ HTML 报错: {e}")
        return None

def scrape_product(url):
    data = scrape_shopify_json(url)
    if not data:
        data = scrape_html_fallback(url)
    return data

# --- 测试 ---
if __name__ == "__main__":
    test_url = "https://knix.com/products/leakproof-bikini"
    print(scrape_product(test_url))