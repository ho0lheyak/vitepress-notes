# 关于这个站

这是一个用 **VitePress** 搭的纯本地笔记站，目的很简单：把散落的想法用 Markdown 记下来，交给 Git 管版本，需要时一键生成网站。

## 三个组成部分

| 部分 | 作用 | 位置 |
|---|---|---|
| Markdown 文件 | 内容 | `docs/notes/` |
| VitePress | 把 Markdown 编译成网站 | `docs/.vitepress/` |
| Git | 记录每次改动 | 仓库根目录 |

三者互不干涉：VitePress 只读 Markdown，压根不知道 Git 的存在。

## 日常怎么用

```bash
# 本地预览，边写边看
npm run docs:dev

# 写完存个版本
git add -A
git commit -m "新增一篇笔记"

# 生成静态网站（产物在 docs/.vitepress/dist）
npm run docs:build
```

## 新增一篇笔记

在 `docs/notes/` 里随便建个 `.md`，开头写上元信息：

```md
---
title: 笔记标题
description: 一句话说明
date: 2026-01-15
tags: [标签一, 标签二]
---

正文从这里开始……
```

保存后：侧边栏自动出现、全部笔记页自动收录、搜索自动索引。**不需要改任何配置。**

## 想改外观

打开 `docs/.vitepress/theme/custom.css`，改几个颜色变量就够了：

```css
:root {
  --vp-c-brand-1: #d97706;  /* 主色 */
  --vp-c-brand-2: #b45309;  /* 按钮色 */
}
```

改完保存，浏览器立刻变色。
