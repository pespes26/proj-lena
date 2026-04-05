<template>
  <div class="ui-subtitle">
    <slot>{{ text }}</slot>
    <span v-if="source" class="ui-subtitle__source">— {{ source }}</span>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '' },
  source: { type: String, default: '' },
})
</script>

<style scoped>
.ui-subtitle {
  font-family: var(--font-sans);
  font-weight: 400;
  font-size: 0.9375rem;
  color: var(--ink-muted);
  line-height: 1.55;
  margin: 0 0 1rem 0;
  max-width: 60ch;
}
.ui-subtitle__source {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-faint);
  margin-top: 0.25rem;
}
</style>
