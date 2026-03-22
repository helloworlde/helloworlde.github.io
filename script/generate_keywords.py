# Usage:
#   AI_API_URL="http://192.168.2.121:11434/v1/chat/completions" \
#   AI_API_KEY="ollama" \
#   AI_MODEL="qwen3.5:4b" \
#   python script/generate_keywords.py

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
MAX_CONTENT_CHARS = 2000

PROMPT_TEMPLATE = (
    "你是一个 SEO 专家。请为以下技术博客文章提取 5-8 个精准的中英文关键词，用于 HTML meta keywords 标签。\n"
    "要求：\n"
    "1. 关键词应精准反映文章的具体技术点，比标签更细粒度\n"
    "2. 中英文均可，技术术语保留英文原文\n"
    "3. 每个关键词 1-5 个词，不要短语或句子\n"
    "4. 以英文逗号分隔，输出一行\n"
    "5. 只返回关键词列表本身，不要任何前缀、解释或标点\n"
    "\n"
    "文章标题：{title}\n"
    "文章内容：\n{content}"
)


def parse_frontmatter(text):
    if not text.startswith('---'):
        return None, text, 0
    end = text.find('---', 3)
    if end == -1:
        return None, text, 0
    return text[3:end].strip(), text[end + 3:], end + 3


def get_field(fm_str, field):
    for line in fm_str.split('\n'):
        s = line.strip()
        if s.startswith('#'):
            continue
        if s.startswith(f'{field}:'):
            return s.split(':', 1)[1].strip().strip('"').strip("'")
    return ''


def has_keywords(fm_str):
    for line in fm_str.split('\n'):
        s = line.strip()
        if s.startswith('#'):
            continue
        if s.startswith('keywords:'):
            val = s.split(':', 1)[1].strip()
            return bool(val)
    return False


def _detect_ollama():
    if USE_OLLAMA:
        return True
    return ':11434' in AI_API_URL


def _ollama_base_url():
    from urllib.parse import urlparse
    parsed = urlparse(AI_API_URL)
    return f"{parsed.scheme}://{parsed.netloc}"


def call_ai_api(title, content):
    truncated = content[:MAX_CONTENT_CHARS]
    prompt = PROMPT_TEMPLATE.format(title=title, content=truncated)
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
    return _clean(resp.json()['message']['content'])


def _call_openai(prompt):
    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 200,
    }
    headers = {}
    if AI_API_KEY:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"
    resp = requests.post(AI_API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return _clean(resp.json()['choices'][0]['message']['content'])


def _clean(text):
    kw = text.strip()
    kw = re.sub(r'<think>.*?</think>', '', kw, flags=re.DOTALL).strip()
    kw = kw.strip('"').strip("'").replace('\n', ',')
    kw = re.sub(r',\s*,', ',', kw)
    return kw.strip(',').strip()


def keywords_to_yaml_list(kw_str):
    """将逗号分隔的关键词转为 YAML 列表字符串"""
    items = [k.strip().strip('"').strip("'") for k in kw_str.split(',') if k.strip()]
    return '\n'.join(f'  - "{item}"' for item in items if item)


def update_frontmatter(filepath, keywords_str):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    yaml_list = keywords_to_yaml_list(keywords_str)
    if not yaml_list:
        return False

    keywords_block = f'keywords:\n{yaml_list}'

    if re.search(r'^keywords:', content, re.MULTILINE):
        # 替换已有的 keywords 块（多行列表）
        new_content = re.sub(
            r'^keywords:.*?(?=^\S|\Z)',
            keywords_block + '\n',
            content, count=1, flags=re.MULTILINE | re.DOTALL
        )
    elif re.search(r'^title:', content, re.MULTILINE):
        # 插在 title 字段后面
        new_content = re.sub(
            r'^(title:.*)',
            f'\\1\n{keywords_block}',
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
            raw = f.read()

        fm_str, body, _ = parse_frontmatter(raw)
        if fm_str is None:
            skipped += 1
            log.info("%s -> 跳过: 无 frontmatter", prefix)
            continue

        title = get_field(fm_str, 'title')
        if not title:
            skipped += 1
            log.info("%s -> 跳过: 无标题", prefix)
            continue

        if has_keywords(fm_str):
            skipped += 1
            log.info("%s -> 跳过: 已有 keywords", prefix)
            continue

        if not body.strip():
            skipped += 1
            log.info("%s -> 跳过: 正文为空", prefix)
            continue

        try:
            keywords = call_ai_api(title, body)
            if not keywords:
                failed += 1
                log.warning("%s -> AI 返回空内容", prefix)
                continue
            if update_frontmatter(filepath, keywords):
                generated += 1
                log.info("%s -> %s", prefix, keywords)
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
