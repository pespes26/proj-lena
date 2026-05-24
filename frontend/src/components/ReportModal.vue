<template>
  <Teleport to="body">
    <div v-if="show" class="ui-modal-layer" dir="rtl">
      <!-- Backdrop -->
      <div class="ui-modal-backdrop" @click="$emit('close')"></div>

      <!-- Modal -->
      <div class="ui-modal-card animate-fade-up" style="max-width: 36rem;">
        <!-- Header -->
        <header class="px-7 pt-6 pb-4">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="ui-label mb-1">דיווח נקודתי</div>
              <h3 class="ui-display" style="color: var(--ink);">הוסף דיווח</h3>
              <p class="font-sans mt-1.5 text-sm ed-tone-muted">{{ project }}</p>
            </div>
            <button
              @click="$emit('close')"
              class="ui-icon-btn"
              type="button"
              aria-label="סגור"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </header>

        <!-- Form body -->
        <div class="flex-1 overflow-y-auto px-7 py-5 space-y-6">
          <!-- Type selector grid -->
          <fieldset class="border-0 p-0 m-0">
            <legend class="ui-form-label mb-2">סוג דיווח</legend>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <button
                v-for="t in types"
                :key="t.id"
                type="button"
                @click="form.type = t.id"
                class="ui-press font-sans font-medium text-sm flex flex-col items-center justify-center gap-2 py-3 px-2"
                :style="form.type === t.id
                  ? 'background: var(--accent-soft); border: 1px solid var(--accent); color: var(--accent); border-radius: 12px;'
                  : 'background: var(--surface); border: 1px solid var(--border); color: var(--ink-muted); border-radius: 12px;'"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.75">
                  <path v-if="t.id === 'expense'" stroke-linecap="round" stroke-linejoin="round" d="M15.75 15.75l-2.489-2.489m0 0a3.375 3.375 0 10-4.773-4.773 3.375 3.375 0 004.773 4.773zM21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path v-else-if="t.id === 'revenue'" stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path v-else-if="t.id === 'issue'" stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                  <path v-else stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                </svg>
                <span>{{ t.label }}</span>
              </button>
            </div>
          </fieldset>

          <!-- Month -->
          <div>
            <label class="ui-form-label" for="report-month">חודש (אופציונלי)</label>
            <select id="report-month" v-model="form.month" class="ui-select">
              <option :value="null">כללי — לא קשור לחודש ספציפי</option>
              <option v-for="m in 12" :key="m" :value="m">חודש {{ m }}</option>
            </select>
          </div>

          <!-- Title -->
          <div>
            <label class="ui-form-label" for="report-title">כותרת *</label>
            <input
              id="report-title"
              v-model="form.title"
              type="text"
              placeholder="למשל: הוצאה חריגה על תיקון…"
              maxlength="100"
              @blur="validateTitle"
              class="ui-input"
              :class="{ 'is-error': fe.title }"
            />
            <div class="flex justify-between mt-1 items-center">
              <span v-if="fe.title" class="ui-field-error">{{ fe.title }}</span>
              <span v-else></span>
              <span class="ui-label ui-num" style="font-size: 0.625rem;"><bdi>{{ form.title.length }}/100</bdi></span>
            </div>
          </div>

          <!-- Amount -->
          <div v-if="form.type === 'expense' || form.type === 'revenue'">
            <label class="ui-form-label" for="report-amount">סכום (₪) *</label>
            <input
              id="report-amount"
              v-model.number="form.amount"
              type="number"
              placeholder="0"
              min="1"
              @blur="validateAmount"
              class="ui-input ui-num"
              :class="{ 'is-error': fe.amount }"
            />
            <span v-if="fe.amount" class="ui-field-error mt-1 block">{{ fe.amount }}</span>
          </div>

          <!-- Description -->
          <div>
            <label class="ui-form-label" for="report-detail">פירוט</label>
            <textarea
              id="report-detail"
              v-model="form.description"
              rows="3"
              placeholder="תיאור מפורט…"
              maxlength="500"
              class="ui-input"
              style="resize: none; background: var(--surface); border-color: var(--border);"
            ></textarea>
            <div class="flex justify-end mt-1">
              <span
                class="ui-label ui-num"
                :class="form.description.length > 480 ? 'ed-tone-warning' : ''"
                style="font-size: 0.625rem;"
              >
                <bdi>{{ form.description.length }}/500</bdi>
              </span>
            </div>
          </div>

          <!-- Error -->
          <p v-if="error" class="ui-field-error">{{ error }}</p>
        </div>

        <!-- Footer -->
        <footer class="px-7 py-5 flex items-center justify-between gap-4" style="border-top: 1px solid var(--border-strong);">
          <button @click="$emit('close')" class="ui-btn" type="button">ביטול</button>
          <button
            @click="submit"
            :disabled="!canSubmit || submitting"
            class="ui-btn ui-btn-dark"
            type="button"
          >
            {{ submitting ? 'שומר…' : 'שמור דיווח' }}
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
