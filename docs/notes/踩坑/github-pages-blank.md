---
title: 部署到 GitHub Pages 的白屏问题
description: base 路径没配对，资源全部 404
date: 2026-02-05
tags: [踩坑, 部署]
order: 1
---

# 部署到 GitHub Pages 的白屏问题

本地预览一切正常，推到 GitHub Pages 之后打开是一片白。控制台里全是 404。

## 原因

部署地址是子路径：

```
https://你的用户名.github.io/仓库名/
```

但构建出的资源引用指向根路径 `/assets/...`，于是全部落空。

## 解决

在 `docs/.vitepress/config.mts` 里补上 `base`：

```ts
export default defineConfig({
  base: '/仓库名/',   // 前后斜杠都要有
})
```

重新构建部署就好了。

## 判断方法

打开浏览器开发者工具，看 Network 面板：

- 请求路径以 `/assets/` 开头 → 缺 `base` 配置
- 请求路径是 `/仓库名/assets/` → 正常

## 顺带记一笔

如果用自定义域名（比如 `notes.example.com`），站点在根路径，那么 `base` 应该删掉或设为 `'/'`。

> 记住一句话：**部署在哪个路径，base 就写哪个路径。**
