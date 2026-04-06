<template>
  <div>
    <div v-if="loading" class="space-y-8 py-4">
      <SkeletonLoader variant="kpi" :count="5" />
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SkeletonLoader variant="chart" height="220px" />
        <SkeletonLoader variant="chart" height="220px" />
      </div>
      <SkeletonLoader variant="table" :columns="6" :rows="6" />
    </div>

    <!-- No project selected -->
    <div v-else-if="!selectedProject" class="ed-section text-center py-16">
      <div class="ed-eyebrow mb-3">פרויקט</div>
      <p class="font-sans text-2xl text-ink leading-tight max-w-lg mx-auto">
        אין פרויקט נבחר.
      </p>
      <div class="ed-eyebrow mt-3 ed-tone-muted">יש לבחור פרויקט מהרשימה במסדר העליון</div>
    </div>

    <template v-else>
      <!-- Header -->
      <SectionHeader
        eyebrow="פרויקט"
        :kicker="dateLabel"
        :title="selectedProject"
      />

      <!-- Section markers for tabs -->
      <div class="flex gap-x-8 gap-y-2 flex-wrap items-center mb-8 pb-2 border-b border-rule-strong ed-fade-up">
        <SectionMarker label="דו״ח P&L" :active="viewMode === 'pnl'" @click="viewMode = 'pnl'" />
        <SectionMarker
          label="ניהול פרויקט"
          :active="viewMode === 'dashboard'"
          :badge="formDataStatus === 'incomplete' || formDataStatus === 'empty' ? '!' : null"
          @click="viewMode = 'dashboard'"
        />
        <SectionMarker label="פרטי פרויקט" :active="viewMode === 'details'" @click="viewMode = 'details'" />

        <div class="mr-auto flex gap-4">
          <button @click="showReportModal = true" class="ed-link text-sm">+ דיווח נקודתי</button>
        </div>
      </div>

      <!-- Dashboard view -->
      <div v-if="viewMode === 'dashboard'">
        <ProjectFormDashboard :project="selectedProject" @edit="showProjectForm = true" />
        <div class="mt-8">
          <MonthlyActualsEditor :project="selectedProject" @saved="loadPnl" />
        </div>
      </div>

      <!-- Project Details view -->
      <div v-else-if="viewMode === 'details'">
        <ProjectDetailsView :project="selectedProject" @edit="showProjectForm = true" />
      </div>

      <!-- P&L view -->
      <template v-else-if="pnlData">
        <!-- Project meta strip -->
        <section class="ed-section-top mb-6">
          <div class="flex flex-wrap gap-x-10 gap-y-4 ed-col-rule">
            <div>
              <div class="ed-eyebrow mb-1">מס׳ עדיפות</div>
              <div class="font-sans font-semibold text-ink"><bdi lang="en" class="ed-num">{{ pnlData.meta?.priority_id || '—' }}</bdi></div>
            </div>
            <div>
              <div class="ed-eyebrow mb-1">מנהל פרויקט</div>
              <div class="font-sans font-semibold text-ink">{{ pnlData.meta?.manager || '—' }}</div>
            </div>
            <div>
              <div class="ed-eyebrow mb-1">תחום</div>
              <div class="font-sans font-semibold text-ink">{{ pnlData.meta?.area || '—' }}</div>
            </div>
            <div>
              <div class="ed-eyebrow mb-1">ציר</div>
              <div class="font-sans font-semibold text-ink">{{ pnlData.meta?.axis || '—' }}</div>
            </div>
          </div>
        </section>

        <!-- Reports list (if any) -->
        <RuledSection v-if="reports.length" eyebrow="דיווחים נקודתיים" :title="reports.length + ' דיווחים'">
          <div class="divide-y divide-rule">
            <article v-for="r in reports" :key="r.id" class="py-3 flex items-start gap-4">
              <div class="ed-eyebrow mt-1 min-w-[60px]" :class="reportTone(r.type)">{{ typeLabel(r.type) }}</div>
              <div class="flex-1 min-w-0">
                <div class="flex items-baseline gap-3 flex-wrap">
                  <span class="font-sans font-semibold text-ink">{{ r.title }}</span>
                  <span v-if="r.month" class="ed-eyebrow">חודש {{ r.month }}</span>
                  <span v-if="r.amount" class="font-sans font-semibold ed-num" :class="r.type === 'revenue' ? 'ed-tone-positive' : 'ed-tone-negative'">
                    {{ r.type === 'revenue' ? '+' : '−' }}<bdi>{{ fmt(Math.abs(r.amount)) }}</bdi>
                  </span>
                </div>
                <p v-if="r.description" class="font-sans text-sm text-ink-muted mt-1">{{ r.description }}</p>
                <div class="ed-eyebrow mt-1" style="font-size: 0.625rem;">{{ formatDate(r.created_at) }}</div>
              </div>
            </article>
          </div>
        </RuledSection>

        <!-- KPI hero strip -->
        <section class="ed-section ed-fade-up-delay-1">
          <div class="flex flex-wrap gap-y-8 ed-col-rule">
            <div class="flex-1" style="min-width: 160px;">
              <HeroNumber label="הכנסות שנתיות" :value="pnlData.summary.total_revenue" prefix="₪" size="md" />
            </div>
            <div class="flex-1" style="min-width: 160px;">
              <HeroNumber label="הוצאות תפעול" :value="pnlData.summary.total_op_expenses" prefix="₪" size="md" />
            </div>
            <div class="flex-1" style="min-width: 160px;">
              <HeroNumber label="הוצאות שכר" :value="pnlData.summary.total_salary_expenses" prefix="₪" size="md" />
            </div>
            <div class="flex-1" style="min-width: 160px;">
              <HeroNumber
                label="רווח תפעולי"
                :value="pnlData.summary.total_operating_profit"
                prefix="₪"
                :tone="pnlData.summary.total_operating_profit >= 0 ? 'positive' : 'negative'"
                size="md"
              />
            </div>
            <div class="flex-1" style="min-width: 160px;">
              <HeroNumber
                label="מרווח תפעולי"
                :value="pnlData.summary.margin != null ? pnlData.summary.margin : 0"
                suffix="%"
                format="percent"
                :tone="pnlData.summary.margin >= 20 ? 'positive' : 'warning'"
                size="md"
              />
            </div>
          </div>
        </section>

        <!-- Charts row 1: P&L + profit bar -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 mt-2">
          <RuledSection eyebrow="הכנסות והוצאות" title="תנועה חודשית">
            <template #actions>
              <div class="flex gap-3">
                <button
                  v-for="p in periods"
                  :key="p.id"
                  @click="selectedPeriod = p.id"
                  class="ed-link text-xs"
                  :class="{ 'is-active': selectedPeriod === p.id }"
                >
                  {{ p.label }}
                </button>
              </div>
            </template>
            <PnlChart :data="filteredMonths" :projectName="selectedProject" chartType="area" />
          </RuledSection>

          <RuledSection eyebrow="רווח" title="רווח תפעולי חודשי">
            <ProfitBarChart :data="filteredMonths" />
          </RuledSection>
        </div>

        <!-- Charts row 2: cashflow + expense breakdown -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 mt-2">
          <RuledSection eyebrow="תזרים" title="תזרים הפרויקט">
            <div v-if="!cashflowData" class="font-sans text-ink-faint text-center py-10">טוען…</div>
            <ProjectCashflowChart v-else :data="cashflowData" />
          </RuledSection>

          <RuledSection eyebrow="פילוח" title="פילוח הוצאות">
            <ExpenseBreakdown :summary="pnlData.summary" />
          </RuledSection>
        </div>

        <!-- Detail table with drill-down -->
        <RuledSection eyebrow="פירוט חודשי" title="תחזית ופועל">
          <template #actions>
            <span class="ed-eyebrow">לחץ על שורה לפירוט הוצאות</span>
          </template>
          <div class="overflow-x-auto">
            <table class="ed-table" style="min-width: 700px;">
              <thead>
                <tr>
                  <th style="width: 32px;"></th>
                  <th>חודש</th>
                  <th class="num ui-table-sortable" @click="togglePnlSort('revenue')">
                    <span class="inline-flex items-center gap-1">הכנסה
                      <svg v-if="pnlSortKey === 'revenue'" class="w-3 h-3 transition-transform" :class="pnlSortDir === 'desc' ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" d="M5 15l7-7 7 7"/></svg>
                    </span>
                  </th>
                  <th class="num ui-table-sortable" @click="togglePnlSort('op_expenses')">
                    <span class="inline-flex items-center gap-1">הוצ׳ תפעול
                      <svg v-if="pnlSortKey === 'op_expenses'" class="w-3 h-3 transition-transform" :class="pnlSortDir === 'desc' ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" d="M5 15l7-7 7 7"/></svg>
                    </span>
                  </th>
                  <th class="num">רווח גולמי</th>
                  <th class="num">הוצ׳ שכר</th>
                  <th class="num ui-table-sortable" @click="togglePnlSort('operating_profit')">
                    <span class="inline-flex items-center gap-1">רווח תפעולי
                      <svg v-if="pnlSortKey === 'operating_profit'" class="w-3 h-3 transition-transform" :class="pnlSortDir === 'desc' ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" d="M5 15l7-7 7 7"/></svg>
                    </span>
                  </th>
                  <th class="num">מרווח</th>
                  <th class="hidden sm:table-cell">הערות</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="m in sortedMonths" :key="m.month">
                  <tr @click="toggleDrilldown(m.month)" class="is-clickable" style="cursor: pointer;">
                    <td>
                      <span class="inline-block transition-transform duration-200 text-ink-faint" :style="{ transform: expandedMonth === m.month ? 'rotate(90deg)' : 'rotate(0)' }">›</span>
                    </td>
                    <td>
                      <span class="font-sans font-semibold">{{ m.month }}</span>
                      <span v-if="m.is_actual" class="ed-eyebrow ed-tone-positive" style="font-size: 0.5625rem; margin-inline-start: 0.35rem;">● בפועל</span>
                    </td>
                    <td class="num"><bdi class="ed-num">{{ fmt(m.revenue) }}</bdi></td>
                    <td class="num"><bdi class="ed-num">{{ fmt(m.op_expenses) }}</bdi></td>
                    <td class="num" :class="m.gross_profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
                      <bdi class="ed-num">{{ fmt(m.gross_profit) }}</bdi>
                    </td>
                    <td class="num"><bdi class="ed-num">{{ fmt(m.salary_expenses) }}</bdi></td>
                    <td class="num" :class="m.operating_profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
                      <bdi class="ed-num">{{ fmt(m.operating_profit) }}</bdi>
                    </td>
                    <td class="num">
                      <span v-if="m.margin != null" class="ed-eyebrow" :class="m.margin_alert ? 'ed-tone-negative' : 'ed-tone-positive'">
                        {{ m.margin }}%
                      </span>
                      <span v-else class="ed-tone-faint">—</span>
                    </td>
                    <td class="hidden sm:table-cell text-ink-muted text-xs max-w-[180px] truncate">{{ m.notes }}</td>
                  </tr>
                  <!-- Drill-down row -->
                  <tr v-if="expandedMonth === m.month">
                    <td colspan="9" class="bg-paper-dark/30 py-5 px-4">
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div>
                          <div class="ed-eyebrow mb-3 ed-tone-warning">
                            הוצאות תפעול · <bdi class="ed-num">{{ fmt(m.op_expenses) }}</bdi>
                          </div>
                          <div v-if="breakdownForMonth(m.month).op_components?.length" class="space-y-2 border-t border-rule">
                            <div v-for="(comp, i) in breakdownForMonth(m.month).op_components" :key="i" class="flex items-baseline justify-between py-2 border-b border-rule">
                              <span class="font-sans text-sm text-ink">{{ comp.name }}</span>
                              <span class="font-sans text-sm font-bold text-ink ed-num"><bdi>{{ comp.amount != null ? fmt(comp.amount) : 'משתנה' }}</bdi></span>
                            </div>
                          </div>
                          <p v-else class="font-sans text-ink-faint text-sm">אין הוצאות בחודש זה</p>
                        </div>
                        <div>
                          <div class="ed-eyebrow mb-3 ed-tone-negative">
                            הוצאות שכר · <bdi class="ed-num">{{ fmt(m.salary_expenses) }}</bdi>
                          </div>
                          <div v-if="breakdownForMonth(m.month).salary_components?.length" class="space-y-2 border-t border-rule">
                            <div v-for="(comp, i) in breakdownForMonth(m.month).salary_components" :key="i" class="flex items-baseline justify-between py-2 border-b border-rule">
                              <span class="font-sans text-sm text-ink">{{ comp.name }}</span>
                              <span class="font-sans text-sm font-bold text-ink ed-num"><bdi>{{ fmt(comp.amount) }}</bdi></span>
                            </div>
                          </div>
                          <p v-else class="font-sans text-ink-faint text-sm">אין הוצאות שכר</p>
                        </div>
                        <div v-if="breakdownForMonth(m.month).milestones?.length" class="md:col-span-2">
                          <div class="ed-eyebrow mb-3">פעימות תשלום</div>
                          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div v-for="(ms, i) in breakdownForMonth(m.month).milestones" :key="i" class="py-3 border-t border-rule-strong border-b border-rule">
                              <div class="font-sans font-semibold text-ink text-sm mb-1">{{ ms.name }}</div>
                              <div class="flex justify-between text-[0.6875rem] ed-num">
                                <span class="ed-tone-positive">הכנסה <bdi>{{ fmt(ms.revenue) }}</bdi></span>
                                <span class="ed-tone-negative">הוצאה <bdi>{{ fmt(ms.expense) }}</bdi></span>
                              </div>
                              <div class="ed-eyebrow mt-1" style="font-size: 0.5625rem;">{{ ms.month }}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
              <tfoot>
                <tr>
                  <td></td>
                  <td>סה״כ</td>
                  <td class="num"><bdi class="ed-num">{{ fmt(pnlData.summary.total_revenue) }}</bdi></td>
                  <td class="num"><bdi class="ed-num">{{ fmt(pnlData.summary.total_op_expenses) }}</bdi></td>
                  <td class="num"><bdi class="ed-num">{{ fmt(pnlData.summary.total_gross_profit) }}</bdi></td>
                  <td class="num"><bdi class="ed-num">{{ fmt(pnlData.summary.total_salary_expenses) }}</bdi></td>
                  <td class="num" :class="pnlData.summary.total_operating_profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
                    <bdi class="ed-num">{{ fmt(pnlData.summary.total_operating_profit) }}</bdi>
                  </td>
                  <td class="num">
                    <span v-if="pnlData.summary.margin != null" class="ed-eyebrow ed-tone-positive">
                      {{ pnlData.summary.margin }}%
                    </span>
                  </td>
                  <td class="hidden sm:table-cell"></td>
                </tr>
              </tfoot>
            </table>
          </div>
          <template #footnote>
            <FootnoteSource label="מקור:" text="דיווחי חשבשבת + עדכוני בפועל" :updated="updatedLabel" />
          </template>
        </RuledSection>
      </template>

      <!-- No P&L data -->
      <div v-else class="ed-section text-center py-16">
        <div class="ed-eyebrow mb-3">אין נתוני P&L</div>
        <p class="font-sans text-xl text-ink max-w-md mx-auto">
          לא נמצאו נתוני P&L מקובץ Excel לפרויקט זה.
        </p>
        <button @click="viewMode = 'dashboard'" class="ed-btn ed-btn-primary mt-6">
          עבור לניהול פרויקט →
        </button>
      </div>
    </template>

    <!-- Report Modal -->
    <ReportModal :show="showReportModal" :project="selectedProject" @close="showReportModal = false" @saved="loadReports" />
    <ProjectFormModal :show="showProjectForm" :project="selectedProject" @close="onFormClose" @saved="onFormSaved" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getProjects, getProjectsDetail, getPnl, getProjectCashflow, getReports, getProjectForm, importExcelProject, formatNumber } from '../services/api'
