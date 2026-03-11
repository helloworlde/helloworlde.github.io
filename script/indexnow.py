import os
import sys
import requests
import xml.etree.ElementTree as ET
import time
import random

SITE_URL = 'https://blog.hellowood.dev'
HOST = 'blog.hellowood.dev'
SITEMAP_FILE = 'public/sitemap.xml'

SEARCH_ENGINES = {
    "IndexNow": "https://api.indexnow.org/indexnow",
    "Microsoft Bing": "https://www.bing.com/indexnow",
    "Naver": "https://searchadvisor.naver.com/indexnow",
    "Yandex": "https://yandex.com/indexnow",
    "Yep": "https://indexnow.yep.com/indexnow",
}

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}


def create_session():
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)
    return session


def get_sitemap_urls(sitemap_file):
    if not os.path.isfile(sitemap_file):
        print(f"sitemap 文件不存在: {sitemap_file}")
        return []

    try:
        tree = ET.parse(sitemap_file)
        root = tree.getroot()
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = [
            url.text for url in root.findall('.//ns:loc', namespace)
            if url.text and '/tags/' not in url.text
        ]
        return urls
    except ET.ParseError as e:
        print(f"解析 sitemap XML 失败: {e}")
        return []


def submit_to_indexnow(session, urls, api_key):
    key_location = f"https://{HOST}/{api_key}.txt"

    payload = {
        'host': HOST,
        'key': api_key,
        'keyLocation': key_location,
        'urlList': urls,
    }

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Origin': f'https://{HOST}',
        'Referer': f'https://{HOST}/',
    }

    has_failure = False
    for engine, api_url in SEARCH_ENGINES.items():
        try:
            time.sleep(random.uniform(1, 3))
            response = session.post(api_url, json=payload, headers=headers, timeout=30)
            if response.status_code in (200, 202):
                print(f"成功提交 {len(urls)} 个 URL 到 {engine}")
            else:
                print(f"提交到 {engine} 失败: {response.status_code}, {response.text}")
                has_failure = True
        except requests.RequestException as e:
            print(f"提交到 {engine} 异常: {e}")
            has_failure = True

    return not has_failure


def main():
    api_key = os.environ.get('INDEXNOW_API_KEY')
    if not api_key:
        print("错误: 未设置 INDEXNOW_API_KEY 环境变量")
        sys.exit(1)

    session = create_session()

    urls = get_sitemap_urls(SITEMAP_FILE)
    if not urls:
        print("未获取到有效 URL，跳过提交")
        return

    print(f"获取到 {len(urls)} 个有效 URL")

    submit_to_indexnow(session, urls, api_key)


if __name__ == '__main__':
    main()
