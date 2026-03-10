import os
import sys
import requests
import xml.etree.ElementTree as ET

SITEMAP_URL = 'https://blog.hellowood.dev/sitemap.xml'
HOST = 'blog.hellowood.dev'

SEARCH_ENGINES = {
    "IndexNow": "https://api.indexnow.org/indexnow",
    "Microsoft Bing": "https://www.bing.com/indexnow",
    "Naver": "https://searchadvisor.naver.com/indexnow",
    "Seznam.cz": "https://search.seznam.cz/indexnow",
    "Yandex": "https://yandex.com/indexnow",
    "Yep": "https://indexnow.yep.com/indexnow",
}


def get_sitemap_urls(sitemap_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; SEO-Submit-Bot/1.0)',
        'Accept': 'application/xml,text/xml',
    }

    try:
        response = requests.get(sitemap_url, headers=headers)
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


def submit_to_indexnow(urls, api_key):
    key_location = f"https://{HOST}/{api_key}.txt"

    payload = {
        'host': HOST,
        'key': api_key,
        'keyLocation': key_location,
        'urlList': urls,
    }

    headers = {'Content-Type': 'application/json; charset=utf-8'}

    has_failure = False
    for engine, api_url in SEARCH_ENGINES.items():
        try:
            response = requests.post(api_url, json=payload, headers=headers)
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

    urls = get_sitemap_urls(SITEMAP_URL)
    if not urls:
        print("未获取到有效 URL，跳过提交")
        return

    print(f"获取到 {len(urls)} 个有效 URL")

    success = submit_to_indexnow(urls, api_key)
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
