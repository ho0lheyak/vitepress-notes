import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import NoteList from './NoteList.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    // 注册全局组件，任意 .md 里可直接写 <NoteList />
    app.component('NoteList', NoteList)
  },
} satisfies Theme
