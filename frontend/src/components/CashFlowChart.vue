<template>
  <Line :data="chartData" :options="chartOptions" style="max-height: 320px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, legendConfig, COLORS, hebrewLabelCallback } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [
    {
      label: 'תזרים חודשי נטו',
      data: props.data.monthly_net.map(m => m.value),
      borderColor: COLORS.primary,
      backgroundColor: COLORS.primaryFill,
      tension: 0.4,
      fill: false,
      pointBackgroundColor: COLORS.primary,
      pointRadius: 4,
      pointHoverRadius: 6,
      borderWidth: 2.5,
    },
    {
      label: 'מצטבר',
      data: props.data.cumulative.map(m => m.value),
      borderColor: COLORS.green,
      backgroundColor: COLORS.greenFill,
      tension: 0.4,
      fill: true,
      pointBackgroundColor: COLORS.green,
      pointRadius: 4,
      pointHoverRadius: 6,
      borderWidth: 2.5,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
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
}
</script>
