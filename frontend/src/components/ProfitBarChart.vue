<template>
  <div class="ui-chart-container" role="img" aria-label="גרף רווח תפעולי: פירוט חודשי">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
import { tooltipConfig, axisConfig, COLORS } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps({ data: Array })

const chartData = computed(() => ({
  labels: props.data.map(m => 'חודש ' + m.month),
  datasets: [{
    label: 'רווח תפעולי',
    data: props.data.map(m => m.operating_profit),
    backgroundColor: props.data.map(m => m.operating_profit >= 0 ? COLORS.green : COLORS.red),
    borderRadius: 0,
    barPercentage: 0.65,
  }],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      ...tooltipConfig,
      callbacks: { label: ctx => ` רווח: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { ...axisConfig.x },
    y: { ...axisConfig.y },
  },
}
</script>
