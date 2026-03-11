import os
import sys
import requests
import xml.etree.ElementTree as ET
import json
import time
import random

SITE_URL = 'https://blog.hellowood.dev'
SITEMAP_FILE = 'public/sitemap.xml'
MAX_SUBMIT_URLS = 500

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


def submit_urls_to_bing(session, site_url, urls, api_key):
    bing_url = f"https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={api_key}"

    payload = {
        "siteUrl": site_url,
        "urlList": urls
    }

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Origin': 'https://www.bing.com',
        'Referer': 'https://www.bing.com/webmaster/home/dashboard',
    }

    try:
        time.sleep(random.uniform(1, 3))
        response = session.post(bing_url, data=json.dumps(payload), headers=headers, timeout=60)
        response.raise_for_status()
        print(f"成功提交 {len(urls)} 个 URL 到 Bing")
        print(response.json())
    except requests.RequestException as e:
        print(f"提交 URL 到 Bing 失败: {e}")


def main():
    api_key = os.environ.get('BING_API_KEY')
    if not api_key:
        print("错误: 未设置 BING_API_KEY 环境变量")
        sys.exit(1)

    session = create_session()

    urls = get_sitemap_urls(SITEMAP_FILE)
    if not urls:
        print("未获取到有效 URL，跳过提交")
        return

    print(f"获取到 {len(urls)} 个有效 URL")
    submit_urls_to_bing(session, SITE_URL, urls[:MAX_SUBMIT_URLS], api_key)


if __name__ == '__main__':
    main()
