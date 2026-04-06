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

      <!-- KPI hero strip -->
      <section class="ed-section ed-fade-up">
        <div class="flex flex-wrap gap-y-8 ed-col-rule">
          <div class="flex-1" style="min-width: 160px;">
            <HeroNumber
              label="מצב מזומנים"
              :value="data.cash_position"
              :tone="data.cash_position >= 0 ? 'neutral' : 'negative'"
              prefix="₪"
              size="md"
            />
          </div>
          <div class="flex-1" style="min-width: 160px;">
            <HeroNumber
              label="רווח תפעולי"
              :value="data.total_operating_profit"
              :tone="data.total_operating_profit >= 0 ? 'positive' : 'negative'"
              prefix="₪"
              size="md"
            />
          </div>
          <div class="flex-1" style="min-width: 140px;">
            <HeroNumber
              label="פרויקטים בסיכון"
              :value="projectsAtRisk"
              :tone="projectsAtRisk > 0 ? 'accent' : 'positive'"
              size="md"
              :footnote="projectsAtRisk > 0 ? 'מרווח מתחת ל־10%' : 'הכל תקין'"
            />
          </div>
          <div class="flex-1" style="min-width: 140px;">
            <HeroNumber
              label='סה״כ פרויקטים'
              :value="totalProjects"
              size="md"
            />
          </div>
          <div class="flex-1" style="min-width: 140px;">
            <HeroNumber
              label="מרווח תפעולי"
              :value="data.margin != null ? data.margin : 0"
              :tone="data.margin >= 20 ? 'positive' : 'negative'"
              suffix="%"
              format="percent"
              size="md"
            />
          </div>
        </div>
      </section>

      <!-- Manager Performance -->
      <RuledSection
        eyebrow="ביצועי מנהלים"
        title="טבלת מנהלים"
        caption="מרווח תפעולי ממוצע, מדורג מהגבוה לנמוך."
      >
        <DataTable
          v-if="managerRows.length > 0"
          :columns="managerColumns"
          :rows="managerRows"
        >
          <template #cell-avgMargin="{ row }">
            <bdi class="ed-num" :class="marginTone(row.avgMargin)">{{ row.avgMargin.toFixed(1) }}%</bdi>
          </template>
          <template #cell-status="{ row }">
            <span class="ed-eyebrow" :class="marginTone(row.avgMargin)">
              {{ row.avgMargin >= 20 ? 'תקין' : row.avgMargin >= 10 ? 'לתשומת לב' : 'חריג' }}
            </span>
          </template>
        </DataTable>
        <p v-else class="font-sans text-ink-muted text-center py-8">אין נתוני מנהלים</p>
        <template #footnote>
          <FootnoteSource label="מקור:" text="נתוני P&L מערכת IFMLogiX" :updated="updatedLabel" />
        </template>
      </RuledSection>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboard, getPnl } from '../services/api'
import { SectionHeader, RuledSection, HeroNumber, DataTable, FootnoteSource, SkeletonLoader, currentHebrewDate } from './editorial'

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
