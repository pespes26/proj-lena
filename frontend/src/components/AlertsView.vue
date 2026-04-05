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
          class="ed-link text-sm"
        >
          איפוס התראות ←
        </button>
      </template>
    </SectionHeader>

    <div v-if="loading" class="font-sans text-ink-muted py-20 text-center">טוען נתונים…</div>

    <template v-if="!loading">
      <!-- Empty state -->
      <div v-if="alerts.length === 0" class="ed-section text-center py-16">
        <div class="ed-eyebrow mb-3">—</div>
        <p class="font-sans text-2xl text-ink leading-tight max-w-lg mx-auto">
          כל הפרויקטים פועלים בטווח התקין.
        </p>
        <div class="ed-eyebrow mt-4">אין התראות פתוחות כרגע</div>
      </div>

      <div v-else class="space-y-6">
        <!-- Summary strip -->
        <div class="ed-section flex flex-wrap gap-8 ed-col-rule ed-fade-up">
          <div>
            <div class="ed-eyebrow mb-2">סה״כ התראות</div>
            <div class="font-sans font-semibold text-ink ed-num" style="font-size: clamp(2rem, 4vw, 3rem); line-height: 1;">{{ alerts.length }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-2 ed-tone-accent">חמור</div>
            <div class="font-sans font-semibold ed-tone-accent ed-num" style="font-size: clamp(2rem, 4vw, 3rem); line-height: 1;">{{ highCount }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-2 ed-tone-warning">בינוני</div>
            <div class="font-sans font-semibold ed-tone-warning ed-num" style="font-size: clamp(2rem, 4vw, 3rem); line-height: 1;">{{ mediumCount }}</div>
          </div>
        </div>

        <!-- High-severity: pull-quote treatment -->
        <template v-if="highAlerts.length > 0">
          <div class="ed-eyebrow mb-2">חריגות חמורות</div>
          <PullQuote
            v-for="(alert, i) in highAlerts"
            :key="'high-' + i"
            severity="high"
            :eyebrow="alert.project"
          >
            {{ alert.message }}
            <template #cite>
              {{ alert.detail }}
            </template>
          </PullQuote>
        </template>

        <!-- Medium-severity: hairline list -->
        <template v-if="mediumAlerts.length > 0">
          <div class="ed-eyebrow mt-8 mb-2">התראות לתשומת לב</div>
          <div class="border-t border-rule-strong">
            <article
              v-for="(alert, i) in mediumAlerts"
              :key="'med-' + i"
              class="py-5 border-b border-rule"
            >
              <div class="flex items-baseline gap-3 mb-2 flex-wrap">
                <span class="ed-eyebrow ed-tone-warning">בינוני</span>
                <h3 class="font-sans font-semibold text-ink text-xl leading-tight">{{ alert.project }}</h3>
              </div>
              <p class="font-sans text-ink text-[0.9375rem] leading-relaxed">{{ alert.message }}</p>
              <p v-if="alert.detail" class="ed-footnote mt-1.5" style="padding-top: 0; border-top: 0;">{{ alert.detail }}</p>
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
import { SectionHeader, PullQuote, currentHebrewDate } from './editorial'

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
