<template>
  <Line :data="chartData" :options="chartOptions" style="max-height: 220px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Tooltip)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [
    {
      label: 'מצטבר',
      data: props.data.cumulative.map(m => m.value),
      borderColor: '#84cc16',
      backgroundColor: 'rgba(132,204,22,0.12)',
      tension: 0.4,
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: '#84cc16',
      borderWidth: 2.5,
    },
    {
      label: 'חודשי',
      data: props.data.monthly_net.map(m => m.value),
      borderColor: '#a3e635',
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
      rtl: true,
      backgroundColor: 'rgba(255,255,255,0.95)',
      titleColor: '#1a1a2e',
      bodyColor: '#374151',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      cornerRadius: 10,
      padding: 8,
      callbacks: { label: ctx => ` ${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { display: false },
    y: {
      grid: { color: '#f3f4f6', drawBorder: false },
      ticks: { font: { size: 9 }, color: '#9ca3af', callback: v => v.toLocaleString('he-IL'), maxTicksLimit: 5 },
      border: { display: false },
    },
  },
}
</script>
