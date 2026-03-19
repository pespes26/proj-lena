<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center" dir="rtl">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>

      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-3xl mx-4 max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header + Stepper -->
        <div class="px-8 pt-6 pb-4 border-b border-gray-100">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-lg font-bold text-gray-800">הגדרת פרויקט — {{ project }}</h3>
            <button @click="$emit('close')" class="p-2 rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <!-- Stepper -->
          <div class="flex items-center justify-center gap-0">
            <template v-for="(s, i) in steps" :key="i">
              <div class="flex items-center gap-2 cursor-pointer" @click="i < step ? step = i : null">
                <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all',
                  i < step ? 'bg-lime-500 text-white' : i === step ? 'bg-lime-100 text-lime-700 ring-2 ring-lime-400' : 'bg-gray-100 text-gray-400']">
                  <svg v-if="i < step" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                  <span v-else>{{ i + 1 }}</span>
                </div>
                <span class="text-xs font-medium" :class="i <= step ? 'text-gray-700' : 'text-gray-400'">{{ s }}</span>
              </div>
              <div v-if="i < steps.length - 1" class="w-12 h-px mx-2" :class="i < step ? 'bg-lime-400' : 'bg-gray-200'"></div>
            </template>
          </div>
        </div>

        <!-- Content (scrollable) -->
        <div class="flex-1 overflow-y-auto px-8 py-6">

          <!-- Step 1: Project Details -->
          <div v-if="step === 0" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">מספר Priority *</label>
                <input v-model="form.priority_id" type="text" placeholder="P-1001"
                  class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-lime-300 transition" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">תאריך התחלה *</label>
                <input v-model="form.start_date" type="date"
                  class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">שם מנהל פרויקט *</label>
                <input v-model="form.manager" type="text" placeholder="שם מלא"
                  class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">שם המזמין *</label>
                <input v-model="form.client" type="text" placeholder="שם החברה/לקוח"
                  class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">תחום</label>
                <select v-model="form.area" class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition">
                  <option value="מסחרי פרטי">מסחרי פרטי</option>
                  <option value="פרוייקטים">פרוייקטים</option>
                  <option value="מטה">מטה</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">ציר</label>
                <select v-model="form.axis" class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition">
                  <option value="FM">FM</option>
                  <option value="אחר">אחר</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1.5">תיאור פרויקט *</label>
              <textarea v-model="form.description" rows="3" placeholder="תיאור כללי של הפרויקט..."
                class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition resize-none"></textarea>
            </div>
          </div>

          <!-- Step 2: Revenue -->
          <div v-if="step === 1" class="space-y-5">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">סה"כ הכנסה צפויה (ש"ח) *</label>
                <input v-model.number="form.total_revenue" type="number" placeholder="0"
                  class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">תנאי תשלום הכנסה</label>
                <div class="flex gap-2">
                  <select v-model="form.payment_terms_revenue.type" class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition">
                    <option value="שוטף">שוטף</option>
                    <option value="שוטף+30">שוטף+30</option>
                    <option value="שוטף+60">שוטף+60</option>
                    <option value="שוטף+90">שוטף+90</option>
                  </select>
                  <input v-model="form.payment_terms_revenue.notes" type="text" placeholder="הערות"
                    class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition" />
                </div>
              </div>
            </div>

            <!-- Revenue forecast table -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs font-medium text-gray-600">תחזית הכנסות — אחוז לכל חודש</label>
                <span class="text-xs font-bold" :class="forecastTotal === 100 ? 'text-lime-600' : 'text-orange-500'">
                  סה"כ: {{ forecastTotal }}%
                </span>
              </div>
              <div class="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                <table class="w-full text-xs">
                  <thead>
                    <tr class="bg-gray-100/50">
                      <th v-for="m in 12" :key="m" class="px-1 py-2 text-center font-medium text-gray-500 w-[8.33%]">{{ m }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td v-for="m in 12" :key="m" class="px-1 py-1.5 text-center">
                        <input v-model.number="form.revenue_forecast[m]" @input="clampForecast(m)" type="number" min="0" max="100" placeholder="0"
                          class="w-full bg-white border border-gray-200 rounded-lg px-1 py-1.5 text-center text-xs focus:outline-none focus:ring-1 focus:ring-lime-300 transition" />
                      </td>
                    </tr>
                    <tr class="bg-lime-50/50">
                      <td v-for="m in 12" :key="m" class="px-1 py-1.5 text-center text-[10px] font-medium text-gray-500">
                        {{ form.total_revenue && form.revenue_forecast[m] ? Math.round(form.total_revenue * form.revenue_forecast[m] / 100).toLocaleString('he-IL') : '-' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Step 3: Expenses -->
          <div v-if="step === 2" class="space-y-5">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">סה"כ תקציב הוצאות (ש"ח) *</label>
                <input v-model.number="form.total_budget" type="number" placeholder="0"
                  class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1.5">תנאי תשלום הוצאות</label>
                <div class="flex gap-2">
                  <select v-model="form.payment_terms_expense.type" class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition">
                    <option value="שוטף">שוטף</option>
                    <option value="שוטף+30">שוטף+30</option>
                    <option value="שוטף+60">שוטף+60</option>
                    <option value="שוטף+90">שוטף+90</option>
                  </select>
                  <input v-model="form.payment_terms_expense.notes" type="text" placeholder="הערות"
                    class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 transition" />
                </div>
              </div>
            </div>

            <!-- Expense lines -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs font-medium text-gray-600">שורות הוצאה</label>
                <span class="text-xs text-gray-400">סה"כ חודשי: {{ expenseMonthlyTotal.toLocaleString('he-IL') }} ש"ח</span>
              </div>

              <div class="space-y-2">
                <div v-for="(line, i) in form.expense_lines" :key="i"
                  class="bg-gray-50 rounded-xl border border-gray-200 p-3">
                  <div class="flex items-start gap-3">
                    <div class="flex-1 grid grid-cols-5 gap-2">
                      <select v-model="line.category" class="bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-lime-300">
                        <option value="תשלום לספקים">תשלום לספקים</option>
                        <option value="העמסות שכר">העמסות שכר</option>
                        <option value="ניקיון">ניקיון</option>
                        <option value="חומרים">חומרים</option>
                        <option value="אחר">אחר</option>
                      </select>
                      <input v-model="line.name" type="text" placeholder="פירוט"
                        class="bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-lime-300" />
                      <input v-model.number="line.monthly_amount" type="number" placeholder="סכום חודשי"
                        class="bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-lime-300" />
                      <select v-model.number="line.start_month" class="bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-lime-300">
                        <option v-for="m in 12" :key="m" :value="m">מ-{{ m }}</option>
                      </select>
                      <select v-model.number="line.end_month" class="bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-lime-300">
                        <option v-for="m in 12" :key="m" :value="m">עד-{{ m }}</option>
                      </select>
                    </div>
                    <button @click="form.expense_lines.splice(i, 1)"
                      class="p-1.5 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition mt-0.5">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                  </div>
                </div>
              </div>

              <button @click="addExpenseLine"
                class="mt-3 w-full py-2.5 border-2 border-dashed border-lime-300 rounded-xl text-sm text-lime-600 font-medium hover:bg-lime-50 transition flex items-center justify-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                הוסף שורת הוצאה
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-8 py-4 border-t border-gray-100 flex items-center justify-between">
          <button v-if="step > 0" @click="step--"
            class="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 transition flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
            חזרה
          </button>
          <div v-else></div>

          <div class="flex items-center gap-3">
            <div v-if="error" class="text-red-500 text-xs">{{ error }}</div>
            <button v-if="step < steps.length - 1" @click="nextStep"
              class="px-5 py-2.5 bg-lime-500 text-white text-sm font-medium rounded-xl hover:bg-lime-600 transition flex items-center gap-1">
              הבא
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
            </button>
            <button v-else @click="save" :disabled="saving"
              class="px-6 py-2.5 bg-lime-500 text-white text-sm font-medium rounded-xl hover:bg-lime-600 disabled:opacity-50 transition flex items-center gap-2">
              <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
              {{ saving ? 'שומר...' : 'שמור פרויקט' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { getProjectForm, saveProjectForm } from '../services/api'

const props = defineProps({ show: Boolean, project: String })
const emit = defineEmits(['close', 'saved'])

const steps = ['פרטי פרויקט', 'הכנסות', 'הוצאות']
const step = ref(0)
const saving = ref(false)
const error = ref(null)

const defaultForm = () => ({
  priority_id: '',
  start_date: '',
  description: '',
  manager: '',
  client: '',
  area: 'מסחרי פרטי',
  axis: 'FM',
  payment_terms_revenue: { type: 'שוטף+60', notes: '' },
  payment_terms_expense: { type: 'שוטף+30', notes: '' },
  total_revenue: null,
  revenue_forecast: Object.fromEntries(Array.from({ length: 12 }, (_, i) => [i + 1, 0])),
  total_budget: null,
  expense_lines: [],
})

const form = reactive(defaultForm())

const forecastTotal = computed(() => {
  return Object.values(form.revenue_forecast).reduce((a, v) => a + (Number(v) || 0), 0)
})

const expenseMonthlyTotal = computed(() => {
  return form.expense_lines.reduce((a, l) => a + (Number(l.monthly_amount) || 0), 0)
})

function addExpenseLine() {
  form.expense_lines.push({ category: 'תשלום לספקים', name: '', monthly_amount: null, start_month: 1, end_month: 12 })
}

function nextStep() {
  error.value = null
  if (step.value === 0) {
    if (!form.priority_id) { error.value = 'מספר Priority הוא שדה חובה'; return }
    if (!form.start_date) { error.value = 'תאריך התחלה הוא שדה חובה'; return }
    if (!form.manager) { error.value = 'שם מנהל פרויקט הוא שדה חובה'; return }
    if (!form.client) { error.value = 'שם המזמין הוא שדה חובה'; return }
    if (!form.description) { error.value = 'תיאור פרויקט הוא שדה חובה'; return }
  }
  if (step.value === 1) {
    if (!form.total_revenue || form.total_revenue <= 0) { error.value = 'יש להזין סה"כ הכנסה צפויה'; return }
    if (forecastTotal.value > 100) { error.value = 'סה"כ אחוזי תחזית לא יכול לעלות על 100%'; return }
    if (forecastTotal.value === 0) { error.value = 'יש להזין תחזית הכנסות לפחות לחודש אחד'; return }
  }
  step.value++
}

function clampForecast(month) {
  const current = Number(form.revenue_forecast[month]) || 0
  const othersTotal = Object.entries(form.revenue_forecast)
    .filter(([k]) => Number(k) !== month)
    .reduce((a, [, v]) => a + (Number(v) || 0), 0)
  const max = 100 - othersTotal
  if (current > max) form.revenue_forecast[month] = Math.max(0, max)
  if (current < 0) form.revenue_forecast[month] = 0
}

async function save() {
  error.value = null
  if (!form.total_budget && form.total_budget !== 0) { error.value = 'יש להזין סה"כ תקציב הוצאות'; return }
  if (form.expense_lines.length === 0) { error.value = 'יש להוסיף לפחות שורת הוצאה אחת'; return }
  for (const line of form.expense_lines) {
    if (!line.name || !line.monthly_amount) { error.value = 'יש למלא את כל שדות שורות ההוצאה'; return }
  }
  saving.value = true
  try {
    await saveProjectForm(props.project, { ...form })
    emit('saved')
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

watch(() => props.show, async (val) => {
  if (val) {
    step.value = 0
    error.value = null
    Object.assign(form, defaultForm())
    try {
      const data = await getProjectForm(props.project)
      if (data) {
        Object.keys(data).forEach(k => {
          if (k in form) {
            if (typeof form[k] === 'object' && !Array.isArray(form[k]) && form[k] !== null) {
              Object.assign(form[k], data[k])
            } else {
              form[k] = data[k]
            }
          }
        })
      }
    } catch {}
  }
})
</script>
