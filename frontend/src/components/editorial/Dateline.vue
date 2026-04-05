<template>
  <div class="ui-dateline-wrap" :class="`ui-dateline-wrap--${align}`">
    <span v-if="date" class="ui-dateline-wrap__date">{{ date }}</span>
    <span v-if="extra" class="ui-dateline-wrap__sep">·</span>
    <span v-if="extra" class="ui-dateline-wrap__extra">{{ extra }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  issue: { type: String, default: '' }, // kept for backward compat but intentionally ignored
  date: { type: String, default: '' },
  extra: { type: String, default: '' },
  align: { type: String, default: 'start' }, // 'start' | 'center'
  auto: { type: Boolean, default: false },
})

const hebrewMonths = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']
const autoDate = computed(() => {
  if (!props.auto || props.date) return props.date
  const d = new Date()
  return `${hebrewMonths[d.getMonth()]} ${d.getFullYear()}`
})
void autoDate
</script>

<style scoped>
.ui-dateline-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink-muted);
  font-feature-settings: "lnum" 1, "tnum" 1;
}
.ui-dateline-wrap--center { justify-content: center; }
.ui-dateline-wrap__sep { color: var(--ink-faint); font-weight: 400; }
.ui-dateline-wrap__date, .ui-dateline-wrap__extra { color: var(--ink-muted); }
</style>
