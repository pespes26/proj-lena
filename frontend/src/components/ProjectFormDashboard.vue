<template>
  <div v-if="loading" class="space-y-6 py-4">
    <SkeletonLoader variant="kpi" :count="4" />
    <SkeletonLoader variant="chart" height="200px" />
  </div>
  <div v-else-if="!formData" class="ui-card text-center py-16 animate-fade-up">
    <div class="ui-label mb-3">אין נתונים</div>
    <p class="ui-display max-w-md mx-auto">לפרויקט זה אין עדיין נתונים.</p>
  </div>
  <div v-else>
    <!-- Project Header -->
    <header class="ui-card animate-fade-up mb-6">
      <div class="flex items-start justify-between flex-wrap gap-4">
        <div class="min-w-0">
          <div class="ui-label mb-2">ניהול פרויקט · {{ formData.area || 'FM' }}</div>
          <h2 class="ui-display leading-tight">{{ project }}</h2>
          <div class="font-sans text-ink-muted text-sm mt-3 flex items-center gap-3 flex-wrap">
            <span v-if="formData.manager" class="ui-label">{{ formData.manager }}</span>
            <span v-if="formData.client" class="ui-label">· {{ formData.client }}</span>
            <span v-if="formData.start_date" class="ui-label ui-num">· {{ formatDate(formData.start_date) }}</span>
            <span v-if="formData.priority_id" class="ui-pill ui-pill-neutral"><bdi lang="en" class="ui-num">{{ formData.priority_id }}</bdi></span>
          </div>
          <p v-if="formData.description" class="font-sans text-ink-faint text-sm mt-3 max-w-xl">{{ formData.description }}</p>
        </div>
      </div>
    </header>

    <!-- KPI strip -->
    <section class="ui-stagger grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="ui-mini-card">
        <div class="ui-label mb-2">סך הכנסות</div>
        <div class="ui-num font-semibold text-ink text-xl"><bdi>₪ {{ fmt(totalRevenue) }}</bdi></div>
      </div>
      <div class="ui-mini-card">
        <div class="ui-label mb-2">סך הוצאות</div>
        <div class="ui-num font-semibold text-xl ed-tone-warning"><bdi>₪ {{ fmt(totalExpenses) }}</bdi></div>
      </div>
      <div class="ui-mini-card">
        <div class="ui-label mb-2">רווח צפוי</div>
        <div class="ui-num font-semibold text-xl" :class="profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'"><bdi>₪ {{ fmt(profit) }}</bdi></div>
      </div>
      <div class="ui-mini-card">
        <div class="ui-label mb-2">מרווח צפוי</div>
        <div class="flex items-baseline gap-2">
          <span class="ui-num font-semibold text-xl" :class="margin >= 20 ? 'ed-tone-positive' : margin >= 0 ? 'ed-tone-warning' : 'ed-tone-negative'">
            {{ margin.toFixed(1) }}%
          </span>
          <span class="ui-pill" :class="margin >= 20 ? 'ui-pill-positive' : margin >= 0 ? 'ui-pill-warning' : 'ui-pill-negative'">
            {{ margin >= 20 ? 'חזק' : margin >= 0 ? 'לבדוק' : 'הפסד' }}
          </span>
        </div>
      </div>
    </section>

    <!-- Payment Terms + Revenue Chart -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <section class="ui-card">
        <div class="ui-label mb-2">תנאי תשלום</div>
        <h3 class="font-sans font-semibold text-ink text-lg mb-5">הכנסה</h3>
        <div v-if="paymentTerms.length" class="space-y-5">
          <div v-for="(term, i) in paymentTerms" :key="i">
            <div class="flex items-baseline justify-between mb-1.5">
              <span class="font-sans font-semibold text-ink">{{ term.type }}</span>
              <span class="ui-num font-semibold text-ink"><bdi>{{ term.percent }}%</bdi></span>
            </div>
            <div style="width: 100%; height: 2px; background: var(--surface-muted); overflow: hidden;">
              <div style="height: 100%; width: 100%; transform-origin: right center; transition: transform 180ms var(--ease-out);" :style="{ transform: `scaleX(${term.percent / 100})`, background: term.type === 'מקדמה' || term.type === 'מזומן' ? 'var(--positive)' : 'var(--warning)' }"></div>
            </div>
            <div class="ui-label mt-1.5" style="font-size: 0.625rem;">
              <bdi class="ui-num">{{ fmt(Math.round(totalRevenue * term.percent / 100)) }} ₪</bdi>
              <span v-if="term.type !== 'מקדמה' && term.type !== 'מזומן'" class="ed-tone-warning"> · תשלום בהשהייה</span>
            </div>
          </div>
        </div>
        <p v-else class="font-sans text-ink-faint text-sm text-center py-6">לא הוגדרו תנאי תשלום</p>
      </section>

      <section class="ui-card lg:col-span-2">
        <div class="ui-label mb-2">תחזית</div>
        <h3 class="font-sans font-semibold text-ink text-lg mb-5">הכנסות חודשיות</h3>
        <div class="ui-chart-container ui-chart-container--sm" role="img" aria-label="גרף עמודות: הכנסות חודשיות">
          <Bar v-if="revenueChartData" :data="revenueChartData" :options="barOptions" />
        </div>
      </section>
    </div>

    <!-- Expenses Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <section class="ui-card">
        <div class="ui-label mb-2">פילוח</div>
        <h3 class="font-sans font-semibold text-ink text-lg mb-5">קטגוריות הוצאה</h3>
        <div class="ui-chart-container" style="height: 192px;" v-if="expenseChartData" role="img" aria-label="גרף עוגה: קטגוריות הוצאה">
          <Doughnut :data="expenseChartData" :options="doughnutOptions" />
        </div>
        <p v-else class="font-sans text-ink-faint text-center py-8">אין הוצאות</p>
        <div class="space-y-2 mt-5 pt-4" style="border-top: 1px solid var(--border);">
          <div v-for="cat in expenseCategories" :key="cat.key" class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span style="width: 8px; height: 8px; display: inline-block;" :style="{ backgroundColor: cat.chartColor }"></span>
              <span class="font-sans text-sm text-ink">{{ cat.label }}</span>
            </div>
            <span class="ui-num font-semibold text-ink text-sm"><bdi>{{ fmt(cat.total) }} ₪</bdi></span>
          </div>
        </div>
      </section>

      <section class="ui-card lg:col-span-2">
        <div class="ui-label mb-2">ספקים וקבלנים</div>
        <h3 class="font-sans font-semibold text-ink text-lg mb-5">{{ allSuppliers.length }} ספקים</h3>
        <div v-if="allSuppliers.length" class="ui-stagger grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto pr-1">
          <div v-for="(sup, i) in allSuppliers" :key="i" class="ui-mini-card">
            <div class="flex items-baseline justify-between gap-3 mb-1">
              <div class="font-sans font-semibold text-ink truncate">{{ sup.name || 'ללא שם' }}</div>
              <div class="ui-num font-semibold text-ink"><bdi>{{ fmt(sup.amount) }} ₪</bdi></div>
            </div>
            <div class="ui-label" style="font-size: 0.625rem;">
              <span>{{ sup.category }}</span>
              <span v-if="sup.payment_terms"> · {{ sup.payment_terms }}</span>
              <span v-if="sup.start_date"> · {{ formatDate(sup.start_date) }}</span>
              <span v-if="sup.start_date && sup.end_date"> → </span>
              <span v-if="sup.end_date">{{ formatDate(sup.end_date) }}</span>
            </div>
          </div>
        </div>
        <p v-else class="font-sans text-ink-faint text-center py-8">לא הוגדרו ספקים</p>
      </section>
    </div>

    <!-- Monthly Expense Breakdown -->
    <section class="ui-card mb-6">
      <div class="ui-label mb-2">פירוט חודשי</div>
      <h3 class="font-sans font-semibold text-ink text-lg mb-5">הוצאות לפי קטגוריה</h3>
      <div class="overflow-x-auto">
        <table class="ui-table" style="min-width: 600px;" dir="rtl">
          <thead>
            <tr>
              <th>קטגוריה / ספק</th>
              <th v-for="m in activeMonths" :key="m" class="num" style="min-width: 70px;">{{ monthName(m) }}</th>
              <th class="num">סה״כ</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="cat in monthlyBreakdown" :key="cat.key">
              <tr style="background: var(--surface-muted);">
                <td class="font-sans font-semibold text-ink">{{ cat.label }}</td>
                <td v-for="m in activeMonths" :key="m" class="num font-sans font-semibold">
                  <bdi class="ui-num">{{ cat.monthlyTotals[m] ? fmt(cat.monthlyTotals[m]) : '—' }}</bdi>
                </td>
                <td class="num font-sans font-semibold ed-tone-positive"><bdi class="ui-num">{{ fmt(cat.grandTotal) }}</bdi></td>
              </tr>
              <tr v-for="(line, li) in cat.lines" :key="li">
                <td class="text-ink-muted" style="padding-inline-start: 2rem;">{{ line.name || 'ללא שם' }}</td>
                <td v-for="m in activeMonths" :key="m" class="num" :class="line.months[m] ? '' : 'ed-tone-faint'">
                  <bdi class="ui-num">{{ line.months[m] ? fmt(line.months[m]) : '—' }}</bdi>
                </td>
                <td class="num"><bdi class="ui-num">{{ fmt(line.total) }}</bdi></td>
              </tr>
            </template>
            <tr style="border-top: 2px solid var(--border-strong);">
              <td class="font-sans font-semibold text-ink">סה״כ הוצאות</td>
              <td v-for="m in activeMonths" :key="m" class="num font-sans font-semibold">
                <bdi class="ui-num">{{ grandMonthlyTotal(m) ? fmt(grandMonthlyTotal(m)) : '—' }}</bdi>
              </td>
              <td class="num font-sans font-semibold ed-tone-negative"><bdi class="ui-num">{{ fmt(grandTotal) }}</bdi></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Cashflow Chart -->
    <section class="ui-card mb-6">
      <div class="ui-label mb-2">תזרים צפוי</div>
      <h3 class="font-sans font-semibold text-ink text-lg mb-5">כניסות, יציאות, ומצטבר</h3>
      <div class="ui-chart-container ui-chart-container--md" role="img" aria-label="גרף עמודות: תזרים מזומנים צפוי">
        <Bar v-if="cashflowChartData" :data="cashflowChartData" :options="cashflowOptions" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend, PointElement, LineElement } from 'chart.js'
