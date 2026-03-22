<template>
  <Line :data="chartData" :options="chartOptions" style="max-height: 260px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, legendConfig, COLORS, hebrewLabelCallback } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip, Legend)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [
    {
      label: 'נטו חודשי',
      data: props.data.data.map(d => d.net),
      borderColor: COLORS.primary,
      backgroundColor: COLORS.primaryLight,
      tension: 0.4,
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 5,
      borderWidth: 2,
    },
    {
      label: 'מצטבר',
      data: props.data.data.map(d => d.cumulative),
      borderColor: COLORS.green,
      backgroundColor: COLORS.greenFill,
      tension: 0.4,
      fill: false,
      pointRadius: 0,
      pointHoverRadius: 5,
      borderWidth: 2,
      borderDash: [4, 4],
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { ...legendConfig, labels: { ...legendConfig.labels, padding: 12 } },
    tooltip: {
      ...tooltipConfig,
      callbacks: { label: hebrewLabelCallback() },
    },
  },
  scales: {
    x: { ...axisConfig.x, ticks: { ...axisConfig.x.ticks, maxRotation: 45 } },
    y: { ...axisConfig.y },
  },
}
</script>
