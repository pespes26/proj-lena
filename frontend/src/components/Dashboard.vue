<template>
  <div>
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm">{{ error }}</div>
    <div v-if="loading" class="text-center py-20 text-gray-400 text-lg">טוען נתונים...</div>

    <template v-if="data">
      <!-- KPI Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-gray-400">הכנסה כוללת</span>
            <span class="w-9 h-9 bg-lime-50 rounded-xl flex items-center justify-center text-lime-600 font-bold text-sm">&#8362;</span>
          </div>
          <div class="text-2xl font-bold text-gray-800">{{ fmt(data.total_revenue) }}</div>
          <div class="text-[10px] text-gray-400 mt-1">אלפי ש"ח — שנתי</div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-gray-400">סה"כ הוצאות</span>
            <span class="w-9 h-9 bg-amber-50 rounded-xl flex items-center justify-center text-amber-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17 9l-5 5-5-5"/></svg>
            </span>
          </div>
          <div class="text-2xl font-bold text-gray-800">{{ fmt(data.total_expenses) }}</div>
          <div class="text-[10px] text-gray-400 mt-1">אלפי ש"ח — שנתי</div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-gray-400">רווח תפעולי</span>
            <span class="w-9 h-9 rounded-xl flex items-center justify-center"
              :class="data.total_operating_profit >= 0 ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-500'">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
            </span>
          </div>
          <div class="text-2xl font-bold" :class="data.total_operating_profit >= 0 ? 'text-green-600' : 'text-red-500'">
            {{ fmt(data.total_operating_profit) }}
          </div>
          <div class="text-[10px] mt-1" :class="data.margin >= 20 ? 'text-green-500' : 'text-orange-500'">
            מרווח: {{ data.margin != null ? data.margin + '%' : '-' }}
          </div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-gray-400">מצב מזומנים</span>
            <span class="w-9 h-9 bg-purple-50 rounded-xl flex items-center justify-center text-purple-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8V7m0 1v8m0 0v1"/></svg>
            </span>
          </div>
          <div class="text-2xl font-bold" :class="data.cash_position >= 0 ? 'text-gray-800' : 'text-red-500'">
            {{ fmt(data.cash_position) }}
          </div>
          <div class="text-[10px] text-gray-400 mt-1">יתרה מצטברת</div>
        </div>
      </div>

      <!-- Row 1: Money Flow (big chart) + Cashflow mini -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
        <div class="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h3 class="font-semibold text-gray-700">תזרים כספי</h3>
              <p class="text-xs text-gray-400 mt-0.5">הכנסות מול הוצאות — כלל הפרויקטים</p>
            </div>
            <div class="flex bg-gray-100 rounded-xl p-1 gap-0.5">
              <button v-for="mode in chartModes" :key="mode.id"
                @click="chartMode = mode.id"
                :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition-all', chartMode === mode.id ? 'bg-white shadow-sm text-gray-700' : 'text-gray-500 hover:text-gray-600']">
                {{ mode.label }}
              </button>
            </div>
          </div>
          <ProjectCompareChart :summaries="data.project_summaries" :mode="chartMode" />
        </div>

        <!-- Cashflow area chart -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-700 mb-1">תזרים מצטבר</h3>
          <p class="text-xs text-gray-400 mb-4">מגמה חודשית</p>
          <CashflowMiniChart v-if="cfData" :data="cfData" />
          <div v-else class="text-center py-12 text-gray-300 text-sm">טוען...</div>
        </div>
      </div>

      <!-- Row 2: Project cards + Expense breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
        <!-- Project performance cards (2 cols) -->
        <div class="lg:col-span-2">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="(summary, name) in data.project_summaries" :key="name"
              class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                    :class="summary.margin != null && summary.margin >= 20 ? 'bg-lime-500' : 'bg-orange-400'">
                    {{ name.charAt(0) }}
                  </div>
                  <div>
                    <span class="text-sm font-medium text-gray-700">{{ name }}</span>
                    <div class="text-[10px] font-mono text-blue-500">{{ priorityIds[name] }}</div>
                  </div>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold"
                  :class="summary.margin != null && summary.margin >= 20 ? 'bg-lime-50 text-lime-600' : 'bg-orange-50 text-orange-500'">
                  {{ summary.margin != null ? summary.margin + '%' : '-' }}
                </span>
              </div>
              <div class="grid grid-cols-3 gap-3 mb-3">
                <div>
                  <div class="text-[10px] text-gray-400">הכנסה</div>
                  <div class="text-sm font-bold text-gray-800">{{ fmt(summary.total_revenue) }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-400">הוצאות</div>
                  <div class="text-sm font-bold text-gray-800">{{ fmt(summary.total_op_expenses + summary.total_salary_expenses) }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-400">רווח</div>
                  <div class="text-sm font-bold" :class="summary.total_operating_profit >= 0 ? 'text-green-600' : 'text-red-500'">
                    {{ fmt(summary.total_operating_profit) }}
                  </div>
                </div>
              </div>
              <div class="flex h-2 rounded-full overflow-hidden bg-gray-100">
                <div class="bg-lime-400 transition-all" :style="{ width: getRevenueRatio(summary) + '%' }"></div>
                <div class="bg-amber-400 transition-all" :style="{ width: getExpenseRatio(summary) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Overall expense breakdown -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-700 mb-1">פילוח הוצאות</h3>
          <p class="text-xs text-gray-400 mb-4">כלל הפרויקטים</p>
          <ExpenseBreakdown :summary="totalSummary" />
        </div>
      </div>

      <!-- Row 3: Table + Quick stats -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="font-semibold text-gray-700">סיכום לפי פרויקט</h3>
          </div>
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-gray-50/50">
                <th class="px-5 py-3 text-right font-medium text-gray-500">פרויקט</th>
                <th class="px-5 py-3 text-right font-medium text-gray-500">מנהל</th>
                <th class="px-5 py-3 text-right font-medium text-gray-500">הכנסות</th>
                <th class="px-5 py-3 text-right font-medium text-gray-500">הוצאות</th>
                <th class="px-5 py-3 text-right font-medium text-gray-500">רווח</th>
                <th class="px-5 py-3 text-right font-medium text-gray-500">מרווח</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(summary, name) in data.project_summaries" :key="name"
                class="border-t border-gray-50 hover:bg-gray-50/50 transition-colors">
                <td class="px-5 py-3.5">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-lg flex items-center justify-center text-white text-[10px] font-bold"
                      :class="summary.margin != null && summary.margin >= 20 ? 'bg-lime-500' : 'bg-orange-400'">
                      {{ name.charAt(0) }}
                    </div>
                    <div>
                      <span class="font-medium text-gray-800">{{ name }}</span>
                      <div class="text-[10px] font-mono text-blue-500">{{ priorityIds[name] }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-3.5 text-gray-500 text-xs">{{ managers[name] || '-' }}</td>
                <td class="px-5 py-3.5 text-gray-600">{{ fmt(summary.total_revenue) }}</td>
                <td class="px-5 py-3.5 text-gray-600">{{ fmt(summary.total_op_expenses + summary.total_salary_expenses) }}</td>
                <td class="px-5 py-3.5 font-semibold" :class="summary.total_operating_profit >= 0 ? 'text-green-600' : 'text-red-500'">
                  {{ fmt(summary.total_operating_profit) }}
                </td>
                <td class="px-5 py-3.5">
                  <span v-if="summary.margin != null"
                    class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
                    :class="summary.margin < 20 ? 'bg-red-50 text-red-600' : 'bg-lime-50 text-lime-700'">
                    {{ summary.margin }}%
                  </span>
                  <span v-else class="text-gray-400">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Financial health -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-700 mb-4">בריאות פיננסית</h3>
          <div class="space-y-5">
            <div>
              <div class="flex justify-between text-sm mb-1.5">
                <span class="text-gray-500">הכנסות</span>
                <span class="font-bold text-gray-800">{{ fmt(data.total_revenue) }}</span>
              </div>
              <div class="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-lime-400 rounded-full" style="width: 100%"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-sm mb-1.5">
                <span class="text-gray-500">הוצאות</span>
                <span class="font-bold text-gray-800">{{ fmt(data.total_expenses) }}</span>
              </div>
              <div class="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-amber-400 rounded-full"
                  :style="{ width: (data.total_expenses / data.total_revenue * 100) + '%' }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-sm mb-1.5">
                <span class="text-gray-500">רווח נקי</span>
                <span class="font-bold" :class="data.total_operating_profit >= 0 ? 'text-green-600' : 'text-red-500'">
                  {{ fmt(data.total_operating_profit) }}
                </span>
              </div>
              <div class="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-green-400 rounded-full"
                  :style="{ width: Math.max(0, data.total_operating_profit / data.total_revenue * 100) + '%' }"></div>
              </div>
            </div>

            <div class="pt-4 border-t border-gray-100">
              <div class="text-xs text-gray-400 mb-2">פרויקטים מתחת לסף (20%)</div>
              <div v-for="(summary, name) in data.project_summaries" :key="name">
                <div v-if="summary.margin != null && summary.margin < 20"
                  class="flex items-center justify-between py-1.5">
                  <span class="text-sm text-gray-600">{{ name }}</span>
                  <span class="text-sm font-bold text-orange-500">{{ summary.margin }}%</span>
                </div>
              </div>
              <div v-if="!hasAlerts" class="text-sm text-lime-600 font-medium py-1">כל הפרויקטים מעל הסף</div>
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
import CashflowMiniChart from './CashflowMiniChart.vue'

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

const managers = { 'מנרב סנטר': 'אתי', 'קריית מנרב': 'אתי', 'הדסה': 'אתי', 'עמיגור באר שבע': 'אלון' }
const priorityIds = { 'מנרב סנטר': 'P-1001', 'קריית מנרב': 'P-1002', 'הדסה': 'P-1003', 'עמיגור באר שבע': 'P-2001' }

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
