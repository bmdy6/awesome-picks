#!/usr/bin/env python3
"""Validate repos.yaml and generate README. Requires PyYAML 6.0.3."""
import argparse
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
TIERS = ('精选', '值得看', '看过没选')
STATUSES = ('在用', '试过', '收藏')


def validate(data):
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(isinstance(data, dict) and set(data) == {'updated_at', 'repos', 'own_projects'}, 'invalid top-level fields')
    require(isinstance(data['updated_at'], str), 'updated_at must be a date string')
    date.fromisoformat(data['updated_at'])
    seen = set()
    for group, fields in [('repos', {'repo', 'category', 'tier', 'what', 'verdict', 'status'}), ('own_projects', {'repo', 'what'})]:
        require(isinstance(data[group], list) and data[group], f'{group} must be a nonempty list')
        for row in data[group]:
            require(isinstance(row, dict) and set(row) == fields, f'{group}: invalid fields')
            require(all(isinstance(v, str) and v.strip() and '\n' not in v for v in row.values()), 'all fields must be nonempty single-line strings')
            repo = row['repo']
            require(re.fullmatch(r'[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', repo) is not None, f'invalid repo: {repo}')
            require(repo.lower() not in seen, f'duplicate repo: {repo}')
            seen.add(repo.lower())
            require(repo.lower() != 'eolix/photosuite', 'restricted repository')
            if group == 'repos':
                require(row['tier'] in TIERS and row['status'] in STATUSES, f'invalid tier/status: {repo}')
                require(row['verdict'] != '收藏待试', f'missing reason: {repo}')
                require(row['what'] != row['verdict'], f'duplicate description/reason: {repo}')
            else:
                require(repo.startswith('bmdy6/'), 'own projects must belong to bmdy6')


def cell(text):
    return escape(text, quote=False).replace('|', '&#124;')


def table(rows):
    lines = ['| 项目 | 是什么 | 为什么收藏 | 状态 |', '| --- | --- | --- | --- |']
    for r in sorted(rows, key=lambda x: x['repo'].lower()):
        lines.append(f"| [{r['repo']}](https://github.com/{r['repo']}) | {cell(r['what'])} | {cell(r['verdict'])} | {r['status']} |")
    return lines


def starter_cards(repos):
    picks = ['stablyai/orca', 'NousResearch/hermes-agent', 'obra/superpowers',
             'farion1231/cc-switch', 'exa-labs/exa-mcp-server', 'Panniantong/Agent-Reach']
    selected = [next(r for r in repos if r['repo'] == name and r['tier'] == '精选') for name in picks]
    lines = ['## 从这几个开始', '', '<table>']
    for i in range(0, len(selected), 2):
        lines.append('<tr>')
        for row in selected[i:i + 2]:
            name = row['repo']
            lines.append(f'<td width="50%" valign="top"><a href="https://github.com/{name}"><img src="https://opengraph.githubassets.com/1/{name}" width="400" alt="{name} GitHub 仓库社交图"></a><br><strong><a href="https://github.com/{name}">{name}</a></strong> · {row["status"]}<br>{cell(row["what"])}</td>')
        lines.append('</tr>')
    return lines + ['</table>', '']


def render(data):
    validate(data)
    repos, own = data['repos'], data['own_projects']
    categories = list(dict.fromkeys(r['category'] for r in repos))
    tiers = Counter(r['tier'] for r in repos)
    lines = ['# Awesome Picks', '', '我的 GitHub 项目收藏，按用途保留亮点、取舍和使用状态。', '',
             '- **精选**：有主动收藏、star、正面判断或有效试用记录。',
             '- **值得看**：有阅读、讨论或调研线索，尚未形成采用结论。',
             '- **看过没选**：保留当时暂缓或不用的理由，只针对原场景。', '',
             '状态只用 **在用 / 试过 / 收藏**；收藏不代表已试用，历史试用也不代表持续在用。',
             '“为什么收藏”优先保留已有判断；缺少判断时概括仓库 README 的客观亮点，不代表效果已经验证。', '', *starter_cards(repos), '## 目录', '']
    lines += [f'- [{category}](#category-{i})' for i, category in enumerate(categories, 1)]
    lines += ['- [我自己的项目](#own-projects)', '- [维护方式](#maintenance)', '',
              f"外部项目 **{len(repos)}** 个：精选 {tiers['精选']}、值得看 {tiers['值得看']}、看过没选 {tiers['看过没选']}；自有公开项目 **{len(own)}** 个。", f"整理日期：{data['updated_at']}。", '']
    for i, category in enumerate(categories, 1):
        lines += [f'<a id="category-{i}"></a>', '', f'## {category}', '']
        for tier in ('精选', '看过没选', '值得看'):
            rows = [r for r in repos if r['category'] == category and r['tier'] == tier]
            if not rows:
                continue
            if tier == '值得看':
                lines += [f'<details><summary>值得看（{len(rows)}）</summary>', '']
            else:
                lines += [f'### {tier}（{len(rows)}）', '']
            lines += table(rows) + ['']
            if tier == '值得看':
                lines += ['</details>', '']
    lines += ['', '<a id="maintenance"></a>', '', '## 维护方式', '',
              '唯一数据源是 [data/repos.yaml](data/repos.yaml)，请勿手改生成的 README。', '',
              '新增项目时填写 `repo`、`category`、`tier`、`what`、`verdict`（为什么收藏）、`status`；没有试用证据时状态填“收藏”。', '',
              '```bash', 'python3 -m pip install PyYAML==6.0.3', 'python3 scripts/build_readme.py', 'python3 scripts/build_readme.py --check', '```', '',
              'CI 校验 YAML 字段与 README 是否同步。公开数据不保存私人路径、浏览记录、会话原文或来源证据字段。', '',
              '本清单采用 [CC0-1.0](LICENSE)；所链接项目按各自条款使用。']
    lines += ['<a id="own-projects"></a>', '', '## 我自己的项目', '', '这里只列公开仓库，不推断使用频率。', '', '| 项目 | 是什么 |', '| --- | --- |']
    lines += [f"| [{r['repo']}](https://github.com/{r['repo']}) | {cell(r['what'])} |" for r in own]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='validate without writing and fail if README differs')
    args = parser.parse_args()
    try:
        content = render(yaml.safe_load((ROOT / 'data/repos.yaml').read_text(encoding='utf-8')))
        target = ROOT / 'README.md'
        if args.check:
            if not target.exists() or target.read_text(encoding='utf-8') != content:
                raise ValueError('README differs; run python3 scripts/build_readme.py')
        else:
            target.write_text(content, encoding='utf-8')
    except (ValueError, yaml.YAMLError) as exc:
        print(f'Validation failed: {exc}', file=sys.stderr)
        return 1
    print('YAML and README OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
