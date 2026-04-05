<template>
  <div>
    <SectionHeader
      eyebrow="תזרים"
      :kicker="dateLabel"
      title="תזרים מזומנים"
      subtitle="סקירת תזרים מאוחדת של כלל פרויקטי הקבוצה · כניסות, יציאות, ויתרה מצטברת"
    />

    <p v-if="error" class="font-sans ed-tone-negative mb-6">{{ error }}</p>
    <div v-if="loading" class="font-sans text-ink-muted py-20 text-center">טוען נתונים…</div>

    <template v-if="cfData">
      <!-- KPI strip -->
      <section class="ed-section ed-fade-up">
        <div class="flex flex-wrap gap-y-8 ed-col-rule">
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber label="סך הכנסות" :value="totalRevenue" prefix="₪" size="md" />
          </div>
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber label="סך הוצאות" :value="totalExpenses" prefix="₪" size="md" />
          </div>
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber
              label="נטו תקופתי"
              :value="totalNet"
              prefix="₪"
              :tone="totalNet >= 0 ? 'positive' : 'negative'"
              size="md"
            />
          </div>
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber
              label="יתרה מצטברת"
              :value="lastCumulative"
              prefix="₪"
              :tone="lastCumulative >= 0 ? 'positive' : 'negative'"
              size="md"
            />
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
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="(months, pname) in cfData.projects"
            :key="pname"
            class="ui-mini-card"
          >
            <div class="flex items-baseline justify-between gap-3 mb-3">
              <span class="font-sans font-semibold text-ink text-sm tracking-tight truncate">{{ pname }}</span>
              <span
                class="font-sans font-semibold text-base ed-num flex-shrink-0"
                :class="projectTotal(months) >= 0 ? 'text-positive' : 'text-negative'"
              >
                <bdi>{{ fmt(projectTotal(months)) }}</bdi>
              </span>
            </div>
            <div class="flex h-1.5 overflow-hidden bg-slate-100 rounded-full">
              <div class="bg-accent transition-all" :style="{ width: projectRevenuePercent(months) + '%' }"></div>
              <div class="bg-warning transition-all" :style="{ width: projectExpensePercent(months) + '%' }"></div>
            </div>
            <div class="flex justify-between mt-2 text-[11px] font-medium text-ink-muted">
              <span>הכנסה <bdi class="ed-num font-semibold">{{ fmt(projectRevSum(months)) }}</bdi></span>
              <span>הוצאה <bdi class="ed-num font-semibold">{{ fmt(projectExpSum(months)) }}</bdi></span>
            </div>
          </div>
        </div>
      </RuledSection>

      <!-- Tables -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 mt-2">
        <RuledSection eyebrow="חודשי ומצטבר" title="פירוט חודשי">
          <div class="max-h-[420px] overflow-y-auto">
            <table class="ed-table">
              <thead>
                <tr>
                  <th>חודש</th>
                  <th class="num">הכנסה</th>
                  <th class="num">הוצאה</th>
                  <th class="num">נטו</th>
                  <th class="num">מצטבר</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(m, i) in cfData.monthly_net" :key="i">
                  <td>{{ m.month }}</td>
                  <td class="num"><bdi class="ed-num">{{ fmt(cfData.totals[i]?.revenue) }}</bdi></td>
                  <td class="num"><bdi class="ed-num">{{ fmt(cfData.totals[i]?.expenses) }}</bdi></td>
                  <td class="num" :class="m.value >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
                    <bdi class="ed-num">{{ fmt(m.value) }}</bdi>
                  </td>
                  <td class="num" :class="cfData.cumulative[i].value >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
                    <bdi class="ed-num">{{ fmt(cfData.cumulative[i].value) }}</bdi>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </RuledSection>

        <RuledSection eyebrow="מטריצת פרויקטים" title="נטו לפי פרויקט">
          <div class="max-h-[420px] overflow-auto">
            <table class="ed-table" style="min-width: 600px;">
              <thead>
                <tr>
                  <th>חודש</th>
                  <th v-for="pname in Object.keys(cfData.projects)" :key="pname" class="num">{{ pname }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(label, i) in cfData.month_labels" :key="label">
                  <td>{{ label }}</td>
                  <td
                    v-for="pname in Object.keys(cfData.projects)"
                    :key="pname"
                    class="num"
                    :class="cfData.projects[pname][i].profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'"
                  >
                    <bdi class="ed-num">{{ fmt(cfData.projects[pname][i].profit) }}</bdi>
                  </td>
                </tr>
              </tbody>
            </table>
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
import { SectionHeader, RuledSection, HeroNumber, FootnoteSource, currentHebrewDate } from './editorial'

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
