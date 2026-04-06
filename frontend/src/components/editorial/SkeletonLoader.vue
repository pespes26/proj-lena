<template>
  <div class="skeleton-root" :class="'skeleton--' + variant">
    <!-- KPI variant: label rect + big value rect -->
    <template v-if="variant === 'kpi'">
      <div class="flex flex-wrap gap-y-6" :class="horizontal ? 'flex-row gap-x-8' : 'flex-col gap-y-6'">
        <div v-for="n in count" :key="n" class="flex-1" style="min-width: 140px;">
          <div class="skeleton-pulse h-3 w-16 rounded mb-3"></div>
          <div class="skeleton-pulse h-8 w-28 rounded"></div>
          <div class="skeleton-pulse h-2.5 w-12 rounded mt-2"></div>
        </div>
      </div>
    </template>

    <!-- Chart variant: rectangular area with faint bar shapes -->
    <template v-else-if="variant === 'chart'">
      <div class="skeleton-chart" :style="{ height: height || '220px' }">
        <div class="flex items-end gap-2 h-full px-4 pb-4 pt-8">
          <div v-for="n in 12" :key="n"
            class="skeleton-pulse flex-1 rounded-t"
            :style="{ height: barHeight(n) }">
          </div>
        </div>
      </div>
    </template>

    <!-- Table variant: header row + body rows -->
    <template v-else-if="variant === 'table'">
      <div class="space-y-0">
        <div class="flex gap-4 py-3 border-b border-border">
          <div v-for="n in columns" :key="'h'+n" class="skeleton-pulse h-3 rounded flex-1"></div>
        </div>
        <div v-for="r in rows" :key="'r'+r" class="flex gap-4 py-3.5 border-b border-border/50">
          <div v-for="n in columns" :key="'c'+n" class="skeleton-pulse h-3 rounded flex-1"
            :style="{ opacity: 0.5 + Math.random() * 0.5, width: (40 + Math.random() * 60) + '%' }">
          </div>
        </div>
      </div>
    </template>

    <!-- Card grid variant: mini cards -->
    <template v-else-if="variant === 'cards'">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="n in count" :key="n" class="ui-mini-card">
          <div class="flex justify-between mb-3">
            <div class="skeleton-pulse h-3.5 w-24 rounded"></div>
            <div class="skeleton-pulse h-3.5 w-16 rounded"></div>
          </div>
          <div class="skeleton-pulse h-1.5 rounded-full w-full mb-2"></div>
          <div class="flex justify-between">
            <div class="skeleton-pulse h-2.5 w-16 rounded"></div>
            <div class="skeleton-pulse h-2.5 w-16 rounded"></div>
          </div>
        </div>
      </div>
    </template>

    <!-- Line variant: text lines -->
    <template v-else>
      <div class="space-y-3">
        <div v-for="n in lines" :key="n"
          class="skeleton-pulse h-3 rounded"
          :style="{ width: n === lines ? '60%' : '100%' }">
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'line' },
  lines: { type: Number, default: 3 },
  count: { type: Number, default: 4 },
  columns: { type: Number, default: 5 },
  rows: { type: Number, default: 5 },
  height: { type: String, default: '' },
  horizontal: { type: Boolean, default: true },
})

function barHeight(n) {
  const heights = [45, 70, 55, 85, 60, 90, 40, 75, 50, 80, 65, 55]
  return heights[(n - 1) % heights.length] + '%'
}
</script>

<style scoped>
.skeleton-pulse {
  background: var(--border);
  animation: skeleton-shimmer 1.8s ease-in-out infinite;
}

.skeleton-chart {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
}

@keyframes skeleton-shimmer {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
</style>
