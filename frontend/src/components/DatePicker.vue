<template>
  <div class="relative" ref="wrapper">
    <div class="relative">
      <input
        ref="inputEl"
        type="text"
        :value="displayValue"
        :placeholder="placeholder"
        :class="[inputClass, invalidDate ? 'border-red-400! bg-red-50!' : '']"
        @input="onInput"
        @focus="showCalendar = true"
        @keydown.escape="showCalendar = false"
        maxlength="10"
        dir="ltr"
      />
      <button type="button" @click="showCalendar = !showCalendar"
        class="absolute right-2 top-1/2 -translate-y-1/2 p-0.5 text-gray-400 hover:text-gray-600 transition">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
      </button>
    </div>
    <span v-if="invalidDate" class="text-red-500 text-[10px] mt-0.5 block">תאריך לא תקין</span>

    <!-- Calendar dropdown -->
    <Teleport to="body">
      <div v-if="showCalendar" class="fixed inset-0 z-[100]" @click="showCalendar = false"></div>
      <div v-if="showCalendar" ref="calendarEl"
        class="fixed z-[101] bg-white rounded-xl shadow-xl border border-gray-200 p-3 w-[280px]"
        :style="calendarPosition">
        <!-- Month/Year navigation -->
        <div class="flex items-center justify-between mb-3">
          <button type="button" @click="prevMonth"
            class="p-1 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
          </button>
          <div class="text-sm font-medium text-gray-800">
            {{ hebrewMonths[viewMonth] }} {{ viewYear }}
          </div>
          <button type="button" @click="nextMonth"
            class="p-1 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
          </button>
        </div>

        <!-- Day headers -->
        <div class="grid grid-cols-7 mb-1">
          <div v-for="d in dayHeaders" :key="d" class="text-center text-[10px] font-medium text-gray-400 py-1">{{ d }}</div>
        </div>

        <!-- Days grid -->
        <div class="grid grid-cols-7">
          <div v-for="(day, i) in calendarDays" :key="i" class="p-0.5">
            <button v-if="day"
              type="button"
              @click="selectDay(day)"
              :disabled="isBeforeMin(day)"
              :class="[
                'w-full aspect-square rounded-lg text-xs transition flex items-center justify-center',
                isBeforeMin(day) ? 'text-gray-200 cursor-not-allowed' :
                isSelected(day) ? 'bg-emerald-700 text-white font-bold' :
                isToday(day) ? 'bg-emerald-50 text-emerald-800 font-semibold ring-1 ring-emerald-300' :
                day.outside ? 'text-gray-300' :
                'text-gray-700 hover:bg-gray-100'
              ]">
              {{ day.date }}
            </button>
            <div v-else class="w-full aspect-square"></div>
          </div>
        </div>

        <!-- Today button -->
        <div class="mt-2 pt-2 border-t border-gray-100">
          <button type="button" @click="goToday"
            class="w-full text-center text-xs text-emerald-700 font-medium hover:bg-emerald-50 rounded-lg py-1.5 transition">
            היום
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
