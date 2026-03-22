<template>
  <Bar :key="mode" :data="chartData" :options="chartOptions" style="max-height: 320px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, legendConfig, COLORS, absLabelCallback } from '../utils/chartDefaults'

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
        backgroundColor: names.map(n => props.summaries[n].total_operating_profit >= 0 ? COLORS.primary : COLORS.red),
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
        backgroundColor: COLORS.primary,
        borderRadius: stacked ? 0 : 6,
        barPercentage: stacked ? 0.5 : 0.7,
        stack: stacked ? 'combined' : undefined,
      },
      {
        label: 'הוצאות תפעול',
        data: names.map(n => -props.summaries[n].total_op_expenses),
        backgroundColor: COLORS.amber,
        borderRadius: stacked ? 0 : 6,
        barPercentage: stacked ? 0.5 : 0.7,
        stack: stacked ? 'combined' : undefined,
      },
      {
        label: 'הוצאות שכר',
        data: names.map(n => -props.summaries[n].total_salary_expenses),
        backgroundColor: COLORS.orange,
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
      ...legendConfig,
      labels: { ...legendConfig.labels, pointStyle: 'rectRounded' },
    },
    tooltip: {
      ...tooltipConfig,
      callbacks: { label: absLabelCallback() },
    },
  },
  scales: {
    x: {
      ...axisConfig.x,
      stacked: props.mode === 'stacked',
    },
    y: {
      ...axisConfig.y,
      stacked: props.mode === 'stacked',
      ticks: {
        ...axisConfig.y.ticks,
        callback: v => Math.abs(v).toLocaleString('he-IL'),
      },
    },
  },
}))
</script>
