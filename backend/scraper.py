import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlencode

# ==========================================
# 🔑 配置 ScraperAPI
# ==========================================
SCRAPERAPI_KEY = '67882d33fd16a8d8a668f37d984cf7c2'

def get_scraperapi_url(url):
    """包装 ScraperAPI 请求"""
    payload = {
        'api_key': SCRAPERAPI_KEY,
        'url': url,
        'country_code': 'us', 
        'keep_headers': 'true'
    }
    return 'http://api.scraperapi.com/?' + urlencode(payload)

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

# 🔥 新增：智能图片过滤器
def is_high_quality_image(url):
    """过滤掉 Logo、图标、小图和无关图片"""
    if not url: return False
    url_lower = url.lower()
    
    # 1. 垃圾关键词黑名单
    blacklist = [
        'logo', 'icon', 'arrow', 'payment', 'footer', 'svg', 
        'blank', 'star', 'rating', 'avatar', 'user', 'cart',
        'facebook', 'twitter', 'instagram', 'search', 'button'
    ]
    if any(x in url_lower for x in blacklist):
        return False
        
    # 2. Shopify 特有的小图后缀过滤
    # Shopify 会生成 _32x32, _50x50, _small, _thumb, _pico 等缩略图
    size_blacklist = ['_32x32', '_50x50', '_64x64', '_100x100', '_small', '_thumb', '_icon', '_pico', '_compact']
    if any(x in url_lower for x in size_blacklist):
        return False
        
    return True

def scrape_shopify_json(url):
    """策略A: JSON"""
    try:
        json_url = url.split('?')[0]
        if not json_url.endswith('.json'):
            json_url += '.json'
        
        target_url = get_scraperapi_url(json_url)
        print(f"⚡ [ScraperAPI] 请求 JSON: {json_url}")
        
        resp = requests.get(target_url, timeout=60)
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                product = data.get('product')
                if not product: return None
                
                # ✅ 应用过滤器
                raw_images = [img['src'] for img in product.get('images', [])]
                clean_images = [img for img in raw_images if is_high_quality_image(img)]
                
                return {
                    'title': product.get('title'),
                    'description': clean_html(product.get('body_html', ''))[:500],
                    'images': clean_images[:8], # 只取前8张最好的
                    'source': 'shopify_json'
                }
            except:
                pass
    except Exception as e:
        print(f"⚠️ JSON 报错: {e}")
    return None

def scrape_html_fallback(url):
    """策略B: HTML"""
    print(f"🐢 [ScraperAPI] 切换到 HTML 模式...")
    target_url = get_scraperapi_url(url)
    
    try:
        resp = requests.get(target_url, timeout=60)
        if resp.status_code != 200: return None
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 提取信息
        title = soup.find('meta', property='og:title')
        title_content = title['content'] if title else soup.title.string
        
        desc = soup.find('meta', property='og:description')
        desc_content = desc['content'] if desc else ""
        
        # ✅ 提取图片并过滤
        images = []
        
        # 1. 优先拿 OG Image (通常是主图)
        og_img = soup.find('meta', property='og:image')
        if og_img and is_high_quality_image(og_img['content']):
            images.append(og_img['content'])
        
        # 2. 遍历页面图片
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('//'): src = 'https:' + src
            
            # 必须包含 products 或者是 cdn 链接，且通过过滤器
            if ('products/' in src or 'cdn.shopify.com' in src) and is_high_quality_image(src):
                if src not in images:
                    images.append(src)
        
        return {
            'title': title_content,
            'description': desc_content,
            'images': images[:8],
            'source': 'html_fallback'
        }
            
    except Exception as e:
        print(f"❌ HTML 报错: {e}")
        return None

def scrape_product(url):
    data = scrape_shopify_json(url)
    if not data:
        data = scrape_html_fallback(url)
    return data