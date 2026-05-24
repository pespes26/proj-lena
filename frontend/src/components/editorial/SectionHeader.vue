<template>
  <header class="ui-section-header" :class="`ui-section-header--${align}`">
    <div v-if="eyebrow || kicker" class="ui-section-header__meta">
      <span v-if="eyebrow" class="ui-section-header__eyebrow">{{ eyebrow }}</span>
      <span v-if="eyebrow && kicker" class="ui-section-header__sep">·</span>
      <span v-if="kicker" class="ui-section-header__kicker">{{ kicker }}</span>
    </div>
    <div class="ui-section-header__main">
      <component :is="'h' + level" v-if="title" class="ui-section-header__title">{{ title }}</component>
      <div v-if="$slots.actions" class="ui-section-header__actions">
        <slot name="actions" />
      </div>
    </div>
    <p v-if="subtitle" class="ui-section-header__subtitle">{{ subtitle }}</p>
  </header>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  kicker: { type: String, default: '' },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  level: { type: Number, default: 2 }, // heading level: 1-4
  rule: { type: String, default: 'none' }, // kept for backward compat — no longer renders a rule
  align: { type: String, default: 'start' }, // 'start' | 'center'
})
</script>

<style scoped>
.ui-section-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.ui-section-header--center {
  align-items: center;
  text-align: center;
}
.ui-section-header__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--ink-muted);
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 500;
}
.ui-section-header__sep {
  color: var(--ink-faint);
  font-weight: 400;
}
.ui-section-header__kicker {
  color: var(--ink-faint);
  font-weight: 500;
}
.ui-section-header__main {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.ui-section-header__title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: clamp(1.625rem, 3.2vw, 2.125rem);
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--ink);
  margin: 0;
  font-feature-settings: "lnum" 1, "kern" 1, "liga" 1;
}
.ui-section-header__actions {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  margin-inline-start: auto;
}
.ui-section-header__subtitle {
  font-family: var(--font-sans);
  font-weight: 400;
  font-size: 0.9375rem;
  color: var(--ink-muted);
  margin: 0;
  line-height: 1.55;
  max-width: 64ch;
}
</style>
