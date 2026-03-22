<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">תזרים מזומנים</h2>
        <p class="text-sm text-gray-400 mt-1">סקירת תזרים כלל הפרויקטים</p>
      </div>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm">{{ error }}</div>
    <div v-if="loading" class="text-center py-20 text-gray-400">טוען נתונים...</div>

    <template v-if="cfData">
      <!-- KPI Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <div class="ios-card p-6">
          <div class="text-sm text-gray-500 font-medium mb-2">סך הכנסות תקופתי</div>
          <div class="text-3xl font-bold text-gray-900">{{ fmt(totalRevenue) }}</div>
        </div>
        <div class="ios-card p-6">
          <div class="text-sm text-gray-500 font-medium mb-2">סך הוצאות תקופתי</div>
          <div class="text-3xl font-bold text-gray-900">{{ fmt(totalExpenses) }}</div>
        </div>
        <div class="ios-card p-6">
          <div class="text-sm text-gray-500 font-medium mb-2">נטו תקופתי</div>
          <div class="text-3xl font-bold" :class="totalNet >= 0 ? 'text-green-600' : 'text-red-500'">{{ fmt(totalNet) }}</div>
        </div>
        <div class="ios-card p-6">
          <div class="text-sm text-gray-500 font-medium mb-2">יתרה מצטברת</div>
          <div class="text-3xl font-bold" :class="lastCumulative >= 0 ? 'text-green-600' : 'text-red-500'">{{ fmt(lastCumulative) }}</div>
        </div>
      </div>

      <!-- Row 1: Main chart + view toggle -->
      <div class="ios-card p-6 mb-6">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-lg font-bold text-gray-900">תזרים מזומנים</h3>
          <div class="flex bg-gray-100 rounded-xl p-1 gap-0.5">
            <button v-for="v in views" :key="v.id"
              @click="activeView = v.id"
              :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                activeView === v.id ? 'bg-white shadow-sm text-gray-700' : 'text-gray-500 hover:text-gray-600']">
              {{ v.label }}
            </button>
          </div>
        </div>

        <!-- Cumulative area chart -->
        <CashFlowChart v-if="activeView === 'cumulative'" :data="cfData" />

        <!-- Revenue vs Expenses bars -->
        <RevenueExpenseChart v-else-if="activeView === 'revexp'" :data="cfData" />

        <!-- Monthly net waterfall -->
        <MonthlyNetChart v-else-if="activeView === 'monthly'" :data="cfData" />
      </div>

      <!-- Row 2: Per-project comparison + breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        <!-- Per-project stacked bar -->
        <div class="ios-card p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">השוואת פרויקטים — נטו</h3>
          <ProjectNetChart :data="cfData" />
        </div>

        <!-- Per-project totals cards -->
        <div class="ios-card p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">סיכום לפי פרויקט</h3>
          <div class="space-y-3">
            <div v-for="(months, pname) in cfData.projects" :key="pname"
              class="bg-gray-50 rounded-xl p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">{{ pname }}</span>
                <span class="text-sm font-bold"
                  :class="projectTotal(months) >= 0 ? 'text-green-600' : 'text-red-500'">
                  {{ fmt(projectTotal(months)) }}
                </span>
              </div>
              <div class="flex h-2 rounded-full overflow-hidden bg-gray-200">
                <div class="bg-emerald-500 transition-all"
                  :style="{ width: projectRevenuePercent(months) + '%' }"></div>
                <div class="bg-amber-400 transition-all"
                  :style="{ width: projectExpensePercent(months) + '%' }"></div>
              </div>
              <div class="flex justify-between mt-1.5 text-[10px] text-gray-400">
                <span>הכנסה: {{ fmt(projectRevSum(months)) }}</span>
                <span>הוצאה: {{ fmt(projectExpSum(months)) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Row 3: Tables -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- Monthly + Cumulative table -->
        <div class="ios-card overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="text-lg font-bold text-gray-900">תזרים חודשי ומצטבר</h3>
          </div>
          <div class="overflow-y-auto max-h-[400px]">
            <table class="w-full text-sm">
              <thead class="sticky top-0 bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-right font-medium text-gray-500">חודש</th>
                  <th class="px-4 py-3 text-right font-medium text-gray-500">הכנסה</th>
                  <th class="px-4 py-3 text-right font-medium text-gray-500">הוצאה</th>
                  <th class="px-4 py-3 text-right font-medium text-gray-500">נטו</th>
                  <th class="px-4 py-3 text-right font-medium text-gray-500">מצטבר</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(m, i) in cfData.monthly_net" :key="i"
                  class="border-t border-gray-50 hover:bg-gray-50/50 transition-colors">
                  <td class="px-4 py-2.5 font-medium text-gray-700">{{ m.month }}</td>
                  <td class="px-4 py-2.5 text-gray-600">{{ fmt(cfData.totals[i]?.revenue) }}</td>
                  <td class="px-4 py-2.5 text-gray-600">{{ fmt(cfData.totals[i]?.expenses) }}</td>
                  <td class="px-4 py-2.5 font-semibold" :class="m.value >= 0 ? 'text-green-600' : 'text-red-500'">
                    {{ fmt(m.value) }}
                  </td>
                  <td class="px-4 py-2.5 font-semibold" :class="cfData.cumulative[i].value >= 0 ? 'text-green-600' : 'text-red-500'">
                    {{ fmt(cfData.cumulative[i].value) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Per-project detail table -->
        <div class="ios-card overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="text-lg font-bold text-gray-900">פירוט נטו לפי פרויקט</h3>
          </div>
          <div class="overflow-auto max-h-[400px]">
            <table class="w-full text-sm whitespace-nowrap">
              <thead class="sticky top-0 bg-gray-50">
                <tr>
                  <th class="px-3 py-3 text-right font-medium text-gray-500 sticky right-0 bg-gray-50 z-10">חודש</th>
                  <th v-for="pname in Object.keys(cfData.projects)" :key="pname"
                    class="px-3 py-3 text-right font-medium text-gray-500">{{ pname }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(label, i) in cfData.month_labels" :key="label"
                  class="border-t border-gray-50 hover:bg-gray-50/50 transition-colors">
                  <td class="px-3 py-2.5 font-medium text-gray-700 sticky right-0 bg-white z-10">{{ label }}</td>
                  <td v-for="pname in Object.keys(cfData.projects)" :key="pname"
                    class="px-3 py-2.5 font-medium"
                    :class="cfData.projects[pname][i].profit >= 0 ? 'text-green-600' : 'text-red-500'">
                    {{ fmt(cfData.projects[pname][i].profit) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCashflow, formatNumber } from '../services/api'
import CashFlowChart from './CashFlowChart.vue'
import RevenueExpenseChart from './RevenueExpenseChart.vue'
import MonthlyNetChart from './MonthlyNetChart.vue'
import ProjectNetChart from './ProjectNetChart.vue'

const cfData = ref(null)
const loading = ref(true)
const error = ref(null)
const fmt = formatNumber
const activeView = ref('cumulative')

const views = [
  { id: 'cumulative', label: 'מצטבר' },
  { id: 'revexp', label: 'הכנסות/הוצאות' },
  { id: 'monthly', label: 'נטו חודשי' },
]

const totalRevenue = computed(() => cfData.value?.totals.reduce((a, t) => a + t.revenue, 0) || 0)
const totalExpenses = computed(() => cfData.value?.totals.reduce((a, t) => a + t.expenses, 0) || 0)
const totalNet = computed(() => totalRevenue.value - totalExpenses.value)
const lastCumulative = computed(() => {
  const c = cfData.value?.cumulative
  return c?.length ? c[c.length - 1].value : 0
})

function projectTotal(months) { return months.reduce((a, m) => a + m.profit, 0) }
function projectRevSum(months) { return months.reduce((a, m) => a + m.revenue, 0) }
function projectExpSum(months) { return months.reduce((a, m) => a + m.expenses, 0) }
function projectRevenuePercent(months) {
  const r = projectRevSum(months), e = projectExpSum(months), t = r + e
  return t > 0 ? (r / t * 100).toFixed(0) : 50
}
function projectExpensePercent(months) {
  const r = projectRevSum(months), e = projectExpSum(months), t = r + e
  return t > 0 ? (e / t * 100).toFixed(0) : 50
}

onMounted(async () => {
  try {
    cfData.value = await getCashflow()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
