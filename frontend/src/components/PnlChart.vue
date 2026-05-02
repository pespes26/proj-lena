<template>
  <div class="ui-chart-container ui-chart-container--md">
    <Line :key="chartType" :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, legendConfig, COLORS, hebrewLabelCallback } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend)

const props = defineProps({
  data: Array,
  projectName: String,
  chartType: { type: String, default: 'area' },
})

const isArea = computed(() => props.chartType === 'area')

const chartData = computed(() => ({
  labels: props.data.map(m => 'חודש ' + m.month),
  datasets: [
    {
      label: 'הכנסה צפויה',
      data: props.data.map(m => m.revenue),
      borderColor: COLORS.primary,
      backgroundColor: isArea.value ? COLORS.primaryLight : COLORS.primaryFill,
      tension: 0.4,
      fill: isArea.value,
      pointBackgroundColor: COLORS.primary,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: isArea.value ? 0 : 5,
      pointHoverRadius: 6,
      borderWidth: 2,
    },
    {
      label: 'הוצאות תפעול',
      data: props.data.map(m => m.op_expenses),
      borderColor: COLORS.amber,
      backgroundColor: isArea.value ? COLORS.amberLight : 'rgba(166,124,0,0.06)',
      tension: 0.4,
      fill: isArea.value,
      pointBackgroundColor: COLORS.amber,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: isArea.value ? 0 : 5,
      pointHoverRadius: 6,
      borderWidth: 2,
      borderDash: isArea.value ? [] : [6, 3],
    },
    {
      label: 'רווח תפעולי',
      data: props.data.map(m => m.operating_profit),
      borderColor: COLORS.green,
      backgroundColor: isArea.value ? COLORS.greenLight : COLORS.greenFill,
      tension: 0.4,
      fill: isArea.value,
      pointBackgroundColor: props.data.map(m => m.operating_profit >= 0 ? COLORS.green : COLORS.red),
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: isArea.value ? 0 : 5,
      pointHoverRadius: 6,
      borderWidth: 2,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    title: { display: false },
    legend: { ...legendConfig },
    tooltip: {
      ...tooltipConfig,
      callbacks: { label: hebrewLabelCallback() },
    },
  },
  scales: {
    x: { ...axisConfig.x },
    y: { ...axisConfig.y },
  },
}))
</script>
