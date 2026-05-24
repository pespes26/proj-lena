<template>
  <div class="ui-chart-container ui-chart-container--xl" role="img" aria-label="גרף נטו לפי פרויקט: השוואה חודשית בין פרויקטים">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, legendConfig, hebrewLabelCallback, COLORS } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({ data: Object })

// Distinct 12-color palette — each project gets its own hue
const PROJECT_PALETTE = [
  '#059669', // emerald-600
  '#2563eb', // blue-600
  '#d97706', // amber-600
  '#7c3aed', // violet-600
  '#0891b2', // cyan-600
  '#e11d48', // rose-600
  '#0f172a', // slate-900
  '#ea580c', // orange-600
  '#4f46e5', // indigo-600
  '#65a30d', // lime-600
  '#db2777', // pink-600
  '#0d9488', // teal-600
]

const chartData = computed(() => {
  const pnames = Object.keys(props.data.projects)
  return {
    labels: props.data.month_labels,
    datasets: pnames.map((name, idx) => ({
      label: name,
      data: props.data.projects[name].map(m => m.profit),
      backgroundColor: PROJECT_PALETTE[idx % PROJECT_PALETTE.length],
      hoverBackgroundColor: PROJECT_PALETTE[idx % PROJECT_PALETTE.length],
      borderColor: COLORS.paperLight,
      borderWidth: 1.5,
      borderRadius: 3,
      borderSkipped: false,
      barPercentage: 0.82,
      categoryPercentage: 0.78,
      stack: 'combined',
    })),
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      ...legendConfig,
      position: 'bottom',
      align: 'center',
      labels: {
        ...legendConfig.labels,
        font: { family: legendConfig.labels.font.family, size: 11, weight: '500' },
        pointStyle: 'rectRounded',
        padding: 14,
        boxWidth: 10,
        boxHeight: 10,
      },
    },
    tooltip: {
      ...tooltipConfig,
      callbacks: { label: hebrewLabelCallback() },
    },
  },
  scales: {
    x: {
      ...axisConfig.x,
      stacked: true,
      ticks: { ...axisConfig.x.ticks, font: { family: axisConfig.x.ticks.font.family, size: 11, weight: '500' }, maxRotation: 0 },
    },
    y: { ...axisConfig.y, stacked: true },
  },
}
</script>
