<template>
  <div class="ui-kpi" :class="[`ui-kpi--${size}`, `ui-kpi--${tone}`]">
    <div v-if="label" class="ui-kpi__label">{{ label }}</div>
    <div class="ui-kpi__value">
      <span v-if="prefix" class="ui-kpi__affix">{{ prefix }}</span>
      <bdi class="ui-num">{{ formattedValue }}</bdi>
      <span v-if="suffix" class="ui-kpi__affix">{{ suffix }}</span>
    </div>
    <div v-if="delta !== null && delta !== undefined" class="ui-kpi__delta-row">
      <span class="ui-pill" :class="deltaPillClass">
        <span class="ui-kpi__arrow">{{ deltaArrow }}</span>
        <bdi class="ui-num">{{ formattedDelta }}</bdi>
      </span>
      <span v-if="deltaLabel" class="ui-kpi__delta-caption">{{ deltaLabel }}</span>
    </div>
    <div v-if="footnote" class="ui-kpi__footnote">{{ footnote }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, default: '' },
  value: { type: [Number, String], required: true },
  prefix: { type: String, default: '' },
  suffix: { type: String, default: '' },
  size: { type: String, default: 'md' }, // 'xl' | 'lg' | 'md' | 'sm'
  tone: { type: String, default: 'neutral' }, // 'neutral' | 'positive' | 'negative' | 'accent'
  delta: { type: [Number, String], default: null },
  deltaSuffix: { type: String, default: '%' },
  deltaLabel: { type: String, default: '' },
  footnote: { type: String, default: '' },
  format: { type: String, default: 'number' }, // 'number' | 'percent' | 'raw'
})

const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined || props.value === '') return '—'
  const n = Number(props.value)
  if (Number.isNaN(n)) return String(props.value)
  if (props.format === 'percent') return n.toFixed(1)
  if (props.format === 'raw') return String(props.value)
  return n.toLocaleString('he-IL', { maximumFractionDigits: 0 })
})

const formattedDelta = computed(() => {
  if (props.delta === null || props.delta === undefined) return ''
  const n = Number(props.delta)
  if (Number.isNaN(n)) return String(props.delta)
  const abs = Math.abs(n).toFixed(1)
  return `${abs}${props.deltaSuffix}`
})

const deltaArrow = computed(() => {
  const n = Number(props.delta)
  if (Number.isNaN(n) || n === 0) return '·'
  return n > 0 ? '▲' : '▼'
})

const deltaPillClass = computed(() => {
  const n = Number(props.delta)
  if (Number.isNaN(n) || n === 0) return 'ui-pill-neutral'
  return n > 0 ? 'ui-pill-positive' : 'ui-pill-negative'
})
</script>

<style scoped>
.ui-kpi {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  align-items: flex-start;
  font-feature-settings: "lnum" 1, "tnum" 1;
}
.ui-kpi__label {
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink-muted);
  margin-bottom: 0.125rem;
}
.ui-kpi__value {
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--ink);
  line-height: 1;
  letter-spacing: -0.02em;
  display: flex;
  align-items: baseline;
  gap: 0.15em;
}
.ui-kpi__affix {
  font-size: 0.5em;
  font-weight: 600;
  color: var(--ink-muted);
  align-self: flex-start;
  margin-top: 0.22em;
}
.ui-kpi__delta-row {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.125rem;
}
.ui-kpi__arrow {
  font-size: 0.7em;
  line-height: 1;
}
.ui-kpi__delta-caption {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-faint);
}
.ui-kpi__footnote {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  color: var(--ink-faint);
  margin-top: 0.25rem;
}

/* Sizes */
.ui-kpi--xl .ui-kpi__value { font-size: clamp(2.75rem, 5.5vw, 4rem); font-weight: 700; letter-spacing: -0.025em; }
.ui-kpi--lg .ui-kpi__value { font-size: clamp(2.25rem, 4.5vw, 3.25rem); font-weight: 700; letter-spacing: -0.022em; }
.ui-kpi--md .ui-kpi__value { font-size: clamp(1.75rem, 3vw, 2.25rem); font-weight: 700; letter-spacing: -0.015em; }
.ui-kpi--sm .ui-kpi__value { font-size: clamp(1.25rem, 2vw, 1.625rem); font-weight: 700; letter-spacing: -0.008em; }

/* Tones */
.ui-kpi--positive .ui-kpi__value { color: var(--positive); }
.ui-kpi--negative .ui-kpi__value { color: var(--negative); }
.ui-kpi--accent   .ui-kpi__value { color: var(--accent); }
</style>
