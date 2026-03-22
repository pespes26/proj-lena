<template>
  <Bar :data="chartData" :options="chartOptions" style="max-height: 280px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, legendConfig, COLORS, hebrewLabelCallback } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({ data: Object })

const chartColors = [COLORS.primary, COLORS.green, COLORS.cyan, COLORS.purple]

const chartData = computed(() => {
  const pnames = Object.keys(props.data.projects)
  return {
    labels: props.data.month_labels,
    datasets: pnames.map((name, idx) => ({
      label: name,
      data: props.data.projects[name].map(m => m.profit),
      backgroundColor: chartColors[idx % chartColors.length] + 'cc',
      borderRadius: 4,
      barPercentage: 0.8,
      stack: 'combined',
    })),
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { ...legendConfig, labels: { ...legendConfig.labels, font: { size: 10 }, pointStyle: 'rectRounded', padding: 12 } },
    tooltip: {
      ...tooltipConfig,
      callbacks: { label: hebrewLabelCallback() },
    },
  },
  scales: {
    x: { ...axisConfig.x, stacked: true, ticks: { ...axisConfig.x.ticks, font: { size: 9 }, maxRotation: 45 } },
    y: { ...axisConfig.y, stacked: true },
  },
}
</script>
