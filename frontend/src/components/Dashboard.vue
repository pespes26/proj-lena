<template>
  <div>
    <div v-if="error" class="text-red-500 text-sm mb-6">{{ error }}</div>
    <div v-if="loading" class="text-center py-20 text-gray-400 text-lg">טוען נתונים...</div>

    <template v-if="data">
      <!-- Hero KPI -->
      <div class="bg-white rounded-xl p-8 mb-8">
        <div class="mb-6">
          <div class="text-xs text-gray-400 mb-1">הכנסה כוללת</div>
          <div class="text-5xl font-extrabold tracking-tight text-gray-900">{{ fmt(data.total_revenue) }}</div>
          <div class="text-xs text-gray-400 mt-1">אלפי ש"ח — שנתי</div>
        </div>

        <div class="flex items-baseline gap-10 flex-wrap">
          <div>
            <div class="text-xs text-gray-400 mb-0.5">הוצאות</div>
            <div class="text-xl font-semibold text-gray-900">{{ fmt(data.total_expenses) }}</div>
          </div>
          <div>
            <div class="text-xs text-gray-400 mb-0.5">רווח תפעולי</div>
            <div class="flex items-baseline gap-2">
              <span class="text-xl font-semibold" :class="data.total_operating_profit >= 0 ? 'text-gray-900' : 'text-red-500'">
                {{ fmt(data.total_operating_profit) }}
              </span>
              <span class="text-sm font-medium" :class="data.margin >= 20 ? 'text-emerald-700' : 'text-red-500'">
                {{ data.margin != null ? data.margin + '%' : '' }}
              </span>
            </div>
          </div>
          <div>
            <div class="text-xs text-gray-400 mb-0.5">מצב מזומנים</div>
            <div class="text-xl font-semibold" :class="data.cash_position >= 0 ? 'text-gray-900' : 'text-red-500'">
              {{ fmt(data.cash_position) }}
            </div>
          </div>
          <div v-if="cfData">
            <div class="text-xs text-gray-400 mb-0.5">תזרים מצטבר</div>
            <div class="text-xl font-semibold text-gray-900">
              {{ fmt(cfData.cumulative?.[cfData.cumulative.length - 1]?.value || 0) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Chart Section -->
      <div class="bg-white rounded-xl p-8 mb-8">
        <div class="flex items-center justify-between mb-6">
          <span class="section-label">תזרים כספי</span>
          <div class="flex items-center gap-1">
            <button v-for="mode in chartModes" :key="mode.id"
              @click="chartMode = mode.id"
              :class="['px-3 py-1 text-xs font-medium transition-colors rounded-lg',
                chartMode === mode.id
                  ? 'text-gray-900 bg-gray-100'
                  : 'text-gray-400 hover:text-gray-600']">
              {{ mode.label }}
            </button>
          </div>
        </div>
        <ProjectCompareChart :summaries="data.project_summaries" :mode="chartMode" />
      </div>

      <!-- Table + Sidebar -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Project Table -->
        <div class="lg:col-span-2 bg-white rounded-xl overflow-hidden">
          <div class="px-8 pt-6 pb-4">
            <span class="section-label">פרויקטים</span>
          </div>
          <table class="w-full text-sm">
            <thead>
              <tr>
                <th class="px-8 pb-3 text-right text-xs uppercase tracking-wide text-gray-400 font-medium">פרויקט</th>
                <th class="px-4 pb-3 text-right text-xs uppercase tracking-wide text-gray-400 font-medium">מנהל</th>
                <th class="px-4 pb-3 text-right text-xs uppercase tracking-wide text-gray-400 font-medium">הכנסות</th>
                <th class="px-4 pb-3 text-right text-xs uppercase tracking-wide text-gray-400 font-medium">הוצאות</th>
                <th class="px-4 pb-3 text-right text-xs uppercase tracking-wide text-gray-400 font-medium">רווח</th>
                <th class="px-4 pb-3 text-right text-xs uppercase tracking-wide text-gray-400 font-medium">מרווח</th>
                <th class="px-8 pb-3 text-right text-xs uppercase tracking-wide text-gray-400 font-medium w-28">יחס</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(summary, name) in data.project_summaries" :key="name"
                class="border-t border-gray-100 hover:bg-gray-50/60 transition-colors">
                <td class="px-8 py-4">
                  <div class="font-medium text-gray-800">{{ name }}</div>
                  <div class="text-xs text-gray-400 font-mono">{{ priorityIds[name] }}</div>
                </td>
                <td class="px-4 py-4 text-gray-500 text-xs">{{ managers[name] || '-' }}</td>
                <td class="px-4 py-4 text-gray-700">{{ fmt(summary.total_revenue) }}</td>
                <td class="px-4 py-4 text-gray-700">{{ fmt(summary.total_op_expenses + summary.total_salary_expenses) }}</td>
                <td class="px-4 py-4 font-semibold" :class="summary.total_operating_profit >= 0 ? 'text-gray-900' : 'text-red-500'">
                  {{ fmt(summary.total_operating_profit) }}
                </td>
                <td class="px-4 py-4">
                  <span v-if="summary.margin != null" class="font-medium"
                    :class="summary.margin >= 20 ? 'text-emerald-700' : 'text-red-500'">
                    {{ summary.margin }}%
                  </span>
                  <span v-else class="text-gray-300">-</span>
                </td>
                <td class="px-8 py-4">
                  <div class="flex h-[2px] rounded-full overflow-hidden bg-gray-200">
                    <div class="bg-emerald-600 transition-all" :style="{ width: getRevenueRatio(summary) + '%' }"></div>
                    <div class="bg-gray-400 transition-all" :style="{ width: getExpenseRatio(summary) + '%' }"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Sidebar -->
        <div class="space-y-8">
          <!-- Financial Health -->
          <div class="bg-white rounded-xl p-6">
            <span class="section-label">בריאות פיננסית</span>
            <div class="mt-5 space-y-5">
              <div>
                <div class="flex justify-between text-sm mb-2">
                  <span class="text-gray-500">הכנסות</span>
                  <span class="font-semibold text-gray-800">{{ fmt(data.total_revenue) }}</span>
                </div>
                <div class="h-[2px] bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-emerald-600 rounded-full" style="width: 100%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm mb-2">
                  <span class="text-gray-500">הוצאות</span>
                  <span class="font-semibold text-gray-800">{{ fmt(data.total_expenses) }}</span>
                </div>
                <div class="h-[2px] bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-gray-500 rounded-full"
                    :style="{ width: (data.total_expenses / data.total_revenue * 100) + '%' }"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm mb-2">
                  <span class="text-gray-500">רווח נקי</span>
                  <span class="font-semibold" :class="data.total_operating_profit >= 0 ? 'text-emerald-700' : 'text-red-500'">
                    {{ fmt(data.total_operating_profit) }}
                  </span>
                </div>
                <div class="h-[2px] bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-emerald-600 rounded-full"
                    :style="{ width: Math.max(0, data.total_operating_profit / data.total_revenue * 100) + '%' }"></div>
                </div>
              </div>

              <div class="pt-4 border-t border-gray-100">
                <div class="text-xs text-gray-400 mb-3">פרויקטים מתחת לסף (20%)</div>
                <div v-for="(summary, name) in data.project_summaries" :key="name">
                  <div v-if="summary.margin != null && summary.margin < 20"
                    class="flex items-center justify-between py-1.5">
                    <span class="text-sm text-gray-600">· {{ name }}</span>
                    <span class="text-sm font-medium text-red-500">{{ summary.margin }}%</span>
                  </div>
                </div>
                <div v-if="!hasAlerts" class="text-sm text-emerald-700 font-medium py-1">כל הפרויקטים מעל הסף</div>
              </div>
            </div>
          </div>

          <!-- Expense Breakdown -->
          <div class="bg-white rounded-xl p-6">
            <span class="section-label">פילוח הוצאות</span>
            <div class="mt-5">
              <ExpenseBreakdown :summary="totalSummary" />
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboard, getCashflow, formatNumber } from '../services/api'
import ProjectCompareChart from './ProjectCompareChart.vue'
import ExpenseBreakdown from './ExpenseBreakdown.vue'

