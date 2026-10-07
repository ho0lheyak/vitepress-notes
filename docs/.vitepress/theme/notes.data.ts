import { createContentLoader } from 'vitepress'

export interface Note {
  title: string
  url: string
  description?: string
  date: string
  tags?: string[]
}

declare const data: Note[]
export { data }

export default createContentLoader('notes/**/*.md', {
  excerpt: false,
  transform(raw): Note[] {
    return raw
      .filter((page) => page.url !== '/notes/') // 排除列表页自身
      .map(({ url, frontmatter }) => ({
        title: frontmatter.title ?? '未命名笔记',
        url,
        description: frontmatter.description ?? '',
        date: formatDate(frontmatter.date),
        tags: frontmatter.tags ?? [],
      }))
      .sort((a, b) => (a.date < b.date ? 1 : -1)) // 最新的排前面
  },
})

function formatDate(raw: unknown): string {
  if (!raw) return ''
  const d = new Date(raw as string)
  return Number.isNaN(d.getTime())
    ? String(raw)
    : d.toISOString().slice(0, 10)
}
