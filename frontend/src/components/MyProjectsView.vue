<template>
  <div>
    <div v-if="loading" class="space-y-6 py-4">
      <SkeletonLoader variant="kpi" :count="2" />
      <SkeletonLoader variant="cards" :count="3" />
    </div>
    <p v-if="error" class="font-sans ed-tone-negative mb-6">{{ error }}</p>

    <template v-if="!loading && myProjects.length > 0">
      <SectionHeader
        eyebrow="אזור אישי"
        :kicker="dateLabel"
        :title="'שלום ' + userName"
        :subtitle="myProjects.length + ' פרויקטים פעילים תחת אחריותך'"
      />

      <!-- Project list — ruled rows, not cards -->
      <div class="border-t border-rule-strong">
        <article
          v-for="proj in myProjects"
          :key="proj.name"
          class="py-6 border-b border-rule group"
        >
          <div class="flex items-start justify-between gap-6 flex-wrap">
            <!-- Title column -->
            <div class="flex-1 min-w-0" style="min-width: 260px;">
              <div class="ed-eyebrow mb-2" v-if="proj.priority_id">
                <bdi lang="en">עדיפות {{ proj.priority_id }}</bdi>
              </div>
              <h3 class="font-sans font-semibold text-ink leading-tight" style="font-size: clamp(1.5rem, 2.5vw, 2rem);">
                {{ proj.name }}
              </h3>
              <div class="mt-2">
                <span class="ed-eyebrow" :class="marginToneClass(proj.margin)">
                  מרווח {{ proj.margin != null ? proj.margin.toFixed(1) + '%' : '—' }}
                </span>
              </div>
            </div>

            <!-- KPI column (hero numbers) -->
            <div class="flex items-start gap-8 flex-wrap ed-col-rule">
              <div>
                <div class="ed-eyebrow mb-1">הכנסות</div>
                <div class="font-sans font-semibold text-ink ed-num" style="font-size: clamp(1.375rem, 2.2vw, 1.875rem); line-height: 1;">
                  <bdi>{{ formatNumber(proj.revenue) }}</bdi>
                </div>
              </div>
              <div>
                <div class="ed-eyebrow mb-1">הוצאות</div>
                <div class="font-sans font-semibold text-ink ed-num" style="font-size: clamp(1.375rem, 2.2vw, 1.875rem); line-height: 1;">
                  <bdi>{{ formatNumber(proj.expenses) }}</bdi>
                </div>
              </div>
              <div>
                <div class="ed-eyebrow mb-1">רווח</div>
                <div class="font-sans font-semibold ed-num" :class="proj.profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'" style="font-size: clamp(1.375rem, 2.2vw, 1.875rem); line-height: 1;">
                  <bdi>{{ formatNumber(proj.profit) }}</bdi>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="mt-5 flex flex-wrap gap-6">
            <button class="ed-link text-sm">עדכן ביצוע →</button>
            <button class="ed-link text-sm">הוסף הערה →</button>
            <button @click="$emit('select-project', proj.name)" class="ed-link text-sm font-bold">
              צפה בפרויקט המלא →
            </button>
          </div>
        </article>
      </div>
    </template>

    <template v-if="!loading && myProjects.length === 0 && !error">
      <div class="ed-section text-center py-16">
        <div class="ed-eyebrow mb-3">האזור האישי שלך</div>
        <p class="font-sans text-2xl text-ink leading-tight max-w-lg mx-auto">
          אין פרויקטים משויכים.
        </p>
        <div class="ed-eyebrow mt-3 ed-tone-muted">פנה למנהל המערכת לשיוך פרויקטים</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPnl, getProjectsDetail, getProfile, formatNumber } from '../services/api'
import { SectionHeader, SkeletonLoader, currentHebrewDate } from './editorial'

defineEmits(['select-project'])

const loading = ref(true)
const error = ref('')
const userName = ref('')
const pnlData = ref(null)
const projectsDetail = ref([])
const linkedManager = ref('')

const dateLabel = computed(() => currentHebrewDate())

const myProjects = computed(() => {
  if (!pnlData.value) return []
  const results = []
  for (const [name, project] of Object.entries(pnlData.value)) {
    const manager = project.meta?.manager || ''
    if (linkedManager.value && manager !== linkedManager.value) continue
    results.push({
      name,
      priority_id: project.meta?.priority_id || '',
      margin: project.summary?.margin ?? null,
      revenue: project.summary?.total_revenue ?? 0,
      expenses: project.summary?.total_expenses ?? 0,
      profit: project.summary?.operating_profit ?? 0,
    })
  }
  return results
})

function marginToneClass(margin) {
  if (margin == null) return 'ed-tone-muted'
  if (margin >= 20) return 'ed-tone-positive'
  if (margin >= 10) return 'ed-tone-warning'
  return 'ed-tone-negative'
}

onMounted(async () => {
  try {
    const [profile, pnl, detail] = await Promise.all([getProfile(), getPnl(), getProjectsDetail()])
    userName.value = profile.full_name || profile.username || ''
    linkedManager.value = profile.linked_manager || ''
    pnlData.value = pnl
    projectsDetail.value = detail || []
  } catch (e) {
    error.value = e.message || 'שגיאה בטעינת נתונים'
  } finally {
    loading.value = false
  }
})
</script>
