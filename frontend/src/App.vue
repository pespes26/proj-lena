<template>
  <div class="min-h-screen flex" dir="rtl" style="background: var(--bg);">
    <!-- Sidebar -->
    <aside
      :class="[
        'bg-white border-l border-gray-200 flex flex-col fixed top-0 right-0 h-full z-30 transition-all duration-300',
        collapsed ? 'w-[72px]' : 'w-60'
      ]"
    >
      <!-- Logo / Home -->
      <div class="flex items-center gap-3 p-4" :class="collapsed ? 'justify-center' : 'px-5'">
        <button @click="activeTab = 'dashboard'; selectedProject = ''"
          class="flex items-center gap-3 group"
          :title="collapsed ? 'דשבורד' : ''">
          <div class="w-10 h-10 bg-lime-500 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:bg-lime-600 transition-colors">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
          </div>
          <div v-if="!collapsed" class="transition-opacity duration-200">
            <div class="text-sm font-bold text-gray-800 leading-tight">סנג'ר של לנה</div>
            <div class="text-[10px] text-gray-400">ניהול פיננסי</div>
          </div>
        </button>
      </div>

      <div v-if="!collapsed" class="px-5 mb-2">
        <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">כללי</div>
      </div>

      <!-- Nav items -->
      <nav class="flex-1 px-2 space-y-1 overflow-y-auto">

        <!-- Projects accordion -->
        <div>
          <button
            @click="collapsed ? (activeTab = 'pnl') : (pnlOpen = !pnlOpen)"
            :title="collapsed ? 'פרויקטים' : ''"
            :class="[
              'w-full flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200',
              collapsed ? 'justify-center px-0 py-3' : 'px-4 py-2.5',
              activeTab === 'pnl'
                ? 'bg-lime-50 text-lime-700'
                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
            ]"
          >
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            <span v-if="!collapsed" class="flex-1 text-right">פרויקטים</span>
            <!-- Accordion arrow -->
            <svg v-if="!collapsed" class="w-4 h-4 text-gray-400 transition-transform duration-200"
              :class="pnlOpen ? 'rotate-180' : ''"
              fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          <!-- Sub-items (projects list) -->
          <div v-if="pnlOpen && !collapsed"
            class="overflow-hidden transition-all duration-200 mr-4 border-r-2 border-gray-100">
            <button
              v-for="p in projects" :key="p"
              @click="selectProject(p)"
              :class="[
                'w-full flex items-center gap-2 pr-5 pl-3 py-2 text-xs rounded-lg transition-all duration-150',
                activeTab === 'pnl' && selectedProject === p
                  ? 'bg-lime-50 text-lime-700 font-semibold'
                  : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
              ]"
            >
              <span class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                :class="activeTab === 'pnl' && selectedProject === p ? 'bg-lime-500' : 'bg-gray-300'"></span>
              {{ p }}
            </button>
          </div>
        </div>

        <!-- Cash flow -->
        <button
          @click="activeTab = 'cashflow'"
          :title="collapsed ? 'תזרים' : ''"
          :class="[
            'w-full flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200 relative',
            collapsed ? 'justify-center px-0 py-3' : 'px-4 py-2.5',
            activeTab === 'cashflow'
              ? 'bg-lime-50 text-lime-700'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
          ]"
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span v-if="!collapsed">תזרים</span>
        </button>

        <!-- Alerts -->
        <button
          @click="activeTab = 'alerts'"
          :title="collapsed ? 'התראות' : ''"
          :class="[
            'w-full flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200 relative',
            collapsed ? 'justify-center px-0 py-3' : 'px-4 py-2.5',
            activeTab === 'alerts'
              ? 'bg-lime-50 text-lime-700'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
          ]"
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
          </svg>
          <span v-if="!collapsed">התראות</span>
          <span v-if="alertCount > 0"
            :class="[
              'bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center',
              collapsed ? 'absolute -top-0.5 -left-0.5 w-4 h-4' : 'mr-auto w-5 h-5'
            ]">
            {{ alertCount }}
          </span>
        </button>

        <!-- Data management -->
        <button
          @click="activeTab = 'data'"
          :title="collapsed ? 'נתונים' : ''"
          :class="[
            'w-full flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200 relative',
            collapsed ? 'justify-center px-0 py-3' : 'px-4 py-2.5',
            activeTab === 'data'
              ? 'bg-lime-50 text-lime-700'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
          ]"
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
          </svg>
          <span v-if="!collapsed">נתונים</span>
        </button>

        <!-- Attendance -->
        <button
          @click="activeTab = 'attendance'"
          :title="collapsed ? 'נוכחות' : ''"
          :class="[
            'w-full flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200 relative',
            collapsed ? 'justify-center px-0 py-3' : 'px-4 py-2.5',
            activeTab === 'attendance'
              ? 'bg-lime-50 text-lime-700'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
          ]"
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span v-if="!collapsed">נוכחות</span>
        </button>
      </nav>

    </aside>

    <!-- Main content area -->
    <div class="flex-1 transition-all duration-300" :class="collapsed ? 'mr-[72px]' : 'mr-60'">
      <!-- Top header -->
      <header class="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between sticky top-0 z-20">
        <div class="flex items-center gap-3">
          <button @click="collapsed = !collapsed"
            class="p-2 rounded-xl text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
          <div class="relative">
            <input type="text" placeholder="חיפוש מהיר..."
              class="bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 pr-10 text-sm w-72 focus:outline-none focus:ring-2 focus:ring-lime-300 focus:border-lime-400 transition" />
            <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <button @click="activeTab = 'alerts'" class="relative p-2 rounded-xl hover:bg-gray-50 transition">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
            <span v-if="alertCount > 0" class="absolute -top-0.5 -left-0.5 bg-red-500 text-white text-[10px] w-5 h-5 rounded-full flex items-center justify-center font-bold">{{ alertCount }}</span>
          </button>
          <!-- Robot button -->
          <button @click="showRobotMsg = true"
            class="p-2 rounded-xl hover:bg-lime-50 transition group relative" title="הסנג'ר">
            <svg class="w-6 h-6 text-gray-400 group-hover:text-lime-500 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714a2.25 2.25 0 00.659 1.591L19 14.5M14.25 3.104c.251.023.501.05.75.082M19 14.5l-1.482 1.484a2.25 2.25 0 00-.659 1.59V21a.75.75 0 01-.75.75h-8.22a.75.75 0 01-.75-.75v-3.426a2.25 2.25 0 00-.659-1.59L5 14.5m14 0h-2.25m-10.5 0H4"/>
            </svg>
          </button>
          <div class="flex items-center gap-3 pr-4 border-r border-gray-200">
            <div class="w-9 h-9 bg-lime-100 rounded-full flex items-center justify-center">
              <span class="text-lime-700 font-bold text-sm">FM</span>
            </div>
            <div>
              <div class="text-sm font-semibold text-gray-700">מנהל מערכת</div>
              <div class="text-xs text-gray-400">סנג'ר של לנה</div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="p-8">
        <Dashboard v-if="activeTab === 'dashboard'" />
        <PnlView v-else-if="activeTab === 'pnl'" :initialProject="selectedProject" />
        <CashFlowView v-else-if="activeTab === 'cashflow'" />
        <AlertsView v-else-if="activeTab === 'alerts'" />
        <DataView v-else-if="activeTab === 'data'" />
        <AttendanceView v-else-if="activeTab === 'attendance'" />
      </main>
    </div>

    <!-- Robot popup -->
    <Teleport to="body">
      <div v-if="showRobotMsg" class="fixed inset-0 z-[100] flex items-center justify-center" dir="rtl">
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm" @click="showRobotMsg = false"></div>
        <div class="relative bg-white rounded-3xl shadow-2xl p-8 max-w-sm mx-4 text-center transform animate-bounce-in">
          <div class="text-6xl mb-4">🤖</div>
          <div class="text-xl font-bold text-gray-800 mb-2">איזה כיף להיות הסנג'ר של לנה!</div>
          <div class="text-sm text-gray-500 mb-5">אני כאן כדי לעזור לך לנהל את הפיננסים</div>
          <button @click="showRobotMsg = false"
            class="px-6 py-2.5 bg-lime-500 text-white rounded-xl font-medium hover:bg-lime-600 transition">
            תודה! 💚
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Dashboard from './components/Dashboard.vue'
import PnlView from './components/PnlView.vue'
import CashFlowView from './components/CashFlowView.vue'
import AlertsView from './components/AlertsView.vue'
import DataView from './components/DataView.vue'
import AttendanceView from './components/AttendanceView.vue'
import { getPnl, getProjects } from './services/api'

const activeTab = ref('dashboard')
const collapsed = ref(false)
const showRobotMsg = ref(false)
const alertCount = ref(0)
const pnlOpen = ref(false)
const projects = ref([])
const selectedProject = ref('')

function selectProject(name) {
  selectedProject.value = name
  activeTab.value = 'pnl'
}

getProjects().then(list => { projects.value = list }).catch(() => {})

getPnl().then(data => {
  let count = 0
  for (const project of Object.values(data)) {
    if (project.summary.margin != null && project.summary.margin < 20) count++
    const zeroMonths = project.months.filter(m => m.revenue === 0)
    if (zeroMonths.length > 6) count++
  }
  alertCount.value = count
}).catch(() => {})
</script>
