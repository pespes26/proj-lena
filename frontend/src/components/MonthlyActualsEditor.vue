<template>
  <section class="ui-card">
    <div class="flex items-start justify-between mb-6 flex-wrap gap-4">
      <div>
        <div class="ui-label mb-1">עדכון ידני</div>
        <h3 class="ui-display" style="color: var(--ink);">ביצוע בפועל</h3>
        <p class="font-sans text-sm mt-1.5 ed-tone-muted">הזן הכנסות והוצאות בפועל לחודש נבחר</p>
      </div>
      <div>
        <label class="ui-form-label">חודש</label>
        <select v-model="selectedMonth" class="ui-select" style="min-width: 180px;">
          <option v-for="m in 12" :key="m" :value="m">{{ monthNames[m - 1] }}</option>
        </select>
      </div>
    </div>

    <div v-if="saving" class="font-sans text-center py-8 ed-tone-muted">שומר…</div>
    <p
      v-else-if="success"
      class="font-sans ed-tone-positive mb-5 pb-3"
      style="border-bottom: 1px solid var(--border);"
    >
      ✓ {{ success }}
    </p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6 mb-8">
      <div>
        <label class="ui-form-label">הכנסה בפועל (₪)</label>
        <input v-model.number="form.revenue" type="number" min="0" step="0.01" class="ui-input ui-num" />
        <div v-if="forecastRevenue" class="ui-label mt-1.5" style="font-size: 0.625rem;">
          תחזית: <bdi class="ui-num">{{ forecastRevenue.toLocaleString('he-IL') }}</bdi>
        </div>
      </div>
      <div>
        <label class="ui-form-label">הוצאות תפעול בפועל (₪)</label>
        <input v-model.number="form.op_expenses" type="number" min="0" step="0.01" class="ui-input ui-num" />
      </div>
      <div>
        <label class="ui-form-label">הוצאות שכר בפועל (₪)</label>
        <input v-model.number="form.salary_expenses" type="number" min="0" step="0.01" class="ui-input ui-num" />
      </div>
      <div>
        <label class="ui-form-label">הערות</label>
        <textarea
          v-model="form.notes"
          maxlength="200"
          rows="2"
          class="ui-input"
          placeholder="הערה לחודש…"
          style="resize: none; background: var(--surface); border-color: var(--border);"
        ></textarea>
      </div>
    </div>

    <!-- Variance -->
    <div
      v-if="forecastRevenue || form.revenue"
      class="ui-stagger grid grid-cols-1 sm:grid-cols-3 gap-3 pt-6 mb-6"
      style="border-top: 1px solid var(--border-strong);"
    >
      <div class="ui-mini-card">
        <div class="ed-eyebrow mb-1.5">רווח תחזית</div>
        <div class="ui-num font-semibold text-lg" style="color: var(--ink);">
          <bdi>₪{{ forecastProfit.toLocaleString('he-IL') }}</bdi>
        </div>
      </div>
      <div class="ui-mini-card">
        <div class="ed-eyebrow mb-1.5">רווח בפועל</div>
        <div
          class="ui-num font-semibold text-lg"
          :class="actualProfit >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'"
        >
          <bdi>₪{{ actualProfit.toLocaleString('he-IL') }}</bdi>
        </div>
      </div>
      <div class="ui-mini-card">
        <div class="ed-eyebrow mb-1.5">סטייה</div>
        <div
          class="ui-num font-semibold text-lg"
          :class="variance >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'"
        >
          <bdi>₪{{ variance.toLocaleString('he-IL') }}</bdi>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <button @click="save" :disabled="saving" class="ui-btn-primary">
        שמור ביצוע בפועל
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { saveProjectActuals, getProjectForm } from '../services/api'
import { useToast } from '../composables/useToast'

const props = defineProps({
  project: { type: String, required: true },
})
const emit = defineEmits(['saved'])
const toast = useToast()

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
    toast.success(`נתוני חודש ${monthNames[selectedMonth.value - 1]} נשמרו`)
    emit('saved')
    await loadFormData()
  } catch (e) { success.value = null; alert(e.message) }
  finally { saving.value = false }
}
</script>
