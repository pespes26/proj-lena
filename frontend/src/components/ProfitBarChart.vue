<template>
  <Bar :data="chartData" :options="chartOptions" style="max-height: 260px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({ data: Array })

const chartData = computed(() => ({
  labels: props.data.map(m => 'חודש ' + m.month),
  datasets: [{
    label: 'רווח תפעולי',
    data: props.data.map(m => m.operating_profit),
    backgroundColor: props.data.map(m => m.operating_profit >= 0 ? 'rgba(13,148,136,0.8)' : 'rgba(239,68,68,0.8)'),
    borderRadius: 6,
    barPercentage: 0.6,
  }],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      rtl: true,
      backgroundColor: 'rgba(255,255,255,0.95)',
      titleColor: '#1a1a2e',
      bodyColor: '#374151',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      cornerRadius: 12,
      padding: 10,
      callbacks: { label: ctx => `רווח: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#9ca3af' } },
    y: {
      grid: { color: '#f3f4f6', drawBorder: false },
      ticks: { font: { size: 10 }, color: '#9ca3af', callback: v => v.toLocaleString('he-IL') },
      border: { display: false },
    },
  },
}
</script>
