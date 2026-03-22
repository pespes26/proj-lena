<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-center justify-between mb-5">
      <div>
        <h3 class="font-semibold text-gray-700">עדכון ביצוע בפועל</h3>
        <p class="text-xs text-gray-400 mt-0.5">הזן נתוני הכנסות והוצאות בפועל לחודש נבחר</p>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="selectedMonth"
          class="bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300">
          <option v-for="m in 12" :key="m" :value="m">{{ monthNames[m - 1] }}</option>
        </select>
      </div>
    </div>

    <div v-if="saving" class="text-center py-8 text-gray-400 text-sm">שומר...</div>
    <div v-else-if="success" class="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl mb-4 text-sm flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
      {{ success }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1.5">הכנסה בפועל (אלפי ש"ח)</label>
        <input v-model.number="form.revenue" type="number" min="0" step="0.01"
          class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
        <div v-if="forecastRevenue" class="text-[10px] text-gray-400 mt-1">תחזית: {{ forecastRevenue.toLocaleString('he-IL') }}</div>
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1.5">הוצאות תפעול בפועל (אלפי ש"ח)</label>
        <input v-model.number="form.op_expenses" type="number" min="0" step="0.01"
          class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1.5">הוצאות שכר בפועל (אלפי ש"ח)</label>
        <input v-model.number="form.salary_expenses" type="number" min="0" step="0.01"
          class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1.5">הערות</label>
        <input v-model="form.notes" type="text" maxlength="200"
          class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" placeholder="הערה לחודש..." />
      </div>
    </div>

    <!-- Variance card -->
    <div v-if="forecastRevenue || form.revenue" class="grid grid-cols-3 gap-3 mb-5">
      <div class="bg-gray-50 rounded-xl p-3 text-center">
        <div class="text-[10px] text-gray-400 mb-1">רווח תחזית</div>
        <div class="text-sm font-semibold text-gray-700">{{ forecastProfit.toLocaleString('he-IL') }}</div>
      </div>
      <div class="bg-gray-50 rounded-xl p-3 text-center">
        <div class="text-[10px] text-gray-400 mb-1">רווח בפועל</div>
        <div class="text-sm font-semibold" :class="actualProfit >= 0 ? 'text-green-600' : 'text-red-500'">{{ actualProfit.toLocaleString('he-IL') }}</div>
      </div>
      <div class="rounded-xl p-3 text-center" :class="variance >= 0 ? 'bg-green-50' : 'bg-red-50'">
        <div class="text-[10px] text-gray-400 mb-1">סטייה</div>
        <div class="text-sm font-semibold" :class="variance >= 0 ? 'text-green-600' : 'text-red-500'">
          {{ variance >= 0 ? '+' : '' }}{{ variance.toLocaleString('he-IL') }}
        </div>
      </div>
    </div>

    <button @click="save" :disabled="saving"
      class="w-full py-2.5 bg-emerald-700 text-white text-sm font-medium rounded-xl hover:bg-emerald-800 disabled:opacity-50 transition">
      שמור ביצוע בפועל
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { saveProjectActuals, getProjectForm } from '../services/api'

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
    // Load existing actuals for selected month
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
    // Refresh form data
    await loadFormData()
  } catch (e) { success.value = null; alert(e.message) }
  finally { saving.value = false }
}
</script>
