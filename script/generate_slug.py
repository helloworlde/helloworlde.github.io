# Usage:
#   AI_API_URL="http://192.168.2.121:11434/v1/chat/completions" \
#   AI_API_KEY="ollama" \
#   AI_MODEL="qwen3.5:4b" \
#   python script/generate_slug.py

import os
import sys
import re
import time
import logging
import requests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger(__name__)

AI_API_URL = os.environ.get('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
AI_API_KEY = os.environ.get('AI_API_KEY', '')
AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4o-mini')
USE_OLLAMA = os.environ.get('USE_OLLAMA', '').lower() in ('1', 'true', 'yes')

POSTS_DIR = os.environ.get('POSTS_DIR', 'content/posts')

PROMPT_TEMPLATE = (
    "你是一个 SEO 专家。请根据以下博客文章的标题，生成一个简洁、有效的英文 URL slug。\n"
    "要求：\n"
    "1. 只使用小写英文字母、数字和连字符（-）\n"
    "2. 单词之间用连字符（-）分隔，不要使用下划线或空格\n"
    "3. 简洁精炼，通常 3-8 个单词\n"
    "4. 能准确反映文章主题，有利于 SEO\n"
    "5. 不要包含介词、冠词等无意义的停用词（如 a, an, the, in, on, at, for）\n"
    "6. 只返回 slug 本身，不要任何前缀、解释或标点\n"
    "\n"
    "文章标题：{title}"
)


def parse_frontmatter(text):
    if not text.startswith('---'):
        return None, text, 0
    end = text.find('---', 3)
    if end == -1:
        return None, text, 0
    fm = text[3:end].strip()
    body = text[end + 3:]
    return fm, body, end + 3


def get_field(fm_str, field):
    for line in fm_str.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if stripped.startswith(f'{field}:'):
            return stripped.split(':', 1)[1].strip().strip('"').strip("'")
    return ''


def has_slug(fm_str):
    for line in fm_str.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if stripped.startswith('slug:'):
            val = stripped.split(':', 1)[1].strip().strip('"').strip("'")
            return len(val) > 0
    return False


def _detect_ollama():
    if USE_OLLAMA:
        return True
    return ':11434' in AI_API_URL


def _ollama_base_url():
    from urllib.parse import urlparse
    parsed = urlparse(AI_API_URL)
    return f"{parsed.scheme}://{parsed.netloc}"


def call_ai_api(title):
    prompt = PROMPT_TEMPLATE.format(title=title)
    if _detect_ollama():
        return _call_ollama(prompt)
    return _call_openai(prompt)


def _call_ollama(prompt):
    url = _ollama_base_url() + '/api/chat'
    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,
        "options": {"temperature": 0.2},
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return _clean_slug(resp.json()['message']['content'])


def _call_openai(prompt):
    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 100,
    }
    headers = {}
    if AI_API_KEY:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"
    resp = requests.post(AI_API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return _clean_slug(resp.json()['choices'][0]['message']['content'])


def _clean_slug(text):
    slug = text.strip()
    slug = re.sub(r'<think>.*?</think>', '', slug, flags=re.DOTALL).strip()
    slug = slug.strip('"').strip("'").strip('`').lower()
    slug = re.sub(r'[^a-z0-9\-]', '-', slug)
    slug = re.sub(r'-{2,}', '-', slug)
    slug = slug.strip('-')
    return slug


def filename_to_old_path(fname):
    """将文件名转换为旧的 URL 路径（用于 aliases 重定向）"""
    name = fname[:-3] if fname.endswith('.md') else fname
    # Hugo 默认将文件名转为小写作为 URL，alias 中直接写小写路径即可，无需 URL 编码
    return f"/posts/{name.lower()}/"


def update_frontmatter(filepath, slug, old_path):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fm_str, _, fm_end = parse_frontmatter(content)
    if fm_str is None:
        return False

    slug_line = f'slug: "{slug}"'
    aliases_block = f'aliases:\n  - "{old_path}"'

    # 在 title 字段后插入 slug 和 aliases
    if re.search(r'^title:', content, re.MULTILINE):
        new_content = re.sub(
            r'^(title:.*)',
            f'\\1\n{slug_line}\n{aliases_block}',
            content, count=1, flags=re.MULTILINE
        )
    else:
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


def main():
    if not AI_API_KEY:
        log.error("未设置 AI_API_KEY 环境变量")
        sys.exit(1)

    mode = "Ollama" if _detect_ollama() else "OpenAI Compatible"
    log.info("API: %s (%s)", AI_API_URL, mode)
    log.info("Model: %s", AI_MODEL)
    log.info("Posts: %s", POSTS_DIR)

    files = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')])

    total = len(files)
    generated = 0
    skipped = 0
    failed = 0

    for i, fname in enumerate(files):
        filepath = os.path.join(POSTS_DIR, fname)
        prefix = f"[{i+1}/{total}] {fname}"

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        fm_str, _, _ = parse_frontmatter(content)
        if fm_str is None:
            skipped += 1
            log.info("%s -> 跳过: 无 frontmatter", prefix)
            continue

        title = get_field(fm_str, 'title')
        if not title:
            skipped += 1
            log.info("%s -> 跳过: 无标题", prefix)
            continue

        if has_slug(fm_str):
            skipped += 1
            log.info("%s -> 跳过: 已有 slug", prefix)
            continue

        try:
            slug = call_ai_api(title)
            if not slug:
                failed += 1
                log.warning("%s -> AI 返回空内容", prefix)
                continue

            old_path = filename_to_old_path(fname)
            if update_frontmatter(filepath, slug, old_path):
                generated += 1
                log.info("%s -> slug: %s  alias: %s", prefix, slug, old_path)
            else:
                failed += 1
                log.error("%s -> 写入 frontmatter 失败", prefix)
        except Exception as e:
            failed += 1
            log.error("%s -> %s", prefix, e)

        time.sleep(0.5)

    log.info("完成 (共 %d 篇) - 生成: %d, 跳过: %d, 失败: %d", total, generated, skipped, failed)


if __name__ == '__main__':
    main()
