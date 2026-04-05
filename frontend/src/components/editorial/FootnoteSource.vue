<template>
  <p class="ui-footnote-source">
    <span v-if="label" class="ui-footnote-source__label">{{ label }}</span>
    <slot>{{ text }}</slot>
    <span v-if="updated" class="ui-footnote-source__sep">·</span>
    <span v-if="updated" class="ui-footnote-source__updated">עדכון אחרון {{ updated }}</span>
  </p>
</template>

<script setup>
defineProps({
  label: { type: String, default: 'מקור:' },
  text: { type: String, default: '' },
  updated: { type: String, default: '' },
})
</script>

<style scoped>
.ui-footnote-source {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  font-family: var(--font-sans);
  font-style: normal;
  font-size: 0.75rem;
  color: var(--ink-faint);
  line-height: 1.5;
  margin: 0;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border);
}
.ui-footnote-source__label {
  font-weight: 600;
  color: var(--ink-muted);
}
.ui-footnote-source__sep { color: var(--ink-faint); }
.ui-footnote-source__updated {
  font-feature-settings: "lnum" 1, "tnum" 1;
}
</style>
