#!/usr/bin/env python3
"""
Copy local images referenced in a .md or .ipynb source file to the
translation/zh/ mirror directory.

Usage (run from repo root):
    python .trae/skills/translation-1.0.1/copy_images.py <source_file>

Example:
    python .trae/skills/translation-1.0.1/copy_images.py \
        "N001 - Building Micrograd/N001 - Micrograd.ipynb"
    python .trae/skills/translation-1.0.1/copy_images.py \
        "G001 - Deep Dive into LLMs/G001 - Deep Dive into LLMs.md"
"""

import sys
import re
import json
import shutil
from pathlib import Path
from urllib.parse import unquote


def extract_local_images(text: str) -> set[str]:
    """Return relative image paths that are NOT remote URLs."""
    found = set()
    # <img src="..."> — exclude http/https/protocol-relative
    for m in re.finditer(r'<img\s[^>]*src="([^"]+)"', text, re.IGNORECASE):
        url = m.group(1)
        if not re.match(r'https?://|//', url):
            found.add(url)
    # ![alt](path) — exclude http/https
    for m in re.finditer(r'!\[[^\]]*\]\((?!https?://)([^)\s]+)\)', text):
        found.add(m.group(1))
    return found


def collect_markdown_texts(src_file: Path) -> list[str]:
    """Return a list of markdown text blocks from the source file."""
    suffix = src_file.suffix.lower()
    if suffix == '.md':
        return [src_file.read_text(encoding='utf-8')]
    if suffix == '.ipynb':
        nb = json.loads(src_file.read_text(encoding='utf-8'))
        return [
            ''.join(cell.get('source', []))
            for cell in nb.get('cells', [])
            if cell.get('cell_type') == 'markdown'
        ]
    print(f"[copy_images] Unsupported file type: {suffix}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src_file = Path(sys.argv[1])
    repo_root = Path.cwd()

    # Resolve to absolute; compute relative path from repo root
    src_abs = (repo_root / src_file).resolve()
    if not src_abs.exists():
        print(f"[copy_images] Error: file not found: {src_abs}", file=sys.stderr)
        sys.exit(1)

    try:
        rel = src_abs.relative_to(repo_root.resolve())
    except ValueError:
        rel = src_file  # already relative-looking

    src_dir = src_abs.parent
    dst_parent = repo_root / 'translation' / 'zh' / rel.parent

    # Collect all markdown text blocks
    texts = collect_markdown_texts(src_abs)

    # Extract local image paths
    all_images: set[str] = set()
    for text in texts:
        all_images.update(extract_local_images(text))

    if not all_images:
        print('[copy_images] No local images found — nothing to copy.')
        return

    copied: list[str] = []
    missing: list[str] = []

    for img_rel in sorted(all_images):
        # URL-decode path (e.g. %20 → space, handles cross-chapter refs like ../N008%20-...)
        img_decoded = unquote(img_rel)
        src_img = (src_dir / img_decoded).resolve()

        if not src_img.exists():
            missing.append(img_rel)
            continue

        # Compute destination: mirror resolved path under translation/zh/
        try:
            src_img_rel = src_img.relative_to(repo_root.resolve())
        except ValueError:
            # Outside repo root — skip
            missing.append(f'{img_rel} (outside repo root)')
            continue

        dst_img = repo_root / 'translation' / 'zh' / src_img_rel
        dst_img.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_img, dst_img)
        copied.append(str(src_img_rel))

    # Summary
    print(f'[copy_images] Source : {rel}')
    print(f'[copy_images] Target : translation/zh/{rel.parent}/')
    if copied:
        print(f'[copy_images] Copied  : {len(copied)} image(s)')
        for p in copied:
            print(f'              {p}')
    if missing:
        print(f'[copy_images] Missing : {len(missing)} image(s) not found in source')
        for p in missing:
            print(f'              {p}')
    if not copied and not missing:
        print('[copy_images] No images to copy.')


if __name__ == '__main__':
    main()
