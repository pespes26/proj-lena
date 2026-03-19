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
  datasets: [{
    label: 'נטו חודשי',
    data: props.data.monthly_net.map(m => m.value),
    backgroundColor: props.data.monthly_net.map(m => m.value >= 0 ? 'rgba(132,204,22,0.8)' : 'rgba(239,68,68,0.8)'),
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
      rtl: true, backgroundColor: 'rgba(255,255,255,0.95)', titleColor: '#1a1a2e', bodyColor: '#374151',
      borderColor: '#e5e7eb', borderWidth: 1, cornerRadius: 12, padding: 10,
      callbacks: { label: ctx => ` נטו: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#9ca3af' } },
    y: { grid: { color: '#f3f4f6', drawBorder: false }, border: { display: false },
      ticks: { font: { size: 10 }, color: '#9ca3af', callback: v => v.toLocaleString('he-IL') } },
  },
}
</script>
