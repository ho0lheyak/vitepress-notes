# -*- coding: utf-8 -*-
"""
Obsidian -> VitePress 笔记迁移脚本
可重复执行：再次运行会覆盖目标目录，源目录始终只读。

用法：
    python migrate-notes.py            # 正式迁移
    python migrate-notes.py --dry-run  # 只看分类结果，不写文件
"""

import argparse
import hashlib
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------- 路径配置 ----------
SOURCE = Path(r"C:\Users\14440\Desktop\新建文件夹\大三上\大三\csharp")
PROJECT = Path(r"C:\Users\14440\Desktop\新建文件夹\vitepress")
DOCS = PROJECT / "docs"
NOTES_ROOT = DOCS / "notes" / "CSharp"      # 笔记落点：docs/notes/CSharp/
IMAGE_ROOT = DOCS / "public" / "csharp"     # 图片落点：docs/public/csharp/

# ---------- 分类规则 ----------
# 按文件名（不含扩展名）匹配关键词，从上到下第一个命中者生效。
# 未命中的归入「其他」。
CATEGORIES = [
    ("01-基础语法", [
        "基础语法", "总体语法", "花括号和分号", "布尔类型", "数组",
        "枚举类型", "自动类型推导", "静态主函数", "自带函数区别",
        "强类型禁止隐式转换",
    ]),
    ("02-类型系统", [
        "引用类型", "值类型", "装箱和拆箱", "结构体", "object",
        "new-引用类型", "托管引用", "堆和栈", "对齐",
        "隐式收缩转换", "自定义类型转换", "readonly",
    ]),
    ("03-面向对象", [
        "类/", "抽象类", "虚函数", "多态", "继承", "访问修饰符",
        "构造函数", "析构方法", "属性", "方法的重写", "静态字段",
        "命名方法",
    ]),
    ("04-泛型", ["泛型"]),
    ("05-委托与事件", ["委托", "事件"]),
    ("06-进阶", ["LINQ", "运算符重载", "方法参数"]),
]

# 源文件相对路径 -> 强制归类（优先于关键词匹配）
# 让子目录里的笔记落到对应分类
PATH_OVERRIDES = {
    "泛型": "04-泛型",
    "类": "03-面向对象",
}

# Obsidian 图片语法：![[xxx.png]] 或 ![[xxx.png|宽]]
WIKI_IMAGE = re.compile(r"!\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")
# 标准 Markdown 图片：![alt](path)
MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
# Obsidian 内部双链：[[note]] 或 [[note|别名]]
WIKI_LINK = re.compile(r"(?<!!)\[\[([^\]|]+?)(?:\|([^\]]+))?\]\]")


def slug_safe(name: str) -> str:
    """把文件名转成安全的 URL 片段，保留中文。"""
    return name.strip().replace("\\", "-").replace("/", "-")


def classify(rel_path: Path) -> str:
    """决定一篇笔记归入哪个分类目录。"""
    parts = rel_path.parts
    # 1. 子目录强制归类
    if len(parts) > 1:
        top = parts[0]
        if top in PATH_OVERRIDES:
            return PATH_OVERRIDES[top]
    # 2. 关键词匹配（对完整相对路径匹配，便于命中 "类/"）
    joined = "/".join(parts)
    for category, keywords in CATEGORIES:
        for kw in keywords:
            if kw in joined or kw in rel_path.stem:
                return category
    return "99-其他"


