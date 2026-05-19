<template>
  <div>
    <div v-if="loading" class="space-y-8 py-4">
      <SkeletonLoader variant="kpi" :count="3" />
      <SkeletonLoader variant="table" :columns="6" :rows="5" />
    </div>
    <p v-if="error" class="font-sans ed-tone-negative mb-6">{{ error }}</p>

    <template v-if="data">
      <SectionHeader
        eyebrow="דו״ח הנהלה"
        :kicker="dateLabel"
        title="מבט כללי"
        subtitle="סיכום ביצועים רבעוני · נתונים מאוחדים מכל הפרויקטים והמנהלים"
      />

      <!-- Hero KPI — operating profit (the headline business outcome) -->
      <section class="ui-card mb-5 animate-fade-up">
        <HeroNumber
          label="רווח תפעולי"
          :value="data.total_operating_profit"
          prefix="₪"
          size="xl"
          :tone="data.total_operating_profit >= 0 ? 'positive' : 'negative'"
          footnote="מצטבר · מאוחד מכל הפרויקטים"
        />
      </section>

      <!-- Secondary KPIs — same content, demoted visual weight -->
      <div class="ui-stagger grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="ui-card">
          <div class="ui-label ed-tone-muted mb-2">מצב מזומנים</div>
          <div class="ui-num font-semibold text-ink" style="font-size: 1.5rem; line-height: 1.1;" :class="data.cash_position >= 0 ? '' : 'ed-tone-negative'">
            <bdi>₪{{ formatShort(data.cash_position) }}</bdi>
          </div>
          <div class="mt-2">
            <span class="ui-pill" :class="data.cash_position >= 0 ? 'ui-pill-neutral' : 'ui-pill-negative'">
              {{ data.cash_position >= 0 ? 'חיובי' : 'שלילי' }}
            </span>
          </div>
        </div>

        <div class="ui-card">
          <div class="ui-label ed-tone-muted mb-2">מרווח תפעולי</div>
          <div class="ui-num font-semibold" style="font-size: 1.5rem; line-height: 1.1;" :class="data.margin >= 20 ? 'ed-tone-positive' : data.margin >= 10 ? 'ed-tone-warning' : 'ed-tone-negative'">
            <bdi>{{ data.margin != null ? Number(data.margin).toFixed(1) : 0 }}%</bdi>
          </div>
          <div class="mt-2">
            <span class="ui-pill" :class="data.margin >= 20 ? 'ui-pill-positive' : data.margin >= 10 ? 'ui-pill-warning' : 'ui-pill-negative'">
              {{ data.margin >= 20 ? 'תקין' : data.margin >= 10 ? 'לתשומת לב' : 'חריג' }}
            </span>
          </div>
        </div>

        <div class="ui-card">
          <div class="ui-label ed-tone-muted mb-2">פרויקטים בסיכון</div>
          <div class="ui-num font-semibold" style="font-size: 1.5rem; line-height: 1.1;" :class="projectsAtRisk > 0 ? 'ed-tone-warning' : 'ed-tone-positive'">
            <bdi>{{ projectsAtRisk }}</bdi>
          </div>
          <div class="mt-2">
            <span class="ui-pill" :class="projectsAtRisk > 0 ? 'ui-pill-warning' : 'ui-pill-positive'">
              {{ projectsAtRisk > 0 ? 'מרווח < 10%' : 'הכל תקין' }}
            </span>
          </div>
        </div>

        <div class="ui-card">
          <div class="ui-label ed-tone-muted mb-2">סה״כ פרויקטים</div>
          <div class="ui-num font-semibold text-ink" style="font-size: 1.5rem; line-height: 1.1;">
            <bdi>{{ totalProjects }}</bdi>
          </div>
          <div class="mt-2">
            <span class="ui-pill ui-pill-neutral">פעילים</span>
          </div>
        </div>
      </div>

      <!-- Manager Performance -->
      <div class="ui-card mb-8">
        <div class="mb-6">
          <div class="ui-label ed-tone-muted mb-1">ביצועי מנהלים</div>
          <h2 class="font-sans font-semibold text-ink text-xl leading-tight">טבלת מנהלים</h2>
          <p class="font-sans ed-tone-muted text-sm mt-1">מרווח תפעולי ממוצע, מדורג מהגבוה לנמוך.</p>
        </div>
        <DataTable
          v-if="managerRows.length > 0"
          :columns="managerColumns"
          :rows="managerRows"
        >
          <template #cell-avgMargin="{ row }">
            <bdi class="ui-num" :class="marginTone(row.avgMargin)">{{ row.avgMargin.toFixed(1) }}%</bdi>
          </template>
          <template #cell-status="{ row }">
            <span class="ui-pill" :class="marginPillClass(row.avgMargin)">
              {{ row.avgMargin >= 20 ? 'תקין' : row.avgMargin >= 10 ? 'לתשומת לב' : 'חריג' }}
            </span>
          </template>
        </DataTable>
        <p v-else class="font-sans ed-tone-muted text-center py-8">אין נתוני מנהלים</p>
        <div class="mt-6 pt-4 border-t border-border">
          <FootnoteSource label="מקור:" text="נתוני P&L מערכת IFMLogiX" :updated="updatedLabel" />
        </div>
      </div>

      <!-- Quick actions -->
      <div class="ui-card mb-8">
        <div class="ui-label ed-tone-muted mb-3">פעולות מהירות</div>
        <div class="flex flex-wrap gap-3">
          <button class="ui-btn ui-btn-primary" @click="$emit('switch-to-operations')">
            מעבר לתצוגה תפעולית
          </button>
          <button class="ui-btn" @click="$emit('new-project')">
            פרויקט חדש
          </button>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboard, getPnl, formatNumber } from '../services/api'