import ReportModal from './ReportModal.vue'
import ProjectFormModal from './ProjectFormModal.vue'
import PnlChart from './PnlChart.vue'
import ProfitBarChart from './ProfitBarChart.vue'
import ProjectCashflowChart from './ProjectCashflowChart.vue'
import ExpenseBreakdown from './ExpenseBreakdown.vue'
import ProjectFormDashboard from './ProjectFormDashboard.vue'
import ProjectDetailsView from './ProjectDetailsView.vue'
import MonthlyActualsEditor from './MonthlyActualsEditor.vue'
import { SectionHeader, SectionMarker, RuledSection, HeroNumber, FootnoteSource, SkeletonLoader, currentHebrewDate } from './editorial'

const props = defineProps({ initialProject: { type: String, default: '' } })

const projects = ref([])
const selectedProject = ref(props.initialProject || '')
const pnlData = ref(null)
const cashflowData = ref(null)
const loading = ref(true)
const error = ref(null)
const fmt = formatNumber
const selectedPeriod = ref('year')
const expandedMonth = ref(null)
const pnlSortKey = ref('')
const pnlSortDir = ref('asc')

function togglePnlSort(key) {
  if (pnlSortKey.value === key) {
    if (pnlSortDir.value === 'asc') pnlSortDir.value = 'desc'
    else { pnlSortKey.value = ''; pnlSortDir.value = 'asc' }
  } else {
    pnlSortKey.value = key
    pnlSortDir.value = 'asc'
  }
}