import { getProjectForm } from '../services/api'
import { SkeletonLoader } from './editorial'
import { COLORS, tooltipConfig, axisConfig, hebrewLabelCallback } from '../utils/chartDefaults'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend, PointElement, LineElement)

const props = defineProps({ project: String })
defineEmits(['edit'])

const loading = ref(true)
const formData = ref(null)

const fmt = (val) => val != null ? Number(val).toLocaleString('he-IL', { maximumFractionDigits: 0 }) : '—'
const formatDate = (d) => {
  if (!d) return ''
  const parts = d.split('-')
  return parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : d
}

function extractShotefDays(type) {
  if (!type) return 0
  if (type.includes('שוטף+90')) return 90
  if (type.includes('שוטף+60')) return 60
  if (type.includes('שוטף+45')) return 45
  if (type.includes('שוטף+30')) return 30
  if (type.includes('שוטף+0') || type === 'שוטף') return 0
  return 0
}

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

function monthlyRevenue(m) {
  if (!formData.value?.total_revenue || !formData.value?.revenue_forecast) return 0
  const pct = Number(formData.value.revenue_forecast[m]) || 0
  return Math.round(formData.value.total_revenue * pct / 100)
}

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
        if (m === targetMonth) total += Math.round(rev * pct / 100)
      } else {
        const xDays = extractShotefDays(termType)
        const payMonth = shotefPaymentMonth(m, startYear, xDays)
        if (payMonth === targetMonth) total += Math.round(rev * pct / 100)
      }
    }
  }
  return total
}

