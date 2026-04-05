<template>
  <div class="ui-alert" :class="`ui-alert--${severity}`">
    <div class="ui-alert__icon" aria-hidden="true">
      <svg v-if="severity === 'high'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
    </div>
    <div class="ui-alert__body">
      <div v-if="eyebrow" class="ui-alert__eyebrow">{{ eyebrow }}</div>
      <div class="ui-alert__text">
        <slot>{{ text }}</slot>
      </div>
      <div v-if="cite || $slots.cite" class="ui-alert__cite">
        <slot name="cite">{{ cite }}</slot>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '' },
  cite: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  severity: { type: String, default: 'neutral' }, // 'neutral' | 'high' | 'medium' | 'low'
})
</script>

<style scoped>
.ui-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-inline-start: 4px solid var(--border-strong);
  border-radius: var(--radius-lg);
  padding: 1.125rem 1.25rem;
  box-shadow: var(--shadow-sm);
  margin: 0.75rem 0;
}
.ui-alert__icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-muted);
  color: var(--ink-muted);
}
.ui-alert__body {
  flex: 1;
  min-width: 0;
}
.ui-alert__eyebrow {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink-muted);
  margin-bottom: 0.25rem;
  text-transform: none;
}
.ui-alert__text {
  font-family: var(--font-sans);
  font-weight: 500;
  font-style: normal;
  font-size: 0.9375rem;
  line-height: 1.55;
  color: var(--ink);
}
.ui-alert__cite {
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--ink-faint);
  margin-top: 0.375rem;
}

/* Severity accents */
.ui-alert--high {
  border-inline-start-color: var(--negative);
  background: var(--negative-soft);
}
.ui-alert--high .ui-alert__icon {
  background: var(--surface);
  color: var(--negative);
}
.ui-alert--high .ui-alert__eyebrow {
  color: var(--negative);
}
.ui-alert--medium {
  border-inline-start-color: var(--warning);
  background: var(--warning-soft);
}
.ui-alert--medium .ui-alert__icon {
  background: var(--surface);
  color: var(--warning);
}
.ui-alert--medium .ui-alert__eyebrow {
  color: var(--warning);
}
.ui-alert--low {
  border-inline-start-color: var(--info);
}
</style>
