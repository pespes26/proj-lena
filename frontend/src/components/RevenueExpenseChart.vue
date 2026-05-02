<template>
  <div class="ui-chart-container ui-chart-container--lg">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, legendConfig, COLORS, hebrewLabelCallback } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [
    {
      label: 'הכנסות',
      data: props.data.totals.map(t => t.revenue),
      backgroundColor: COLORS.primary,
      borderRadius: 0,
      barPercentage: 0.7,
    },
    {
      label: 'הוצאות',
      data: props.data.totals.map(t => t.expenses),
      backgroundColor: COLORS.amber,
      borderRadius: 0,
      barPercentage: 0.7,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { ...legendConfig, labels: { ...legendConfig.labels, pointStyle: 'rectRounded' } },
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
