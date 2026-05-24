<template>
  <div class="relative" ref="wrapper">
    <div class="relative">
      <input
        ref="inputEl"
        type="text"
        :value="displayValue"
        :placeholder="placeholder"
        :class="[inputClass || 'ui-input', invalidDate ? 'is-error' : '']"
        style="padding-right: 3rem;"
        @input="onInput"
        @focus="showCalendar = true"
        @keydown.escape="showCalendar = false"
        maxlength="10"
        dir="ltr"
      />
      <button type="button" @click="showCalendar = !showCalendar"
        class="ui-datepicker-trigger ui-press" aria-label="בחר תאריך">
        <svg class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.6">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
      </button>
    </div>
    <div v-if="invalidDate" class="ui-field-error ui-field-error--animate">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <span>תאריך לא תקין</span>
    </div>

    <!-- Calendar dropdown — origin-aware popover -->
    <Teleport to="body">
      <div v-if="showCalendar" class="fixed inset-0 z-[100]" @click="showCalendar = false"></div>
      <div v-if="showCalendar" ref="calendarEl"
        class="ui-datepicker-popover ui-popover"
        :style="calendarPosition">
        <!-- Month/Year navigation -->
        <div class="flex items-center justify-between px-4 pt-3 pb-2">
          <button type="button" @click="prevMonth" class="ui-datepicker-nav ui-press" aria-label="חודש קודם">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
          </button>
          <div class="font-sans font-semibold text-sm ui-num" style="color: var(--ink);">
            <span>{{ hebrewMonths[viewMonth] }}</span> <bdi>{{ viewYear }}</bdi>
          </div>
          <button type="button" @click="nextMonth" class="ui-datepicker-nav ui-press" aria-label="חודש הבא">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
          </button>
        </div>
        <div class="ui-datepicker-rule"></div>

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
                'ui-date-cell',
                isBeforeMin(day) ? 'is-disabled' : '',
                isSelected(day) ? 'is-selected' : '',
                isToday(day) && !isSelected(day) ? 'is-today' : '',
                day.outside ? 'is-outside' : '',
              ]">
              <bdi class="ui-num">{{ day.date }}</bdi>
            </button>
          </div>
        </div>

        <!-- Today button -->
        <div class="ui-datepicker-footer">
          <button type="button" @click="goToday" class="ui-datepicker-today ui-press">
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
    window.addEventListener('scroll', onScrollOrResize, { passive: true, capture: true })
    window.addEventListener('resize', onScrollOrResize, { passive: true })
  } else {
    window.removeEventListener('scroll', onScrollOrResize, { passive: true, capture: true })
    window.removeEventListener('resize', onScrollOrResize, { passive: true })
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScrollOrResize, { passive: true, capture: true })
  window.removeEventListener('resize', onScrollOrResize, { passive: true })
})

function updatePosition() {
  if (!wrapper.value) return
  const rect = wrapper.value.getBoundingClientRect()
  const calHeight = 340
  const calWidth = 300
  const spaceBelow = window.innerHeight - rect.bottom
  const spaceAbove = rect.top

  let top, left
  let originY = 'top'
  if (spaceBelow >= calHeight) {
    top = rect.bottom + 6
    originY = 'top'
  } else if (spaceAbove >= calHeight) {
    top = rect.top - calHeight - 6
    originY = 'bottom'
  } else {
    top = Math.max(8, (window.innerHeight - calHeight) / 2)
    originY = 'top'
  }

  // Anchor to right side of input (RTL-friendly)
  left = rect.right - calWidth
  let originX = 'right'
  if (left < 8) {
    left = 8
    originX = 'left'
  }
  if (left + calWidth > window.innerWidth - 8) {
    left = window.innerWidth - calWidth - 8
  }

  calendarPosition.value = {
    top: top + 'px',
    left: left + 'px',
    '--transform-origin': `${originY} ${originX}`
  }
}
</script>

<style scoped>
/* Inline calendar trigger inside input */
.ui-datepicker-trigger {
  position: absolute;
  right: 0.25rem;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-muted);
  background: transparent;
  border: 0;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: color 180ms var(--ease-out), background 180ms var(--ease-out), transform var(--dur-press) var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .ui-datepicker-trigger:hover {
    color: var(--accent);
    background: var(--surface-muted);
  }
}
.ui-datepicker-trigger:active {
  transform: translateY(-50%) scale(0.97);
}

/* Calendar popover */
.ui-datepicker-popover {
  position: fixed;
  z-index: 101;
  width: min(300px, calc(100vw - 2rem));
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
}
.ui-datepicker-rule {
  height: 1px;
  background: var(--border);
  margin: 0 1rem;
}

/* Prev/next month nav */
.ui-datepicker-nav {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--ink-muted);
  background: transparent;
  border: 0;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: color 180ms var(--ease-out), background 180ms var(--ease-out), transform var(--dur-press) var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .ui-datepicker-nav:hover {
    color: var(--ink);
    background: var(--surface-muted);
  }
}
.ui-datepicker-nav:active {
  transform: scale(0.97);
}

/* Footer */
.ui-datepicker-footer {
  border-top: 1px solid var(--border);
  padding: 0.5rem 1rem;
}
.ui-datepicker-today {
  width: 100%;
  display: block;
  text-align: center;
  background: transparent;
  border: 0;
  color: var(--accent);
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 600;
  padding: 0.375rem 0.5rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 180ms var(--ease-out), transform var(--dur-press) var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .ui-datepicker-today:hover {
    background: var(--accent-soft);
  }
}
.ui-datepicker-today:active {
  transform: scale(0.98);
}

/* Day cells */
.ui-date-cell {
  width: 100%;
  aspect-ratio: 1;
  border: 0;
  background: transparent;
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-feature-settings: "lnum" 1, "tnum" 1;
  transition: background 140ms var(--ease-out), color 140ms var(--ease-out), transform var(--dur-press) var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .ui-date-cell:hover:not(.is-disabled):not(.is-selected) {
    background: var(--surface-muted);
    color: var(--accent);
  }
}
.ui-date-cell:active:not(.is-disabled) {
  transform: scale(0.94);
}
.ui-date-cell.is-outside {
  color: var(--ink-faint);
}
.ui-date-cell.is-today {
  box-shadow: inset 0 0 0 1px var(--border-strong);
  font-weight: 700;
}
.ui-date-cell.is-selected {
  background: var(--accent);
  color: var(--surface);
  font-weight: 700;
}
.ui-date-cell.is-disabled {
  color: var(--ink-faint);
  cursor: not-allowed;
  opacity: 0.4;
}
</style>
