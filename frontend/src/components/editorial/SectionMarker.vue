<template>
  <button
    type="button"
    class="ui-tab"
    :class="{ 'is-active': active, 'is-disabled': disabled }"
    :disabled="disabled"
    @click="$emit('click')"
  >
    <span v-if="kicker" class="ui-tab__kicker">{{ kicker }}</span>
    <span class="ui-tab__label">{{ label }}</span>
    <span v-if="badge !== null && badge !== undefined && badge !== ''" class="ui-tab__badge">{{ badge }}</span>
  </button>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  kicker: { type: String, default: '' },
  active: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  badge: { type: [String, Number], default: null },
})
defineEmits(['click'])
</script>

<style scoped>
.ui-tab {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink-muted);
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
  white-space: nowrap;
  line-height: 1.2;
}
.ui-tab:hover {
  color: var(--ink);
  background: var(--surface-muted);
}
.ui-tab.is-active {
  color: var(--surface);
  background: var(--ink);
  font-weight: 600;
}
.ui-tab.is-active:hover {
  background: var(--ink-strong);
  color: var(--surface);
}
.ui-tab.is-disabled {
  color: var(--ink-faint);
  cursor: not-allowed;
  opacity: 0.6;
}
.ui-tab__kicker {
  font-family: var(--font-sans);
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--ink-faint);
}
.ui-tab.is-active .ui-tab__kicker { color: rgba(255, 255, 255, 0.7); }
.ui-tab__label {
  letter-spacing: 0;
}
.ui-tab__badge {
  font-family: var(--font-sans);
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--surface);
  background: var(--negative);
  padding: 0.0625rem 0.4375rem;
  border-radius: 999px;
  min-width: 1.125rem;
  text-align: center;
  line-height: 1.3;
}
.ui-tab.is-active .ui-tab__badge { background: var(--accent); color: var(--surface); }
</style>
