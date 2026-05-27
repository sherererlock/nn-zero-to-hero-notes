#!/usr/bin/env python3
"""Quick translation quality check for a translated .ipynb or .md file."""
import sys, json, re
from pathlib import Path

path = Path(sys.argv[1])
text_raw = path.read_text(encoding='utf-8')

if path.suffix == '.ipynb':
    nb = json.loads(text_raw)
    cells = nb['cells']
else:
    cells = [{'cell_type': 'markdown', 'source': [text_raw]}]

issues = []
samples = []
stats = dict(md=0, code=0, md_zh=0, formula_ok=0, formula_broken=0, code_zh=0)

for i, cell in enumerate(cells):
    src = ''.join(cell.get('source', []))
    ct = cell['cell_type']

    if ct == 'markdown':
        stats['md'] += 1
        has_zh = bool(re.search(r'[\u4e00-\u9fff]', src))
        if has_zh:
            stats['md_zh'] += 1
        else:
            issues.append(f'[Cell {i}] markdown: 无中文 (可能未翻译)')

        # formulas: $...$ should not contain Chinese
        for f in re.findall(r'\$\$[\s\S]{1,600}?\$\$|\$[^$\n]{1,200}?\$', src):
            if re.search(r'[\u4e00-\u9fff]', f):
                stats['formula_broken'] += 1
                issues.append(f'[Cell {i}] 公式含中文: {f[:60]}')
            else:
                stats['formula_ok'] += 1

        # image src/href should not be changed
        for m in re.finditer(r'<img[^>]+src="([^"]+)"', src, re.I):
            url = m.group(1)
            if re.search(r'[\u4e00-\u9fff]', url):
                issues.append(f'[Cell {i}] img src含中文: {url}')

        # long all-English lines (possible untranslated prose)
        for li, line in enumerate(src.split('\n')):
            s = line.strip()
            if (len(s) > 80
                    and re.fullmatch(r'[A-Za-z0-9 \t\.,\-\(\)\[\]\'"/:;!?@#%&*+=<>~^]+', s)
                    and not re.match(r'```|^#{1,6} |^\|', s)):
                issues.append(f'[Cell {i} L{li}] 疑似未翻译: "{s[:90]}"')

        if stats['md'] <= 6:
            samples.append((i, src[:300]))

    elif ct == 'code':
        stats['code'] += 1
        if re.search(r'[\u4e00-\u9fff]', src):
            stats['code_zh'] += 1
            issues.append(f'[Cell {i}] CODE CELL 含中文 — 不应被翻译!')

# key terminology spot-check
full_md = '\n'.join(
    ''.join(c.get('source', [])) for c in cells if c['cell_type'] == 'markdown'
)
term_pairs = [
    ('backpropagation', '反向传播'),
    ('gradient', '梯度'),
    ('neural network', '神经网络'),
    ('derivative', '导数'),
    ('loss', '损失'),
]
for en, zh in term_pairs:
    if re.search(en, full_md, re.I) and zh not in full_md:
        issues.append(f'[术语] "{en}" 出现但未见中文对应 "{zh}"')

# ---- report ----
print('=== 统计 ===')
print(f'Markdown cells : {stats["md"]}  (含中文: {stats["md_zh"]})')
print(f'Code cells     : {stats["code"]}  (含中文: {stats["code_zh"]}，应为 0)')
print(f'公式           : {stats["formula_ok"]} 正常, {stats["formula_broken"]} 异常')
print()
print('=== 问题清单 ===')
if not issues:
    print('无问题，翻译质量通过基础检查。')
else:
    for x in issues[:50]:
        print(' -', x)
print()
print('=== Markdown Cell 样本 ===')
for idx, txt in samples:
    print(f'[Cell {idx}]')
    print(txt)
    print('---')
