<template>
  <div v-if="loading" class="space-y-6 py-4">
    <SkeletonLoader variant="kpi" :count="3" />
    <SkeletonLoader variant="table" :columns="4" :rows="4" />
  </div>
  <div v-else-if="!formData" class="ui-card text-center py-16 animate-fade-up">
    <div class="ui-label mb-3">אין נתונים</div>
    <p class="ui-display max-w-md mx-auto">לא נמצאו נתוני טופס לפרויקט זה.</p>
  </div>
  <div v-else class="space-y-6">
    <!-- Header -->
    <header class="ui-card animate-fade-up">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="min-w-0">
          <div class="ui-label mb-2">פרטי פרויקט</div>
          <h2 class="ui-display leading-tight">{{ project }}</h2>
        </div>
        <button @click="exportPDF" :disabled="exporting" class="ui-btn">
          {{ exporting ? 'מייצא…' : 'ייצוא PDF' }} ↓
        </button>
      </div>
    </header>

    <!-- PDF content wrapper -->
    <div ref="pdfContent">

      <!-- PDF header (visible only inside generated PDF) -->
      <div class="pdf-header" style="display:none">
        <div style="text-align:center; margin-bottom:24px; padding-bottom:16px; border-bottom:2px solid var(--ink);">
          <h1 style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:26px; font-weight:700; color:var(--ink); margin:0; letter-spacing:-0.02em;">IFMLogiX</h1>
          <p style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:11px; color:var(--ink-muted); margin:4px 0 10px; font-weight:500;">ניהול פיננסי חכם</p>
          <h2 style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:20px; font-weight:700; color:var(--ink); margin:10px 0 4px;">{{ formData.project_name || project }}</h2>
          <p style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:11px; color:var(--ink-muted);">מספר עדיפות: {{ formData.priority_id || '—' }} · מנהל: {{ formData.manager || '—' }} · ציר: {{ formData.axis || '—' }} — {{ formData.area || '—' }}</p>
          <p style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:10px; color:var(--ink-whisper);">הופק בתאריך: {{ new Date().toLocaleDateString('he-IL') }}</p>
        </div>
      </div>

      <!-- Project Info -->
      <section class="ui-card mb-6">
        <div class="ui-label mb-2">מידע כללי</div>
        <h3 class="font-sans font-semibold text-ink text-xl mb-6">מסמך פרויקט</h3>
        <div class="ui-stagger grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-8 gap-y-5">
          <div v-if="formData.project_name">
            <div class="ui-label mb-1">שם פרויקט</div>
            <div class="font-sans font-semibold text-ink">{{ formData.project_name }}</div>
          </div>
          <div>
            <div class="ui-label mb-1">מספר עדיפות</div>
            <div class="ui-num font-semibold text-ink"><bdi lang="en">{{ formData.priority_id || '—' }}</bdi></div>
          </div>
          <div>
            <div class="ui-label mb-1">מנהל פרויקט</div>
            <div class="font-sans font-semibold text-ink">{{ formData.manager || '—' }}</div>
          </div>
          <div>
            <div class="ui-label mb-1">מזמין</div>
            <div class="font-sans font-semibold text-ink">{{ formData.client || '—' }}</div>
          </div>
          <div>
            <div class="ui-label mb-1">תאריך התחלה</div>
            <div class="ui-num font-semibold text-ink">{{ formatDate(formData.start_date) }}</div>
          </div>
          <div>
            <div class="ui-label mb-1">צפי סיום</div>
            <div class="ui-num font-semibold text-ink">{{ formatDate(formData.expected_end_date) }}</div>
          </div>
          <div>
            <div class="ui-label mb-1">ציר</div>
            <div class="font-sans font-semibold text-ink">{{ formData.axis || '—' }}</div>
          </div>
          <div>
            <div class="ui-label mb-1">תחום</div>
            <div class="font-sans font-semibold text-ink">{{ formData.area || '—' }}</div>
          </div>
          <div>
            <div class="ui-label mb-1">סטטוס</div>
            <span class="ui-pill" :class="statusPillClass">{{ statusLabel }}</span>
          </div>
        </div>
        <div v-if="formData.description" class="mt-6 pt-4" style="border-top: 1px solid var(--border);">
          <div class="ui-label mb-2">תיאור</div>
          <p class="font-sans text-ink leading-relaxed">{{ formData.description }}</p>
        </div>
      </section>

      <!-- Revenue Summary -->
      <section class="ui-card mb-6">
        <div class="ui-label mb-2">הכנסות</div>
        <h3 class="font-sans font-semibold text-ink text-xl mb-6">סיכום הכנסות</h3>
        <div class="ui-mini-card" style="max-width: 340px;">
          <div class="ui-label mb-2">סך הכנסות (₪)</div>
          <div class="ui-num font-semibold text-ink text-2xl ed-tone-positive"><bdi>₪ {{ fmt(formData.total_revenue || 0) }}</bdi></div>
        </div>
        <div v-if="formData.revenue_payment_terms?.length" class="mt-8">
          <div class="ui-label mb-3">תנאי תשלום הכנסה</div>
          <table class="ui-table">
            <thead>
              <tr>
                <th>סוג</th>
                <th class="num">אחוז</th>
                <th class="num">סכום (₪)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(term, i) in formData.revenue_payment_terms" :key="i">
                <td>
                  <span class="ui-pill" :class="term.type === 'מקדמה' || term.type === 'מזומן' ? 'ui-pill-positive' : 'ui-pill-warning'">{{ term.type }}</span>
                </td>
                <td class="num"><bdi class="ui-num">{{ term.percent }}%</bdi></td>
                <td class="num"><bdi class="ui-num">{{ fmt(Math.round((formData.total_revenue || 0) * (term.percent || 0) / 100)) }}</bdi></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Expenses Summary -->
      <section class="ui-card mb-6">
        <div class="ui-label mb-2">הוצאות</div>
        <h3 class="font-sans font-semibold text-ink text-xl mb-6">סיכום הוצאות</h3>

        <!-- Subcontractors -->
        <div v-if="formData.subcontractors?.length" class="mb-8">
          <div class="ui-label mb-3">קבלני משנה · <bdi class="ui-num">{{ formData.subcontractors.length }}</bdi></div>
          <div class="ui-stagger grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="(sub, i) in formData.subcontractors" :key="i" class="ui-mini-card">
              <div class="flex items-baseline justify-between mb-2 gap-3">
                <span class="font-sans font-semibold text-ink truncate">{{ sub.name }}</span>
                <bdi class="ui-num font-semibold text-ink">{{ fmt(sub.total_amount || sub.monthly_amount || 0) }} ₪</bdi>
              </div>
              <div class="ui-label mb-1" style="font-size: 0.625rem;">
                <template v-if="Array.isArray(sub.payment_terms)">
                  <span v-for="(t, j) in sub.payment_terms" :key="j">{{ t.type }} {{ t.percent }}%<template v-if="j < sub.payment_terms.length - 1">, </template></span>
                </template>
                <template v-else>{{ sub.payment_terms || '—' }}</template>
              </div>
              <div class="ui-label ed-tone-muted" style="font-size: 0.625rem;">{{ formatDate(sub.start_date) }} — {{ formatDate(sub.end_date) }}</div>
            </div>
          </div>
        </div>

        <!-- Expense categories -->
        <template v-for="cat in expenseCategories" :key="cat.key">
          <div v-if="formData['expense_lines_' + cat.key]?.length" class="mb-8">
            <div class="ui-label mb-3">{{ cat.label }} · <bdi class="ui-num">{{ formData['expense_lines_' + cat.key].length }}</bdi></div>
            <table class="ui-table">
              <thead>
                <tr>
                  <th>שם</th>
                  <th class="num">סכום חודשי (₪)</th>
                  <th>תנאי תשלום</th>
                  <th>תקופה</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(line, i) in formData['expense_lines_' + cat.key]" :key="i">
                  <td class="font-sans font-semibold">{{ line.name }}</td>
                  <td class="num"><bdi class="ui-num">{{ fmt(line.monthly_amount || 0) }}</bdi></td>
                  <td>{{ line.payment_terms || '—' }}</td>
                  <td class="text-ink-muted text-xs">
                    <template v-if="line.start_date">{{ formatDate(line.start_date) }} — {{ formatDate(line.end_date) }}</template>
                    <template v-else>—</template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- Total expenses -->
        <div class="mt-6 pt-4" style="border-top: 1px solid var(--border-strong);">
          <div class="ui-mini-card" style="max-width: 340px;">
            <div class="ui-label mb-2">סה״כ הוצאות משוערכות</div>
            <div class="ui-num font-semibold text-ink text-2xl ed-tone-warning"><bdi>₪ {{ fmt(totalExpenses) }}</bdi></div>
          </div>
        </div>
      </section>

      <!-- Profit Summary -->
      <section class="ui-card mb-6">
        <div class="ui-label mb-2">רווחיות</div>
        <h3 class="font-sans font-semibold text-ink text-xl mb-6">סיכום רווחיות</h3>
        <div class="ui-stagger grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="ui-mini-card">
            <div class="ui-label mb-2">הכנסות</div>
            <div class="ui-num font-semibold text-ink text-xl ed-tone-positive"><bdi>₪ {{ fmt(formData.total_revenue || 0) }}</bdi></div>
          </div>
          <div class="ui-mini-card">
            <div class="ui-label mb-2">הוצאות</div>
            <div class="ui-num font-semibold text-xl ed-tone-warning"><bdi>₪ {{ fmt(totalExpenses) }}</bdi></div>
          </div>
          <div class="ui-mini-card">
            <div class="ui-label mb-2">רווח צפוי</div>
            <div class="ui-num font-semibold text-xl" :class="profit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'"><bdi>₪ {{ fmt(profit) }}</bdi></div>
            <div class="ui-label mt-2" style="font-size: 0.625rem;">מרווח {{ marginPercent }}</div>
          </div>
        </div>
      </section>

      <!-- PDF footer -->
      <div class="pdf-footer" style="display:none; text-align:center; margin-top:24px; padding-top:12px; border-top:1px solid #d8cfbe; font-size:10px; color:#928a7e;">
        מסמך זה הופק ממערכת IFMLogiX · {{ new Date().toLocaleDateString('he-IL') }} {{ new Date().toLocaleTimeString('he-IL', {hour:'2-digit', minute:'2-digit'}) }}
      </div>

    </div><!-- /pdfContent -->
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getProjectForm, formatNumber } from '../services/api'
import html2pdf from 'html2pdf.js'
import { SkeletonLoader } from './editorial'

