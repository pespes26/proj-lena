<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-gray-800">נוכחות עובדים</h2>
        <p class="text-sm text-gray-400 mt-1">העלאת קובץ נוכחות ופיצול לפי פרויקט</p>
      </div>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm">{{ error }}</div>
    <div v-if="success" class="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl mb-6 text-sm flex items-center gap-2">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
      {{ success }}
    </div>

    <!-- Upload section -->
    <div v-if="!data" class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 class="font-semibold text-gray-700 mb-4">העלאת קובץ נוכחות</h3>
        <div
          @dragover.prevent="dragActive = true" @dragleave.prevent="dragActive = false" @drop.prevent="onDrop"
          @click="$refs.fileInput.click()"
          :class="['border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all',
            dragActive ? 'border-emerald-400 bg-emerald-50' : 'border-gray-200 hover:border-emerald-300 hover:bg-gray-50']">
          <div class="w-14 h-14 mx-auto mb-3 bg-emerald-50 rounded-2xl flex items-center justify-center">
            <svg class="w-7 h-7 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <p class="text-sm font-medium text-gray-700 mb-1">גרור קובץ נוכחות לכאן או לחץ</p>
          <p class="text-xs text-gray-400">Excel עם עמודות: שם עובד, תאריך, כניסה, יציאה, מספר פרויקט</p>
          <input ref="fileInput" type="file" accept=".xlsx,.xls" class="hidden" @change="onFileSelect" />
        </div>

        <div v-if="selectedFile" class="mt-4 bg-gray-50 rounded-xl p-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <div>
              <div class="text-sm font-medium text-gray-700">{{ selectedFile.name }}</div>
              <div class="text-xs text-gray-400">{{ (selectedFile.size / 1024).toFixed(1) }} KB</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button @click="selectedFile = null" class="p-2 rounded-lg text-gray-400 hover:bg-gray-200 transition">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
            <button @click="upload" :disabled="uploading"
              class="px-4 py-2 bg-emerald-700 text-white text-sm font-medium rounded-xl hover:bg-emerald-800 disabled:opacity-50 transition flex items-center gap-2">
              <svg v-if="uploading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
              {{ uploading ? 'מעבד...' : 'העלה ועבד' }}
            </button>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 class="font-semibold text-gray-700 mb-3">הגדרות</h3>
        <div class="mb-4">
          <label class="block text-xs font-medium text-gray-600 mb-1.5">תעריף שעתי (ש"ח)</label>
          <input v-model.number="hourlyRate" type="number" min="1" max="1000" step="1"
            @blur="hourlyRate = Math.max(1, Math.min(1000, Math.round(hourlyRate || 1)))"
            :class="['w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition',
              hourlyRate < 1 || hourlyRate > 1000 ? 'border-red-400! bg-red-50!' : '']" />
          <span v-if="hourlyRate < 1 || hourlyRate > 1000" class="text-red-500 text-[10px] mt-0.5 block">תעריף חייב להיות בין 1 ל-1000 ש"ח</span>
        </div>
        <div class="bg-gray-50 rounded-xl p-4 space-y-2 text-xs text-gray-500">
          <div class="flex items-start gap-2"><span class="text-emerald-700 mt-0.5">&#x25CF;</span><span>שם עובד / שם</span></div>
          <div class="flex items-start gap-2"><span class="text-emerald-700 mt-0.5">&#x25CF;</span><span>תאריך</span></div>
          <div class="flex items-start gap-2"><span class="text-emerald-700 mt-0.5">&#x25CF;</span><span>שעת כניסה / שעת יציאה</span></div>
          <div class="flex items-start gap-2"><span class="text-emerald-700 mt-0.5">&#x25CF;</span><span>מספר פרויקט / project</span></div>
          <div class="flex items-start gap-2"><span class="text-emerald-700 mt-0.5">&#x25CF;</span><span>סה"כ שעות (אופציונלי)</span></div>
        </div>
      </div>
    </div>

    <!-- Results -->
    <template v-if="data">
      <!-- Re-upload button -->
      <div class="flex items-center justify-between mb-6">
        <div class="text-xs text-gray-400">קובץ: {{ data.filename }} · {{ data.record_count }} רשומות · תעריף: {{ data.hourly_rate }} ש"ח/שעה</div>
        <button @click="data = null; selectedFile = null"
          class="px-3 py-1.5 text-xs text-gray-500 border border-gray-200 rounded-lg hover:bg-gray-50 transition">העלה קובץ חדש</button>
      </div>

      <!-- KPI Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="text-xs text-gray-400 mb-2">סה"כ שעות</div>
          <div class="text-2xl font-bold text-gray-800">{{ totalHours.toLocaleString('he-IL') }}</div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="text-xs text-gray-400 mb-2">עובדים</div>
          <div class="text-2xl font-bold text-gray-800">{{ Object.keys(data.by_employee).length }}</div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="text-xs text-gray-400 mb-2">פרויקטים</div>
          <div class="text-2xl font-bold text-gray-800">{{ Object.keys(data.by_project).length }}</div>
        </div>
        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div class="text-xs text-gray-400 mb-2">עלות העמסה כוללת</div>
          <div class="text-2xl font-bold text-emerald-700">{{ totalCost.toLocaleString('he-IL') }} &#8362;</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-700 mb-4">שעות לפי פרויקט</h3>
          <Bar :data="projectChartData" :options="barOptions" style="max-height: 280px;" />
        </div>
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-700 mb-4">חלוקת שעות לפי עובד</h3>
          <Doughnut :data="employeeChartData" :options="doughnutOptions" style="max-height: 280px;" />
        </div>
      </div>

      <!-- Tables -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="font-semibold text-gray-700">פיצול לפי פרויקט</h3>
          </div>
          <table class="w-full text-sm">
            <thead><tr class="bg-gray-50/50">
              <th class="px-4 py-3 text-right font-medium text-gray-500">מספר פרויקט</th>
              <th class="px-4 py-3 text-right font-medium text-gray-500">שעות</th>
              <th class="px-4 py-3 text-right font-medium text-gray-500">עובדים</th>
              <th class="px-4 py-3 text-right font-medium text-gray-500">עלות העמסה</th>
            </tr></thead>
            <tbody>
              <tr v-for="(info, proj) in data.by_project" :key="proj" class="border-t border-gray-50 hover:bg-gray-50/50 transition">
                <td class="px-4 py-3 font-mono font-medium text-emerald-700">{{ proj }}</td>
                <td class="px-4 py-3 text-gray-600">{{ info.total_hours.toLocaleString('he-IL') }}</td>
                <td class="px-4 py-3 text-gray-600">{{ info.employees }}</td>
                <td class="px-4 py-3 font-semibold text-gray-800">{{ info.cost.toLocaleString('he-IL') }} &#8362;</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="font-semibold text-gray-700">פירוט לפי עובד</h3>
          </div>
          <div class="overflow-y-auto max-h-[400px]">
            <table class="w-full text-sm">
              <thead class="sticky top-0 bg-gray-50"><tr>
                <th class="px-4 py-3 text-right font-medium text-gray-500">עובד</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">סה"כ שעות</th>
                <th class="px-4 py-3 text-right font-medium text-gray-500">פרויקטים</th>
              </tr></thead>
              <tbody>
                <tr v-for="(info, emp) in data.by_employee" :key="emp" class="border-t border-gray-50 hover:bg-gray-50/50 transition">
                  <td class="px-4 py-3 font-medium text-gray-700">{{ emp }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ info.total_hours }}</td>
                  <td class="px-4 py-3">
                    <div class="flex flex-wrap gap-1">
                      <span v-for="(hrs, p) in info.projects" :key="p"
                        class="text-[10px] bg-emerald-50 text-emerald-700 font-mono px-1.5 py-0.5 rounded">
                        {{ p }}: {{ hrs }}h
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAttendance, uploadAttendance } from '../services/api'
import { Bar, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const data = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const error = ref(null)
const success = ref(null)
const dragActive = ref(false)
const hourlyRate = ref(50)

const totalHours = computed(() => data.value ? Object.values(data.value.by_project).reduce((a, p) => a + p.total_hours, 0) : 0)
const totalCost = computed(() => data.value ? Object.values(data.value.by_project).reduce((a, p) => a + p.cost, 0) : 0)

const colors = ['#0D9488', '#22c55e', '#06b6d4', '#8b5cf6', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6']

const projectChartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const projs = Object.keys(data.value.by_project)
  return {
    labels: projs,
    datasets: [{
      label: 'שעות',
      data: projs.map(p => data.value.by_project[p].total_hours),
      backgroundColor: projs.map((_, i) => colors[i % colors.length] + 'cc'),
      borderRadius: 6,
    }],
  }
})

const employeeChartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const emps = Object.keys(data.value.by_employee)
  return {
    labels: emps,
    datasets: [{
      data: emps.map(e => data.value.by_employee[e].total_hours),
      backgroundColor: emps.map((_, i) => colors[i % colors.length] + 'cc'),
      borderWidth: 0,
      cutout: '65%',
    }],
  }
})

const barOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { rtl: true, cornerRadius: 12, callbacks: { label: ctx => ` ${ctx.raw} שעות` } } }, scales: { x: { grid: { display: false } }, y: { grid: { color: '#f3f4f6' }, ticks: { callback: v => v.toLocaleString('he-IL') } } } }
const doughnutOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', rtl: true, labels: { font: { size: 10 }, padding: 8 } }, tooltip: { rtl: true, cornerRadius: 12, callbacks: { label: ctx => ` ${ctx.label}: ${ctx.raw} שעות` } } } }

function onFileSelect(e) { if (e.target.files[0]) selectedFile.value = e.target.files[0] }
function onDrop(e) {
  dragActive.value = false
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) selectedFile.value = file
  else error.value = 'יש להעלות קובץ Excel בלבד'
}

async function upload() {
  if (!selectedFile.value) return
  uploading.value = true; error.value = null; success.value = null
  try {
    const res = await uploadAttendance(selectedFile.value, hourlyRate.value)
    success.value = res.message
    data.value = res.data
    selectedFile.value = null
  } catch (e) { error.value = e.message }
  finally { uploading.value = false }
}

onMounted(async () => {
  try { data.value = await getAttendance() } catch {}
})
</script>
