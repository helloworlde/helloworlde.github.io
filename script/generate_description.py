import os
import sys
import re
import time
import json
import urllib.request
import urllib.error

AI_API_URL = os.environ.get('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
AI_API_KEY = os.environ.get('AI_API_KEY', '')
AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4o-mini')
USE_OLLAMA = os.environ.get('USE_OLLAMA', '').lower() in ('1', 'true', 'yes')

POSTS_DIR = os.environ.get('POSTS_DIR', 'content/posts')
MAX_CONTENT_CHARS = 3000
PROMPT_TEMPLATE = (
    "你是一个 SEO 专家。请为以下技术博客文章生成一段简洁的中文 description，用于 HTML meta description 标签。\n"
    "要求：\n"
    "1. 长度在 80-150 个字符之间\n"
    "2. 提炼文章的核心内容和价值\n"
    "3. 包含关键技术术语，有利于搜索引擎收录\n"
    "4. 不要使用引号、换行符或特殊字符\n"
    "5. 只返回 description 文本本身，不要任何前缀或解释\n"
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
    fm = text[3:end].strip()
    body = text[end + 3:].strip()
    return fm, body, end + 3


def has_description(fm_str):
    for line in fm_str.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if stripped.startswith('description:'):
            val = stripped.split(':', 1)[1].strip().strip('"').strip("'")
            return len(val) > 10
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
    payload = json.dumps({
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,
        "options": {"temperature": 0.3},
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method='POST')
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    return _clean_desc(data['message']['content'])


def _call_openai(prompt):
    payload = json.dumps({
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 500,
    }).encode('utf-8')

    headers = {"Content-Type": "application/json"}
    if AI_API_KEY:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    req = urllib.request.Request(AI_API_URL, data=payload, headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    return _clean_desc(data['choices'][0]['message']['content'])


def _clean_desc(text):
    desc = text.strip()
    desc = re.sub(r'<think>.*?</think>', '', desc, flags=re.DOTALL).strip()
    desc = desc.strip('"').strip("'").replace('\n', ' ').replace('"', '')
    return desc


def update_frontmatter(filepath, description):
    if not description:
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fm_str, _, _ = parse_frontmatter(content)
    if fm_str is None:
        return False

    desc_line = f'description: "{description}"'

    if re.search(r'^description:\s', content, re.MULTILINE):
        new_content = re.sub(r'^description:\s.*$', desc_line, content, count=1, flags=re.MULTILINE)
    elif re.search(r'^#\s*description:\s', content, re.MULTILINE):
        new_content = re.sub(r'^#\s*description:\s.*$', desc_line, content, count=1, flags=re.MULTILINE)
    elif re.search(r'^title:', content, re.MULTILINE):
        new_content = re.sub(
            r'^(title:)',
            f'{desc_line}\n\\1',
            content, count=1, flags=re.MULTILINE
        )
    else:
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


def get_title(fm_str):
    for line in fm_str.split('\n'):
        if line.strip().startswith('title:'):
            return line.split(':', 1)[1].strip().strip('"').strip("'")
    return ''


def main():
    if not AI_API_KEY:
        print("错误: 未设置 AI_API_KEY 环境变量")
        sys.exit(1)

    mode = "Ollama" if _detect_ollama() else "OpenAI Compatible"
    print(f"API: {AI_API_URL} ({mode})")
    print(f"Model: {AI_MODEL}")
    print(f"Posts: {POSTS_DIR}")
    print()

    files = sorted([
        f for f in os.listdir(POSTS_DIR) if f.endswith('.md')
    ])

    total = len(files)
    processed = 0
    skipped = 0
    failed = 0

    for i, fname in enumerate(files):
        filepath = os.path.join(POSTS_DIR, fname)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        fm_str, body, _ = parse_frontmatter(content)
        if fm_str is None:
            skipped += 1
            continue

        if has_description(fm_str):
            skipped += 1
            continue

        title = get_title(fm_str)
        if not title:
            skipped += 1
            continue

        print(f"[{i+1}/{total}] {title}")

        try:
            description = call_ai_api(title, body)
            if not description:
                failed += 1
                print(f"  -> AI 返回空内容，跳过")
                continue
            if update_frontmatter(filepath, description):
                processed += 1
                print(f"  -> {description}")
            else:
                failed += 1
                print(f"  -> 写入失败")
        except Exception as e:
            failed += 1
            print(f"  -> 错误: {e}")

        time.sleep(0.5)

    print(f"\n--- 完成 ---")
    print(f"生成: {processed}, 跳过: {skipped}, 失败: {failed}")


if __name__ == '__main__':
    main()