const props = defineProps({
  project: { type: String, required: true }
})
defineEmits(['edit'])

const formData = ref(null)
const loading = ref(true)
const exporting = ref(false)
const pdfContent = ref(null)
const fmt = formatNumber

const expenseCategories = [
  { key: 'manpower', label: 'כוח אדם' },
  { key: 'equipment', label: 'ציוד וכלים' },
  { key: 'insurance', label: 'ביטוחים' },
  { key: 'consultants', label: 'מתכננים ויועצים' },
  { key: 'financing', label: 'הוצאות מימון' },
  { key: 'other', label: 'אחר' },
]

const statusLabel = computed(() => {
  const s = formData.value?.status
  if (s === 'active') return 'פעיל'
  if (s === 'on-hold') return 'מושהה'
  if (s === 'completed') return 'הושלם'
  return '—'
})
const statusPillClass = computed(() => {
  const s = formData.value?.status
  if (s === 'active') return 'ui-pill-positive'
  if (s === 'on-hold') return 'ui-pill-warning'
  if (s === 'completed') return 'ui-pill-neutral'
  return 'ui-pill-neutral'
})

const totalExpenses = computed(() => {
  if (!formData.value) return 0
  let total = 0
  for (const sub of formData.value.subcontractors || []) {
    total += sub.total_amount || sub.monthly_amount || 0
  }
  for (const cat of expenseCategories) {
    for (const line of formData.value['expense_lines_' + cat.key] || []) {
      const sm = parseMonth(line.start_date, 1)
      const em = parseMonth(line.end_date, 12)
      const months = Math.max(1, em - sm + 1)
      total += (line.monthly_amount || 0) * months
    }
  }
  return Math.round(total)
})

