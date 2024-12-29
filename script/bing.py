import requests
import xml.etree.ElementTree as ET
import json

def get_sitemap_urls(sitemap_url):
    """
    从 sitemap.xml 获取所有 URL
    
    :param sitemap_url: sitemap 的 URL
    :return: URL 列表
    """
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # 处理 XML 命名空间
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # 提取所有 URL，排除包含 /tags/ 的路径
        urls = [
            url.text for url in root.findall('.//ns:loc', namespace)
            if url.text and '/tags/' not in url.text
        ]
        
        return urls
    
    except requests.RequestException as e:
        print(f"获取 sitemap 失败: {e}")
        return []
    except ET.ParseError as e:
        print(f"解析 sitemap XML 失败: {e}")
        return []

def submit_urls_to_bing(site_url, urls, api_key):
    """
    将 URL 提交到 Bing 网站管理工具
    
    :param site_url: 站点根 URL
    :param urls: 要提交的 URL 列表
    :param api_key: Bing 网站管理工具 API key
    """
    bing_url = f"https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={api_key}"
    
    payload = {
        "siteUrl": site_url,
        "urlList": urls
    }
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    try:
        response = requests.post(bing_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        
        print("成功提交 URL 到 Bing")
        print(response.json())
    
    except requests.RequestException as e:
        print(f"提交 URL 到 Bing 失败: {e}")
        if response.text:
            print("响应内容:", response.text)

def main():
    # 配置参数
    SITEMAP_URL = 'https://blog.hellowood.dev/sitemap.xml'
    SITE_URL = 'https://blog.hellowood.dev'
    BING_API_KEY = 'c54be019c120456397110b486575ee3d'
    
    # 获取 sitemap URLs
    urls = get_sitemap_urls(SITEMAP_URL)
    
    # 打印获取的 URL 数量
    print(f"获取到 {len(urls)} 个有效 URL")
    
    # 提交到 Bing（可选：限制提交数量以避免超出限制）
    max_submit_urls = 50  # Bing 可能有提交限制
    submit_urls_to_bing(SITE_URL, urls[:max_submit_urls], BING_API_KEY)

if __name__ == '__main__':
    main()