const data = ref(null)
const cfData = ref(null)
const loading = ref(true)
const error = ref(null)
const fmt = formatNumber
const chartMode = ref('grouped')

const chartModes = [
  { id: 'grouped', label: 'מקובץ' },
  { id: 'stacked', label: 'מוערם' },
  { id: 'profit', label: 'רווח בלבד' },
]

const managers = computed(() => {
  if (!data.value) return {}
  const m = {}
  for (const [name, s] of Object.entries(data.value.project_summaries)) {
    m[name] = s.meta?.manager || ''
  }
  return m
})
const priorityIds = computed(() => {
  if (!data.value) return {}
  const p = {}
  for (const [name, s] of Object.entries(data.value.project_summaries)) {
    p[name] = s.meta?.priority_id || ''
  }
  return p
})

const totalSummary = computed(() => {
  if (!data.value) return { total_op_expenses: 0, total_salary_expenses: 0 }
  const sums = Object.values(data.value.project_summaries)
  return {
    total_op_expenses: sums.reduce((a, s) => a + s.total_op_expenses, 0),
    total_salary_expenses: sums.reduce((a, s) => a + s.total_salary_expenses, 0),
  }
})

const hasAlerts = computed(() => {
  if (!data.value) return false
  return Object.values(data.value.project_summaries).some(s => s.margin != null && s.margin < 20)
})

function getRevenueRatio(summary) {
  const total = summary.total_revenue + summary.total_op_expenses + summary.total_salary_expenses
  return total > 0 ? (summary.total_revenue / total * 100).toFixed(0) : 50
}
function getExpenseRatio(summary) {
  const total = summary.total_revenue + summary.total_op_expenses + summary.total_salary_expenses
  return total > 0 ? ((summary.total_op_expenses + summary.total_salary_expenses) / total * 100).toFixed(0) : 50
}

onMounted(async () => {
  try {
    data.value = await getDashboard()
    getCashflow().then(d => { cfData.value = d }).catch(() => {})
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
