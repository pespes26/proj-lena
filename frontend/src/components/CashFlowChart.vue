<template>
  <Line :data="chartData" :options="chartOptions" style="max-height: 320px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [
    {
      label: 'תזרים חודשי נטו',
      data: props.data.monthly_net.map(m => m.value),
      borderColor: '#84cc16',
      backgroundColor: 'rgba(132,204,22,0.08)',
      tension: 0.4,
      fill: false,
      pointBackgroundColor: '#84cc16',
      pointRadius: 4,
      pointHoverRadius: 6,
      borderWidth: 2.5,
    },
    {
      label: 'מצטבר',
      data: props.data.cumulative.map(m => m.value),
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34,197,94,0.08)',
      tension: 0.4,
      fill: true,
      pointBackgroundColor: '#22c55e',
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
    title: { display: true, text: 'תזרים מזומנים — חודשי ומצטבר', font: { size: 15, family: 'Segoe UI, Arial' }, color: '#374151' },
    legend: { position: 'top', rtl: true, labels: { font: { family: 'Segoe UI, Arial', size: 12 }, usePointStyle: true, pointStyle: 'circle' } },
    tooltip: {
      rtl: true,
      backgroundColor: '#1a1a2e',
      cornerRadius: 12,
      callbacks: { label: ctx => `${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { family: 'Segoe UI, Arial', size: 11 } } },
    y: { grid: { color: '#f3f4f6' }, ticks: { font: { family: 'Segoe UI, Arial', size: 11 }, callback: v => v.toLocaleString('he-IL') } },
  },
}
</script>
