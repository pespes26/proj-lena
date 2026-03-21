<template>
  <Line :key="chartType" :data="chartData" :options="chartOptions" style="max-height: 300px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Filler, Title, Tooltip, Legend)

const props = defineProps({
  data: Array,
  projectName: String,
  chartType: { type: String, default: 'area' },
})

const isArea = computed(() => props.chartType === 'area')

const chartData = computed(() => ({
  labels: props.data.map(m => 'חודש ' + m.month),
  datasets: [
    {
      label: 'הכנסה צפויה',
      data: props.data.map(m => m.revenue),
      borderColor: '#0D9488',
      backgroundColor: isArea.value ? 'rgba(13,148,136,0.15)' : 'rgba(13,148,136,0.08)',
      tension: 0.4,
      fill: isArea.value,
      pointBackgroundColor: '#0D9488',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: isArea.value ? 0 : 5,
      pointHoverRadius: 6,
      borderWidth: 2,
    },
    {
      label: 'הוצאות תפעול',
      data: props.data.map(m => m.op_expenses),
      borderColor: '#fbbf24',
      backgroundColor: isArea.value ? 'rgba(251,191,36,0.1)' : 'rgba(251,191,36,0.06)',
      tension: 0.4,
      fill: isArea.value,
      pointBackgroundColor: '#fbbf24',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: isArea.value ? 0 : 5,
      pointHoverRadius: 6,
      borderWidth: 2,
      borderDash: isArea.value ? [] : [6, 3],
    },
    {
      label: 'רווח תפעולי',
      data: props.data.map(m => m.operating_profit),
      borderColor: '#22c55e',
      backgroundColor: isArea.value ? 'rgba(34,197,94,0.1)' : 'rgba(34,197,94,0.06)',
      tension: 0.4,
      fill: isArea.value,
      pointBackgroundColor: props.data.map(m => m.operating_profit >= 0 ? '#22c55e' : '#ef4444'),
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: isArea.value ? 0 : 5,
      pointHoverRadius: 6,
      borderWidth: 2,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    title: { display: false },
    legend: {
      position: 'top',
      rtl: true,
      labels: {
        font: { family: 'Segoe UI, Arial', size: 11 },
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 16,
      },
    },
    tooltip: {
      rtl: true,
      backgroundColor: 'rgba(255,255,255,0.95)',
      titleColor: '#1a1a2e',
      bodyColor: '#374151',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      cornerRadius: 12,
      padding: 12,
      boxPadding: 4,
      usePointStyle: true,
      callbacks: {
        label: ctx => ` ${ctx.dataset.label}: ${Number(ctx.raw).toLocaleString('he-IL')}`,
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { family: 'Segoe UI, Arial', size: 11 }, color: '#9ca3af' },
    },
    y: {
      grid: { color: '#f3f4f6', drawBorder: false },
      ticks: {
        font: { family: 'Segoe UI, Arial', size: 11 },
        color: '#9ca3af',
        callback: v => v.toLocaleString('he-IL'),
      },
      border: { display: false },
    },
  },
}))
</script>
