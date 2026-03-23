<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center" dir="rtl">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/40" @click="$emit('close')"></div>

      <!-- Modal -->
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-2 sm:mx-4 overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h3 class="font-bold text-gray-800">דיווח נקודתי</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ project }}</p>
          </div>
          <button @click="$emit('close')"
            class="p-2 rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <div class="px-6 py-5 space-y-4">
          <!-- Type -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-2">סוג דיווח</label>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <button v-for="t in types" :key="t.id" @click="form.type = t.id"
                :class="[
                  'px-3 py-2.5 rounded-xl text-xs font-medium border transition-all text-center',
                  form.type === t.id
                    ? 'border-emerald-400 bg-emerald-50 text-emerald-800'
                    : 'border-gray-200 bg-white text-gray-500 hover:border-gray-300'
                ]">
                <div class="text-lg mb-0.5">{{ t.icon }}</div>
                {{ t.label }}
              </button>
            </div>
          </div>

          <!-- Month -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">חודש (אופציונלי)</label>
            <select v-model="form.month"
              class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 focus:border-emerald-400 transition">
              <option :value="null">כללי — לא קשור לחודש ספציפי</option>
              <option v-for="m in 12" :key="m" :value="m">חודש {{ m }}</option>
            </select>
          </div>

          <!-- Title -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">כותרת *</label>
            <input v-model="form.title" type="text" placeholder="למשל: הוצאה חריגה על תיקון..."
              maxlength="100"
              @blur="validateTitle"
              :class="['w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 focus:border-emerald-400 transition',
                fe.title ? 'border-red-400! bg-red-50!' : '']" />
            <div class="flex justify-between mt-0.5">
              <span v-if="fe.title" class="text-red-500 text-[10px]">{{ fe.title }}</span>
              <span v-else></span>
              <span class="text-gray-400 text-[10px]">{{ form.title.length }}/100</span>
            </div>
          </div>

          <!-- Amount (for expense/revenue) -->
          <div v-if="form.type === 'expense' || form.type === 'revenue'">
            <label class="block text-xs font-medium text-gray-600 mb-1.5">סכום (ש"ח) *</label>
            <input v-model.number="form.amount" type="number" placeholder="0" min="1"
              @blur="validateAmount"
              :class="['w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 focus:border-emerald-400 transition',
                fe.amount ? 'border-red-400! bg-red-50!' : '']" />
            <span v-if="fe.amount" class="text-red-500 text-[10px] mt-0.5 block">{{ fe.amount }}</span>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">פירוט</label>
            <textarea v-model="form.description" rows="3" placeholder="תיאור מפורט..." maxlength="500"
              :class="['w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 focus:border-emerald-400 transition resize-none',
                form.description.length > 500 ? 'border-red-400! bg-red-50!' : '']"></textarea>
            <div class="flex justify-end mt-0.5">
              <span :class="['text-[10px]', form.description.length > 480 ? 'text-orange-500' : 'text-gray-400']">{{ form.description.length }}/500</span>
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="bg-red-50 text-red-600 text-xs px-3 py-2 rounded-lg">{{ error }}</div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
          <button @click="$emit('close')"
            class="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 transition">ביטול</button>
          <button @click="submit" :disabled="!canSubmit || submitting"
            class="px-6 py-2.5 bg-emerald-700 text-white text-sm font-medium rounded-xl hover:bg-emerald-800 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2">
            <svg v-if="submitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <span>{{ submitting ? 'שומר...' : 'שמור דיווח' }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { createReport } from '../services/api'

const props = defineProps({
  show: Boolean,
  project: String,
})

const emit = defineEmits(['close', 'saved'])

const types = [
  { id: 'expense', label: 'הוצאה', icon: '💸' },
  { id: 'revenue', label: 'הכנסה', icon: '💰' },
  { id: 'issue', label: 'בעיה', icon: '⚠️' },
  { id: 'note', label: 'הערה', icon: '📝' },
]

const form = reactive({
  type: 'expense',
  month: null,
  title: '',
  amount: null,
  description: '',
})

const fe = reactive({})
const submitting = ref(false)
const error = ref(null)

function validateTitle() {
  const v = form.title.trim()
  if (!v) fe.title = 'שדה חובה'
  else if (v.length < 2) fe.title = 'מינימום 2 תווים'
  else if (v.length > 100) fe.title = 'מקסימום 100 תווים'
  else fe.title = ''
}

function validateAmount() {
  if (form.type !== 'expense' && form.type !== 'revenue') { fe.amount = ''; return }
  const v = form.amount
  if (v === null || v === undefined || v === '') fe.amount = 'שדה חובה'
  else if (v <= 0) fe.amount = 'חייב להיות מספר חיובי'
  else if (v > 100000000) fe.amount = 'מקסימום 100,000,000'
  else fe.amount = ''
}

const canSubmit = computed(() => {
  if (!form.title || form.title.trim().length < 2) return false
  if ((form.type === 'expense' || form.type === 'revenue') && (!form.amount || form.amount <= 0)) return false
  return true
})

watch(() => props.show, (val) => {
  if (val) {
    form.type = 'expense'
    form.month = null
    form.title = ''
    form.amount = null
    form.description = ''
    error.value = null
    Object.keys(fe).forEach(k => delete fe[k])
  }
})

async function submit() {
  validateTitle()
  if (form.type === 'expense' || form.type === 'revenue') validateAmount()
  if (fe.title || fe.amount) { error.value = 'יש לתקן את השדות המסומנים'; return }
  if (!form.title || form.title.trim().length < 2) return
  submitting.value = true
  error.value = null
  try {
    await createReport({
      project: props.project,
      month: form.month,
      type: form.type,
      title: form.title.trim(),
      amount: form.amount,
      description: form.description.trim(),
    })
    emit('saved')
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>
