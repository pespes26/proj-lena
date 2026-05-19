<template>
  <div>
    <SectionHeader
      eyebrow="התראות"
      :kicker="dateLabel"
      title="התראות פיננסיות"
      subtitle="מעקב אחר חריגות מרווח, הפסדים תפעוליים, וחודשים ללא הכנסה."
    >
      <template #actions>
        <button
          v-if="!loading && alerts.length > 0"
          @click="clearAlerts"
          class="ui-btn ed-tone-muted"
          type="button"
        >
          איפוס התראות
        </button>
      </template>
    </SectionHeader>

    <div v-if="loading" class="font-sans py-20 text-center" style="color: var(--ink-muted);">טוען נתונים…</div>

    <template v-if="!loading">
      <!-- Empty state -->
      <div v-if="alerts.length === 0" class="ui-card text-center py-16">
        <div class="mx-auto mb-4 flex items-center justify-center" style="width: 56px; height: 56px; border-radius: 9999px; background: var(--positive-soft); color: var(--positive);">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
        </div>
        <div class="ui-display" style="color: var(--ink);">כל הפרויקטים פועלים בטווח התקין.</div>
        <div class="ed-tone-faint mt-3 font-sans text-sm">אין התראות פתוחות כרגע</div>
      </div>

      <div v-else class="space-y-6">
        <!-- Summary strip -->
        <div class="ui-stagger grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="ui-card">
            <div class="ed-eyebrow mb-2">סה״כ התראות</div>
            <div class="ui-display ui-num" style="color: var(--ink);">{{ alerts.length }}</div>
          </div>
          <div class="ui-card">
            <div class="ed-eyebrow mb-2 ed-tone-negative">חמור</div>
            <div class="ui-display ui-num ed-tone-negative">{{ highCount }}</div>
          </div>
          <div class="ui-card">
            <div class="ed-eyebrow mb-2 ed-tone-warning">בינוני</div>
            <div class="ui-display ui-num ed-tone-warning">{{ mediumCount }}</div>
          </div>
        </div>

        <!-- High-severity -->
        <template v-if="highAlerts.length > 0">
          <h2 class="ed-eyebrow mt-8 mb-3">חריגות חמורות</h2>
          <div class="ui-stagger space-y-3">
            <article
              v-for="(alert, i) in highAlerts"
              :key="'high-' + i"
              class="ui-card"
              :style="{ background: 'var(--negative-soft)', borderColor: 'var(--negative)' }"
            >
              <div class="flex items-start gap-4">
                <div class="flex-shrink-0 ed-tone-negative mt-0.5" aria-hidden="true">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-baseline gap-3 mb-1 flex-wrap">
                    <span class="ui-pill ui-pill-negative">חמור</span>
                    <h3 class="font-sans font-semibold text-lg leading-tight" style="color: var(--ink);">{{ alert.project }}</h3>
                  </div>
                  <p class="font-sans ed-tone-muted text-[0.9375rem] leading-relaxed mt-1">{{ alert.message }}</p>
                  <p v-if="alert.detail" class="ui-footnote mt-2">{{ alert.detail }}</p>
                </div>
              </div>
            </article>
          </div>
        </template>

        <!-- Medium-severity -->
        <template v-if="mediumAlerts.length > 0">
          <h2 class="ed-eyebrow mt-8 mb-3">התראות לתשומת לב</h2>
          <div class="ui-stagger space-y-3">
            <article
              v-for="(alert, i) in mediumAlerts"
              :key="'med-' + i"
              class="ui-mini-card"
              :style="{ background: 'var(--warning-soft)', borderColor: 'var(--warning)' }"
            >
              <div class="flex items-start gap-4">
                <div class="flex-shrink-0 ed-tone-warning mt-0.5" aria-hidden="true">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-baseline gap-3 mb-1 flex-wrap">
                    <span class="ui-pill ui-pill-warning">בינוני</span>
                    <h3 class="font-sans font-semibold text-base leading-tight" style="color: var(--ink);">{{ alert.project }}</h3>
                  </div>
                  <p class="font-sans ed-tone-muted text-[0.9375rem] leading-relaxed mt-1">{{ alert.message }}</p>
                  <p v-if="alert.detail" class="ui-footnote mt-2">{{ alert.detail }}</p>
                </div>
              </div>
            </article>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getPnl } from '../services/api'
import { SectionHeader, currentHebrewDate } from './editorial'

const emit = defineEmits(['alertsCleared'])

const alerts = ref([])
const loading = ref(true)

const dateLabel = computed(() => currentHebrewDate())
const highAlerts = computed(() => alerts.value.filter(a => a.severity === 'high'))
const mediumAlerts = computed(() => alerts.value.filter(a => a.severity !== 'high'))
const highCount = computed(() => highAlerts.value.length)
const mediumCount = computed(() => mediumAlerts.value.length)

function clearAlerts() {
  alerts.value = []
  emit('alertsCleared')
}

onMounted(async () => {
  try {
    const data = await getPnl()
    for (const [name, project] of Object.entries(data)) {
      if (project.summary.margin != null && project.summary.margin < 20) {
        alerts.value.push({
          project: name,
          severity: project.summary.margin < 10 ? 'high' : 'medium',
          message: `מרווח תפעולי שנתי נמוך: ${project.summary.margin}%`,
          detail: `הסף הנדרש: 20%. הפרש: ${(20 - project.summary.margin).toFixed(1)}%`,
        })
      }

      const negativeProfitMonths = project.months.filter(m => m.operating_profit < 0 && m.revenue > 0)
      if (negativeProfitMonths.length > 0) {
        alerts.value.push({
          project: name,
          severity: 'medium',
          message: `${negativeProfitMonths.length} חודשים עם הפסד תפעולי למרות הכנסות`,
          detail: `חודשים: ${negativeProfitMonths.map(m => m.month).join(', ')}`,
        })
      }

      const startMonth = project.meta?.start_month || 1
      const endMonth = project.meta?.end_month || 12
      const projectMonths = project.months.filter(m => m.month >= startMonth && m.month <= endMonth)
      const zeroRevenueMonths = projectMonths.filter(m => m.revenue === 0)
      if (zeroRevenueMonths.length > 0 && zeroRevenueMonths.length >= projectMonths.length / 2) {
        alerts.value.push({
          project: name,
          severity: 'medium',
          message: `${zeroRevenueMonths.length} חודשים ללא הכנסה (מתוך ${projectMonths.length} חודשי פרויקט)`,
          detail: `חודשים: ${zeroRevenueMonths.map(m => m.month).join(', ')}`,
        })
      }
    }
  } catch (e) {
    alerts.value.push({ project: 'מערכת', severity: 'high', message: `שגיאה בטעינת נתונים: ${e.message}` })
  } finally {
    loading.value = false
  }
})
</script>