import { SectionHeader, HeroNumber, DataTable, FootnoteSource, SkeletonLoader, currentHebrewDate } from './editorial'

function formatShort(v) {
  if (v == null) return '0'
  return formatNumber(Math.round(v))
}

defineEmits(['switch-to-operations', 'new-project'])

const loading = ref(true)
const error = ref('')
const data = ref(null)
const pnlData = ref(null)

const dateLabel = computed(() => currentHebrewDate())
const updatedLabel = computed(() => {
  const d = new Date()
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
})

const managerColumns = [
  { key: 'name', label: 'מנהל' },
  { key: 'projectCount', label: 'פרויקטים', align: 'end', format: 'number' },
  { key: 'avgMargin', label: 'מרווח ממוצע', align: 'end' },
  { key: 'status', label: 'סטטוס', align: 'end' },
]

const totalProjects = computed(() => {
  if (!pnlData.value) return 0
  return Object.keys(pnlData.value).length
})

const projectsAtRisk = computed(() => {
  if (!pnlData.value) return 0
  return Object.values(pnlData.value).filter(p => p.summary?.margin != null && p.summary.margin < 10).length
})

const managerRows = computed(() => {
  if (!pnlData.value) return []
  const byManager = {}
  for (const [name, project] of Object.entries(pnlData.value)) {
    const manager = project.meta?.manager || 'לא משויך'
    if (!byManager[manager]) {
      byManager[manager] = { name: manager, margins: [], projectCount: 0 }
    }
    byManager[manager].projectCount++
    if (project.summary?.margin != null) {
      byManager[manager].margins.push(project.summary.margin)
    }
  }
  return Object.values(byManager).map(m => ({
    name: m.name,
    projectCount: m.projectCount,
    avgMargin: m.margins.length > 0 ? m.margins.reduce((a, b) => a + b, 0) / m.margins.length : 0,
    status: '',
  })).sort((a, b) => b.avgMargin - a.avgMargin)
})

function marginTone(m) {
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

onMounted(async () => {
  try {
    const [dashData, pnl] = await Promise.all([getDashboard(), getPnl()])
    data.value = dashData
    pnlData.value = pnl
  } catch (e) {
    error.value = e.message || 'שגיאה בטעינת נתונים'
  } finally {
    loading.value = false
  }
})
</script>
