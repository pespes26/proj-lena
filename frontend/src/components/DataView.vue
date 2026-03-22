<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-gray-800">ניהול נתונים</h2>
        <p class="text-sm text-gray-400 mt-1">העלאת קבצים וניהול מקורות מידע</p>
      </div>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm">{{ error }}</div>
    <div v-if="success" class="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl mb-6 text-sm flex items-center gap-2">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
      {{ success }}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Upload card (2 cols) -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Upload zone -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="font-semibold text-gray-700">העלאת קובץ Excel</h3>
          </div>
          <div class="p-6">
            <div
              @dragover.prevent="dragActive = true"
              @dragleave.prevent="dragActive = false"
              @drop.prevent="onDrop"
              @click="$refs.fileInput.click()"
              :class="[
                'border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200',
                dragActive ? 'border-emerald-400 bg-emerald-50' : 'border-gray-200 hover:border-emerald-300 hover:bg-gray-50'
              ]"
            >
              <div class="w-16 h-16 mx-auto mb-4 bg-emerald-50 rounded-2xl flex items-center justify-center">
                <svg class="w-8 h-8 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
                </svg>
              </div>
              <p class="text-sm font-medium text-gray-700 mb-1">גרור קובץ לכאן או לחץ לבחירה</p>
              <p class="text-xs text-gray-400">קובץ Excel בלבד (.xlsx)</p>
              <input ref="fileInput" type="file" accept=".xlsx,.xls" class="hidden" @change="onFileSelect" />
            </div>

            <!-- Selected file preview -->
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
                <button @click="selectedFile = null"
                  class="p-2 rounded-lg text-gray-400 hover:bg-gray-200 hover:text-gray-600 transition">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
                <button @click="upload" :disabled="uploading"
                  class="px-4 py-2 bg-emerald-700 text-white text-sm font-medium rounded-xl hover:bg-emerald-800 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2">
                  <svg v-if="uploading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                  <span>{{ uploading ? 'מעלה...' : 'העלה קובץ' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Backups -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h3 class="font-semibold text-gray-700">גיבויים</h3>
          </div>
          <div v-if="backups.length === 0" class="p-8 text-center text-gray-400 text-sm">אין גיבויים עדיין</div>
          <div v-else class="divide-y divide-gray-50">
            <div v-for="b in backups" :key="b.filename" class="px-6 py-3 flex items-center justify-between hover:bg-gray-50/50 transition">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                  <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8"/>
                  </svg>
                </div>
                <div>
                  <div class="text-sm text-gray-700">{{ b.filename }}</div>
                  <div class="text-xs text-gray-400">{{ formatDate(b.modified) }} · {{ b.size_kb }} KB</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Status card (1 col) -->
      <div class="space-y-6">
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 class="font-semibold text-gray-700 mb-4">מצב נוכחי</h3>
          <div v-if="!status" class="text-center text-gray-400 text-sm py-4">טוען...</div>
          <template v-else-if="status.exists">
            <div class="space-y-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
                  <svg class="w-5 h-5 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                </div>
                <div>
                  <div class="text-sm font-medium text-gray-700">קובץ פעיל</div>
                  <div class="text-xs text-gray-400">{{ status.filename }}</div>
                </div>
              </div>

              <div class="bg-gray-50 rounded-xl p-4 space-y-3">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">גודל</span>
                  <span class="font-medium text-gray-700">{{ status.size_kb }} KB</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">עדכון אחרון</span>
                  <span class="font-medium text-gray-700">{{ formatDate(status.modified) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">פרויקטים</span>
                  <span class="font-medium text-gray-700">{{ status.project_count }}</span>
                </div>
              </div>

              <div>
                <div class="text-xs text-gray-400 mb-2">פרויקטים בקובץ:</div>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="p in status.projects" :key="p"
                    class="bg-emerald-50 text-emerald-800 text-[11px] font-medium px-2.5 py-1 rounded-lg">
                    {{ p }}
                  </span>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="text-center py-4">
            <div class="w-12 h-12 mx-auto mb-3 bg-orange-50 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>
            </div>
            <div class="text-sm font-medium text-gray-700">לא נמצא קובץ נתונים</div>
            <div class="text-xs text-gray-400 mt-1">העלה קובץ Excel כדי להתחיל</div>
          </div>
        </div>

        <!-- Quick info -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 class="font-semibold text-gray-700 mb-3">מבנה נדרש</h3>
          <div class="space-y-2 text-xs text-gray-500">
            <div class="flex items-start gap-2">
              <span class="text-emerald-700 mt-0.5">&#x25CF;</span>
              <span>לשונית <strong>"פרוייקטים מנרב IFM"</strong> — נתוני P&L לכל פרויקט לפי חודש</span>
            </div>
            <div class="flex items-start gap-2">
              <span class="text-emerald-700 mt-0.5">&#x25CF;</span>
              <span>לשונית <strong>"ריכוז"</strong> — תזרים מזומנים מצטבר</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDataStatus, uploadData, getBackups } from '../services/api'

const status = ref(null)
const backups = ref([])
const selectedFile = ref(null)
const uploading = ref(false)
const error = ref(null)
const success = ref(null)
const dragActive = ref(false)

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleDateString('he-IL') + ' ' + d.toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
}

function onFileSelect(e) {
  const file = e.target.files[0]
  if (file) selectedFile.value = file
}

function onDrop(e) {
  dragActive.value = false
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    selectedFile.value = file
  } else {
    error.value = 'יש להעלות קובץ Excel בלבד (.xlsx)'
  }
}

async function upload() {
  if (!selectedFile.value) return
  uploading.value = true
  error.value = null
  success.value = null
  try {
    const res = await uploadData(selectedFile.value)
    success.value = `${res.message} (${res.size_kb} KB)`
    selectedFile.value = null
    await loadStatus()
    await loadBackups()
  } catch (e) {
    error.value = e.message
  } finally {
    uploading.value = false
  }
}

async function loadStatus() {
  try { status.value = await getDataStatus() } catch {}
}

async function loadBackups() {
  try { backups.value = await getBackups() } catch {}
}

onMounted(() => {
  loadStatus()
  loadBackups()
})
</script>