const sortedMonths = computed(() => {
  if (!pnlData.value?.months) return []
  if (!pnlSortKey.value) return pnlData.value.months
  const key = pnlSortKey.value
  return [...pnlData.value.months].sort((a, b) => {
    const av = a[key] ?? 0, bv = b[key] ?? 0
    const cmp = av < bv ? -1 : av > bv ? 1 : 0
    return pnlSortDir.value === 'desc' ? -cmp : cmp
  })
})
const showReportModal = ref(false)
const showProjectForm = ref(false)
const reports = ref([])
const viewMode = ref('pnl')
const formDataStatus = ref(null)
const projectsDetail = ref([])
const projectSource = computed(() => {
  const detail = projectsDetail.value.find(p => p.name === selectedProject.value)
  return detail?.source || 'excel'
})
const importingExcel = ref(false)

const dateLabel = computed(() => currentHebrewDate())
const updatedLabel = computed(() => {
  const d = new Date()
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
})

async function checkFormStatus() {
  if (!selectedProject.value) { formDataStatus.value = null; return }
  try {
    const data = await getProjectForm(selectedProject.value)
    if (!data) { formDataStatus.value = 'empty'; return }
    const missing = []
    if (!data.total_revenue) missing.push('הכנסות')
    if (!data.manager) missing.push('מנהל')
    if (!data.client) missing.push('מזמין')
    if (!data.start_date) missing.push('תאריך')
    const hasExpenses = (data.subcontractors?.length > 0) ||
      ['manpower','equipment','insurance','consultants','financing','other'].some(c => data['expense_lines_' + c]?.length > 0)
    if (!hasExpenses) missing.push('הוצאות')
    formDataStatus.value = missing.length ? 'incomplete' : 'complete'
  } catch { formDataStatus.value = 'empty' }
}

