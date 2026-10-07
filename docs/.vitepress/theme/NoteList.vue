<script setup lang="ts">
import { data as notes } from './notes.data'

// 支持传入要过滤的分类，例如 <NoteList tag="Vue" />
const props = defineProps<{ tag?: string }>()

const shown = props.tag
  ? notes.filter((n) => n.tags?.includes(props.tag!))
  : notes
</script>

<template>
  <div class="note-list">
    <a
      v-for="note in shown"
      :key="note.url"
      class="note-card"
      :href="note.url"
    >
      <div class="note-title">{{ note.title }}</div>
      <div v-if="note.description" class="note-desc">{{ note.description }}</div>
      <div class="note-meta">
        {{ note.date }}<template v-if="note.tags?.length"> · {{ note.tags.join(' / ') }}</template>
      </div>
    </a>
    <p v-if="!shown.length">这里还没有笔记。</p>
  </div>
</template>
