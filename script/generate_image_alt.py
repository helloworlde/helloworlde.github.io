# Usage:
#   AI_API_URL="http://192.168.2.121:11434/v1/chat/completions" \
#   AI_API_KEY="ollama" \
#   AI_MODEL="qwen3.5:4b" \
#   python script/generate_image_alt.py

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
CONTEXT_CHARS = 300

PROMPT_TEMPLATE = (
    "你是一个 SEO 专家。请为技术博客文章中的一张图片生成简洁的中文 alt 描述文本。\n"
    "要求：\n"
    "1. 长度在 10-50 个字符之间\n"
    "2. 准确描述图片内容，有利于无障碍访问和搜索引擎收录\n"
    "3. 不要使用引号、换行符或特殊字符\n"
    "4. 不要包含文件名或扩展名\n"
    "5. 只返回 alt 文本本身，不要任何前缀或解释\n"
    "\n"
    "文章标题：{title}\n"
    "图片文件名：{filename}\n"
    "图片上下文：\n{context}"
)

IMG_PATTERN = re.compile(r'(!\[)(.*?)(\]\()([^)]*?)(\))', re.DOTALL)


def _detect_ollama():
    if USE_OLLAMA:
        return True
    return ':11434' in AI_API_URL


def _ollama_base_url():
    from urllib.parse import urlparse
    parsed = urlparse(AI_API_URL)
    return f"{parsed.scheme}://{parsed.netloc}"


def call_ai_api(title, filename, context):
    prompt = PROMPT_TEMPLATE.format(title=title, filename=filename, context=context)
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
        "max_tokens": 150,
    }
    headers = {}
    if AI_API_KEY:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"
    resp = requests.post(AI_API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return _clean(resp.json()['choices'][0]['message']['content'])


def _clean(text):
    alt = text.strip()
    alt = re.sub(r'<think>.*?</think>', '', alt, flags=re.DOTALL).strip()
    alt = alt.strip('"').strip("'").replace('\n', ' ').replace('"', '')
    return alt


def needs_update(alt):
    """判断 alt 是否需要更新：空 alt 或文件名 alt"""
    if not alt.strip():
        return True
    if re.search(r'\.(png|jpg|jpeg|gif|webp|svg|bmp)$', alt.strip(), re.I):
        return True
    return False


def extract_filename(url):
    """从 URL 或路径中提取文件名"""
    name = url.split('/')[-1].split('?')[0]
    name = re.sub(r'\.(png|jpg|jpeg|gif|webp|svg|bmp)$', '', name, flags=re.I)
    return name


def get_context(content, match_start, match_end):
    """提取图片前后的上下文文本"""
    before = content[max(0, match_start - CONTEXT_CHARS):match_start]
    after = content[match_end:match_end + CONTEXT_CHARS]
    before = re.sub(r'!\[.*?\]\(.*?\)', '', before)
    after = re.sub(r'!\[.*?\]\(.*?\)', '', after)
    before = re.sub(r'```.*?```', '', before, flags=re.DOTALL)
    after = re.sub(r'```.*?```', '', after, flags=re.DOTALL)
    before = re.sub(r'\s+', ' ', before).strip()
    after = re.sub(r'\s+', ' ', after).strip()
    parts = []
    if before:
        parts.append(f"前文：{before}")
    if after:
        parts.append(f"后文：{after}")
    return '\n'.join(parts)


def parse_frontmatter(text):
    if not text.startswith('---'):
        return None, text
    end = text.find('---', 3)
    if end == -1:
        return None, text
    return text[3:end].strip(), text[end + 3:]


def get_title(fm_str):
    if not fm_str:
        return ''
    for line in fm_str.split('\n'):
        if line.strip().startswith('title:'):
            return line.split(':', 1)[1].strip().strip('"').strip("'")
    return ''


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    fm_str, _ = parse_frontmatter(original)
    title = get_title(fm_str)

    updated = 0
    result = original

    # 逐个匹配，记录偏移变化
    offset = 0
    for m in IMG_PATTERN.finditer(original):
        alt = m.group(2)
        url = m.group(4)

        if not needs_update(alt):
            continue

        filename = extract_filename(url)
        if not filename:
            continue

        # 在原始内容中计算上下文位置（考虑偏移）
        ctx_start = m.start() + offset
        ctx_end = m.end() + offset
        context = get_context(result, ctx_start, ctx_end)

        try:
            new_alt = call_ai_api(title, filename, context)
            if not new_alt:
                continue

            old_img = m.group(0)
            new_img = f"{m.group(1)}{new_alt}{m.group(3)}{url}{m.group(5)}"

            # 在当前 result 中替换第一个匹配
            pos = result.find(old_img, max(0, ctx_start - len(old_img) * 2))
            if pos == -1:
                pos = result.find(old_img)
            if pos == -1:
                continue

            result = result[:pos] + new_img + result[pos + len(old_img):]
            offset += len(new_img) - len(old_img)
            updated += 1

            log.info("  [%s] -> [%s]", filename[:40], new_alt)
        except Exception as e:
            log.error("  %s -> %s", filename, e)

        time.sleep(0.3)

    if updated > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result)

    return updated


def main():
    if not AI_API_KEY:
        log.error("未设置 AI_API_KEY 环境变量")
        sys.exit(1)

    mode = "Ollama" if _detect_ollama() else "OpenAI Compatible"
    log.info("API: %s (%s)", AI_API_URL, mode)
    log.info("Model: %s", AI_MODEL)
    log.info("Posts: %s", POSTS_DIR)

    files = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')])

    total_files = len(files)
    processed_files = 0
    total_updated = 0
    skipped_files = 0

    for i, fname in enumerate(files):
        filepath = os.path.join(POSTS_DIR, fname)
        prefix = f"[{i+1}/{total_files}] {fname}"

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 快速判断是否有需要更新的图片
        imgs = IMG_PATTERN.findall(content)
        need = [(alt, url) for _, alt, _, url, _ in imgs if needs_update(alt)]
        if not need:
            skipped_files += 1
            log.info("%s -> 跳过 (无需更新的图片)", prefix)
            continue

        log.info("%s -> 处理 %d 张图片", prefix, len(need))
        updated = process_file(filepath)
        total_updated += updated
        processed_files += 1

    log.info(
        "完成 (共 %d 篇) - 处理: %d, 跳过: %d, 更新图片: %d 张",
        total_files, processed_files, skipped_files, total_updated
    )


if __name__ == '__main__':
    main()
