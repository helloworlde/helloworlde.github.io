# Usage:
#   AI_API_URL="http://192.168.2.121:11434/v1/chat/completions" \
#   AI_API_KEY="ollama" \
#   AI_MODEL="qwen3.5:4b" \
#   python script/generate_tag_description.py

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
TAGS_DIR = os.environ.get('TAGS_DIR', 'content/tags')

PROMPT_TEMPLATE = (
    "你是一个 SEO 专家。请为技术博客的标签页面生成一段简洁的中文 description，用于 HTML meta description 标签。\n"
    "要求：\n"
    "1. 长度在 60-120 个字符之间\n"
    "2. 体现该标签涵盖的技术领域和内容范围\n"
    "3. 包含关键技术术语，有利于搜索引擎收录\n"
    "4. 不要使用引号、换行符或特殊字符\n"
    "5. 只返回 description 文本本身，不要任何前缀或解释\n"
    "\n"
    "标签名称：{tag}\n"
    "相关文章标题：\n{titles}"
)


def _detect_ollama():
    if USE_OLLAMA:
        return True
    return ':11434' in AI_API_URL


def _ollama_base_url():
    from urllib.parse import urlparse
    parsed = urlparse(AI_API_URL)
    return f"{parsed.scheme}://{parsed.netloc}"


def call_ai_api(tag, titles):
    titles_text = '\n'.join(f'- {t}' for t in titles[:20])
    prompt = PROMPT_TEMPLATE.format(tag=tag, titles=titles_text)
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
        "options": {"temperature": 0.3},
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return _clean(resp.json()['message']['content'])


def _call_openai(prompt):
    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 300,
    }
    headers = {}
    if AI_API_KEY:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"
    resp = requests.post(AI_API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return _clean(resp.json()['choices'][0]['message']['content'])


def _clean(text):
    desc = text.strip()
    desc = re.sub(r'<think>.*?</think>', '', desc, flags=re.DOTALL).strip()
    desc = desc.strip('"').strip("'").replace('\n', ' ').replace('"', '')
    return desc


def collect_tag_posts(posts_dir):
    """扫描所有文章，收集每个 tag 关联的文章标题"""
    tag_posts = {}

    for fname in os.listdir(posts_dir):
        if not fname.endswith('.md'):
            continue
        with open(os.path.join(posts_dir, fname), encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            continue
        end = content.find('---', 3)
        if end == -1:
            continue
        fm = content[3:end]

        title = ''
        for line in fm.split('\n'):
            if line.strip().startswith('title:'):
                title = line.split(':', 1)[1].strip().strip('"').strip("'")
                break
        if not title:
            continue

        in_tags = False
        for line in fm.split('\n'):
            stripped = line.strip()
            if stripped.startswith('tags:'):
                in_tags = True
                continue
            if in_tags:
                if stripped.startswith('-'):
                    tag = stripped[1:].strip().strip('"').strip("'").lower()
                    tag_posts.setdefault(tag, []).append(title)
                elif stripped and not stripped.startswith('#'):
                    in_tags = False

    return tag_posts


def index_path(tags_dir, tag):
    return os.path.join(tags_dir, tag, '_index.md')


def has_existing_description(filepath):
    if not os.path.exists(filepath):
        return False
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if stripped.startswith('description:'):
            val = stripped.split(':', 1)[1].strip().strip('"').strip("'")
            return len(val) > 0
    return False


def write_index(filepath, tag, description):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if os.path.exists(filepath):
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                desc_line = f'description: "{description}"'
                if re.search(r'^description:', content, re.MULTILINE):
                    new_content = re.sub(r'^description:.*$', desc_line, content, count=1, flags=re.MULTILINE)
                else:
                    new_content = content[:3] + f'\ndescription: "{description}"' + content[3:]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return
    # 创建新文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f'---\ntitle: "{tag}"\ndescription: "{description}"\n---\n')


def main():
    if not AI_API_KEY:
        log.error("未设置 AI_API_KEY 环境变量")
        sys.exit(1)

    mode = "Ollama" if _detect_ollama() else "OpenAI Compatible"
    log.info("API: %s (%s)", AI_API_URL, mode)
    log.info("Model: %s", AI_MODEL)

    tag_posts = collect_tag_posts(POSTS_DIR)
    tags = sorted(tag_posts.keys())
    total = len(tags)
    log.info("共 %d 个 tag", total)

    generated = 0
    skipped = 0
    failed = 0

    for i, tag in enumerate(tags):
        prefix = f"[{i+1}/{total}] {tag}"
        filepath = index_path(TAGS_DIR, tag)

        if has_existing_description(filepath):
            skipped += 1
            log.info("%s -> 跳过: 已有 description", prefix)
            continue

        titles = tag_posts[tag]
        try:
            description = call_ai_api(tag, titles)
            if not description:
                failed += 1
                log.warning("%s -> AI 返回空内容", prefix)
                continue
            write_index(filepath, tag, description)
            generated += 1
            log.info("%s (%d 篇) -> %s", prefix, len(titles), description)
        except Exception as e:
            failed += 1
            log.error("%s -> %s", prefix, e)

        time.sleep(0.5)

    log.info("完成 (共 %d 个 tag) - 生成: %d, 跳过: %d, 失败: %d", total, generated, skipped, failed)


if __name__ == '__main__':
    main()
