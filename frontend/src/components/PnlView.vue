<template>
  <div>
    <div v-if="loading" class="text-center py-20 text-gray-400">טוען נתונים...</div>

    <!-- No project selected -->
    <div v-else-if="!selectedProject" class="text-center py-20">
      <div class="text-5xl mb-4 opacity-30">📊</div>
      <div class="text-lg font-medium text-gray-500 mb-2">אין מידע כעת</div>
      <div class="text-sm text-gray-400">יש לבחור פרויקט מהרשימה.</div>
    </div>

    <template v-else>
      <!-- Project header with tabs -->
      <div class="flex items-start justify-between mb-6">
        <div>
          <div class="flex items-center gap-3 mb-1">
            <h2 class="text-2xl font-bold text-gray-800">{{ selectedProject }}</h2>
            <span v-if="pnlData?.meta?.priority_id"
              class="bg-teal-50 text-teal-600 text-xs font-mono font-semibold px-2.5 py-1 rounded-lg border border-teal-100">
              {{ pnlData.meta.priority_id }}
            </span>
          </div>
          <!-- Tab bar (iOS segmented control) -->
          <div class="flex items-center bg-gray-100 rounded-xl p-0.5 mt-3 w-fit">
            <button @click="viewMode = 'pnl'"
              :class="['px-5 py-1.5 text-sm font-medium rounded-lg transition-all',
                viewMode === 'pnl' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400']">
              דוח P&L
            </button>
            <button @click="viewMode = 'dashboard'"
              :class="['px-5 py-1.5 text-sm font-medium rounded-lg transition-all relative',
                viewMode === 'dashboard' ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400']">
              ניהול פרויקט
              <span v-if="formDataStatus === 'incomplete'"
                class="absolute -top-1 -left-1 w-4 h-4 bg-orange-400 text-white text-[9px] font-bold rounded-full flex items-center justify-center">!</span>
              <span v-else-if="formDataStatus === 'empty'"
                class="absolute -top-1 -left-1 w-4 h-4 bg-red-400 text-white text-[9px] font-bold rounded-full flex items-center justify-center">!</span>
            </button>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button @click="showProjectForm = true"
            class="px-4 py-2.5 bg-white text-gray-700 text-sm font-medium rounded-full border border-gray-200/60 hover:bg-gray-50 transition flex items-center gap-2 shadow-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            ערוך טופס
          </button>
          <button @click="showReportModal = true"
            class="px-4 py-2.5 bg-[#0D9488] text-white text-sm font-medium rounded-full hover:bg-[#0F766E] transition flex items-center gap-2 shadow-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            דיווח נקודתי
          </button>
        </div>
      </div>

      <!-- Dashboard view -->
      <ProjectFormDashboard v-if="viewMode === 'dashboard'"
        :project="selectedProject"
        @edit="showProjectForm = true" />

      <!-- P&L view -->
      <template v-else-if="pnlData">

      <!-- Reports list (if any) -->
      <div v-if="reports.length" class="mb-6">
        <div class="ios-card overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 class="font-semibold text-gray-700">דיווחים נקודתיים</h3>
            <span class="text-xs text-gray-400">{{ reports.length }} דיווחים</span>
          </div>
          <div class="divide-y divide-gray-50">
            <div v-for="r in reports" :key="r.id" class="px-6 py-3 flex items-start gap-3">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                :class="{
                  'bg-red-50 text-red-500': r.type === 'expense',
                  'bg-green-50 text-green-500': r.type === 'revenue',
                  'bg-orange-50 text-orange-500': r.type === 'issue',
                  'bg-teal-50 text-teal-500': r.type === 'note'
                }">
                <span class="text-sm">{{ typeIcon(r.type) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-700">{{ r.title }}</span>
                  <span v-if="r.month" class="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">חודש {{ r.month }}</span>
                  <span v-if="r.amount" class="text-xs font-bold"
                    :class="r.type === 'revenue' ? 'text-green-600' : 'text-red-500'">
                    {{ r.type === 'revenue' ? '+' : '-' }}{{ fmt(Math.abs(r.amount)) }}
                  </span>
                </div>
                <p v-if="r.description" class="text-xs text-gray-400 mt-0.5 truncate">{{ r.description }}</p>
                <div class="text-[10px] text-gray-300 mt-0.5">{{ formatDate(r.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Project info card row -->
      <div class="flex items-start justify-between mb-8">
        <div></div>
        <div class="bg-white rounded-2xl px-5 py-3 shadow-sm border border-gray-100 flex items-center gap-4">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-teal-50 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/>
              </svg>
            </div>
            <div>
              <div class="text-[10px] text-gray-400">מס' Priority</div>
              <div class="text-sm font-semibold font-mono text-teal-600">{{ pnlData.meta?.priority_id || '-' }}</div>
            </div>
          </div>
          <div class="w-px h-8 bg-gray-200"></div>
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-teal-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <div>
              <div class="text-[10px] text-gray-400">מנהל פרויקט</div>
              <div class="text-sm font-semibold text-gray-700">{{ pnlData.meta?.manager || '-' }}</div>
            </div>
          </div>
          <div class="w-px h-8 bg-gray-200"></div>
          <div>
            <div class="text-[10px] text-gray-400">תחום</div>
            <div class="text-sm font-medium text-gray-600">{{ pnlData.meta?.area || '-' }}</div>
          </div>
          <div class="w-px h-8 bg-gray-200"></div>
          <div>
            <div class="text-[10px] text-gray-400">ציר</div>
            <div class="text-sm font-medium text-gray-600">{{ pnlData.meta?.axis || '-' }}</div>
          </div>
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div class="ios-card p-5">
          <div class="text-xs text-gray-400 mb-2">הכנסות שנתיות</div>
          <div class="text-2xl font-bold text-gray-800">{{ fmt(pnlData.summary.total_revenue) }}</div>
        </div>
        <div class="ios-card p-5">
          <div class="text-xs text-gray-400 mb-2">הוצאות תפעול</div>
          <div class="text-2xl font-bold text-gray-800">{{ fmt(pnlData.summary.total_op_expenses) }}</div>
        </div>
        <div class="ios-card p-5">
          <div class="text-xs text-gray-400 mb-2">הוצאות שכר</div>
          <div class="text-2xl font-bold text-gray-800">{{ fmt(pnlData.summary.total_salary_expenses) }}</div>
        </div>
        <div class="ios-card p-5">
          <div class="text-xs text-gray-400 mb-2">רווח תפעולי</div>
          <div class="text-2xl font-bold" :class="pnlData.summary.total_operating_profit >= 0 ? 'text-green-600' : 'text-red-500'">
            {{ fmt(pnlData.summary.total_operating_profit) }}
          </div>
        </div>
        <div class="ios-card p-5">
          <div class="text-xs text-gray-400 mb-2">מרווח תפעולי</div>
          <div class="text-2xl font-bold"
            :class="pnlData.summary.margin != null && pnlData.summary.margin >= 20 ? 'text-teal-600' : 'text-orange-500'">
            {{ pnlData.summary.margin != null ? pnlData.summary.margin + '%' : '-' }}
          </div>
          <div class="mt-2 bg-gray-100 rounded-full h-1.5 overflow-hidden">
            <div class="h-full rounded-full transition-all duration-500"
              :class="pnlData.summary.margin >= 20 ? 'bg-teal-400' : 'bg-orange-400'"
              :style="{ width: Math.min(100, Math.max(0, pnlData.summary.margin || 0)) + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- Charts row: P&L + Cashflow side by side -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        <!-- P&L Area Chart -->
        <div class="ios-card p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-gray-700">הכנסות והוצאות</h3>
            <div class="flex bg-gray-100 rounded-xl p-1 gap-0.5">
              <button v-for="p in periods" :key="p.id"
                @click="selectedPeriod = p.id"
                :class="[
                  'px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all',
                  selectedPeriod === p.id ? 'bg-white shadow-sm text-gray-700' : 'text-gray-400 hover:text-gray-600'
                ]">
                {{ p.label }}
              </button>
            </div>
          </div>
          <PnlChart :data="filteredMonths" :projectName="selectedProject" chartType="area" />
        </div>

        <!-- Profit chart (bar) -->
        <div class="ios-card p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-gray-700">רווח תפעולי חודשי</h3>
          </div>
          <ProfitBarChart :data="filteredMonths" />
        </div>
      </div>

      <!-- Second charts row: Cashflow + Expense breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        <!-- Project cashflow -->
        <div class="ios-card p-6">
          <h3 class="font-semibold text-gray-700 mb-4">תזרים מזומנים — פרויקט</h3>
          <div v-if="!cashflowData" class="text-center py-12 text-gray-300 text-sm">טוען...</div>
          <ProjectCashflowChart v-else :data="cashflowData" />
        </div>

        <!-- Expense pie/doughnut -->
        <div class="ios-card p-6">
          <h3 class="font-semibold text-gray-700 mb-4">פילוח הוצאות</h3>
          <ExpenseBreakdown :summary="pnlData.summary" />
        </div>
      </div>

      <!-- Table with drill-down -->
      <div class="ios-card overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 class="font-semibold text-gray-700">פירוט חודשי</h3>
          <span class="text-[10px] text-gray-400">לחץ על שורה לפירוט הוצאות</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-gray-50/50">
                <th class="px-4 py-3.5 text-right font-medium text-gray-500 w-8"></th>
                <th class="px-4 py-3.5 text-right font-medium text-gray-500">חודש</th>
                <th class="px-4 py-3.5 text-right font-medium text-gray-500">הכנסה</th>
                <th class="px-4 py-3.5 text-right font-medium text-gray-500">הוצאות תפעול</th>
                <th class="px-4 py-3.5 text-right font-medium text-gray-500">רווח גולמי</th>
                <th class="px-4 py-3.5 text-right font-medium text-gray-500">הוצאות שכר</th>
                <th class="px-4 py-3.5 text-right font-medium text-gray-500">רווח תפעולי</th>
                <th class="px-4 py-3.5 text-right font-medium text-gray-500">מרווח</th>
                <th class="px-4 py-3.5 text-right font-medium text-gray-500">הערות</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="m in pnlData.months" :key="m.month">
                <!-- Main row -->
                <tr @click="toggleDrilldown(m.month)"
                  class="border-t border-gray-50 hover:bg-gray-50/50 transition-colors cursor-pointer group">
                  <td class="px-4 py-3 text-gray-400">
                    <svg class="w-4 h-4 transition-transform duration-200" :class="expandedMonth === m.month ? 'rotate-90' : ''"
                      fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
                    </svg>
                  </td>
                  <td class="px-4 py-3 font-medium text-gray-700">{{ m.month }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ fmt(m.revenue) }}</td>
                  <td class="px-4 py-3 text-gray-600 group-hover:text-teal-600 group-hover:underline">{{ fmt(m.op_expenses) }}</td>
                  <td class="px-4 py-3" :class="m.gross_profit >= 0 ? 'text-green-600' : 'text-red-500'">{{ fmt(m.gross_profit) }}</td>
                  <td class="px-4 py-3 text-gray-600 group-hover:text-teal-600 group-hover:underline">{{ fmt(m.salary_expenses) }}</td>
                  <td class="px-4 py-3 font-semibold" :class="m.operating_profit >= 0 ? 'text-green-600' : 'text-red-500'">{{ fmt(m.operating_profit) }}</td>
                  <td class="px-4 py-3">
                    <span v-if="m.margin != null"
                      class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
                      :class="m.margin_alert ? 'bg-red-50 text-red-600' : 'bg-teal-50 text-teal-700'">
                      {{ m.margin }}%
                    </span>
                    <span v-else class="text-gray-300">-</span>
                  </td>
                  <td class="px-4 py-3 text-gray-400 text-xs max-w-[180px] truncate">{{ m.notes }}</td>
                </tr>
                <!-- Drill-down row -->
                <tr v-if="expandedMonth === m.month" class="bg-teal-50/30">
                  <td colspan="9" class="px-6 py-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <!-- Op expenses breakdown -->
                      <div class="bg-white rounded-xl p-4 border border-gray-100">
                        <div class="flex items-center gap-2 mb-3">
                          <div class="w-2 h-2 rounded-full bg-amber-400"></div>
                          <span class="text-xs font-semibold text-gray-600">הוצאות תפעול — {{ fmt(m.op_expenses) }}</span>
                        </div>
                        <div v-if="breakdown.op_components?.length" class="space-y-2">
                          <div v-for="(comp, i) in breakdown.op_components" :key="i"
                            class="flex items-center justify-between">
                            <span class="text-xs text-gray-500">{{ comp.name }}</span>
                            <span class="text-xs font-medium text-gray-700">{{ comp.amount != null ? fmt(comp.amount) : 'משתנה' }}</span>
                          </div>
                        </div>
                        <div v-else class="text-xs text-gray-400">אין פירוט זמין</div>
                      </div>

                      <!-- Salary breakdown -->
                      <div class="bg-white rounded-xl p-4 border border-gray-100">
                        <div class="flex items-center gap-2 mb-3">
                          <div class="w-2 h-2 rounded-full bg-orange-400"></div>
                          <span class="text-xs font-semibold text-gray-600">הוצאות שכר — {{ fmt(m.salary_expenses) }}</span>
                        </div>
                        <div v-if="breakdown.salary_components?.length" class="space-y-2">
                          <div v-for="(comp, i) in breakdown.salary_components" :key="i"
                            class="flex items-center justify-between">
                            <span class="text-xs text-gray-500">{{ comp.name }}</span>
                            <span class="text-xs font-medium text-gray-700">{{ fmt(comp.amount) }}</span>
                          </div>
                        </div>
                        <div v-else class="text-xs text-gray-400">אין הוצאות שכר</div>
                      </div>

                      <!-- Milestones (for project-based like עמיגור) -->
                      <div v-if="breakdown.milestones?.length" class="md:col-span-2 bg-white rounded-xl p-4 border border-gray-100">
                        <div class="flex items-center gap-2 mb-3">
                          <div class="w-2 h-2 rounded-full bg-purple-400"></div>
                          <span class="text-xs font-semibold text-gray-600">פעימות תשלום</span>
                        </div>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                          <div v-for="(ms, i) in breakdown.milestones" :key="i"
                            class="bg-gray-50 rounded-lg p-3">
                            <div class="text-xs font-medium text-gray-700 mb-1">{{ ms.name }}</div>
                            <div class="flex justify-between text-[10px]">
                              <span class="text-green-600">הכנסה: {{ fmt(ms.revenue) }}</span>
                              <span class="text-red-500">הוצאה: {{ fmt(ms.expense) }}</span>
                            </div>
                            <div class="text-[10px] text-gray-400 mt-0.5">{{ ms.month }}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
            <tfoot>
              <tr class="bg-teal-50/50 font-bold border-t-2 border-teal-200">
                <td class="px-4 py-4"></td>
                <td class="px-4 py-4 text-gray-700">סה"כ</td>
                <td class="px-4 py-4">{{ fmt(pnlData.summary.total_revenue) }}</td>
                <td class="px-4 py-4">{{ fmt(pnlData.summary.total_op_expenses) }}</td>
                <td class="px-4 py-4">{{ fmt(pnlData.summary.total_gross_profit) }}</td>
                <td class="px-4 py-4">{{ fmt(pnlData.summary.total_salary_expenses) }}</td>
                <td class="px-4 py-4" :class="pnlData.summary.total_operating_profit >= 0 ? 'text-green-600' : 'text-red-500'">
                  {{ fmt(pnlData.summary.total_operating_profit) }}
                </td>
                <td class="px-4 py-4">
                  <span v-if="pnlData.summary.margin != null" class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-teal-100 text-teal-700">
                    {{ pnlData.summary.margin }}%
                  </span>
                </td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      </template>

      <!-- No P&L data, show prompt to switch to dashboard -->
      <div v-else class="text-center py-16">
        <div class="text-4xl mb-3 opacity-30">📋</div>
        <div class="text-sm text-gray-500 mb-3">אין נתוני P&L מה-Excel לפרויקט זה</div>
        <button @click="viewMode = 'dashboard'"
          class="px-5 py-2.5 bg-teal-500 text-white text-sm font-medium rounded-xl hover:bg-teal-600 transition">
          עבור לניהול פרויקט
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
import { getProjects, getPnl, getProjectCashflow, getReports, getProjectForm, formatNumber } from '../services/api'
import ReportModal from './ReportModal.vue'
import ProjectFormModal from './ProjectFormModal.vue'
import PnlChart from './PnlChart.vue'
import ProfitBarChart from './ProfitBarChart.vue'
import ProjectCashflowChart from './ProjectCashflowChart.vue'
import ExpenseBreakdown from './ExpenseBreakdown.vue'
import ProjectFormDashboard from './ProjectFormDashboard.vue'

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
const showReportModal = ref(false)
const showProjectForm = ref(false)
const reports = ref([])
const viewMode = ref('pnl') // 'pnl' or 'dashboard'
const formDataStatus = ref(null) // null = loading, 'complete', 'incomplete', 'empty'

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

const typeIcon = (type) => ({ expense: '💸', revenue: '💰', issue: '⚠️', note: '📝' }[type] || '📋')
function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('he-IL') + ' ' + d.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
}

function onFormClose() { showProjectForm.value = false; checkFormStatus() }
function onFormSaved() { loadPnl(); checkFormStatus() }

async function loadReports() {
  if (!selectedProject.value) return
  try { reports.value = await getReports(selectedProject.value) } catch {}
}

const breakdown = computed(() => pnlData.value?.expense_breakdown || {})

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
