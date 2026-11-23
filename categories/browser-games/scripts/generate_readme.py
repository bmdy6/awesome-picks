#!/usr/bin/env python3
"""Generate README from data/games.json. Standard library only."""
from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "games.json"
README = ROOT / "README.md"
PAGES = "https://bmdy6.github.io/awesome-browser-games-zh/"


def clean(s: str) -> str:
    return s.replace("|", r"\|").replace("\n", " ").strip()


def source_badge(game: dict) -> str:
    if game["source_status"] == "open":
        return f"[代码]({game['source_url']})"
    if game["source_status"] == "unavailable":
        return "⚠️ 源码链接待恢复"
    if game["source_status"] == "unknown":
        return f"[源码公开，许可待核]({game['source_url']})"
    return "未提供"


def chinese_badge(game: dict) -> str:
    return {"yes": "✅ 已确认", "partial": "🟡 部分中文", "unknown": "待核对"}[game["zh_status"]]


def cover(game: dict, width: int = 200) -> str:
    name = escape(game["name"], quote=True)
    url = escape(game["play_url"], quote=True)
    image = escape(game.get("cover_url", ""), quote=True)
    if image:
        return f'<a href="{url}"><img src="{image}" width="{width}" height="{round(width * 9 / 16)}" alt="{name} 官方图片"></a>'
    return f'<a href="{url}"><strong>🎮 {name}</strong><br>官方图片暂缺 · 点击游玩</a>'


def generate(data: dict) -> str:
    cats = [x for x in data["categories"] if x["id"] != "all"]
    games = data["games"]
    featured = [x for x in games if x["featured"]]
    lines = [
        "# 🎮 Awesome Browser Games 中文精选",
        "",
        "> **好游戏，点开就玩。** 从 INKWAVE 涂地、坦克对战，到红警、无双、领土争夺。",
        "> 只精选让人想玩的网页版游戏，既收开源作品，也收非开源官方游戏。**不托管游戏安装包或未经许可的资源**。",
        "",
        f"### 🕹️ [打开网页游戏馆，按分类探索 →]({PAGES})",
        "",
        f"**{len(games)} 款精选 · {len(cats)} 类玩法 · 中文简介 · 官方入口**",
        "",
        "> **状态说明（2026-11-09）**：游戏官网、开源仓库和公开介绍已做初步核对；尚未逐个在真实浏览器中进入对局验收。网站可能受网络、账户、WebGL/移动设备和服务器状态影响。有源码不表示第三方角色、美术、音乐可任意修改或转载。",
        "",
        "## ✨ 从这几款开始",
        "",
        "<table>",
    ]
    for i in range(0, len(featured), 2):
        lines.append("<tr>")
        for game in featured[i:i + 2]:
            title = clean(game["name"])
            image = game.get("cover_url", "")
            content = (
                '<td width="50%" valign="top">'
                + cover(game, 320) + "<br>"
                + f'<strong>{title}</strong><br>'
                + f'{clean(game["summary"])}<br>'
                + f'<a href="{game["play_url"]}">▶ 官方试玩</a>'
                + (f' · <a href="{game["source_url"]}">源码</a>' if game["source_status"] == "open" else "")
                + "</td>"
            )
            lines.append(content)
        lines.append("</tr>")
    lines.extend(["</table>", "",
                  "## 📚 按玩法找游戏", "",
                  " · ".join(f"[{c['emoji']} {c['name']}](#{c['id']})" for c in cats), ""])
    for c in cats:
        within = [g for g in games if g["category"] == c["id"]]
        lines.extend([
            f'<a id="{c["id"]}"></a>',
            f"### {c['emoji']} {c['name']}（{len(within)}）",
            "",
            "| 官方图片 | 游戏 | 为什么值得试 | 入口 | 源码 | 中文 |",
            "| --- | --- | --- | --- | --- | --- |",
        ])
        for game in within:
            name = clean(game["name"])
            reason = clean(game["summary"])
            note = clean(game["note"]) if game.get("note") else ""
            if note:
                reason += f"<br><small>ℹ️ {note}</small>"
            lines.append(
                f"| {cover(game)} | **{name}** | {reason} | [🎮 去玩]({game['play_url']}) "
                f"| {source_badge(game)} | {chinese_badge(game)} |"
            )
        lines.append("")
    lines.extend([
        "## 🧭 这是什么？",
        "",
        "- **导航，不是资源分发站**：只链接原作者或官方游玩页面，不收 ROM、破解包、游戏素材重托管。",
        "- **按玩家兴趣收录**：优先射击、坦克、战争策略、动作、沙盒和联机；经典老作只要仍然好玩，也欢迎。",
        "- **热门不等于 GitHub Star**：综合玩法独特性、公开玩家体验、项目活跃度和入口稳定性判断。当前是人工编辑首批候选，没有声称已完成集体好评统计。",
        "- **中文化是下一阶段**：先记下中文状态，只有在源码、许可证和原作者贡献流程确认后，才考虑提交中文翻译或做独立汉化。",
        "- **可玩性逐条验收**：网页目前仅代表公开页面和源码介绍已核实，未表示实际对局已测试。欢迎提供日期、浏览器与地区的实玩反馈。",
        "",
        "## 🙌 一起收藏好游戏",
        "",
        "发现好玩的网页游戏？[新建游戏推荐 Issue](https://github.com/bmdy6/awesome-browser-games-zh/issues/new/choose)，提供官方试玩链接和你实际体验过的理由；失效链接也欢迎反馈。",
        "",
        "仓库数据在 [data/games.json](data/games.json)，网站不依赖任何构建框架。添加新游戏后运行 python3 scripts/generate_readme.py，再 python3 -m unittest discover -s tests -v。",
        "",
        "详见 [贡献指南](CONTRIBUTING.md)、[来源与素材说明](SOURCES.md)。",
        "",
        "## 🛡️ 版权与免责声明",
        "",
        "所有游戏商标、角色、画面、音乐及截图归各自权利人所有。本仓库不是其官方合作伙伴。项目图片仅引用原项目公开 URL，且明确注明出处；原项目不希望被引用时可提交 Issue 删除。代码与游戏资源授权需要分别核实，不得直接把开源代码许可证套到游戏素材上。",
        "",
        "_最近整理：2026-11-09。_",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if README is not generated from the current JSON")
    args = parser.parse_args()
    text = generate(json.loads(DATA.read_text(encoding="utf-8")))
    if args.check:
        if not README.exists() or README.read_text(encoding="utf-8") != text:
            print("README is out of date. Run python3 scripts/generate_readme.py", file=sys.stderr)
            return 1
        print("README sync: OK")
        return 0
    README.write_text(text, encoding="utf-8")
    print(f"Wrote {README}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
