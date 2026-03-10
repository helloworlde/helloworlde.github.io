import os
import sys
import requests
import xml.etree.ElementTree as ET
import json

SITEMAP_URL = 'https://blog.hellowood.dev/sitemap.xml'
SITE_URL = 'https://blog.hellowood.dev'
MAX_SUBMIT_URLS = 500


def get_sitemap_urls(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

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
        print(f"成功提交 {len(urls)} 个 URL 到 Bing")
        print(response.json())
    except requests.RequestException as e:
        print(f"提交 URL 到 Bing 失败: {e}")
        sys.exit(1)


def main():
    api_key = os.environ.get('BING_API_KEY')
    if not api_key:
        print("错误: 未设置 BING_API_KEY 环境变量")
        sys.exit(1)

    urls = get_sitemap_urls(SITEMAP_URL)
    if not urls:
        print("未获取到有效 URL，跳过提交")
        return

    print(f"获取到 {len(urls)} 个有效 URL")
    submit_urls_to_bing(SITE_URL, urls[:MAX_SUBMIT_URLS], api_key)


if __name__ == '__main__':
    main()
