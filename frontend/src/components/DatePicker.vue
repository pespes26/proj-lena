<template>
  <div class="relative" ref="wrapper">
    <div class="relative">
      <input
        ref="inputEl"
        type="text"
        :value="displayValue"
        :placeholder="placeholder"
        :class="[inputClass || 'ed-input', invalidDate ? 'is-error' : '']"
        style="padding-right: 2.5rem;"
        @input="onInput"
        @focus="showCalendar = true"
        @keydown.escape="showCalendar = false"
        maxlength="10"
        dir="ltr"
      />
      <button type="button" @click="showCalendar = !showCalendar"
        class="absolute right-2 top-1/2 -translate-y-1/2 text-ink-muted hover:text-accent transition-colors p-1 rounded-md hover:bg-slate-100" aria-label="בחר תאריך">
        <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
      </button>
    </div>
    <span v-if="invalidDate" class="font-sans text-[10px] ed-tone-negative mt-1 block">תאריך לא תקין</span>

    <!-- Calendar dropdown — editorial paper sheet -->
    <Teleport to="body">
      <div v-if="showCalendar" class="fixed inset-0 z-[100]" @click="showCalendar = false"></div>
      <div v-if="showCalendar" ref="calendarEl"
        class="fixed z-[101] bg-surface border border-border rounded-xl shadow-lg w-[300px] ed-fade-up"
        :style="calendarPosition">
        <!-- Month/Year navigation -->
        <div class="flex items-center justify-between px-4 pt-3 pb-2">
          <button type="button" @click="prevMonth" class="text-ink-muted hover:text-accent transition-colors p-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5"><path stroke-linecap="square" d="M15 19l-7-7 7-7"/></svg>
          </button>
          <div class="font-sans font-semibold text-ink ed-num">
            <span>{{ hebrewMonths[viewMonth] }}</span> <bdi>{{ viewYear }}</bdi>
          </div>
          <button type="button" @click="nextMonth" class="text-ink-muted hover:text-accent transition-colors p-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5"><path stroke-linecap="square" d="M9 5l7 7-7 7"/></svg>
          </button>
        </div>
        <hr class="ed-rule mx-4" />

        <!-- Day headers -->
        <div class="grid grid-cols-7 px-4 pt-3">
          <div v-for="d in dayHeaders" :key="d" class="ed-eyebrow text-center py-1" style="font-size: 0.625rem;">{{ d }}</div>
        </div>

        <!-- Days grid -->
        <div class="grid grid-cols-7 px-4 pb-3">
          <div v-for="(day, i) in calendarDays" :key="i" class="p-0.5">
            <button v-if="day"
              type="button"
              @click="selectDay(day)"
              :disabled="isBeforeMin(day)"
              :class="[
                'ed-date-cell',
                isBeforeMin(day) ? 'is-disabled' : '',
                isSelected(day) ? 'is-selected' : '',
                isToday(day) && !isSelected(day) ? 'is-today' : '',
                day.outside ? 'is-outside' : '',
              ]">
              <bdi class="ed-num">{{ day.date }}</bdi>
            </button>
          </div>
        </div>

        <!-- Today button -->
        <div class="border-t border-rule px-4 py-2">
          <button type="button" @click="goToday" class="ed-link text-sm w-full text-center block">
            היום →
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'dd/mm/yyyy' },
  inputClass: { type: String, default: '' },
  minDate: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const wrapper = ref(null)
const inputEl = ref(null)
const calendarEl = ref(null)
const showCalendar = ref(false)
const calendarPosition = ref({})
const invalidDate = ref(false)

function isValidDate(day, month, year) {
  if (year < 1900 || year > 2100) return false
  if (month < 1 || month > 12) return false
  if (day < 1) return false
  const daysInMonth = new Date(year, month, 0).getDate()
  return day <= daysInMonth
}

const hebrewMonths = [
  'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
  'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
]

const dayHeaders = ['א׳', 'ב׳', 'ג׳', 'ד׳', 'ה׳', 'ו׳', 'ש׳']

// View state for calendar navigation
const today = new Date()
const viewMonth = ref(today.getMonth())
const viewYear = ref(today.getFullYear())

// Convert modelValue (yyyy-mm-dd) to display (dd/mm/yyyy)
const displayValue = computed(() => {
  if (!props.modelValue) return ''
  const parts = props.modelValue.split('-')
  if (parts.length !== 3) return props.modelValue
  return `${parts[2]}/${parts[1]}/${parts[0]}`
})

// Parse dd/mm/yyyy to yyyy-mm-dd
function parseDisplay(val) {
  const clean = val.replace(/[^\d]/g, '')
  let formatted = ''
  for (let i = 0; i < clean.length && i < 8; i++) {
    if (i === 2 || i === 4) formatted += '/'
    formatted += clean[i]
  }
  return formatted
}