const typeLabel = (type) => ({ expense: 'הוצאה', revenue: 'הכנסה', issue: 'בעיה', note: 'הערה' }[type] || 'דיווח')
const reportTone = (type) => ({
  expense: 'ed-tone-negative',
  revenue: 'ed-tone-positive',
  issue: 'ed-tone-warning',
  note: 'ed-tone-muted',
}[type] || 'ed-tone-muted')

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('he-IL') + ' ' + d.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
}

function onFormClose() { showProjectForm.value = false; checkFormStatus() }
function onFormSaved() { loadPnl(); checkFormStatus() }

async function doImportExcel() {
  if (!selectedProject.value || importingExcel.value) return
  importingExcel.value = true
  try {
    await importExcelProject(selectedProject.value)
    await loadPnl()
    await checkFormStatus()
  } catch (e) { error.value = e.message }
  finally { importingExcel.value = false }
}

async function loadReports() {
  if (!selectedProject.value) return
  try { reports.value = await getReports(selectedProject.value) } catch {}
}

const formDataForBreakdown = ref(null)

function parseMonthFromDate(dateStr) {
  if (!dateStr) return null
  const parts = dateStr.split('-')
  return parts.length >= 2 ? parseInt(parts[1]) : null
}

function breakdownForMonth(month) {
  const excelBreakdown = pnlData.value?.expense_breakdown || {}
  if (excelBreakdown.op_components?.length || excelBreakdown.salary_components?.length) {
    return excelBreakdown
  }
  const fd = formDataForBreakdown.value
  if (!fd) return {}

  const opComponents = []
  for (const sub of fd.subcontractors || []) {
    if (!sub.monthly_amount) continue
    const sm = parseMonthFromDate(sub.start_date) || parseMonthFromDate(fd.start_date) || 1
    const em = parseMonthFromDate(sub.end_date) || parseMonthFromDate(fd.expected_end_date) || 12
    if (month >= sm && month <= em) {
      opComponents.push({ name: sub.name || 'קבלן משנה', amount: sub.monthly_amount })
    }
  }
  const catLabels = { manpower: 'כוח אדם', equipment: 'ציוד', insurance: 'ביטוח', consultants: 'יועצים', financing: 'מימון', other: 'אחר' }
  for (const cat of ['manpower', 'equipment', 'insurance', 'consultants', 'financing', 'other']) {
    for (const line of fd['expense_lines_' + cat] || []) {
      if (!line.monthly_amount) continue
      const sm = parseMonthFromDate(line.start_date) || line.start_month || parseMonthFromDate(fd.start_date) || 1
      const em = parseMonthFromDate(line.end_date) || line.end_month || parseMonthFromDate(fd.expected_end_date) || 12
      if (month >= sm && month <= em) {
        opComponents.push({ name: (line.name || catLabels[cat]) + ` (${catLabels[cat]})`, amount: line.monthly_amount })
      }
    }
  }

  return { op_components: opComponents, salary_components: [] }
}

