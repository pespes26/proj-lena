<template>
  <Bar :key="mode" :data="chartData" :options="chartOptions" style="max-height: 320px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps({
  summaries: Object,
  mode: { type: String, default: 'grouped' },
})

const chartData = computed(() => {
  const names = Object.keys(props.summaries)

  if (props.mode === 'profit') {
    return {
      labels: names,
      datasets: [{
        label: 'רווח תפעולי',
        data: names.map(n => props.summaries[n].total_operating_profit),
        backgroundColor: names.map(n => props.summaries[n].total_operating_profit >= 0 ? '#0D9488' : '#ef4444'),
        borderRadius: 8,
        barPercentage: 0.5,
      }],
    }
  }

  const stacked = props.mode === 'stacked'
  return {
    labels: names,
    datasets: [
      {
        label: 'הכנסות',
        data: names.map(n => props.summaries[n].total_revenue),
        backgroundColor: '#0D9488',
        borderRadius: stacked ? 0 : 6,
        barPercentage: stacked ? 0.5 : 0.7,
        stack: stacked ? 'combined' : undefined,
      },
      {
        label: 'הוצאות תפעול',
        data: names.map(n => -props.summaries[n].total_op_expenses),
        backgroundColor: '#fbbf24',
        borderRadius: stacked ? 0 : 6,
        barPercentage: stacked ? 0.5 : 0.7,
        stack: stacked ? 'combined' : undefined,
      },
      {
        label: 'הוצאות שכר',
        data: names.map(n => -props.summaries[n].total_salary_expenses),
        backgroundColor: '#f97316',
        borderRadius: stacked ? 0 : 6,
        barPercentage: stacked ? 0.5 : 0.7,
        stack: stacked ? 'combined' : undefined,
      },
    ],
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      rtl: true,
      labels: { font: { family: 'Segoe UI, Arial', size: 11 }, padding: 16, usePointStyle: true, pointStyle: 'rectRounded' },
    },
    tooltip: {
      rtl: true,
      backgroundColor: '#1a1a2e',
      cornerRadius: 12,
      padding: 12,
      titleFont: { family: 'Segoe UI, Arial' },
      bodyFont: { family: 'Segoe UI, Arial' },
      callbacks: {
        label: ctx => `${ctx.dataset.label}: ${Math.abs(Number(ctx.raw)).toLocaleString('he-IL')}`,
      },
    },
  },
  scales: {
    x: {
      stacked: props.mode === 'stacked',
      grid: { display: false },
      ticks: { font: { family: 'Segoe UI, Arial', size: 11 } },
    },
    y: {
      stacked: props.mode === 'stacked',
      grid: { color: '#f3f4f6' },
      ticks: {
        font: { family: 'Segoe UI, Arial', size: 11 },
        callback: v => Math.abs(v).toLocaleString('he-IL'),
      },
    },
  },
}))
</script>
