<template>
  <Bar :data="chartData" :options="chartOptions" style="max-height: 280px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({ data: Object })

const colors = ['#0D9488', '#22c55e', '#06b6d4', '#8b5cf6']

const chartData = computed(() => {
  const pnames = Object.keys(props.data.projects)
  return {
    labels: props.data.month_labels,
    datasets: pnames.map((name, idx) => ({
      label: name,
      data: props.data.projects[name].map(m => m.profit),
      backgroundColor: colors[idx % colors.length] + 'cc',
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
    legend: { position: 'top', rtl: true, labels: { font: { size: 10 }, usePointStyle: true, pointStyle: 'rectRounded', padding: 12 } },
    tooltip: {
      rtl: true, backgroundColor: 'rgba(255,255,255,0.95)', titleColor: '#1a1a2e', bodyColor: '#374151',
      borderColor: '#e5e7eb', borderWidth: 1, cornerRadius: 12, padding: 10,
      callbacks: { label: ctx => ` ${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { stacked: true, grid: { display: false }, ticks: { font: { size: 9 }, color: '#9ca3af', maxRotation: 45 } },
    y: { stacked: true, grid: { color: '#f3f4f6', drawBorder: false }, border: { display: false },
      ticks: { font: { size: 10 }, color: '#9ca3af', callback: v => v.toLocaleString('he-IL') } },
  },
}
</script>
