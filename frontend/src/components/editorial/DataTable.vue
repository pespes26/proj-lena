<template>
  <div class="ui-table-wrap">
    <table class="ui-table">
      <thead>
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            :class="{ 'num': col.align === 'end' }"
            :style="col.width ? { width: col.width } : null"
          >
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, i) in rows"
          :key="row._key || row.id || i"
          :class="{ 'is-clickable': clickable }"
          @click="clickable && $emit('row-click', row, i)"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            :class="{ 'num': col.align === 'end' }"
          >
            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]" :index="i">
              <template v-if="col.format === 'number'">
                <bdi class="ui-num">{{ formatNumber(row[col.key]) }}</bdi>
              </template>
              <template v-else-if="col.format === 'percent'">
                <bdi class="ui-num">{{ formatPercent(row[col.key]) }}</bdi>
              </template>
              <template v-else>
                {{ row[col.key] }}
              </template>
            </slot>
          </td>
        </tr>
      </tbody>
      <tfoot v-if="footer">
        <tr>
          <td
            v-for="col in columns"
            :key="col.key"
            :class="{ 'num': col.align === 'end' }"
          >
            <slot :name="`foot-${col.key}`" :row="footer" :value="footer[col.key]">
              <template v-if="col.format === 'number'">
                <bdi class="ui-num">{{ formatNumber(footer[col.key]) }}</bdi>
              </template>
              <template v-else-if="col.format === 'percent'">
                <bdi class="ui-num">{{ formatPercent(footer[col.key]) }}</bdi>
              </template>
              <template v-else>
                {{ footer[col.key] }}
              </template>
            </slot>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script setup>
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  footer: { type: Object, default: null },
  clickable: { type: Boolean, default: false },
})
defineEmits(['row-click'])

function formatNumber(v) {
  if (v === null || v === undefined || v === '') return '—'
  const n = Number(v)
  if (Number.isNaN(n)) return String(v)
  return n.toLocaleString('he-IL', { maximumFractionDigits: 0 })
}
function formatPercent(v) {
  if (v === null || v === undefined || v === '') return '—'
  const n = Number(v)
  if (Number.isNaN(n)) return String(v)
  return n.toFixed(1) + '%'
}
</script>

<style scoped>
.ui-table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface);
}
.ui-table-wrap tr.is-clickable {
  cursor: pointer;
}
.ui-table-wrap tr.is-clickable:hover td {
  color: var(--ink);
  background: var(--surface-muted);
}
</style>
