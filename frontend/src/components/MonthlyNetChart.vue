<template>
  <div class="ui-chart-container ui-chart-container--lg" role="img" aria-label="גרף נטו חודשי: הכנסות פחות הוצאות לכל חודש">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
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
    backgroundColor: props.data.monthly_net.map(m => m.value >= 0 ? COLORS.green : COLORS.red),
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
      callbacks: { label: ctx => ` נטו: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
  scales: {
    x: { ...axisConfig.x },
    y: { ...axisConfig.y },
  },
}
</script>
