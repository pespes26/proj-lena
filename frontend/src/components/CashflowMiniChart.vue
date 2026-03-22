<template>
  <Line :data="chartData" :options="chartOptions" style="max-height: 220px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip } from 'chart.js'
import { tooltipConfig, axisConfig, COLORS, hebrewLabelCallback } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [
    {
      label: 'מצטבר',
      data: props.data.cumulative.map(m => m.value),
      borderColor: COLORS.primary,
      backgroundColor: COLORS.primaryLight,
      tension: 0.4,
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: COLORS.primary,
      borderWidth: 2.5,
    },
    {
      label: 'חודשי',
      data: props.data.monthly_net.map(m => m.value),
      borderColor: COLORS.lime,
      backgroundColor: 'transparent',
      tension: 0.4,
      fill: false,
      pointRadius: 0,
      pointHoverRadius: 4,
      borderWidth: 1.5,
      borderDash: [4, 4],
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: false },
    tooltip: {
      ...tooltipConfig,
      padding: 8,
      callbacks: { label: hebrewLabelCallback() },
    },
  },
  scales: {
    x: { display: false },
    y: {
      ...axisConfig.y,
      ticks: { ...axisConfig.y.ticks, font: { size: 9 }, maxTicksLimit: 5 },
    },
  },
}
</script>
