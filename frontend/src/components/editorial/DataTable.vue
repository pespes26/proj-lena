<template>
  <div class="ui-table-wrap">
    <!-- Search bar -->
    <div v-if="searchable" class="ui-table-search">
      <svg class="w-4 h-4 text-ink-faint flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/></svg>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="חיפוש..."
        class="font-sans text-sm text-ink bg-transparent outline-none flex-1 min-w-0"
      />
      <button v-if="searchQuery" @click="searchQuery = ''" class="text-ink-faint hover:text-ink transition-colors">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </div>

    <table class="ui-table">
      <thead :class="{ 'ui-table-sticky': stickyHeader }">
        <tr>
          <th
            v-for="col in visibleColumns"
            :key="col.key"
            :class="[
              col.align === 'end' ? 'num' : '',
              col.sortable ? 'ui-table-sortable' : '',
              col.hideMobile ? 'hidden sm:table-cell' : '',
            ]"
            :style="col.width ? { width: col.width } : null"
            @click="col.sortable && toggleSort(col.key)"
          >
            <span class="inline-flex items-center gap-1.5">
              {{ col.label }}
              <svg v-if="col.sortable && sortKey === col.key" class="w-3 h-3 flex-shrink-0 transition-transform"
                :class="sortDir === 'desc' ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                <path stroke-linecap="round" d="M5 15l7-7 7 7"/>
              </svg>
              <svg v-else-if="col.sortable" class="w-3 h-3 flex-shrink-0 opacity-25" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" d="M8 9l4-4 4 4M8 15l4 4 4-4"/>
              </svg>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, i) in pagedRows"
          :key="row._key || row.id || i"
          :class="{ 'is-clickable': clickable }"
          @click="clickable && $emit('row-click', row, i)"
        >
          <td
            v-for="col in visibleColumns"
            :key="col.key"
            :class="[
              col.align === 'end' ? 'num' : '',
              col.hideMobile ? 'hidden sm:table-cell' : '',
            ]"
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
      <!-- Empty state -->
      <tbody v-if="processedRows.length === 0">
        <tr>
          <td :colspan="visibleColumns.length" class="text-center py-10">
            <div class="flex flex-col items-center gap-2 text-ink-faint">
              <svg class="w-8 h-8 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-2.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
              </svg>
              <span class="font-sans text-sm">{{ searchQuery ? 'לא נמצאו תוצאות' : 'אין נתונים להצגה' }}</span>
            </div>
          </td>
        </tr>
      </tbody>
      <tfoot v-if="footer && processedRows.length > 0">
        <tr>
          <td
            v-for="col in visibleColumns"
            :key="col.key"
            :class="[
              col.align === 'end' ? 'num' : '',
              col.hideMobile ? 'hidden sm:table-cell' : '',
            ]"
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

    <!-- Pagination -->
    <div v-if="pageSize > 0 && totalPages > 1" class="ui-table-pagination">
      <span class="font-sans text-xs text-ink-muted">
        מציג <bdi class="ui-num">{{ pageStart + 1 }}–{{ pageEnd }}</bdi> מתוך <bdi class="ui-num">{{ processedRows.length }}</bdi>
      </span>
      <div class="flex gap-1">
        <button @click="page > 0 && page--" :disabled="page === 0" class="ui-table-page-btn" aria-label="הקודם">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" d="M9 5l7 7-7 7"/></svg>
        </button>
        <button
          v-for="p in paginationRange" :key="p"
          @click="typeof p === 'number' && (page = p)"
          :class="['ui-table-page-btn', p === page ? 'is-active' : '', typeof p !== 'number' ? 'is-dots' : '']"
        >
          <bdi class="ui-num">{{ typeof p === 'number' ? p + 1 : '…' }}</bdi>
        </button>
        <button @click="page < totalPages - 1 && page++" :disabled="page >= totalPages - 1" class="ui-table-page-btn" aria-label="הבא">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" d="M15 19l-7-7 7-7"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  footer: { type: Object, default: null },
  clickable: { type: Boolean, default: false },
  searchable: { type: Boolean, default: false },
  stickyHeader: { type: Boolean, default: false },
  pageSize: { type: Number, default: 0 },
  defaultSort: { type: String, default: '' },
  defaultSortDir: { type: String, default: 'asc' },
})
defineEmits(['row-click'])

