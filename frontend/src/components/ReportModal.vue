<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center" dir="rtl">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>

      <!-- Modal -->
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
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
            <div class="grid grid-cols-4 gap-2">
              <button v-for="t in types" :key="t.id" @click="form.type = t.id"
                :class="[
                  'px-3 py-2.5 rounded-xl text-xs font-medium border transition-all text-center',
                  form.type === t.id
                    ? 'border-lime-400 bg-lime-50 text-lime-700'
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
              class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 focus:border-lime-400 transition">
              <option :value="null">כללי — לא קשור לחודש ספציפי</option>
              <option v-for="m in 12" :key="m" :value="m">חודש {{ m }}</option>
            </select>
          </div>

          <!-- Title -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">כותרת</label>
            <input v-model="form.title" type="text" placeholder="למשל: הוצאה חריגה על תיקון..."
              class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 focus:border-lime-400 transition" />
          </div>

          <!-- Amount (for expense/revenue) -->
          <div v-if="form.type === 'expense' || form.type === 'revenue'">
            <label class="block text-xs font-medium text-gray-600 mb-1.5">סכום (ש"ח)</label>
            <input v-model.number="form.amount" type="number" placeholder="0"
              class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 focus:border-lime-400 transition" />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">פירוט</label>
            <textarea v-model="form.description" rows="3" placeholder="תיאור מפורט..."
              class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-lime-300 focus:border-lime-400 transition resize-none"></textarea>
          </div>

          <!-- Error -->
          <div v-if="error" class="bg-red-50 text-red-600 text-xs px-3 py-2 rounded-lg">{{ error }}</div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
          <button @click="$emit('close')"
            class="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 transition">ביטול</button>
          <button @click="submit" :disabled="!form.title || submitting"
            class="px-6 py-2.5 bg-lime-500 text-white text-sm font-medium rounded-xl hover:bg-lime-600 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2">
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
import { ref, reactive, watch } from 'vue'
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

const submitting = ref(false)
const error = ref(null)

watch(() => props.show, (val) => {
  if (val) {
    form.type = 'expense'
    form.month = null
    form.title = ''
    form.amount = null
    form.description = ''
    error.value = null
  }
})

async function submit() {
  if (!form.title) return
  submitting.value = true
  error.value = null
  try {
    await createReport({
      project: props.project,
      month: form.month,
      type: form.type,
      title: form.title,
      amount: form.amount,
      description: form.description,
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