// Editorial chart palette
const categoryDefs = [
  { key: 'subcontractors', label: 'קבלני משנה', chartColor: COLORS.primary },
  { key: 'manpower', label: 'כוח אדם', chartColor: COLORS.purple },
  { key: 'equipment', label: 'ציוד וכלים', chartColor: COLORS.orange },
  { key: 'insurance', label: 'ביטוחים', chartColor: COLORS.green },
  { key: 'consultants', label: 'מתכננים ויועצים', chartColor: COLORS.amber },
  { key: 'financing', label: 'הוצאות מימון', chartColor: COLORS.red },
  { key: 'other', label: 'אחר', chartColor: COLORS.inkMuted },
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
  for (const def of categoryDefs.slice(2)) {
    for (const line of formData.value['expense_lines_' + def.key] || []) {
      list.push({ name: line.name, amount: line.monthly_amount, category: def.label, payment_terms: line.payment_terms, start_date: line.start_date, end_date: line.end_date })
    }
  }
  return list
})

const hebrewMonths = { 1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל', 5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט', 9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר' }
function monthName(m) { return hebrewMonths[m] || m }

function parseMonth(dateStr) {
  if (!dateStr) return null
  const parts = dateStr.split('-')
  return parts.length >= 2 ? parseInt(parts[1]) : null
}

const activeMonths = computed(() => {
  if (!formData.value) return []
  const sm = parseMonth(formData.value.start_date) || 1
  const em = parseMonth(formData.value.expected_end_date) || 12
  const result = []
  for (let m = sm; m <= em; m++) result.push(m)
  return result
})

const monthlyBreakdown = computed(() => {
  if (!formData.value) return []
  const result = []

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

  for (const def of categoryDefs.slice(1)) {
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

const months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

const revenueChartData = computed(() => {
  if (!formData.value?.total_revenue) return null
  const activeMos = activeMonths.value.length
    ? activeMonths.value
    : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  return {
    labels: activeMos.map(m => hebrewMonths[m]),
    datasets: [
      { label: 'הכנסה צפויה', data: activeMos.map(m => monthlyRevenue(m)), backgroundColor: COLORS.primary, borderRadius: 0 },
      { label: 'כניסת תשלום', data: activeMos.map(m => cashInflow(m)), backgroundColor: COLORS.amber, borderRadius: 0 },
    ]
  }
})

const expenseChartData = computed(() => {
  const cats = expenseCategories.value
  if (!cats.length) return null
  return {
    labels: cats.map(c => c.label),
    datasets: [{ data: cats.map(c => c.total), backgroundColor: cats.map(c => c.chartColor), borderWidth: 1, borderColor: COLORS.paperLight }]
  }
})

const cashflowChartData = computed(() => {
  if (!formData.value) return null
  const activeMos = activeMonths.value.length
    ? activeMonths.value
    : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  let cumulative = 0
  const inflows = activeMos.map(m => cashInflow(m))
  const outflows = activeMos.map(() => totalExpenses.value / 12)
  const cumulativeData = activeMos.map((_, i) => {
    cumulative += inflows[i] - outflows[i]
    return cumulative
  })
  return {
    labels: activeMos.map(m => hebrewMonths[m]),
    datasets: [
      { label: 'כניסות', data: inflows, backgroundColor: COLORS.positive || COLORS.green, borderRadius: 0, order: 2 },
      { label: 'יציאות', data: outflows.map(v => -v), backgroundColor: COLORS.amber, borderRadius: 0, order: 2 },
      { label: 'מצטבר', data: cumulativeData, type: 'line', borderColor: COLORS.primary, backgroundColor: COLORS.primaryFill, fill: true, tension: 0.25, pointRadius: 3, order: 1 },
    ]
  }
})

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: legendMini(),
    tooltip: { ...tooltipConfig, callbacks: { label: hebrewLabelCallback() } },
  },
  scales: {
    y: axisConfig.y,
    x: { ...axisConfig.x, ticks: { ...axisConfig.x.ticks, maxRotation: 0 } },
  },
}
const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: tooltipConfig },
  cutout: '62%',
}
const cashflowOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: legendMini(),
    tooltip: { ...tooltipConfig, callbacks: { label: hebrewLabelCallback() } },
  },
  scales: {
    y: axisConfig.y,
    x: { ...axisConfig.x, ticks: { ...axisConfig.x.ticks, maxRotation: 0 } },
  },
}

function legendMini() {
  return {
    position: 'bottom',
    rtl: true,
    labels: {
      font: { family: "'Assistant', system-ui, sans-serif", size: 11, weight: '500' },
      color: COLORS.inkMuted,
      padding: 12,
      usePointStyle: true,
      pointStyle: 'rectRounded',
      boxWidth: 8,
      boxHeight: 8,
    },
  }
}

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
