# Usage:
#   python script/update_lastmod.py
#
# Options (env vars):
#   POSTS_DIR   - posts directory (default: content/posts)
#   FORCE       - set to 1 to update even if lastmod already matches (default: 0)

import os
import re
import sys
import logging
import subprocess
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger(__name__)

POSTS_DIR = os.environ.get('POSTS_DIR', 'content/posts')
FORCE = os.environ.get('FORCE', '').lower() in ('1', 'true', 'yes')


def get_git_lastmod(filepath):
    result = subprocess.run(
        ['git', 'log', '-1', '--format=%cI', '--', filepath],
        capture_output=True, text=True
    )
    raw = result.stdout.strip()
    if not raw:
        return None
    dt = datetime.fromisoformat(raw).astimezone(timezone.utc)
    return dt.strftime('%Y-%m-%d')


def update_lastmod(filepath, date_str):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return 'no-frontmatter'

    end = content.find('---', 3)
    if end == -1:
        return 'no-frontmatter'

    fm = content[3:end]

    match = re.search(r'^lastmod:\s*(\S+)', fm, re.MULTILINE)
    if match:
        current = match.group(1).strip()
        if not FORCE and current == date_str:
            return 'skip'
        new_fm = re.sub(r'^lastmod:\s*\S+', f'lastmod: {date_str}', fm, count=1, flags=re.MULTILINE)
    else:
        new_fm = re.sub(r'^(date:\s*\S+)', rf'\1\nlastmod: {date_str}', fm, count=1, flags=re.MULTILINE)
        if new_fm == fm:
            return 'skip'

    new_content = '---' + new_fm + content[end:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return date_str


def main():
    if not os.path.isdir(POSTS_DIR):
        log.error("目录不存在: %s", POSTS_DIR)
        sys.exit(1)

    files = sorted(f for f in os.listdir(POSTS_DIR) if f.endswith('.md'))
    total = len(files)
    updated = skipped = failed = 0

    for i, fname in enumerate(files):
        filepath = os.path.join(POSTS_DIR, fname)
        prefix = f"[{i+1}/{total}] {fname}"

        date_str = get_git_lastmod(filepath)
        if not date_str:
            skipped += 1
            log.info("%s -> 跳过: 无 git 提交记录", prefix)
            continue

        result = update_lastmod(filepath, date_str)
        if result == 'no-frontmatter':
            skipped += 1
            log.info("%s -> 跳过: 无 frontmatter", prefix)
        elif result == 'skip':
            skipped += 1
            log.debug("%s -> 跳过: lastmod 已是最新 (%s)", prefix, date_str)
        else:
            updated += 1
            log.info("%s -> lastmod: %s", prefix, result)

    log.info("完成 (共 %d 篇) - 更新: %d, 跳过: %d, 失败: %d", total, updated, skipped, failed)


if __name__ == '__main__':
    main()
