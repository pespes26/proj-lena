<template>
  <Bar :data="chartData" :options="chartOptions" style="max-height: 320px;" />
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, COLORS } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({ data: Object })

const chartData = computed(() => ({
  labels: props.data.month_labels,
  datasets: [{
    label: 'נטו חודשי',
    data: props.data.monthly_net.map(m => m.value),
    backgroundColor: props.data.monthly_net.map(m => m.value >= 0 ? 'rgba(13,148,136,0.8)' : 'rgba(239,68,68,0.8)'),
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
      ...tooltipConfig,
      callbacks: { label: ctx => ` נטו: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { ...axisConfig.x },
    y: { ...axisConfig.y },
  },
}
</script>
