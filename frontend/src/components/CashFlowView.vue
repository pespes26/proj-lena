<template>
  <div>
    <SectionHeader
      eyebrow="תזרים"
      :kicker="dateLabel"
      title="תזרים מזומנים"
      subtitle="סקירת תזרים מאוחדת של כלל פרויקטי הקבוצה · כניסות, יציאות, ויתרה מצטברת"
    />

    <p v-if="error" class="font-sans ed-tone-negative mb-6">{{ error }}</p>
    <div v-if="loading" class="space-y-8 py-4">
      <SkeletonLoader variant="kpi" :count="4" />
      <SkeletonLoader variant="chart" height="260px" />
      <SkeletonLoader variant="cards" :count="6" />
    </div>

    <template v-if="cfData">
      <!-- Hero KPI — cumulative balance (the "are we solvent?" number) -->
      <section class="ui-card mb-5 animate-fade-up">
        <HeroNumber
          label="יתרה מצטברת"
          :value="lastCumulative"
          prefix="₪"
          size="xl"
          :tone="lastCumulative >= 0 ? 'positive' : 'negative'"
          footnote="סוף תקופה · מצטבר חודשי"
        />
      </section>

      <!-- Secondary KPIs — revenue / expenses / net -->
      <section class="ui-stagger grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div class="ui-card">
          <div class="ui-label ed-tone-muted mb-2">סך הכנסות</div>
          <div class="ui-num font-semibold text-ink" style="font-size: 1.5rem; line-height: 1.1;">
            <bdi>₪{{ fmt(totalRevenue) }}</bdi>
          </div>
        </div>
        <div class="ui-card">
          <div class="ui-label ed-tone-muted mb-2">סך הוצאות</div>
          <div class="ui-num font-semibold text-ink" style="font-size: 1.5rem; line-height: 1.1;">
            <bdi>₪{{ fmt(totalExpenses) }}</bdi>
          </div>
        </div>
        <div class="ui-card">
          <div class="ui-label ed-tone-muted mb-2">נטו תקופתי</div>
          <div class="ui-num font-semibold" style="font-size: 1.5rem; line-height: 1.1;" :class="totalNet >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
            <bdi>₪{{ fmt(totalNet) }}</bdi>
          </div>
        </div>
      </section>

      <!-- Main chart -->
      <RuledSection
        eyebrow="תזרים"
        title="התנהגות תזרים לאורך הזמן"
      >
        <template #actions>
          <div class="flex gap-4">
            <button
              v-for="v in views"
              :key="v.id"
              @click="activeView = v.id"
              class="ed-link text-sm"
              :class="{ 'is-active': activeView === v.id }"
            >
              {{ v.label }}
            </button>
          </div>
        </template>
        <div class="ui-chart-container ui-chart-container--md">
          <CashFlowChart v-if="activeView === 'cumulative'" :data="cfData" />
          <RevenueExpenseChart v-else-if="activeView === 'revexp'" :data="cfData" />
          <MonthlyNetChart v-else-if="activeView === 'monthly'" :data="cfData" />
        </div>
        <template #footnote>
          <FootnoteSource label="מקור:" text="הנהלת חשבונות FM" :updated="updatedLabel" />
        </template>
      </RuledSection>

      <!-- Per-project comparison (full-width chart) -->
      <RuledSection eyebrow="השוואה חודשית" title="נטו לפי פרויקט">
        <div class="ui-chart-container ui-chart-container--lg">
          <ProjectNetChart :data="cfData" />
        </div>
      </RuledSection>

      <!-- Per-project breakdown (3-col card grid) -->
      <RuledSection eyebrow="סיכום" title="סה״כ לפי פרויקט">
        <div class="ui-stagger grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[520px] overflow-y-auto">
          <div
            v-for="(months, pname) in cfData.projects"
            :key="pname"
            class="ui-mini-card"
          >
            <div class="flex items-baseline justify-between gap-3 mb-3">
              <span class="font-sans font-semibold text-sm tracking-tight truncate" style="color: var(--ink);">{{ pname }}</span>
              <span
                class="font-sans font-semibold text-base ui-num flex-shrink-0"
                :class="projectTotal(months) >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'"
              >
                <bdi>{{ fmt(projectTotal(months)) }}</bdi>
              </span>
            </div>
            <div class="flex h-1.5 overflow-hidden rounded-full" style="background: var(--surface-muted);">
              <div style="background: var(--positive); transition: width 180ms cubic-bezier(0.4, 0, 0.2, 1);" :style="{ width: projectRevenuePercent(months) + '%' }"></div>
              <div style="background: var(--warning); transition: width 180ms cubic-bezier(0.4, 0, 0.2, 1);" :style="{ width: projectExpensePercent(months) + '%' }"></div>
            </div>
            <div class="flex justify-between mt-2 text-[11px] font-medium" style="color: var(--ink-muted);">
              <span>הכנסה <bdi class="ui-num font-semibold">{{ fmt(projectRevSum(months)) }}</bdi></span>
              <span>הוצאה <bdi class="ui-num font-semibold">{{ fmt(projectExpSum(months)) }}</bdi></span>
            </div>
          </div>
        </div>
      </RuledSection>

      <!-- Tables -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-2">
        <RuledSection eyebrow="חודשי ומצטבר" title="פירוט חודשי">
          <div class="ui-card" style="padding: 0;">
            <div class="max-h-[420px] overflow-y-auto">
              <DataTable
                :columns="monthlyTableCols"
                :rows="monthlyTableRows"
                :sticky-header="true"
              >
                <template #cell-net="{ row }">
                  <bdi class="ui-num" :class="row.net >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">{{ fmt(row.net) }}</bdi>
                </template>
                <template #cell-cumulative="{ row }">
                  <bdi class="ui-num" :class="row.cumulative >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">{{ fmt(row.cumulative) }}</bdi>
                </template>
              </DataTable>
            </div>
          </div>
        </RuledSection>

        <RuledSection eyebrow="מטריצת פרויקטים" title="נטו לפי פרויקט">
          <div class="ui-card" style="padding: 0;">
            <div class="max-h-[420px] overflow-auto">
              <DataTable
                :columns="matrixTableCols"
                :rows="matrixTableRows"
                :sticky-header="true"
              />
            </div>
          </div>
        </RuledSection>
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
import { SectionHeader, RuledSection, HeroNumber, DataTable, FootnoteSource, SkeletonLoader, currentHebrewDate } from './editorial'

