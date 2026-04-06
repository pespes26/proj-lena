<template>
  <div v-if="loading" class="space-y-6 py-4">
    <SkeletonLoader variant="kpi" :count="3" />
    <SkeletonLoader variant="table" :columns="4" :rows="4" />
  </div>
  <div v-else-if="!formData" class="ed-section text-center py-16">
    <div class="ed-eyebrow mb-3">אין נתונים</div>
    <p class="font-sans text-xl text-ink max-w-md mx-auto">לא נמצאו נתוני טופס לפרויקט זה.</p>
    <button @click="$emit('edit')" class="ed-btn ed-btn-primary mt-6">צור טופס פרויקט →</button>
  </div>
  <div v-else class="space-y-2">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-4 mb-4">
      <div>
        <div class="ed-eyebrow mb-1">פרטי פרויקט</div>
        <h3 class="font-sans font-semibold text-ink text-2xl leading-none">{{ project }}</h3>
      </div>
      <button @click="exportPDF" :disabled="exporting" class="ed-btn">
        {{ exporting ? 'מייצא…' : 'ייצוא PDF' }} ↓
      </button>
    </div>

    <!-- PDF content wrapper -->
    <div ref="pdfContent">

      <!-- PDF header (visible only inside generated PDF) -->
      <div class="pdf-header" style="display:none">
        <div style="text-align:center; margin-bottom:24px; padding-bottom:16px; border-bottom:2px solid #0f172a;">
          <h1 style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:26px; font-weight:700; color:#0f172a; margin:0; letter-spacing:-0.02em;">IFMLogiX</h1>
          <p style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:11px; color:#475569; margin:4px 0 10px; font-weight:500;">ניהול פיננסי חכם</p>
          <h2 style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:20px; font-weight:700; color:#0f172a; margin:10px 0 4px;">{{ formData.project_name || project }}</h2>
          <p style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:11px; color:#475569;">מספר עדיפות: {{ formData.priority_id || '—' }} · מנהל: {{ formData.manager || '—' }} · ציר: {{ formData.axis || '—' }} — {{ formData.area || '—' }}</p>
          <p style="font-family: 'DM Sans', 'Rubik', sans-serif; font-size:10px; color:#94a3b8;">הופק בתאריך: {{ new Date().toLocaleDateString('he-IL') }}</p>
        </div>
      </div>

      <!-- Project Info -->
      <RuledSection eyebrow="מידע כללי" title="מסמך פרויקט">
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-8 gap-y-5">
          <div v-if="formData.project_name">
            <div class="ed-eyebrow mb-1">שם פרויקט</div>
            <div class="font-sans font-semibold text-ink">{{ formData.project_name }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-1">מספר עדיפות</div>
            <div class="font-sans font-semibold text-ink ed-num"><bdi lang="en">{{ formData.priority_id || '—' }}</bdi></div>
          </div>
          <div>
            <div class="ed-eyebrow mb-1">מנהל פרויקט</div>
            <div class="font-sans font-semibold text-ink">{{ formData.manager || '—' }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-1">מזמין</div>
            <div class="font-sans font-semibold text-ink">{{ formData.client || '—' }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-1">תאריך התחלה</div>
            <div class="font-sans font-semibold text-ink ed-num">{{ formatDate(formData.start_date) }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-1">צפי סיום</div>
            <div class="font-sans font-semibold text-ink ed-num">{{ formatDate(formData.expected_end_date) }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-1">ציר</div>
            <div class="font-sans font-semibold text-ink">{{ formData.axis || '—' }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-1">תחום</div>
            <div class="font-sans font-semibold text-ink">{{ formData.area || '—' }}</div>
          </div>
          <div>
            <div class="ed-eyebrow mb-1">סטטוס</div>
            <div class="font-sans font-semibold" :class="statusToneClass">{{ statusLabel }}</div>
          </div>
        </div>
        <div v-if="formData.description" class="mt-6 pt-4 border-t border-rule">
          <div class="ed-eyebrow mb-2">תיאור</div>
          <p class="font-sans text-ink leading-relaxed">{{ formData.description }}</p>
        </div>
      </RuledSection>

      <!-- Revenue Summary -->
      <RuledSection eyebrow="הכנסות" title="סיכום הכנסות">
        <HeroNumber
          :label="'סך הכנסות (₪)'"
          :value="formData.total_revenue || 0"
          prefix="₪"
          size="lg"
        />
        <div v-if="formData.revenue_payment_terms?.length" class="mt-8">
          <div class="ed-eyebrow mb-3">תנאי תשלום הכנסה</div>
          <table class="ed-table">
            <thead>
              <tr>
                <th>סוג</th>
                <th class="num">אחוז</th>
                <th class="num">סכום (₪)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(term, i) in formData.revenue_payment_terms" :key="i">
                <td class="font-sans font-semibold">{{ term.type }}</td>
                <td class="num"><bdi class="ed-num">{{ term.percent }}%</bdi></td>
                <td class="num"><bdi class="ed-num">{{ fmt(Math.round((formData.total_revenue || 0) * (term.percent || 0) / 100)) }}</bdi></td>
              </tr>
            </tbody>
          </table>
        </div>
      </RuledSection>

      <!-- Expenses Summary -->
      <RuledSection eyebrow="הוצאות" title="סיכום הוצאות">
        <!-- Subcontractors -->
        <div v-if="formData.subcontractors?.length" class="mb-8">
          <div class="ed-eyebrow mb-3">קבלני משנה · <bdi class="ed-num">{{ formData.subcontractors.length }}</bdi></div>
          <table class="ed-table">
            <thead>
              <tr>
                <th>שם</th>
                <th class="num">סכום כולל (₪)</th>
                <th>תנאי תשלום</th>
                <th>תקופה</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(sub, i) in formData.subcontractors" :key="i">
                <td class="font-sans font-semibold">{{ sub.name }}</td>
                <td class="num"><bdi class="ed-num">{{ fmt(sub.total_amount || sub.monthly_amount || 0) }}</bdi></td>
                <td>
                  <template v-if="Array.isArray(sub.payment_terms)">
                    <span v-for="(t, j) in sub.payment_terms" :key="j">{{ t.type }} {{ t.percent }}%<template v-if="j < sub.payment_terms.length - 1">, </template></span>
                  </template>
                  <template v-else>{{ sub.payment_terms || '—' }}</template>
                </td>
                <td class="text-ink-muted text-xs">{{ formatDate(sub.start_date) }} — {{ formatDate(sub.end_date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Expense categories -->
        <template v-for="cat in expenseCategories" :key="cat.key">
          <div v-if="formData['expense_lines_' + cat.key]?.length" class="mb-8">
            <div class="ed-eyebrow mb-3">{{ cat.label }} · <bdi class="ed-num">{{ formData['expense_lines_' + cat.key].length }}</bdi></div>
            <table class="ed-table">
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
                  <td class="num"><bdi class="ed-num">{{ fmt(line.monthly_amount || 0) }}</bdi></td>
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
        <div class="mt-6 pt-4 border-t border-rule-strong">
          <HeroNumber label='סה״כ הוצאות משוערכות' :value="totalExpenses" prefix="₪" size="md" />
        </div>
      </RuledSection>

      <!-- Profit Summary -->
      <RuledSection eyebrow="רווחיות" title="סיכום רווחיות">
        <div class="flex flex-wrap gap-y-8 ed-col-rule">
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber label="הכנסות" :value="formData.total_revenue || 0" prefix="₪" size="md" />
          </div>
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber label="הוצאות" :value="totalExpenses" prefix="₪" size="md" tone="warning" />
          </div>
          <div class="flex-1" style="min-width: 180px;">
            <HeroNumber
              label="רווח צפוי"
              :value="profit"
              prefix="₪"
              :tone="profit >= 0 ? 'positive' : 'negative'"
              size="md"
              :footnote="'מרווח ' + marginPercent"
            />
          </div>
        </div>
      </RuledSection>

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
import { RuledSection, HeroNumber, SkeletonLoader } from './editorial'

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
const statusToneClass = computed(() => {
  const s = formData.value?.status
  if (s === 'active') return 'ed-tone-positive'
  if (s === 'on-hold') return 'ed-tone-warning'
  if (s === 'completed') return 'ed-tone-muted'
  return 'text-ink'
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