function onInput(e) {
  const raw = e.target.value
  const formatted = parseDisplay(raw)
  e.target.value = formatted
  invalidDate.value = false

  // If complete dd/mm/yyyy, emit as yyyy-mm-dd
  const match = formatted.match(/^(\d{2})\/(\d{2})\/(\d{4})$/)
  if (match) {
    const [, dd, mm, yyyy] = match
    const day = parseInt(dd), month = parseInt(mm), year = parseInt(yyyy)
    const dateStr = `${yyyy}-${mm}-${dd}`
    if (isValidDate(day, month, year) && (!props.minDate || dateStr >= props.minDate)) {
      emit('update:modelValue', dateStr)
      viewMonth.value = month - 1
      viewYear.value = year
      invalidDate.value = false
    } else {
      invalidDate.value = true
      emit('update:modelValue', '')
    }
  } else if (formatted === '') {
    emit('update:modelValue', '')
  }
}

function isBeforeMin(day) {
  if (!props.minDate) return false
  const dayStr = `${day.year}-${String(day.month + 1).padStart(2, '0')}-${String(day.date).padStart(2, '0')}`
  return dayStr < props.minDate
}

function selectDay(day) {
  if (isBeforeMin(day)) return
  const m = String(day.month + 1).padStart(2, '0')
  const d = String(day.date).padStart(2, '0')
  const y = day.year
  emit('update:modelValue', `${y}-${m}-${d}`)
  showCalendar.value = false
}

function isSelected(day) {
  if (!props.modelValue) return false
  const parts = props.modelValue.split('-')
  if (parts.length !== 3) return false
  return parseInt(parts[0]) === day.year &&
    parseInt(parts[1]) === day.month + 1 &&
    parseInt(parts[2]) === day.date
}

function isToday(day) {
  return !day.outside &&
    day.date === today.getDate() &&
    day.month === today.getMonth() &&
    day.year === today.getFullYear()
}

function prevMonth() {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value--
  } else {
    viewMonth.value--
  }
}

function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value++
  } else {
    viewMonth.value++
  }
}

function goToday() {
  const now = new Date()
  viewMonth.value = now.getMonth()
  viewYear.value = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  emit('update:modelValue', `${now.getFullYear()}-${m}-${d}`)
  showCalendar.value = false
}

const calendarDays = computed(() => {
  const year = viewYear.value
  const month = viewMonth.value
  const firstDay = new Date(year, month, 1)
  // Sunday = 0 in JS, we want Sunday as first day of week
  const startDow = firstDay.getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const daysInPrevMonth = new Date(year, month, 0).getDate()

  const days = []

  // Previous month days
  for (let i = startDow - 1; i >= 0; i--) {
    const prevM = month === 0 ? 11 : month - 1
    const prevY = month === 0 ? year - 1 : year
    days.push({ date: daysInPrevMonth - i, month: prevM, year: prevY, outside: true })
  }

  // Current month days
  for (let d = 1; d <= daysInMonth; d++) {
    days.push({ date: d, month, year, outside: false })
  }

  // Next month days to fill grid
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    const nextM = month === 11 ? 0 : month + 1
    const nextY = month === 11 ? year + 1 : year
    days.push({ date: d, month: nextM, year: nextY, outside: true })
  }

  return days
})

// Position calendar near the input
function onScrollOrResize() {
  if (showCalendar.value) updatePosition()
}

watch(showCalendar, async (val) => {
  if (val) {
    // Set view to current value or today
    if (props.modelValue) {
      const parts = props.modelValue.split('-')
      if (parts.length === 3) {
        viewYear.value = parseInt(parts[0])
        viewMonth.value = parseInt(parts[1]) - 1
      }
    }
    await nextTick()
    updatePosition()
    window.addEventListener('scroll', onScrollOrResize, true)
    window.addEventListener('resize', onScrollOrResize)
  } else {
    window.removeEventListener('scroll', onScrollOrResize, true)
    window.removeEventListener('resize', onScrollOrResize)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScrollOrResize, true)
  window.removeEventListener('resize', onScrollOrResize)
})

function updatePosition() {
  if (!wrapper.value) return
  const rect = wrapper.value.getBoundingClientRect()
  const calHeight = 340
  const calWidth = 280
  const spaceBelow = window.innerHeight - rect.bottom
  const spaceAbove = rect.top

  let top, left
  if (spaceBelow >= calHeight) {
    top = rect.bottom + 6
  } else if (spaceAbove >= calHeight) {
    top = rect.top - calHeight - 6
  } else {
    top = Math.max(8, (window.innerHeight - calHeight) / 2)
  }

  left = rect.left
  if (left + calWidth > window.innerWidth - 8) {
    left = window.innerWidth - calWidth - 8
  }
  if (left < 8) left = 8

  calendarPosition.value = {
    top: top + 'px',
    left: left + 'px'
  }
}
</script>

<style scoped>
.ed-date-cell {
  width: 100%;
  aspect-ratio: 1;
  border: 0;
  background: transparent;
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease, border-bottom-color 0.15s ease;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid transparent;
}
.ed-date-cell:hover:not(.is-disabled) {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.ed-date-cell.is-outside {
  color: var(--ink-faint);
}
.ed-date-cell.is-today {
  border-bottom: 2px solid var(--ink);
  font-weight: 700;
}
.ed-date-cell.is-selected {
  background: var(--ink);
  color: var(--paper);
  font-weight: 900;
}
.ed-date-cell.is-disabled {
  color: var(--ink-faint);
  cursor: not-allowed;
  opacity: 0.4;
}
</style>
