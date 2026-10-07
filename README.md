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
