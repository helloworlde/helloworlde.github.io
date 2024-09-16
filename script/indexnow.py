import requests
import xml.etree.ElementTree as ET

# 目标 sitemap URL
sitemap_url = 'https://blog.hellowood.dev/sitemap.xml'

# IndexNow API的 key 和 keyLocation（请替换为你的实际值）
api_key = '78e11abb43484f688a1312d4a229c25b'  # 请替换为你的 API 密钥
key_location = 'https://blog.hellowood.dev/78e11abb43484f688a1312d4a229c25b.txt'  # 请替换为你的 key 文件位置

# 要提交的搜索引擎API列表
apis = {
    "IndexNow": "https://api.indexnow.org/indexnow",
    "Microsoft Bing": "https://www.bing.com/indexnow",
    "Naver": "https://searchadvisor.naver.com/indexnow",
    "Seznam.cz": "https://search.seznam.cz/indexnow",
    "Yandex": "https://yandex.com/indexnow",
    "Yep": "https://indexnow.yep.com/indexnow"
}

# 1. 获取并解析 sitemap
response = requests.get(sitemap_url)

if response.status_code == 200:
    # 解析 XML 数据，指定命名空间
    xml_data = response.content
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    root = ET.fromstring(xml_data)

    # 提取所有 <loc> 标签中的URL
    urls = [url.text for url in root.findall('.//ns:loc', namespaces=namespace)]

    # 打印所有提取到的URL
    print(f"Found {len(urls)} URLs in the sitemap.")

    # 2. 准备POST请求的payload
    payload = {
        'host': 'blog.hellowood.dev',
        'key': api_key,
        'keyLocation': key_location,
        'urlList': urls
    }

    # 3. 遍历搜索引擎并发送POST请求
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    for engine, api_url in apis.items():
        try:
            # 发送POST请求
            response = requests.post(api_url, json=payload, headers=headers)

            if response.status_code == 200:
                print(f"Successfully submitted URLs to {engine}.")
            else:
                print(f"Failed to submit URLs to {engine}: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error submitting URLs to {engine}: {e}")
else:
    print(f"Failed to retrieve sitemap: {response.status_code}")
