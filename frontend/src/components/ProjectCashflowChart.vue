<template>
  <Line :data="chartData" :options="chartOptions" style="max-height: 260px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip, Legend)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [
    {
      label: 'נטו חודשי',
      data: props.data.data.map(d => d.net),
      borderColor: '#84cc16',
      backgroundColor: 'rgba(132,204,22,0.1)',
      tension: 0.4,
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 5,
      borderWidth: 2,
    },
    {
      label: 'מצטבר',
      data: props.data.data.map(d => d.cumulative),
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34,197,94,0.05)',
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
    legend: { position: 'top', rtl: true, labels: { font: { size: 11 }, usePointStyle: true, pointStyle: 'circle', padding: 12 } },
    tooltip: {
      rtl: true,
      backgroundColor: 'rgba(255,255,255,0.95)',
      titleColor: '#1a1a2e',
      bodyColor: '#374151',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      cornerRadius: 12,
      padding: 10,
      callbacks: { label: ctx => ` ${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#9ca3af', maxRotation: 45 } },
    y: {
      grid: { color: '#f3f4f6', drawBorder: false },
      ticks: { font: { size: 10 }, color: '#9ca3af', callback: v => v.toLocaleString('he-IL') },
      border: { display: false },
    },
  },
}
</script>
