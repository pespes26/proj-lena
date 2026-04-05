<template>
  <section class="ui-card" :class="{ 'ui-card--flush': flush }">
    <header v-if="eyebrow || title || caption || $slots.header || $slots.actions" class="ui-card__header">
      <div class="ui-card__heading">
        <div v-if="eyebrow" class="ui-card__eyebrow">{{ eyebrow }}</div>
        <div class="ui-card__title-row">
          <h3 v-if="title" class="ui-card__title">{{ title }}</h3>
          <slot name="title" />
        </div>
        <p v-if="caption" class="ui-card__caption">{{ caption }}</p>
      </div>
      <div v-if="$slots.actions" class="ui-card__actions">
        <slot name="actions" />
      </div>
      <slot name="header" />
    </header>
    <div class="ui-card__body">
      <slot />
    </div>
    <footer v-if="footnote || $slots.footnote" class="ui-card__footer">
      <slot name="footnote">
        <p class="ui-card__footnote-text">{{ footnote }}</p>
      </slot>
    </footer>
  </section>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, default: '' },
  caption: { type: String, default: '' },
  footnote: { type: String, default: '' },
  flush: { type: Boolean, default: false },
})
</script>

<style scoped>
.ui-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-sm);
  padding: clamp(1.25rem, 2vw, 1.75rem);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: box-shadow 0.22s ease, border-color 0.22s ease;
}
.ui-card:hover {
  box-shadow: var(--shadow-md);
}
.ui-card--flush {
  padding: 0;
}
.ui-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}
.ui-card__heading {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  flex: 1;
  min-width: 0;
}
.ui-card__eyebrow {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-faint);
  margin-bottom: 0.125rem;
}
.ui-card__title-row {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.ui-card__title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.125rem;
  line-height: 1.3;
  letter-spacing: -0.01em;
  color: var(--ink);
  margin: 0;
}
.ui-card__caption {
  font-family: var(--font-sans);
  font-size: 0.875rem;
  color: var(--ink-muted);
  margin: 0;
  line-height: 1.5;
  max-width: 68ch;
}
.ui-card__actions {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-shrink: 0;
}
.ui-card__body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.ui-card__footer {
  padding-top: 0.5rem;
  margin-top: 0.25rem;
  border-top: 1px solid var(--border);
}
.ui-card__footnote-text {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  color: var(--ink-faint);
  margin: 0;
  padding-top: 0.75rem;
  line-height: 1.5;
}
</style>
