<template>
  <Teleport to="body">
    <div v-if="show" class="ui-modal-layer" dir="rtl">
      <!-- Backdrop -->
      <div class="ui-modal-backdrop" @click="$emit('close')"></div>

      <!-- Modal -->
      <div class="ui-modal-card ed-fade-up" style="max-width: 36rem;">
        <!-- Header -->
        <header class="px-7 pt-6 pb-4">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="ed-eyebrow mb-1">דיווח נקודתי</div>
              <h3 class="font-sans font-semibold text-ink leading-none" style="font-size: clamp(1.75rem, 3vw, 2.25rem);">
                הוסף דיווח
              </h3>
              <p class="font-sans text-ink-muted mt-1.5 text-sm">{{ project }}</p>
            </div>
            <button @click="$emit('close')" class="p-2 -m-2 rounded-lg text-ink-muted hover:text-accent hover:bg-surface-muted transition-colors" aria-label="סגור">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="square" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <hr class="ed-rule mt-4" />
        </header>

        <!-- Form body -->
        <div class="flex-1 overflow-y-auto px-7 py-5 space-y-6">
          <!-- Type segmented list -->
          <div>
            <label class="ed-label">סוג דיווח</label>
            <div class="flex flex-wrap gap-x-6 gap-y-2 border-t border-rule pt-3">
              <button
                v-for="t in types"
                :key="t.id"
                type="button"
                @click="form.type = t.id"
                class="ed-link text-base"
                :class="{ 'is-active': form.type === t.id }"
              >
                {{ t.label }}
              </button>
            </div>
          </div>

          <!-- Month -->
          <div>
            <label class="ed-label">חודש (אופציונלי)</label>
            <select v-model="form.month" class="ed-select">
              <option :value="null">כללי — לא קשור לחודש ספציפי</option>
              <option v-for="m in 12" :key="m" :value="m">חודש {{ m }}</option>
            </select>
          </div>

          <!-- Title -->
          <div>
            <label class="ed-label">כותרת *</label>
            <input
              v-model="form.title"
              type="text"
              placeholder="למשל: הוצאה חריגה על תיקון…"
              maxlength="100"
              @blur="validateTitle"
              class="ed-input"
              :class="{ 'is-error': fe.title }"
            />
            <div class="flex justify-between mt-1 items-center">
              <span v-if="fe.title" class="font-sans text-xs ed-tone-negative">{{ fe.title }}</span>
              <span v-else></span>
              <span class="ed-eyebrow ed-num" style="font-size: 0.625rem;"><bdi>{{ form.title.length }}/100</bdi></span>
            </div>
          </div>

          <!-- Amount -->
          <div v-if="form.type === 'expense' || form.type === 'revenue'">
            <label class="ed-label">סכום (₪) *</label>
            <input
              v-model.number="form.amount"
              type="number"
              placeholder="0"
              min="1"
              @blur="validateAmount"
              class="ed-input ed-num"
              :class="{ 'is-error': fe.amount }"
            />
            <span v-if="fe.amount" class="font-sans text-xs ed-tone-negative mt-1 block">{{ fe.amount }}</span>
          </div>

          <!-- Description -->
          <div>
            <label class="ed-label">פירוט</label>
            <textarea
              v-model="form.description"
              rows="3"
              placeholder="תיאור מפורט…"
              maxlength="500"
              class="ed-input"
              style="resize: none;"
            ></textarea>
            <div class="flex justify-end mt-1">
              <span
                class="ed-eyebrow ed-num"
                :class="form.description.length > 480 ? 'ed-tone-warning' : ''"
                style="font-size: 0.625rem;"
              >
                <bdi>{{ form.description.length }}/500</bdi>
              </span>
            </div>
          </div>

          <!-- Error -->
          <p v-if="error" class="font-sans text-sm ed-tone-negative">{{ error }}</p>
        </div>

        <!-- Footer -->
        <footer class="px-7 py-5 border-t border-rule-strong flex items-center justify-between gap-4">
          <button @click="$emit('close')" class="ed-link text-sm">ביטול</button>
          <button
            @click="submit"
            :disabled="!canSubmit || submitting"
            class="ed-btn ed-btn-primary"
          >
            {{ submitting ? 'שומר…' : 'שמור דיווח' }} →
          </button>
        </footer>
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
  { id: 'expense', label: 'הוצאה' },
  { id: 'revenue', label: 'הכנסה' },
  { id: 'issue', label: 'בעיה' },
  { id: 'note', label: 'הערה' },
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
