<template>
  <section class="ed-section">
    <div class="flex items-start justify-between mb-6 flex-wrap gap-4">
      <div>
        <div class="ed-eyebrow mb-1">עדכון ידני</div>
        <h3 class="font-sans font-semibold text-ink text-2xl leading-none">ביצוע בפועל</h3>
        <p class="font-sans text-ink-muted text-sm mt-1.5">הזן הכנסות והוצאות בפועל לחודש נבחר</p>
      </div>
      <div>
        <label class="ed-label">חודש</label>
        <select v-model="selectedMonth" class="ed-select" style="min-width: 180px;">
          <option v-for="m in 12" :key="m" :value="m">{{ monthNames[m - 1] }}</option>
        </select>
      </div>
    </div>

    <div v-if="saving" class="font-sans text-ink-muted text-center py-8">שומר…</div>
    <p
      v-else-if="success"
      class="font-sans ed-tone-positive mb-5 pb-3 border-b border-rule"
    >
      ✓ {{ success }}
    </p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6 mb-8">
      <div>
        <label class="ed-label">הכנסה בפועל (₪)</label>
        <input v-model.number="form.revenue" type="number" min="0" step="0.01" class="ed-input ed-num" />
        <div v-if="forecastRevenue" class="ed-eyebrow mt-1.5" style="font-size: 0.625rem;">
          תחזית: <bdi class="ed-num">{{ forecastRevenue.toLocaleString('he-IL') }}</bdi>
        </div>
      </div>
      <div>
        <label class="ed-label">הוצאות תפעול בפועל (₪)</label>
        <input v-model.number="form.op_expenses" type="number" min="0" step="0.01" class="ed-input ed-num" />
      </div>
      <div>
        <label class="ed-label">הוצאות שכר בפועל (₪)</label>
        <input v-model.number="form.salary_expenses" type="number" min="0" step="0.01" class="ed-input ed-num" />
      </div>
      <div>
        <label class="ed-label">הערות</label>
        <input
          v-model="form.notes"
          type="text"
          maxlength="200"
          class="ed-input"
          placeholder="הערה לחודש…"
        />
      </div>
    </div>

    <!-- Variance -->
    <div v-if="forecastRevenue || form.revenue" class="flex flex-wrap gap-y-6 ed-col-rule border-t border-rule-strong pt-6 mb-6">
      <div class="flex-1" style="min-width: 140px;">
        <HeroNumber label="רווח תחזית" :value="forecastProfit" prefix="₪" size="sm" />
      </div>
      <div class="flex-1" style="min-width: 140px;">
        <HeroNumber
          label="רווח בפועל"
          :value="actualProfit"
          prefix="₪"
          :tone="actualProfit >= 0 ? 'positive' : 'negative'"
          size="sm"
        />
      </div>
      <div class="flex-1" style="min-width: 140px;">
        <HeroNumber
          label="סטייה"
          :value="variance"
          prefix="₪"
          :tone="variance >= 0 ? 'positive' : 'negative'"
          size="sm"
        />
      </div>
    </div>

    <button @click="save" :disabled="saving" class="ed-btn ed-btn-primary">
      שמור ביצוע בפועל →
    </button>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { saveProjectActuals, getProjectForm } from '../services/api'
import { HeroNumber } from './editorial'

const props = defineProps({
  project: { type: String, required: true },
})
const emit = defineEmits(['saved'])

const monthNames = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']
const selectedMonth = ref(new Date().getMonth() + 1)
const saving = ref(false)
const success = ref(null)
const formData = ref(null)

const form = ref({ revenue: 0, op_expenses: 0, salary_expenses: 0, notes: '' })

const forecastRevenue = computed(() => {
  if (!formData.value) return 0
  const total = formData.value.total_revenue || 0
  const pct = formData.value.revenue_forecast?.[String(selectedMonth.value)] || 0
  return Math.round(total * pct / 100)
})

const forecastExpenses = computed(() => {
  if (!formData.value) return 0
  let exp = 0
  for (const cat of ['manpower', 'equipment', 'insurance', 'consultants', 'financing', 'other']) {
    for (const line of (formData.value['expense_lines_' + cat] || [])) {
      const start = line.start_month || 1
      const end = line.end_month || 12
      if (start <= selectedMonth.value && selectedMonth.value <= end) exp += (line.monthly_amount || 0)
    }
  }
  for (const sub of (formData.value.subcontractors || [])) exp += (sub.monthly_amount || 0)
  return exp
})

const forecastProfit = computed(() => forecastRevenue.value - forecastExpenses.value)
const actualProfit = computed(() => (form.value.revenue || 0) - (form.value.op_expenses || 0) - (form.value.salary_expenses || 0))
const variance = computed(() => actualProfit.value - forecastProfit.value)

async function loadFormData() {
  try {
    formData.value = await getProjectForm(props.project)
    const existing = formData.value?.actuals?.[String(selectedMonth.value)]
    if (existing) {
      form.value = { ...existing }
    } else {
      form.value = { revenue: 0, op_expenses: 0, salary_expenses: 0, notes: '' }
    }
  } catch { formData.value = null }
}

watch(selectedMonth, () => {
  const existing = formData.value?.actuals?.[String(selectedMonth.value)]
  if (existing) form.value = { ...existing }
  else form.value = { revenue: 0, op_expenses: 0, salary_expenses: 0, notes: '' }
  success.value = null
})

watch(() => props.project, () => { loadFormData() }, { immediate: true })

async function save() {
  saving.value = true; success.value = null
  try {
    await saveProjectActuals(props.project, { month: selectedMonth.value, ...form.value })
    success.value = `ביצוע בפועל לחודש ${monthNames[selectedMonth.value - 1]} נשמר`
    emit('saved')
    await loadFormData()
  } catch (e) { success.value = null; alert(e.message) }
  finally { saving.value = false }
}
</script>
