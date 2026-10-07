---
title: VitePress 与 Hexo 的取舍
description: 两种静态站点生成器，本质是文档优先还是博客优先
date: 2026-02-10
tags: [工具, 静态站点]
order: 1
---

# VitePress 与 Hexo 的取舍

同样是 Markdown 生成网站，两者的假设完全不同。

## 内容模型

| | VitePress | Hexo |
|---|---|---|
| 组织方式 | 文件夹层级 + 侧边栏 | front-matter 的 date / tags |
| 天然产物 | 左侧目录树、上一页/下一页 | 归档、标签云、分页、RSS |
| 版本管理 | 无（要自己配） | 无 |

VitePress 假设你写的是**会长期增补的手册**，Hexo 假设你写的是**按时间发布的文章**。

## 换外观的方式

- Hexo：换主题。几十套现成的，10 分钟见效，代价是升级主题容易冲突。
- VitePress：一套默认主题，改 CSS 变量或写 Vue 组件，没有主题市场。

## 结论

> 要"干净快"选 VitePress，要"有个性"选 Hexo。

这里就是 VitePress —— 注意左侧目录和右侧大纲，都是自动生成的。

## 一个代码块示例

```bash
npm run docs:dev     # 本地预览
npm run docs:build   # 生成静态文件
```

代码块自带高亮和复制按钮，右上角可以试试。
