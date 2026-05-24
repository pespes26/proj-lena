<template>
  <div>
    <div v-if="loading" class="space-y-6 py-4">
      <SkeletonLoader variant="kpi" :count="2" />
      <SkeletonLoader variant="cards" :count="3" />
    </div>
    <p v-if="error" class="font-sans ed-tone-negative mb-6">{{ error }}</p>

    <template v-if="!loading && myProjects.length > 0">
      <section class="ui-card animate-fade-up mb-8">
        <div class="ui-label ed-tone-muted mb-2">שלום {{ userName }}</div>
        <h1 class="ui-display" style="font-size: clamp(2rem, 4vw, 2.75rem); line-height: 1.05;">
          {{ myProjects.length }} פרויקטים
        </h1>
        <div class="font-sans ed-tone-muted text-sm mt-2">
          פעילים תחת אחריותך · {{ dateLabel }}
        </div>
      </section>

      <!-- Project cards grid -->
      <div class="ui-stagger grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <article
          v-for="proj in myProjects"
          :key="proj.name"
          class="ui-card"
        >
          <div class="flex items-start justify-between gap-4 mb-4">
            <div class="flex-1 min-w-0">
              <h3 class="font-sans font-semibold text-ink leading-tight" style="font-size: clamp(1.125rem, 1.8vw, 1.375rem);">
                {{ proj.name }}
              </h3>
              <div class="ui-label ed-tone-faint mt-1" v-if="proj.priority_id">
                <bdi lang="en">עדיפות {{ proj.priority_id }}</bdi>
              </div>
            </div>
            <span class="ui-pill" :class="marginPillClass(proj.margin)">
              מרווח {{ proj.margin != null ? proj.margin.toFixed(1) + '%' : '—' }}
            </span>
          </div>

          <!-- Mini summary row -->
          <div class="grid grid-cols-3 gap-4 py-4 border-t border-border">
            <div>
              <div class="ui-label ed-tone-muted mb-1">הכנסות</div>
              <div class="ui-num font-semibold text-ink text-base">
                <bdi>{{ formatNumber(proj.revenue) }}</bdi>
              </div>
            </div>
            <div>
              <div class="ui-label ed-tone-muted mb-1">הוצאות</div>
              <div class="ui-num font-semibold text-ink text-base">
                <bdi>{{ formatNumber(proj.expenses) }}</bdi>
              </div>
            </div>
            <div>
              <div class="ui-label ed-tone-muted mb-1">רווח</div>
              <div class="ui-num font-semibold text-base" :class="proj.profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
                <bdi>{{ formatNumber(proj.profit) }}</bdi>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="pt-4 border-t border-border flex flex-wrap gap-2">
            <button class="ui-btn" style="padding: 0.5rem 0.875rem; font-size: 0.8125rem;">
              עדכן ביצוע
            </button>
            <button class="ui-btn" style="padding: 0.5rem 0.875rem; font-size: 0.8125rem;">
              הוסף הערה
            </button>
            <button class="ui-btn ui-btn-primary" style="padding: 0.5rem 0.875rem; font-size: 0.8125rem;" @click="$emit('select-project', proj.name)">
              צפה בפרויקט
            </button>
          </div>
        </article>
      </div>
    </template>

    <template v-if="!loading && myProjects.length === 0 && !error">
      <div class="ui-card text-center py-16">
        <div class="ui-label ed-tone-muted mb-3">האזור האישי שלך</div>
        <p class="ui-display text-ink" style="font-size: clamp(1.5rem, 3vw, 2rem);">
          אין פרויקטים משויכים.
        </p>
        <div class="ui-label ed-tone-muted mt-3">פנה למנהל המערכת לשיוך פרויקטים</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPnl, getProjectsDetail, getProfile, formatNumber } from '../services/api'
import { SkeletonLoader, currentHebrewDate } from './editorial'

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

function marginPillClass(margin) {
  if (margin == null) return 'ui-pill-neutral'
  if (margin >= 20) return 'ui-pill-positive'
  if (margin >= 10) return 'ui-pill-warning'
  return 'ui-pill-negative'
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
