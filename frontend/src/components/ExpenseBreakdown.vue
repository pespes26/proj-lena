<template>
  <div class="flex items-center gap-6">
    <div class="w-48 h-48 flex-shrink-0">
      <Doughnut :data="chartData" :options="chartOptions" />
    </div>
    <div class="flex-1 space-y-3">
      <div v-for="(item, i) in items" :key="i" class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: item.color }"></span>
          <span class="text-sm text-gray-600">{{ item.label }}</span>
        </div>
        <div class="text-left">
          <span class="text-sm font-bold text-gray-800">{{ fmt(item.value) }}</span>
          <span class="text-xs text-gray-400 mr-1">{{ item.percent }}%</span>
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
    borderWidth: 0,
    cutout: '70%',
    borderRadius: 4,
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
