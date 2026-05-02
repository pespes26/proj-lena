<template>
  <div>
    <SectionHeader
      eyebrow="דשבורד"
      :kicker="dateLabel"
      title="מבט כללי"
      subtitle="סקירה מאוחדת של כל פרויקטי הקבוצה · הכנסות, הוצאות ורווח תפעולי"
    />

    <p v-if="error" class="font-sans ed-tone-negative mb-6">{{ error }}</p>
    <div v-if="loading" class="space-y-8 py-4">
      <SkeletonLoader variant="kpi" :count="4" />
      <SkeletonLoader variant="chart" height="240px" />
      <SkeletonLoader variant="table" :columns="5" :rows="6" />
    </div>

    <template v-if="data">
      <!-- Hero KPI — massive total revenue with secondary ruled strip -->
      <section class="ui-card animate-fade-up mb-8">
        <HeroNumber
          label="הכנסה שנתית כוללת"
          :value="data.total_revenue"
          prefix="₪"
          size="xl"
          footnote="אלפי ש״ח · שנתי · מאוחד מכל הפרויקטים"
        />

        <div class="mt-8 flex flex-wrap gap-y-8 ed-col-rule">
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber label="הוצאות" :value="data.total_expenses" prefix="₪" size="md" />
          </div>
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber
              label="רווח תפעולי"
              :value="data.total_operating_profit"
              prefix="₪"
              :tone="data.total_operating_profit >= 0 ? 'positive' : 'negative'"
              :delta="data.margin != null ? Number(data.margin) : null"
              deltaSuffix="%"
              size="md"
            />
          </div>
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber
              label="מצב מזומנים"
              :value="data.cash_position"
              prefix="₪"
              :tone="data.cash_position >= 0 ? 'neutral' : 'negative'"
              size="md"
            />
          </div>
        </div>
      </section>

      <!-- Profit by projects -->
      <RuledSection
        eyebrow="השוואה"
        title="רווח לפי פרויקטים"
        caption="לחץ על המצבים השונים לשינוי אופן הצגת הנתונים."
      >
        <template #actions>
          <div class="flex gap-4">
            <button
              v-for="mode in chartModes"
              :key="mode.id"
              @click="chartMode = mode.id"
              class="ed-link text-sm"
              :class="{ 'is-active': chartMode === mode.id }"
            >
              {{ mode.label }}
            </button>
          </div>
        </template>
        <div class="ui-chart-container ui-chart-container--lg">
          <ProjectCompareChart :summaries="data.project_summaries" :mode="chartMode" />
        </div>
        <template #footnote>
          <FootnoteSource label="מקור:" text="הנהלת חשבונות FM" :updated="updatedLabel" />
        </template>
      </RuledSection>

      <!-- Axis split -->
      <RuledSection
        eyebrow="ציר"
        title="חלוקת רווח תפעולי לפי ציר"
        caption='סך הרווח מחולק בין שלושת הצירים: לוגי, מנרב, פיתוח עסקי.'
      >
        <div class="grid grid-cols-1 lg:grid-cols-5 gap-10 items-center">
          <div class="lg:col-span-2 flex justify-center">
            <div class="ui-chart-container ui-chart-container--md w-full max-w-xs">
              <Doughnut :data="axisPieData" :options="doughnutOptions" />
            </div>
          </div>
          <div class="lg:col-span-3 flex flex-col gap-5">
            <div v-for="axis in axes" :key="axis" class="flex items-baseline justify-between gap-4 pb-3 border-b border-border">
              <div>
                <div class="font-sans font-semibold text-ink text-[15px] leading-tight">{{ axis }}</div>
                <div class="ui-label ed-tone-muted mt-0.5">{{ axisProjects(axis).length }} פרויקטים</div>
              </div>
              <div class="font-sans font-medium ui-num tracking-tight" :class="axisTotal(axis) >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'" style="font-size: clamp(1.375rem, 2.6vw, 1.875rem); line-height: 1;">
                <bdi>{{ fmt(axisTotal(axis)) }}</bdi>
              </div>
            </div>
          </div>
        </div>
      </RuledSection>

      <!-- Per-axis detail (3 columns) -->
      <div class="ui-stagger grid grid-cols-1 md:grid-cols-3 gap-8 mt-2 mb-8">
        <div v-for="axis in axes" :key="axis" class="ui-card flex flex-col gap-3">
          <div class="border-b border-border-strong pb-4">
            <div class="flex items-baseline justify-between mb-1">
              <div class="font-sans font-semibold text-ink text-[15px]">{{ axis }}</div>
              <div class="ui-label ed-tone-faint">{{ axisProjects(axis).length }} פרויקטים</div>
            </div>
            <div class="font-sans font-medium ui-num tracking-tight" :class="axisTotal(axis) >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'" style="font-size: clamp(1.375rem, 2.4vw, 1.75rem); line-height: 1.05;">
              <bdi>{{ fmt(axisTotal(axis)) }}</bdi>
            </div>
          </div>
          <div v-if="axisProjects(axis).length === 0" class="font-sans ed-tone-faint text-sm py-4">אין פרויקטים בציר זה</div>
          <div
            v-for="p in axisProjects(axis)"
            :key="p.name"
            class="ui-mini-card"
          >
            <div class="flex items-baseline justify-between gap-2 mb-1.5">
              <span class="font-sans font-semibold text-ink text-sm truncate">{{ p.name }}</span>
              <span
                class="font-sans font-medium ui-num tracking-tight text-[15px] flex-shrink-0"
                :class="p.profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'"
              >
                <bdi>{{ fmt(p.profit) }}</bdi>
              </span>
            </div>
            <div class="flex items-center gap-2 text-[11px] font-sans font-medium ed-tone-faint">
              <span>הכנסה <bdi class="ui-num ed-tone-muted">{{ fmt(p.revenue) }}</bdi></span>
              <div class="flex-1 h-[2px] overflow-hidden rounded-full" style="background: var(--surface-muted);">
                <div class="h-full rounded-full" :style="{ width: revenueBarPct(p) + '%', background: 'var(--positive)' }"></div>
              </div>
              <span>הוצאה <bdi class="ui-num ed-tone-muted">{{ fmt(p.expenses) }}</bdi></span>
            </div>
            <div class="mt-2">
              <span class="ui-pill" :class="marginPillClass(p.margin)">
                מרווח {{ p.margin != null ? p.margin + '%' : '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Revenue & Expenses -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 mt-2">
        <RuledSection
          eyebrow="תחזית הכנסות"
          title="צפי חודשי"
          caption="סך הכנסות צפויות מכל הפרויקטים לפי חודש."
        >
          <div class="ui-chart-container ui-chart-container--md">
            <Bar :data="monthlyRevenueChartData" :options="barChartOptions" />
          </div>
        </RuledSection>
        <RuledSection
          eyebrow="תחזית הוצאות"
          title="צפי חודשי"
          caption="סך הוצאות צפויות מכל הפרויקטים לפי חודש."
        >
          <div class="ui-chart-container ui-chart-container--md">
            <Bar :data="monthlyExpenseChartData" :options="barChartOptions" />
          </div>
        </RuledSection>
      </div>

      <!-- Project table -->
      <RuledSection eyebrow="פירוט" title="טבלת פרויקטים">
        <DataTable
          :columns="projectTableCols"
          :rows="projectTableRows"
          :searchable="true"
          :sticky-header="true"
          :page-size="15"
          default-sort="profit"
          default-sort-dir="desc"
        >
          <template #cell-name="{ row }">
            <div class="font-sans font-semibold text-ink">{{ row.name }}</div>
            <div class="ui-label ed-tone-faint mt-0.5" style="font-size: 0.625rem;"><bdi lang="en">{{ row.priority_id }}</bdi></div>
          </template>
          <template #cell-profit="{ row }">
            <bdi class="ui-num" :class="row.profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">{{ fmt(row.profit) }}</bdi>
          </template>
          <template #cell-margin="{ row }">
            <span class="ui-pill" :class="marginPillClass(row.margin)">
              <bdi>{{ row.margin != null ? row.margin + '%' : '—' }}</bdi>
            </span>
          </template>
        </DataTable>
      </RuledSection>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboard, getPnl, formatNumber } from '../services/api'
import { Doughnut, Bar } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
import ProjectCompareChart from './ProjectCompareChart.vue'
import { SectionHeader, RuledSection, HeroNumber, DataTable, FootnoteSource, SkeletonLoader, currentHebrewDate } from './editorial'
import { COLORS, tooltipConfig, axisConfig } from '../utils/chartDefaults'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

const data = ref(null)
const pnlData = ref(null)
const loading = ref(true)
const error = ref(null)
const fmt = formatNumber
const chartMode = ref('grouped')

const dateLabel = computed(() => currentHebrewDate())
const updatedLabel = computed(() => {
  const d = new Date()
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
})

const axes = ['לוגי', 'מנרב', 'פיתוח עסקי']
const axisColors = { 'לוגי': COLORS.primary, 'מנרב': COLORS.amber, 'פיתוח עסקי': COLORS.orange }

const chartModes = [
  { id: 'grouped', label: 'מקובץ' },
  { id: 'stacked', label: 'מוערם' },
  { id: 'profit', label: 'רווח בלבד' },
]

function axisProjects(axis) {
  if (!data.value) return []
  return Object.entries(data.value.project_summaries)
    .filter(([, s]) => s.meta?.axis === axis)
    .map(([name, s]) => ({
      name,
      profit: s.total_operating_profit,
      revenue: s.total_revenue,
      expenses: s.total_op_expenses + s.total_salary_expenses,
      margin: s.margin,
    }))
    .sort((a, b) => b.profit - a.profit)
}

function axisTotal(axis) {
  return axisProjects(axis).reduce((sum, p) => sum + p.profit, 0)
}

function revenueBarPct(p) {
  const total = p.revenue + p.expenses
  return total > 0 ? Math.round(p.revenue / total * 100) : 50
}

const projectTableCols = [
  { key: 'name', label: 'פרויקט', sortable: true },
  { key: 'axis', label: 'ציר', hideMobile: true, sortable: true },
  { key: 'revenue', label: 'הכנסות', align: 'end', format: 'number', sortable: true },
  { key: 'expenses', label: 'הוצאות', align: 'end', format: 'number', sortable: true },
  { key: 'profit', label: 'רווח', align: 'end', sortable: true },
  { key: 'margin', label: 'מרווח', align: 'end', sortable: true },
]

const projectTableRows = computed(() => {
  if (!data.value?.project_summaries) return []
  return Object.entries(data.value.project_summaries).map(([name, s]) => ({
    name,
    priority_id: s.meta?.priority_id || '—',
    axis: s.meta?.axis || '—',
    revenue: s.total_revenue,
    expenses: s.total_op_expenses + s.total_salary_expenses,
    profit: s.total_operating_profit,
    margin: s.margin,
  }))
})

function marginTone(m) {
  if (m == null) return 'ed-tone-muted'
  if (m >= 20) return 'ed-tone-positive'
  if (m >= 10) return 'ed-tone-warning'
  return 'ed-tone-negative'
}

function marginPillClass(m) {
  if (m == null) return 'ui-pill-neutral'
  if (m >= 20) return 'ui-pill-positive'
  if (m >= 10) return 'ui-pill-warning'
  return 'ui-pill-negative'
}

// Axis pie
const axisPieData = computed(() => {
  const labels = []
  const values = []
  const colors = []
  for (const axis of axes) {
    const projects = axisProjects(axis)
    if (projects.length === 0) continue
    const total = projects.reduce((sum, p) => sum + p.profit, 0)
    if (total !== 0) {
      labels.push(axis + (total < 0 ? ' (הפסד)' : ''))
      values.push(Math.abs(Math.round(total)))
      colors.push(total >= 0 ? axisColors[axis] : COLORS.negative || COLORS.red)
    }
  }
  return {
    labels,
    datasets: [{
      data: values,
      backgroundColor: colors,
      borderWidth: 2,
      borderColor: '#ffffff',
      hoverOffset: 6,
    }]
  }
})

const doughnutOptions = {
  responsive: true,
  cutout: '62%',
  plugins: {
    legend: {
      position: 'bottom',
      rtl: true,
      labels: { font: { family: "'Assistant', system-ui, sans-serif", size: 12 }, padding: 16, usePointStyle: true, pointStyle: 'rectRounded', color: COLORS.inkMuted },
    },
    tooltip: {
      ...tooltipConfig,
      callbacks: { label: (ctx) => ` ${ctx.label}: ${Number(ctx.raw).toLocaleString('he-IL')}` },
    },
  },
}

// Monthly charts
const monthLabels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

const monthlyRevenueChartData = computed(() => {
  if (!pnlData.value) return { labels: monthLabels, datasets: [] }
  const monthly = new Array(12).fill(0)
  for (const projectPnl of Object.values(pnlData.value)) {
    for (const m of projectPnl.months || []) {
      if (m.month >= 1 && m.month <= 12) monthly[m.month - 1] += m.revenue
    }
  }
  return {
    labels: monthLabels,
    datasets: [{
      label: 'הכנסות',
      data: monthly.map(v => Math.round(v)),
      backgroundColor: COLORS.primary,
      borderRadius: 0,
    }]
  }
})

const monthlyExpenseChartData = computed(() => {
  if (!pnlData.value) return { labels: monthLabels, datasets: [] }
  const monthly = new Array(12).fill(0)
  for (const projectPnl of Object.values(pnlData.value)) {
    for (const m of projectPnl.months || []) {
      if (m.month >= 1 && m.month <= 12) monthly[m.month - 1] += m.op_expenses + m.salary_expenses
    }
  }
  return {
    labels: monthLabels,
    datasets: [{
      label: 'הוצאות',
      data: monthly.map(v => Math.round(v)),
      backgroundColor: COLORS.amber,
      borderRadius: 0,
    }]
  }
})

const barChartOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    tooltip: tooltipConfig,
  },
  scales: {
    y: axisConfig.y,
    x: axisConfig.x,
  }
}

onMounted(async () => {
  try {
    const [dashData, pnl] = await Promise.all([getDashboard(), getPnl()])
    data.value = dashData
    pnlData.value = pnl
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
