<template>
  <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">טוען פרטי פרויקט...</div>
  <div v-else-if="!formData" class="text-center py-12">
    <div class="text-gray-400 text-sm mb-3">לא נמצאו נתוני טופס לפרויקט זה</div>
    <button @click="$emit('edit')" class="px-4 py-2 bg-emerald-800 text-white text-sm font-medium rounded-lg hover:bg-emerald-900 transition">
      צור טופס פרויקט
    </button>
  </div>
  <div v-else class="space-y-6">
    <!-- Header with edit + export buttons -->
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-bold text-gray-800 print-title">פרטי פרויקט — {{ project }}</h3>
      <div class="flex items-center gap-2 no-print">
        <button @click="exportPDF" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 border border-gray-200 rounded-lg hover:bg-gray-50 transition flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          ייצוא PDF
        </button>
        <button @click="$emit('edit')" class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 border border-gray-200 rounded-lg hover:bg-gray-50 transition flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
          ערוך טופס
        </button>
      </div>
    </div>

    <!-- Project Info -->
    <div class="bg-white rounded-xl border border-gray-100 p-6">
      <h4 class="text-sm font-bold text-gray-700 mb-4">מידע כללי</h4>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-x-8 gap-y-4">
        <div v-if="formData.project_name">
          <div class="text-xs text-gray-400 mb-1">שם פרויקט</div>
          <div class="text-sm font-medium text-gray-800">{{ formData.project_name }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-400 mb-1">מספר Priority</div>
          <div class="text-sm font-medium text-gray-800 font-mono">{{ formData.priority_id || '-' }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-400 mb-1">תאריך התחלה</div>
          <div class="text-sm font-medium text-gray-800">{{ formData.start_date || '-' }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-400 mb-1">מנהל פרויקט</div>
          <div class="text-sm font-medium text-gray-800">{{ formData.manager || '-' }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-400 mb-1">מזמין</div>
          <div class="text-sm font-medium text-gray-800">{{ formData.client || '-' }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-400 mb-1">תחום</div>
          <div class="text-sm font-medium text-gray-800">{{ formData.area || '-' }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-400 mb-1">ציר</div>
          <div class="text-sm font-medium text-gray-800">{{ formData.axis || '-' }}</div>
        </div>
        <div>
          <div class="text-xs text-gray-400 mb-1">סטטוס</div>
          <div class="text-sm font-medium text-gray-800">{{ statusLabel }}</div>
        </div>
      </div>
      <div v-if="formData.description" class="mt-4 pt-4 border-t border-gray-100">
        <div class="text-xs text-gray-400 mb-1">תיאור</div>
        <div class="text-sm text-gray-600">{{ formData.description }}</div>
      </div>
    </div>

    <!-- Revenue -->
    <div class="bg-white rounded-xl border border-gray-100 p-6">
      <h4 class="text-sm font-bold text-gray-700 mb-4">הכנסות</h4>
      <div class="grid grid-cols-2 gap-x-8 gap-y-3 mb-5">
        <div>
          <div class="text-xs text-gray-400 mb-1">סך הכנסות</div>
          <div class="text-xl font-bold text-gray-800">{{ (formData.total_revenue || 0).toLocaleString('he-IL') }} ₪</div>
        </div>
      </div>

      <!-- Payment terms -->
      <div v-if="formData.revenue_payment_terms?.length" class="mb-5">
        <div class="text-xs text-gray-400 mb-2">תנאי תשלום</div>
        <div class="flex flex-wrap gap-2">
          <div v-for="(term, i) in formData.revenue_payment_terms" :key="i"
            class="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg border border-gray-100 text-xs">
            <span class="font-medium text-gray-700">{{ term.type }}</span>
            <span class="text-gray-400">{{ term.percent }}%</span>
            <span v-if="formData.total_revenue" class="text-gray-400">
              · {{ Math.round(formData.total_revenue * term.percent / 100).toLocaleString('he-IL') }} ₪
            </span>
          </div>
        </div>
      </div>

      <!-- Revenue forecast -->
      <div>
        <div class="text-xs text-gray-400 mb-2">תחזית הכנסות חודשית</div>
        <div class="bg-gray-50 rounded-xl p-4 overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr>
                <th v-for="m in 12" :key="m" class="px-2 py-1.5 text-center font-medium text-gray-500">{{ m }}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td v-for="m in 12" :key="m" class="px-2 py-1.5 text-center">
                  <span :class="[forecast(m) > 0 ? 'text-emerald-700 font-medium' : 'text-gray-300']">
                    {{ forecast(m) }}%
                  </span>
                </td>
              </tr>
              <tr v-if="formData.total_revenue">
                <td v-for="m in 12" :key="m" class="px-2 py-1 text-center text-[10px] text-gray-400">
                  {{ forecast(m) ? Math.round(formData.total_revenue * forecast(m) / 100).toLocaleString('he-IL') : '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Expenses -->
    <div class="bg-white rounded-xl border border-gray-100 p-6">
      <h4 class="text-sm font-bold text-gray-700 mb-4">הוצאות</h4>
      <div class="grid grid-cols-2 gap-x-8 gap-y-3 mb-5">
        <div>
          <div class="text-xs text-gray-400 mb-1">תקציב הוצאות</div>
          <div class="text-xl font-bold text-gray-800">{{ (formData.total_budget || 0).toLocaleString('he-IL') }} ₪</div>
        </div>
        <div>
          <div class="text-xs text-gray-400 mb-1">תנאי תשלום הוצאות</div>
          <div class="text-sm font-medium text-gray-800">{{ formData.payment_terms_expense?.type || '-' }}</div>
        </div>
      </div>

      <!-- Subcontractors -->
      <div v-if="formData.subcontractors?.length" class="mb-5">
        <div class="text-xs text-gray-400 mb-2 flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          קבלני משנה ({{ formData.subcontractors.length }})
        </div>
        <div class="bg-gray-50 rounded-lg overflow-hidden">
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="text-right px-3 py-2 font-medium text-gray-500">שם</th>
                <th class="text-right px-3 py-2 font-medium text-gray-500">סכום חודשי</th>
                <th class="text-right px-3 py-2 font-medium text-gray-500">תנאי תשלום</th>
                <th class="text-right px-3 py-2 font-medium text-gray-500">תקופה</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(sub, i) in formData.subcontractors" :key="i" class="border-b border-gray-100">
                <td class="px-3 py-2 font-medium text-gray-700">{{ sub.name }}</td>
                <td class="px-3 py-2 text-gray-600">{{ (sub.monthly_amount || 0).toLocaleString('he-IL') }} ₪</td>
                <td class="px-3 py-2 text-gray-600">{{ sub.payment_terms || '-' }}</td>
                <td class="px-3 py-2 text-gray-400">{{ sub.start_date || '-' }} — {{ sub.end_date || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Expense categories -->
      <template v-for="cat in expenseCategories" :key="cat.key">
        <div v-if="formData['expense_lines_' + cat.key]?.length" class="mb-5">
          <div class="text-xs text-gray-400 mb-2 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full" :class="cat.color"></span>
            {{ cat.label }} ({{ formData['expense_lines_' + cat.key].length }})
          </div>
          <div class="bg-gray-50 rounded-lg overflow-hidden">
            <table class="w-full text-xs">
              <thead>
                <tr class="border-b border-gray-200">
                  <th class="text-right px-3 py-2 font-medium text-gray-500">שם</th>
                  <th class="text-right px-3 py-2 font-medium text-gray-500">סכום חודשי</th>
                  <th class="text-right px-3 py-2 font-medium text-gray-500">תקופה</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(line, i) in formData['expense_lines_' + cat.key]" :key="i" class="border-b border-gray-100">
                  <td class="px-3 py-2 font-medium text-gray-700">{{ line.name }}</td>
                  <td class="px-3 py-2 text-gray-600">{{ (line.monthly_amount || 0).toLocaleString('he-IL') }} ₪</td>
                  <td class="px-3 py-2 text-gray-400">
                    <template v-if="line.start_date">{{ line.start_date }} — {{ line.end_date || '-' }}</template>
                    <template v-else-if="line.start_month">חודש {{ line.start_month }} — {{ line.end_month }}</template>
                    <template v-else>-</template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>

    <!-- Attendance summary -->
    <div v-if="formData.manpower_attendance_summary" class="bg-white rounded-xl border border-gray-100 p-6">
      <h4 class="text-sm font-bold text-gray-700 mb-4">נוכחות (מנוכחות)</h4>
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-purple-50 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ formData.manpower_attendance_summary.total_hours?.toFixed(1) }}</div>
          <div class="text-xs text-gray-500 mt-1">שעות</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ formData.manpower_attendance_summary.employees }}</div>
          <div class="text-xs text-gray-500 mt-1">עובדים</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ formData.manpower_attendance_summary.total_cost?.toLocaleString('he-IL') }}</div>
          <div class="text-xs text-gray-500 mt-1">עלות ₪</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getProjectForm } from '../services/api'

const props = defineProps({
  project: { type: String, required: true }
})
defineEmits(['edit'])

const formData = ref(null)
const loading = ref(true)

const expenseCategories = [
  { key: 'manpower', label: 'כוח אדם', color: 'bg-purple-400' },
  { key: 'equipment', label: 'ציוד וכלים', color: 'bg-orange-400' },
  { key: 'insurance', label: 'ביטוחים', color: 'bg-green-400' },
  { key: 'consultants', label: 'מתכננים ויועצים', color: 'bg-yellow-400' },
  { key: 'financing', label: 'הוצאות מימון', color: 'bg-red-400' },
  { key: 'other', label: 'אחר', color: 'bg-gray-400' },
]

const statusLabel = ref('-')

function forecast(m) {
  return formData.value?.revenue_forecast?.[m] || formData.value?.revenue_forecast?.[String(m)] || 0
}

async function loadData() {
  loading.value = true
  try {
    const data = await getProjectForm(props.project)
    formData.value = data
    if (data?.status === 'active') statusLabel.value = 'פעיל'
    else if (data?.status === 'on-hold') statusLabel.value = 'מושהה'
    else if (data?.status === 'completed') statusLabel.value = 'הושלם'
    else statusLabel.value = '-'
  } catch {
    formData.value = null
  } finally {
    loading.value = false
  }
}

function exportPDF() {
  window.print()
}

onMounted(loadData)
watch(() => props.project, loadData)
</script>
