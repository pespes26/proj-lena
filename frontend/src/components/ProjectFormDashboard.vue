<template>
  <div v-if="loading" class="text-center py-20 text-gray-400">טוען נתונים...</div>
  <div v-else-if="!formData" class="text-center py-20">
    <div class="text-5xl mb-4 opacity-30">📊</div>
    <div class="text-lg font-medium text-gray-500 mb-2">אין מידע כעת</div>
    <div class="text-sm text-gray-400">לפרויקט זה אין עדיין נתונים.</div>
  </div>
  <div v-else>
    <!-- Project Header -->
    <div class="flex items-start justify-between mb-8">
      <div>
        <div class="flex items-center gap-3 mb-1">
          <h2 class="text-xl font-bold text-gray-800">{{ project }}</h2>
          <span class="text-xs bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded-full font-medium">{{ formData.area || 'FM' }}</span>
        </div>
        <div class="text-sm text-gray-500 flex items-center gap-4 flex-wrap">
          <span v-if="formData.manager" class="flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            {{ formData.manager }}
          </span>
          <span v-if="formData.client" class="flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
            {{ formData.client }}
          </span>
          <span v-if="formData.start_date" class="flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            {{ formatDate(formData.start_date) }}
          </span>
          <span v-if="formData.priority_id" class="font-mono text-xs text-gray-400">{{ formData.priority_id }}</span>
        </div>
        <p v-if="formData.description" class="text-xs text-gray-400 mt-2 max-w-xl">{{ formData.description }}</p>
      </div>
      <button @click="$emit('edit')"
        class="px-4 py-2 bg-gray-100 text-gray-600 text-sm rounded-xl hover:bg-gray-200 transition flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
        עריכת טופס
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-8">
      <div class="bg-white rounded-2xl border border-gray-200 p-3 sm:p-5">
        <div class="text-xs text-gray-400 mb-1">סך הכנסות</div>
        <div class="text-lg sm:text-2xl font-bold text-gray-800">{{ fmt(totalRevenue) }}</div>
        <div class="text-[10px] text-gray-400 mt-1">₪</div>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-3 sm:p-5">
        <div class="text-xs text-gray-400 mb-1">סך הוצאות</div>
        <div class="text-lg sm:text-2xl font-bold text-orange-600">{{ fmt(totalExpenses) }}</div>
        <div class="text-[10px] text-gray-400 mt-1">₪</div>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-3 sm:p-5">
        <div class="text-xs text-gray-400 mb-1">רווח צפוי</div>
        <div class="text-lg sm:text-2xl font-bold" :class="profit >= 0 ? 'text-emerald-700' : 'text-red-500'">{{ fmt(profit) }}</div>
        <div class="text-[10px] text-gray-400 mt-1">₪</div>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-3 sm:p-5">
        <div class="text-xs text-gray-400 mb-1">מרווח צפוי</div>
        <div class="text-lg sm:text-2xl font-bold" :class="margin >= 20 ? 'text-emerald-700' : margin >= 0 ? 'text-orange-500' : 'text-red-500'">{{ margin.toFixed(1) }}%</div>
        <div class="w-full bg-gray-200 rounded-full h-1.5 mt-2">
          <div class="h-full rounded-full transition-all" :class="margin >= 20 ? 'bg-emerald-700' : margin >= 0 ? 'bg-orange-400' : 'bg-red-500'"
            :style="{ width: Math.min(Math.max(margin, 0), 100) + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Payment Terms + Revenue Chart -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mb-8">
      <!-- Payment Terms -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-4">תנאי תשלום הכנסה</h3>
        <div v-if="paymentTerms.length" class="space-y-3">
          <div v-for="(term, i) in paymentTerms" :key="i">
            <div class="flex items-center justify-between text-xs mb-1">
              <span class="text-gray-600 font-medium">{{ term.type }}</span>
              <span class="text-gray-500">{{ term.percent }}%</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-2.5">
              <div class="h-full rounded-full transition-all" :style="{ width: term.percent + '%' }"
                :class="term.type === 'מקדמה' || term.type === 'מזומן' ? 'bg-emerald-500' : 'bg-amber-400'"></div>
            </div>
            <div class="text-[10px] text-gray-400 mt-0.5">
              {{ fmt(Math.round(totalRevenue * term.percent / 100)) }} ₪
              <span v-if="term.type !== 'מקדמה' && term.type !== 'מזומן'" class="text-amber-500"> — תשלום בהשהייה</span>
            </div>
          </div>
        </div>
        <div v-else class="text-xs text-gray-400 text-center py-4">לא הוגדרו תנאי תשלום</div>
      </div>

      <!-- Revenue Forecast Chart -->
      <div class="sm:col-span-2 bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-4">תחזית הכנסות חודשית</h3>
        <div class="h-48">
          <Bar v-if="revenueChartData" :data="revenueChartData" :options="barOptions" />
        </div>
        <div class="flex items-center gap-4 mt-3 text-[10px] text-gray-400">
          <div class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded bg-emerald-500"></span> הכנסה צפויה</div>
          <div class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded bg-amber-400"></span> כניסת תשלום (שוטף+)</div>
        </div>
      </div>
    </div>

    <!-- Expenses Section -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mb-8">
      <!-- Expense Breakdown Doughnut -->
      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-4">פילוח הוצאות</h3>
        <div class="h-48" v-if="expenseChartData">
          <Doughnut :data="expenseChartData" :options="doughnutOptions" />
        </div>
        <div v-else class="text-xs text-gray-400 text-center py-10">אין הוצאות</div>
        <div class="space-y-1.5 mt-4">
          <div v-for="cat in expenseCategories" :key="cat.key" class="flex items-center justify-between text-xs">
            <div class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: cat.chartColor }"></span>
              <span class="text-gray-600">{{ cat.label }}</span>
            </div>
            <span class="font-medium text-gray-700">{{ fmt(cat.total) }} ₪</span>
          </div>
        </div>
      </div>

      <!-- Suppliers list -->
      <div class="sm:col-span-2 bg-white rounded-2xl border border-gray-200 p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-4">ספקים וקבלנים</h3>
        <div v-if="allSuppliers.length" class="space-y-2 max-h-80 overflow-y-auto">
          <div v-for="(sup, i) in allSuppliers" :key="i"
            class="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3 border border-gray-100">
            <div>
              <div class="text-sm font-medium text-gray-700">{{ sup.name || 'ללא שם' }}</div>
              <div class="text-[10px] text-gray-400 flex items-center gap-2 mt-0.5">
                <span class="px-1.5 py-0.5 rounded bg-gray-200 text-gray-500">{{ sup.category }}</span>
                <span v-if="sup.payment_terms">{{ sup.payment_terms }}</span>
                <span v-if="sup.start_date">{{ formatDate(sup.start_date) }}</span>
                <span v-if="sup.start_date && sup.end_date">→</span>
                <span v-if="sup.end_date">{{ formatDate(sup.end_date) }}</span>
              </div>
            </div>
            <div class="text-sm font-bold text-gray-700">{{ fmt(sup.amount) }} ₪</div>
          </div>
        </div>
        <div v-else class="text-xs text-gray-400 text-center py-10">לא הוגדרו ספקים</div>
      </div>
    </div>

    <!-- Monthly Expense Breakdown -->
    <div class="bg-white rounded-2xl border border-gray-200 p-5 mb-8">
      <h3 class="text-sm font-bold text-gray-700 mb-4">פירוט הוצאות חודשי</h3>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[600px] text-xs" dir="rtl">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="text-right py-2 px-2 font-medium text-gray-500 sticky right-0 bg-white">קטגוריה / ספק</th>
              <th v-for="m in activeMonths" :key="m" class="text-center py-2 px-1.5 font-medium text-gray-400 min-w-[60px]">{{ monthName(m) }}</th>
              <th class="text-center py-2 px-2 font-bold text-gray-600">סה"כ</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="cat in monthlyBreakdown" :key="cat.key">
              <!-- Category header row -->
              <tr class="bg-gray-50/70">
                <td class="py-2 px-2 font-bold text-gray-700 sticky right-0 bg-gray-50/70">{{ cat.label }}</td>
                <td v-for="m in activeMonths" :key="m" class="text-center py-2 px-1.5 font-bold text-gray-700">
                  {{ cat.monthlyTotals[m] ? fmt(cat.monthlyTotals[m]) : '-' }}
                </td>
                <td class="text-center py-2 px-2 font-bold text-emerald-700">{{ fmt(cat.grandTotal) }}</td>
              </tr>
              <!-- Individual line items -->
              <tr v-for="(line, li) in cat.lines" :key="li" class="border-b border-gray-50 hover:bg-gray-50/50">
                <td class="py-1.5 px-2 pr-6 text-gray-500 sticky right-0 bg-white">{{ line.name || 'ללא שם' }}</td>
                <td v-for="m in activeMonths" :key="m" class="text-center py-1.5 px-1.5"
                  :class="line.months[m] ? 'text-gray-700' : 'text-gray-200'">
                  {{ line.months[m] ? fmt(line.months[m]) : '-' }}
                </td>
                <td class="text-center py-1.5 px-2 font-medium text-gray-600">{{ fmt(line.total) }}</td>
              </tr>
            </template>
            <!-- Grand total row -->
            <tr class="border-t-2 border-gray-300 bg-gray-100">
              <td class="py-2.5 px-2 font-bold text-gray-800 sticky right-0 bg-gray-100">סה"כ הוצאות</td>
              <td v-for="m in activeMonths" :key="m" class="text-center py-2.5 px-1.5 font-bold text-gray-800">
                {{ grandMonthlyTotal(m) ? fmt(grandMonthlyTotal(m)) : '-' }}
              </td>
              <td class="text-center py-2.5 px-2 font-bold text-red-600 text-sm">{{ fmt(grandTotal) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Cashflow Chart -->
    <div class="bg-white rounded-2xl border border-gray-200 p-5">
      <h3 class="text-sm font-bold text-gray-700 mb-4">תזרים צפוי</h3>
      <div class="h-56">
        <Bar v-if="cashflowChartData" :data="cashflowChartData" :options="cashflowOptions" />
      </div>
      <div class="flex items-center gap-4 mt-3 text-[10px] text-gray-400">
        <div class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded bg-emerald-500"></span> כניסות</div>
        <div class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded bg-orange-400"></span> יציאות</div>
        <div class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded bg-emerald-500"></span> מצטבר</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend, PointElement, LineElement } from 'chart.js'
import { getProjectForm } from '../services/api'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend, PointElement, LineElement)

const props = defineProps({ project: String })
defineEmits(['edit'])

const loading = ref(true)
const formData = ref(null)

const fmt = (val) => val != null ? Number(val).toLocaleString('he-IL', { maximumFractionDigits: 0 }) : '-'
const formatDate = (d) => {
  if (!d) return ''
  const parts = d.split('-')
  return parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : d
}

// Extract X days from שוטף+X
function extractShotefDays(type) {
  if (!type) return 0
  if (type.includes('שוטף+90')) return 90
  if (type.includes('שוטף+60')) return 60
  if (type.includes('שוטף+45')) return 45
  if (type.includes('שוטף+30')) return 30
  if (type.includes('שוטף+0') || type === 'שוטף') return 0
  return 0
}

// Calculate payment month: end of invoice month + X days
function shotefPaymentMonth(invoiceMonth, invoiceYear, xDays) {
  const lastDay = new Date(invoiceYear, invoiceMonth, 0).getDate()
  const endOfMonth = new Date(invoiceYear, invoiceMonth - 1, lastDay)
  const paymentDate = new Date(endOfMonth.getTime() + xDays * 86400000)
  return paymentDate.getMonth() + 1
}

const paymentTerms = computed(() => formData.value?.revenue_payment_terms || [])
const totalRevenue = computed(() => formData.value?.total_revenue || 0)

const totalExpenses = computed(() => {
  if (!formData.value) return 0
  let total = 0
  for (const sub of formData.value.subcontractors || []) total += Number(sub.monthly_amount) || 0
  for (const cat of ['manpower', 'equipment', 'insurance', 'consultants', 'financing', 'other']) {
    for (const line of formData.value['expense_lines_' + cat] || []) total += Number(line.monthly_amount) || 0
  }
  return total
})

const profit = computed(() => totalRevenue.value - totalExpenses.value)
const margin = computed(() => totalRevenue.value > 0 ? (profit.value / totalRevenue.value) * 100 : 0)

// Monthly revenue
function monthlyRevenue(m) {
  if (!formData.value?.total_revenue || !formData.value?.revenue_forecast) return 0
  const pct = Number(formData.value.revenue_forecast[m]) || 0
  return Math.round(formData.value.total_revenue * pct / 100)
}

// Cash inflow per month (שוטף+X: end of invoice month + X days)
function cashInflow(targetMonth) {
  if (!formData.value?.total_revenue) return 0
  const startYear = formData.value.start_date ? parseInt(formData.value.start_date.split('-')[0]) || 2026 : 2026
  let total = 0
  for (let m = 1; m <= 12; m++) {
    const rev = monthlyRevenue(m)
    if (!rev) continue
    for (const term of paymentTerms.value) {
      const pct = Number(term.percent) || 0
      if (!pct) continue
      const termType = term.type
      if (termType === 'מקדמה' || termType === 'מזומן') {
        // מקדמה/מזומן: no delay, same month
        if (m === targetMonth) {
          total += Math.round(rev * pct / 100)
        }
      } else {
        // שוטף+X: end of invoice month + X days
        const xDays = extractShotefDays(termType)
        const payMonth = shotefPaymentMonth(m, startYear, xDays)
        if (payMonth === targetMonth) {
          total += Math.round(rev * pct / 100)
        }
      }
    }
  }
  return total
}

// Expense categories
const categoryDefs = [
  { key: 'subcontractors', label: 'קבלני משנה', chartColor: '#60a5fa' },
  { key: 'manpower', label: 'כוח אדם', chartColor: '#a78bfa' },
  { key: 'equipment', label: 'ציוד וכלים', chartColor: '#fb923c' },
  { key: 'insurance', label: 'ביטוחים', chartColor: '#34C759' },
  { key: 'consultants', label: 'מתכננים ויועצים', chartColor: '#facc15' },
  { key: 'financing', label: 'הוצאות מימון', chartColor: '#f87171' },
  { key: 'other', label: 'אחר', chartColor: '#94a3b8' },
]

const expenseCategories = computed(() => {
  if (!formData.value) return []
  return categoryDefs.map(def => {
    let total = 0
    if (def.key === 'subcontractors') {
      for (const s of formData.value.subcontractors || []) total += Number(s.monthly_amount) || 0
    } else {
      for (const l of formData.value['expense_lines_' + def.key] || []) total += Number(l.monthly_amount) || 0
    }
    return { ...def, total }
  }).filter(c => c.total > 0)
})

const allSuppliers = computed(() => {
  if (!formData.value) return []
  const list = []
  for (const sub of formData.value.subcontractors || []) {
    list.push({ name: sub.name, amount: sub.monthly_amount, category: 'קבלני משנה', payment_terms: sub.payment_terms, start_date: sub.start_date, end_date: sub.end_date })
  }
  for (const def of categoryDefs.slice(2)) { // skip subcontractors & manpower
    for (const line of formData.value['expense_lines_' + def.key] || []) {
      list.push({ name: line.name, amount: line.monthly_amount, category: def.label, payment_terms: line.payment_terms, start_date: line.start_date, end_date: line.end_date })
    }
  }
  return list
})

// Month helpers
const hebrewMonths = { 1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל', 5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט', 9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר' }
function monthName(m) { return hebrewMonths[m] || m }

function parseMonth(dateStr) {
  if (!dateStr) return null
  const parts = dateStr.split('-')
  return parts.length >= 2 ? parseInt(parts[1]) : null
}

// Active project months (start to end)
const activeMonths = computed(() => {
  if (!formData.value) return []
  const sm = parseMonth(formData.value.start_date) || 1
  const em = parseMonth(formData.value.expected_end_date) || 12
  const result = []
  for (let m = sm; m <= em; m++) result.push(m)
  return result
})

// Monthly expense breakdown by category
const monthlyBreakdown = computed(() => {
  if (!formData.value) return []
  const result = []

  // Subcontractors
  const subLines = (formData.value.subcontractors || []).map(sub => {
    const sm = parseMonth(sub.start_date) || parseMonth(formData.value.start_date) || 1
    const em = parseMonth(sub.end_date) || parseMonth(formData.value.expected_end_date) || 12
    const amount = Number(sub.monthly_amount) || 0
    const months = {}
    let total = 0
    for (let m = sm; m <= em; m++) { months[m] = amount; total += amount }
    return { name: sub.name, months, total }
  })
  if (subLines.length) {
    const monthlyTotals = {}; let grandTotal = 0
    for (const line of subLines) { for (const [m, v] of Object.entries(line.months)) { monthlyTotals[m] = (monthlyTotals[m] || 0) + v }; grandTotal += line.total }
    result.push({ key: 'subcontractors', label: 'קבלני משנה', lines: subLines, monthlyTotals, grandTotal })
  }

  // Other categories
  for (const def of categoryDefs.slice(1)) { // skip subcontractors
    const lines = (formData.value['expense_lines_' + def.key] || []).map(line => {
      const sm = parseMonth(line.start_date) || line.start_month || parseMonth(formData.value.start_date) || 1
      const em = parseMonth(line.end_date) || line.end_month || parseMonth(formData.value.expected_end_date) || 12
      const amount = Number(line.monthly_amount) || 0
      const months = {}
      let total = 0
      for (let m = sm; m <= em; m++) { months[m] = amount; total += amount }
      return { name: line.name, months, total }
    })
    if (lines.length) {
      const monthlyTotals = {}; let grandTotal = 0
      for (const line of lines) { for (const [m, v] of Object.entries(line.months)) { monthlyTotals[m] = (monthlyTotals[m] || 0) + v }; grandTotal += line.total }
      result.push({ key: def.key, label: def.label, lines, monthlyTotals, grandTotal })
    }
  }

  return result
})

function grandMonthlyTotal(m) {
  let total = 0
  for (const cat of monthlyBreakdown.value) { total += cat.monthlyTotals[m] || 0 }
  return total
}

const grandTotal = computed(() => {
  return monthlyBreakdown.value.reduce((sum, cat) => sum + cat.grandTotal, 0)
})

// Charts
const months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

const revenueChartData = computed(() => {
  if (!formData.value?.total_revenue) return null
  return {
    labels: months,
    datasets: [
      { label: 'הכנסה צפויה', data: months.map((_, i) => monthlyRevenue(i + 1)), backgroundColor: 'rgba(163, 230, 53, 0.6)', borderRadius: 6 },
      { label: 'כניסת תשלום', data: months.map((_, i) => cashInflow(i + 1)), backgroundColor: 'rgba(251, 191, 36, 0.6)', borderRadius: 6 },
    ]
  }
})

const expenseChartData = computed(() => {
  const cats = expenseCategories.value
  if (!cats.length) return null
  return {
    labels: cats.map(c => c.label),
    datasets: [{ data: cats.map(c => c.total), backgroundColor: cats.map(c => c.chartColor), borderWidth: 0 }]
  }
})

const cashflowChartData = computed(() => {
  if (!formData.value) return null
  let cumulative = 0
  const inflows = months.map((_, i) => cashInflow(i + 1))
  const outflows = months.map(() => totalExpenses.value / 12) // simplified monthly
  const cumulativeData = months.map((_, i) => {
    cumulative += inflows[i] - outflows[i]
    return cumulative
  })
  return {
    labels: months,
    datasets: [
      { label: 'כניסות', data: inflows, backgroundColor: 'rgba(163, 230, 53, 0.6)', borderRadius: 6, order: 2 },
      { label: 'יציאות', data: outflows.map(v => -v), backgroundColor: 'rgba(251, 146, 60, 0.6)', borderRadius: 6, order: 2 },
      { label: 'מצטבר', data: cumulativeData, type: 'line', borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', fill: true, tension: 0.3, pointRadius: 3, order: 1 },
    ]
  }
})

const barOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { callback: v => v.toLocaleString('he-IL') } } } }
const doughnutOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, cutout: '65%' }
const cashflowOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { ticks: { callback: v => v.toLocaleString('he-IL') } } } }

async function load() {
  if (!props.project) return
  loading.value = true
  try {
    formData.value = await getProjectForm(props.project)
  } catch { formData.value = null }
  finally { loading.value = false }
}

onMounted(load)
watch(() => props.project, load)
</script>
