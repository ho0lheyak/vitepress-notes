import { defineConfig } from 'vitepress'
import { generateSidebar } from 'vitepress-sidebar'

// 自动扫描 docs/ 目录生成侧边栏：新增 .md 文件无需改配置
const rawSidebar = generateSidebar([
  {
    documentRootPath: 'docs',
    scanStartPath: 'notes',
    basePath: '/notes',
    useTitleFromFrontmatter: true,
    useFolderTitleFromIndexFile: true,
    sortMenusByFrontmatterOrder: true,
    collapsed: false,
    hyphenToSpace: true,
    capitalizeFirst: true,
  },
])

// 插件生成的 link 是相对路径，且 basePath 不带结尾斜杠，
// 中文目录名会被拼成 /notes工具/xxx。这里统一改写成绝对路径。
function fixLinks(items: any[]): any[] {
  return items.map((item) => {
    const next = { ...item }
    if (typeof next.link === 'string' && !next.link.startsWith('/')) {
      next.link = `/notes/${next.link}`
    }
    if (Array.isArray(next.items)) {
      next.items = fixLinks(next.items)
    }
    return next
  })
}

const autoSidebar = Object.fromEntries(
  Object.entries(rawSidebar).map(([key, value]: [string, any]) => [
    key,
    { ...value, base: undefined, items: fixLinks(value.items) },
  ]),
)

export default defineConfig({
  lang: 'zh-CN',
  title: '我的笔记',
  description: '随手记的技术笔记与读书摘录',
  // 部署在 https://ho0lheyak.github.io/vitepress-notes/ 的子路径下，
  // 资源必须带这个前缀，否则线上白屏。
  // 本地预览时用根路径，访问 http://localhost:5173/ 更方便。
  base: process.env.GITHUB_ACTIONS ? '/vitepress-notes/' : '/',
  lastUpdated: true,
  cleanUrls: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.svg' }],
  ],

  themeConfig: {
    // 顶部导航
    nav: [
      { text: '首页', link: '/' },
      { text: '全部笔记', link: '/notes/' },
      { text: '关于', link: '/about' },
    ],

    // 左侧边栏：首页/关于等单页不显示，进入 notes 才出现
    sidebar: autoSidebar,

    // 右侧大纲
    outline: { level: [2, 3], label: '本页目录' },

    // 本地搜索（中文分词）
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索笔记', buttonAriaLabel: '搜索笔记' },
          modal: {
            noResultsText: '没有找到结果',
            resetButtonTitle: '清除条件',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' },
          },
        },
      },
    },

    // 页脚翻页文案
    docFooter: { prev: '上一篇', next: '下一篇' },
    darkModeSwitchLabel: '主题',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    sidebarMenuLabel: '目录',
    returnToTopLabel: '回到顶部',

    lastUpdated: {
      text: '最后更新于',
      formatOptions: { dateStyle: 'short', timeStyle: 'short' },
    },

    footer: {
      message: '用 VitePress 搭建',
      copyright: '本地笔记，仅供自己查阅',
    },
  },
})