def read_text(path: Path) -> str:
    """按多种编码尝试读取，返回文本。"""
    for enc in ("utf-8-sig", "utf-8", "gbk", "utf-16"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def convert_images(text: str, image_map: dict, warnings: list, note_name: str) -> str:
    """把 Obsidian 图片语法转成 VitePress 能识别的标准语法。"""

    def wiki_repl(m: re.Match) -> str:
        raw_name = m.group(1).strip()
        alt = (m.group(2) or "").strip()
        # 源里写的可能只是文件名，也可能带路径
        key = Path(raw_name).name
        if key in image_map:
            url = image_map[key]
            label = alt if alt and not alt.isdigit() else Path(key).stem
            return f"![{label}]({url})"
        warnings.append(f"图片未找到: {raw_name}  (来自 {note_name})")
        return f"<!-- 缺失图片: {raw_name} -->"

    text = WIKI_IMAGE.sub(wiki_repl, text)

    # 标准语法里若指向相对路径的本地图片，也重写为 public 路径
    def md_repl(m: re.Match) -> str:
        alt, src = m.group(1), m.group(2).strip()
        if src.startswith(("http://", "https://", "/", "data:")):
            return m.group(0)
        key = Path(src).name
        if key in image_map:
            return f"![{alt}]({image_map[key]})"
        return m.group(0)

    text = MD_IMAGE.sub(md_repl, text)
    return text


def convert_wikilinks(text: str, note_index: dict, warnings: list, note_name: str) -> str:
    """把 Obsidian 双链 [[note]] 转成普通文字（无法可靠解析为 URL）。"""

    def repl(m: re.Match) -> str:
        target = m.group(1).strip()
        alias = (m.group(2) or "").strip()
        label = alias or Path(target).name
        if Path(target).name not in note_index:
            warnings.append(f"双链目标未找到: {target}  (来自 {note_name})")
        return label

    return WIKI_LINK.sub(repl, text)


def yaml_quote(value: str) -> str:
    """把字符串安全地放进 YAML 双引号里。

    YAML 对很多字符敏感：{} 是流式映射、: 和 # 是分隔符、开头是数字的
    会被当成日期或数字。统一加双引号并转义，最省心。
    """
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", " ").replace("\r", " ").strip()
    return f'"{escaped}"'


def escape_angle_brackets(text: str) -> str:
    """转义代码块之外的裸尖括号。

    VitePress 的 Markdown 会被 Vue 编译，正文里像 list<int> 这样的写法
    会被当成 HTML 标签，导致 "Element is missing end tag" 构建失败。
    这里只处理围栏代码块之外的内容，块内保持原样（本就安全）。
    """
    out_lines: list[str] = []
    fence = None

    for line in text.splitlines():
        stripped = line.lstrip()
        # 进入 / 退出围栏代码块
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            out_lines.append(line)
            continue

        if fence is not None:
            out_lines.append(line)      # 代码块内不动
            continue

        # 行内代码 `...` 段先保护起来
        parts = re.split(r"(`[^`]*`)", line)
        for i in range(0, len(parts), 2):   # 偶数索引 = 非行内代码
            seg = parts[i]
            # 只转义"看起来像标签"的尖括号：< 紧跟字母或 /
            seg = re.sub(r"<(?=[A-Za-z/])", "&lt;", seg)
            # 泛型收尾的 >：前面是标识符，且不是 HTML 闭合标签的一部分
            seg = re.sub(r"(?<=[A-Za-z0-9_])>(?![^<]*</)", "&gt;", seg)
            parts[i] = seg
        out_lines.append("".join(parts))

    result = "\n".join(out_lines)
    if text.endswith("\n"):
        result += "\n"
    return result


def escape_bare_brackets(text: str) -> str:
    """转义不是链接的裸方括号。

    像 bool[]() 这种写法，Markdown 会把 `[]()` 当成链接语法，
    生成一个指向空地址的链接（渲染后变成 ./index），导致死链报错。
    这里把紧邻成对、内容为空的 [] 转义掉。
    """
    out_lines: list[str] = []
    fence = None

    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            out_lines.append(line)
            continue

        if fence is not None:
            out_lines.append(line)
            continue

        # 保护行内代码
        parts = re.split(r"(`[^`]*`)", line)
        for i in range(0, len(parts), 2):
            seg = parts[i]
            # [] 后紧跟 () 或 （） ：不是真链接
            seg = seg.replace("[]()", r"\[\]()")
            seg = seg.replace("[]（）", r"\[\]（）")
            # 孤立的 [] 且后面不是 ( ：防止被当作引用式链接
            seg = re.sub(r"\[\](?!\()", r"\\[\\]", seg)
            parts[i] = seg
        out_lines.append("".join(parts))

    result = "\n".join(out_lines)
    if text.endswith("\n"):
        result += "\n"
    return result


def build_frontmatter(title: str, description: str, date_str: str, tags: list) -> str:
    lines = ["---"]
    lines.append(f"title: {yaml_quote(title)}")
    if description:
        lines.append(f"description: {yaml_quote(description)}")
    if date_str:
        # 必须加引号：不加会被 YAML 解析成日期对象
        lines.append(f"date: {yaml_quote(date_str)}")
    if tags:
        quoted = ", ".join(yaml_quote(t) for t in tags)
        lines.append(f"tags: [{quoted}]")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def extract_summary(body: str, limit: int = 80) -> str:
    """从正文里抽一句话当摘要。"""
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "!", "|", ">", "```", "-", "*", "<!--")):
            continue
        s = re.sub(r"[`*_\[\]{}()]", "", s).strip()
        # YAML 里冒号加空格会破坏结构，替换掉
        s = s.replace(": ", "：").replace("\t", " ")
        if len(s) < 4:
            continue
        return s[:limit] + ("…" if len(s) > limit else "")
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只显示分类结果，不写文件")
    args = ap.parse_args()

    if not SOURCE.is_dir():
        print(f"[错误] 源目录不存在: {SOURCE}")
        return 1

    # ---- 1. 收集源文件 ----
    md_files = sorted(p for p in SOURCE.rglob("*.md") if p.is_file())
    img_files = sorted(p for p in SOURCE.rglob("*.png") if p.is_file())

    # ---- 2. 过滤空文件 ----
    skipped: list[str] = []
    valid_md = []
    for p in md_files:
        if p.stat().st_size == 0:
            skipped.append(str(p.relative_to(SOURCE)))
            continue
        valid_md.append(p)

    print("=" * 62)
    print(f"源目录: {SOURCE}")
    print(f"Markdown: {len(md_files)} 篇（有效 {len(valid_md)}，跳过空文件 {len(skipped)}）")
    print(f"图片:     {len(img_files)} 张")
    if skipped:
        print(f"跳过的空文件: {', '.join(skipped)}")
    print("=" * 62)

    # ---- 3. 规划输出路径 ----
    # 图片统一放到 docs/public/csharp/，同名冲突加后缀
    image_map: dict[str, str] = {}
    img_plan: list[tuple[Path, Path]] = []
    used_names: dict[str, int] = {}
    for img in img_files:
        name = img.name
        if name in used_names:
            used_names[name] += 1
            stem, suf = img.stem, img.suffix
            name = f"{stem}-{used_names[name]}{suf}"
        else:
            used_names[name] = 0
        dest = IMAGE_ROOT / name
        image_map[img.name] = f"/csharp/{name}"
        img_plan.append((img, dest))

    # 笔记输出路径
    note_plan: list[tuple[Path, Path, str]] = []
    note_index: dict[str, str] = {}
    name_conflicts: dict[str, int] = {}
    for md in valid_md:
        rel = md.relative_to(SOURCE)
        category = classify(rel)
        stem = slug_safe(md.stem)
        # 同名笔记去重
        if stem in name_conflicts:
            name_conflicts[stem] += 1
            stem = f"{stem}-{name_conflicts[stem]}"
        else:
            name_conflicts[stem] = 0
        dest = NOTES_ROOT / category / f"{stem}.md"
        note_plan.append((md, dest, category))
        note_index[md.stem] = stem

    # ---- 4. 分类结果预览 ----
    from collections import defaultdict
    grouped = defaultdict(list)
    for md, dest, category in note_plan:
        grouped[category].append(md.stem)

    print("\n分类结果:")
    for category in sorted(grouped):
        print(f"\n  【{category}】{len(grouped[category])} 篇")
        for title in grouped[category]:
            print(f"      - {title}")

    if args.dry_run:
        print("\n[dry-run] 未写入任何文件。")
        return 0

    # ---- 5. 写入 ----
    warnings: list[str] = []
    if NOTES_ROOT.exists():
        shutil.rmtree(NOTES_ROOT)
    if IMAGE_ROOT.exists():
        shutil.rmtree(IMAGE_ROOT)
    NOTES_ROOT.mkdir(parents=True, exist_ok=True)
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)

    # 5a. 复制图片
    for src, dest in img_plan:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    # 5b. 处理笔记
    written = 0
    for src, dest, category in note_plan:
        raw = read_text(src)
        # 已有 front-matter 就不再重复注入
        has_fm = raw.lstrip().startswith("---\n")

        body = raw
        if has_fm:
            end = raw.find("\n---", 3)
            body = raw[end + 4:].lstrip("\n") if end != -1 else raw

        # 顺序很重要：先处理 Obsidian 图片语法，再转义其余的裸方括号
        body = convert_images(body, image_map, warnings, src.name)
        body = convert_wikilinks(body, note_index, warnings, src.name)
        body = escape_angle_brackets(body)
        body = escape_bare_brackets(body)

        if has_fm:
            content = convert_images(raw, image_map, warnings, src.name)
            content = convert_wikilinks(content, note_index, warnings, src.name)
            content = escape_angle_brackets(content)
            content = escape_bare_brackets(content)
        else:
            mtime = datetime.fromtimestamp(src.stat().st_mtime, tz=timezone.utc)
            date_str = mtime.astimezone().strftime("%Y-%m-%d")
            summary = extract_summary(body)
            tag = category.split("-", 1)[-1]
            fm = build_frontmatter(src.stem, summary, date_str, [tag])
            content = fm + body.lstrip("\n")

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        written += 1

    # ---- 6. 报告 ----
    print("\n" + "=" * 62)
    print(f"完成：写入 {written} 篇笔记，复制 {len(img_plan)} 张图片")
    print(f"笔记位置: {NOTES_ROOT}")
    print(f"图片位置: {IMAGE_ROOT}")
    if warnings:
        print(f"\n警告 {len(warnings)} 条:")
        for w in warnings[:20]:
            print(f"  ! {w}")
        if len(warnings) > 20:
            print(f"  ... 另有 {len(warnings) - 20} 条")
    else:
        print("无警告，所有图片和链接都解析成功。")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
