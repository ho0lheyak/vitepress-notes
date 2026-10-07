# 我的笔记（VitePress）

一个纯本地、用 Git 管版本的笔记站。写 Markdown，工具负责生成网站。

## 快速开始

```bash
npm install          # 首次运行装依赖
npm run docs:dev     # 本地预览 → http://localhost:5173/
```

浏览器打开 http://localhost:5173/ ，改任何 `.md` 文件保存即自动刷新。

## 新增一篇笔记

在 `docs/notes/` 下按主题建文件夹，放一个 `.md` 文件：

```md
---
title: 笔记标题
description: 一句话说明，会显示在列表里
date: 2026-02-15
tags: [标签一, 标签二]
---

正文……
```

**不用改任何配置**，保存后：

- 左侧侧边栏自动出现
- 「全部笔记」页自动收录（按日期倒序）
- 搜索自动索引

## 目录结构

```
vitepress/
├── docs/
│   ├── .vitepress/
│   │   ├── config.mts              # 站点配置（导航、侧边栏、搜索）
│   │   └── theme/
│   │       ├── index.ts            # 主题入口，注册全局组件
│   │       ├── custom.css          # 换配色改这里
│   │       ├── NoteList.vue        # 笔记列表卡片组件
│   │       └── notes.data.ts       # 扫描 notes/ 收集笔记元信息
│   ├── index.md                    # 首页（landing 模式）
│   ├── about.md                    # 关于页
│   ├── notes/
│   │   ├── index.md                # 「全部笔记」列表页
│   │   ├── 工具/
│   │   ├── 读书/
│   │   └── 踩坑/
│   └── public/                     # 静态资源（favicon 等）
├── package.json
└── .gitignore
```

## 常用命令

| 命令 | 作用 |
|---|---|
| `npm run docs:dev` | 本地预览，热更新 |
| `npm run docs:build` | 生成静态网站到 `docs/.vitepress/dist` |
| `npm run docs:preview` | 本地预览构建产物 |

## 改外观

编辑 `docs/.vitepress/theme/custom.css`：

```css
:root {
  --vp-c-brand-1: #d97706;   /* 主色：链接、高亮 */
  --vp-c-brand-2: #b45309;   /* 按钮底色 */
  --vp-c-brand-3: #f59e0b;   /* 辅助色 */
}
```

改完保存，浏览器立刻变色。想换回 VitePress 默认蓝紫，把这几行删掉即可。

## 从 Obsidian 批量导入笔记

项目根目录有 `migrate-notes.py`，用来把 Obsidian 仓库的笔记搬进来。

```bash
python migrate-notes.py --dry-run   # 先看分类结果，不写文件
python migrate-notes.py             # 正式迁移
```

脚本做的事：

1. 复制 `.md` 到 `docs/notes/CSharp/<分类>/`
2. `![[图片.png]]` 转成标准语法 `![图片](/csharp/图片.png)`
3. 图片复制到 `docs/public/csharp/`
4. 自动生成 front-matter（标题取文件名，日期取文件修改时间）
5. 跳过 0 字节的空文件
6. **源目录始终只读**

脚本可重复执行，每次会重建目标目录。所以在 Obsidian 里改了笔记，重跑一次就同步了。

### 改分类规则

编辑脚本顶部的 `CATEGORIES` 列表，按关键词匹配归入分类；子目录的归类在 `PATH_OVERRIDES` 里配置。

### 迁移时踩过的三个坑（脚本已处理）

| 坑 | 表现 | 处理 |
|---|---|---|
| YAML 日期 | `date: 2026-09-24` 被解析成日期对象，构建报错 | 所有 front-matter 值加双引号 |
| 裸尖括号 | `list<int>` 被 Vue 当 HTML 标签，报 missing end tag | 代码块外转义为 `&lt;` `&gt;` |
| 空方括号 | `bool[]()` 被 Markdown 当链接，产生死链 | 转义为 `\[\]()` |

## 用 Git 管版本

```bash
git add -A
git commit -m "新增一篇笔记"
```

内容全是纯文本，改了什么、什么时候改的，`git log` 和 `git diff` 一目了然。

## 部署（可选）

如果之后要发布到 GitHub Pages，在 `docs/.vitepress/config.mts` 里加上 `base`：

```ts
export default defineConfig({
  base: '/仓库名/',   // 前后斜杠都要有，否则资源 404 白屏
})
```

然后 `npm run docs:build`，把 `docs/.vitepress/dist` 整个目录传上去即可。
