<template>
  <Bar :data="chartData" :options="chartOptions" style="max-height: 320px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [
    {
      label: 'הכנסות',
      data: props.data.totals.map(t => t.revenue),
      backgroundColor: '#0D9488',
      borderRadius: 6,
      barPercentage: 0.7,
    },
    {
      label: 'הוצאות',
      data: props.data.totals.map(t => t.expenses),
      backgroundColor: '#fbbf24',
      borderRadius: 6,
      barPercentage: 0.7,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top', rtl: true, labels: { font: { size: 11 }, usePointStyle: true, pointStyle: 'rectRounded', padding: 16 } },
    tooltip: {
      rtl: true, backgroundColor: 'rgba(255,255,255,0.95)', titleColor: '#1a1a2e', bodyColor: '#374151',
      borderColor: '#e5e7eb', borderWidth: 1, cornerRadius: 12, padding: 10,
      callbacks: { label: ctx => ` ${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#9ca3af' } },
    y: { grid: { color: '#f3f4f6', drawBorder: false }, border: { display: false },
      ticks: { font: { size: 10 }, color: '#9ca3af', callback: v => v.toLocaleString('he-IL') } },
  },
}
</script>