const profit = computed(() => (formData.value?.total_revenue || 0) - totalExpenses.value)
const marginPercent = computed(() => {
  const rev = formData.value?.total_revenue || 0
  if (rev <= 0) return '—'
  return (profit.value / rev * 100).toFixed(1) + '%'
})

function parseMonth(dateStr, def) {
  if (!dateStr) return def
  const parts = dateStr.split('-')
  return parts.length >= 2 ? parseInt(parts[1]) : def
}

function formatDate(d) {
  if (!d) return '—'
  const parts = d.split('-')
  if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`
  return d
}

async function loadData() {
  loading.value = true
  try {
    formData.value = await getProjectForm(props.project)
  } catch {
    formData.value = null
  } finally {
    loading.value = false
  }
}

async function exportPDF() {
  if (!pdfContent.value) return
  exporting.value = true

  // Wait for fonts to be fully loaded before capture
  try {
    if (document.fonts && document.fonts.ready) {
      await document.fonts.ready
    }
  } catch {}

  const header = pdfContent.value.querySelector('.pdf-header')
  const footer = pdfContent.value.querySelector('.pdf-footer')
  if (header) header.style.display = 'block'
  if (footer) footer.style.display = 'block'

  try {
    const filename = `${formData.value?.project_name || props.project}_${new Date().toISOString().slice(0,10)}.pdf`
    await html2pdf().set({
      margin: [10, 10, 10, 10],
      filename,
      image: { type: 'jpeg', quality: 0.95 },
      html2canvas: { scale: 2, useCORS: true, scrollY: 0, backgroundColor: '#ffffff' },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
    }).from(pdfContent.value).save()
  } finally {
    if (header) header.style.display = 'none'
    if (footer) footer.style.display = 'none'
    exporting.value = false
  }
}

onMounted(loadData)
watch(() => props.project, loadData)
</script>