function toggleDrilldown(month) {
  expandedMonth.value = expandedMonth.value === month ? null : month
}

const periods = [
  { id: 'q1', label: 'Q1' },
  { id: 'q2', label: 'Q2' },
  { id: 'q3', label: 'Q3' },
  { id: 'q4', label: 'Q4' },
  { id: 'year', label: 'שנתי' },
]

const filteredMonths = computed(() => {
  if (!pnlData.value) return []
  const months = pnlData.value.months
  if (selectedPeriod.value === 'year') return months
  const qMap = { q1: [1,2,3], q2: [4,5,6], q3: [7,8,9], q4: [10,11,12] }
  return months.filter(m => qMap[selectedPeriod.value]?.includes(m.month))
})

async function loadPnl() {
  if (!selectedProject.value) return
  loading.value = true
  error.value = null
  try {
    const data = await getPnl(selectedProject.value)
    pnlData.value = data[selectedProject.value]
    getProjectCashflow(selectedProject.value).then(d => { cashflowData.value = d }).catch(() => {})
    getProjectForm(selectedProject.value).then(d => { formDataForBreakdown.value = d }).catch(() => { formDataForBreakdown.value = null })
    loadReports()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    projects.value = await getProjects()
    try { projectsDetail.value = await getProjectsDetail() } catch {}
    if (props.initialProject && projects.value.includes(props.initialProject)) {
      selectedProject.value = props.initialProject
    } else if (!selectedProject.value && projects.value.length) {
      selectedProject.value = projects.value[0]
    }
    await loadPnl()
    checkFormStatus()
  } catch (e) {
    error.value = e.message
    loading.value = false
  }
})

watch(() => props.initialProject, (val) => {
  if (val && projects.value.includes(val)) selectedProject.value = val
})

watch(selectedProject, () => { viewMode.value = 'pnl'; loadPnl(); checkFormStatus() })
</script>
