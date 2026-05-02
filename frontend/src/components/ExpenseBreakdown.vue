<template>
  <div class="flex items-center gap-8 flex-wrap">
    <div class="ui-chart-container ui-chart-container--sm" style="width: 12rem; height: 12rem; flex-shrink: 0;">
      <Doughnut :data="chartData" :options="chartOptions" />
    </div>
    <div class="flex-1 min-w-[180px] border-t border-rule">
      <div v-for="(item, i) in items" :key="i" class="flex items-baseline justify-between py-3 border-b border-rule gap-4">
        <div class="flex items-center gap-2.5 min-w-0">
          <span class="w-2 h-2 flex-shrink-0" :style="{ backgroundColor: item.color }"></span>
          <span class="font-sans text-sm text-ink truncate">{{ item.label }}</span>
        </div>
        <div class="flex items-baseline gap-2 flex-shrink-0">
          <bdi class="font-sans font-semibold text-ink ed-num">{{ fmt(item.value) }}</bdi>
          <span class="ed-eyebrow ed-num" style="font-size: 0.625rem;">{{ item.percent }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { formatNumber } from '../services/api'
import { tooltipConfig, COLORS, hebrewLabelCallback } from '../utils/chartDefaults'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({ summary: Object })
const fmt = formatNumber

const items = computed(() => {
  const op = props.summary.total_op_expenses
  const sal = props.summary.total_salary_expenses
  const total = op + sal
  return [
    { label: 'הוצאות תפעול', value: op, color: COLORS.amber, percent: total > 0 ? Math.round(op / total * 100) : 0 },
    { label: 'הוצאות שכר', value: sal, color: COLORS.orange, percent: total > 0 ? Math.round(sal / total * 100) : 0 },
  ]
})

const chartData = computed(() => ({
  labels: items.value.map(i => i.label),
  datasets: [{
    data: items.value.map(i => i.value),
    backgroundColor: items.value.map(i => i.color),
    borderWidth: 2,
    borderColor: COLORS.paperLight,
    cutout: '64%',
  }],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { display: false },
    tooltip: {
      ...tooltipConfig,
      callbacks: { label: hebrewLabelCallback() },
    },
  },
}
</script>
