<template>
  <div class="ui-risk" :title="tooltip">
    <div class="ui-risk__circle" :class="toneClass">
      <bdi class="ui-num">{{ score }}</bdi>
    </div>
    <span class="ui-risk__label" :class="toneClass">{{ levelLabel }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: 0 },
  level: { type: String, default: 'low' },
  factors: { type: Array, default: () => [] }
})

const toneClass = computed(() => ({
  'is-positive': props.level === 'low',
  'is-warning': props.level === 'medium',
  'is-negative': props.level === 'high' || props.level === 'critical',
}))

const levelLabel = computed(() => ({
  'low': 'נמוך',
  'medium': 'בינוני',
  'high': 'גבוה',
  'critical': 'קריטי',
}[props.level] || ''))

const tooltip = computed(() =>
  props.factors.map(f => `${f.label}: ${f.score}/20 — ${f.detail}`).join('\n')
)
</script>

<style scoped>
.ui-risk {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.ui-risk__circle {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  background: var(--surface-muted);
  color: var(--ink);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.9375rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid var(--border);
}
.ui-risk__label {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink-muted);
}
.ui-risk__circle.is-positive { background: var(--positive-soft); color: var(--positive); border-color: rgba(5, 150, 105, 0.3); }
.ui-risk__circle.is-warning  { background: var(--warning-soft);  color: var(--warning);  border-color: rgba(217, 119, 6, 0.3); }
.ui-risk__circle.is-negative { background: var(--negative-soft); color: var(--negative); border-color: rgba(225, 29, 72, 0.3); }
.ui-risk__label.is-positive { color: var(--positive); }
.ui-risk__label.is-warning  { color: var(--warning); }
.ui-risk__label.is-negative { color: var(--negative); }
</style>