const searchQuery = ref('')
const sortKey = ref(props.defaultSort)
const sortDir = ref(props.defaultSortDir)
const page = ref(0)

const visibleColumns = computed(() => props.columns)

function toggleSort(key) {
  if (sortKey.value === key) {
    if (sortDir.value === 'asc') sortDir.value = 'desc'
    else if (sortDir.value === 'desc') { sortKey.value = ''; sortDir.value = 'asc' }
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
  page.value = 0
}

const processedRows = computed(() => {
  let result = [...props.rows]

  // Search
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(row =>
      props.columns.some(col => {
        const v = row[col.key]
        return v != null && String(v).toLowerCase().includes(q)
      })
    )
  }

  // Sort
  if (sortKey.value) {
    const col = props.columns.find(c => c.key === sortKey.value)
    const isNum = col && (col.format === 'number' || col.format === 'percent')
    result.sort((a, b) => {
      let av = a[sortKey.value], bv = b[sortKey.value]
      if (av == null) return 1
      if (bv == null) return -1
      if (isNum) { av = Number(av) || 0; bv = Number(bv) || 0 }
      else { av = String(av); bv = String(bv) }
      const cmp = av < bv ? -1 : av > bv ? 1 : 0
      return sortDir.value === 'desc' ? -cmp : cmp
    })
  }

  return result
})

// Pagination
const totalPages = computed(() => props.pageSize > 0 ? Math.ceil(processedRows.value.length / props.pageSize) : 1)
const pageStart = computed(() => props.pageSize > 0 ? page.value * props.pageSize : 0)
const pageEnd = computed(() => props.pageSize > 0 ? Math.min(pageStart.value + props.pageSize, processedRows.value.length) : processedRows.value.length)
const pagedRows = computed(() => props.pageSize > 0 ? processedRows.value.slice(pageStart.value, pageEnd.value) : processedRows.value)

const paginationRange = computed(() => {
  const total = totalPages.value
  const current = page.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i)
  const range = []
  range.push(0)
  if (current > 2) range.push('...')
  for (let i = Math.max(1, current - 1); i <= Math.min(total - 2, current + 1); i++) range.push(i)
  if (current < total - 3) range.push('...')
  range.push(total - 1)
  return range
})

// Reset page on search or sort change
watch([searchQuery, sortKey, sortDir], () => { page.value = 0 })

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

/* Search */
.ui-table-search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-bottom: 1px solid var(--border);
}

/* Sticky header */
.ui-table-sticky {
  position: sticky;
  top: 0;
  z-index: 2;
}
.ui-table-sticky th {
  background: var(--surface) !important;
  box-shadow: 0 1px 0 var(--border);
}

/* Sortable header */
.ui-table-sortable {
  cursor: pointer;
  user-select: none;
  transition: color 0.15s ease;
}
.ui-table-sortable:hover {
  color: var(--ink);
}

/* Pagination */
.ui-table-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 1rem;
  border-top: 1px solid var(--border);
  gap: 0.75rem;
}
.ui-table-page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 1.75rem;
  height: 1.75rem;
  padding: 0 0.375rem;
  border: 0;
  border-radius: var(--radius);
  background: transparent;
  color: var(--ink-muted);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}
.ui-table-page-btn:hover:not(:disabled):not(.is-dots) {
  background: var(--surface-muted);
  color: var(--ink);
}
.ui-table-page-btn.is-active {
  background: var(--ink);
  color: #fff;
}
.ui-table-page-btn.is-dots {
  cursor: default;
  opacity: 0.4;
}
.ui-table-page-btn:disabled {
  opacity: 0.25;
  cursor: default;
}
</style>