const cfData = ref(null)
const loading = ref(true)
const error = ref(null)
const fmt = formatNumber
const activeView = ref('cumulative')

const dateLabel = computed(() => currentHebrewDate())
const updatedLabel = computed(() => {
  const d = new Date()
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
})

const views = [
  { id: 'cumulative', label: 'מצטבר' },
  { id: 'revexp', label: 'הכנסות / הוצאות' },
  { id: 'monthly', label: 'נטו חודשי' },
]

const totalRevenue = computed(() => cfData.value?.totals.reduce((a, t) => a + t.revenue, 0) || 0)
const totalExpenses = computed(() => cfData.value?.totals.reduce((a, t) => a + t.expenses, 0) || 0)
const totalNet = computed(() => totalRevenue.value - totalExpenses.value)
const lastCumulative = computed(() => {
  const c = cfData.value?.cumulative
  return c?.length ? c[c.length - 1].value : 0
})

// Monthly detail table
const monthlyTableCols = [
  { key: 'month', label: 'חודש' },
  { key: 'revenue', label: 'הכנסה', align: 'end', format: 'number' },
  { key: 'expenses', label: 'הוצאה', align: 'end', format: 'number' },
  { key: 'net', label: 'נטו', align: 'end' },
  { key: 'cumulative', label: 'מצטבר', align: 'end' },
]
const monthlyTableRows = computed(() => {
  if (!cfData.value) return []
  return cfData.value.monthly_net.map((m, i) => ({
    month: m.month,
    revenue: cfData.value.totals[i]?.revenue || 0,
    expenses: cfData.value.totals[i]?.expenses || 0,
    net: m.value,
    cumulative: cfData.value.cumulative[i]?.value || 0,
  }))
})

// Project matrix table (dynamic columns)
const matrixTableCols = computed(() => {
  if (!cfData.value) return []
  return [
    { key: 'month', label: 'חודש' },
    ...Object.keys(cfData.value.projects).map(pname => ({
      key: pname, label: pname, align: 'end', format: 'number',
    })),
  ]
})
const matrixTableRows = computed(() => {
  if (!cfData.value) return []
  const pnames = Object.keys(cfData.value.projects)
  return cfData.value.month_labels.map((label, i) => {
    const row = { month: label }
    for (const pname of pnames) row[pname] = cfData.value.projects[pname][i]?.profit || 0
    return row
  })
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
