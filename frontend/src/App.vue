<template>
  <!-- Login Gate -->
  <LoginPage v-if="!isLoggedIn" @login="isLoggedIn = true; loadAppData()" />

  <div v-else class="min-h-screen" dir="rtl" style="background: var(--bg);">
    <!-- Top Navigation -->
    <header class="sticky top-0 z-30 bg-white border-b border-gray-100">
      <div class="max-w-[1440px] mx-auto px-3 sm:px-6 lg:px-8">
        <div class="flex items-center h-14 sm:h-16 gap-3 sm:gap-6">
          <!-- Logo -->
          <button @click="activeTab = 'dashboard'; selectedProject = ''"
            class="flex items-center gap-2.5 flex-shrink-0 group">
            <div class="w-9 h-9 bg-emerald-800 rounded-xl flex items-center justify-center group-hover:bg-emerald-900 transition-colors">
              <svg class="w-4.5 h-4.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
              </svg>
            </div>
            <div class="hidden sm:block">
              <div class="text-sm font-bold text-gray-800 leading-tight">סנג'ר של לנה</div>
              <div class="text-[11px] text-gray-400">ניהול פיננסי</div>
            </div>
          </button>

          <!-- Hamburger button (mobile only) -->
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 rounded-xl hover:bg-gray-100 transition-colors">
            <svg v-if="!mobileMenuOpen" class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg v-else class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>

          <!-- Separator -->
          <div class="w-px h-8 bg-gray-200 hidden md:block"></div>

          <!-- Nav Pills (hidden on mobile) -->
          <nav class="hidden md:flex items-center gap-1 overflow-x-auto flex-nowrap flex-1 min-w-0">
            <!-- Dashboard -->
            <button @click="activeTab = 'dashboard'; selectedProject = ''"
              :class="[
                'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200',
                activeTab === 'dashboard'
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              ]">
              דשבורד
            </button>

            <!-- Projects (with dropdown) -->
            <div class="relative" ref="projectsBtn">
              <button @click="pnlOpen = !pnlOpen"
                :class="[
                  'flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200',
                  activeTab === 'pnl'
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                ]">
                <span>פרויקטים</span>
                <svg class="w-3.5 h-3.5 transition-transform duration-200" :class="pnlOpen ? 'rotate-180' : ''"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
            </div>

            <!-- Projects dropdown (teleported to escape overflow clipping) -->
            <Teleport to="body">
              <div v-if="pnlOpen" class="fixed inset-0 z-40" @click="pnlOpen = false"></div>
              <div v-if="pnlOpen" dir="rtl"
                class="fixed z-50 bg-white rounded-xl shadow-lg border border-gray-200 py-2 min-w-[240px] max-h-80 overflow-y-auto animate-fade-up"
                :style="dropdownStyle">
                <div class="px-3 pb-2 mb-1 border-b border-gray-100">
                  <span class="text-xs font-medium text-gray-400">רשימת פרויקטים</span>
                </div>
                <button
                  v-for="p in projects" :key="p"
                  @click="selectProject(p); pnlOpen = false"
                  :class="[
                    'w-full flex items-center gap-2.5 px-4 py-2.5 text-sm transition-colors',
                    activeTab === 'pnl' && selectedProject === p
                      ? 'bg-gray-50 text-gray-900 font-medium'
                      : 'text-gray-600 hover:bg-gray-50'
                  ]">
                  <span class="w-2 h-2 rounded-full flex-shrink-0"
                    :class="activeTab === 'pnl' && selectedProject === p ? 'bg-emerald-700' : 'bg-gray-300'"></span>
                  <span class="flex-1 truncate text-right">{{ p }}</span>
                  <span v-if="getProjectStatus(p) === 'completed'" class="text-[10px] bg-gray-100 text-gray-400 px-1.5 py-0.5 rounded">הושלם</span>
                  <span v-else-if="getProjectStatus(p) === 'on-hold'" class="text-[10px] bg-amber-50 text-amber-500 px-1.5 py-0.5 rounded">מושהה</span>
                </button>
              </div>
            </Teleport>

            <!-- Cash flow -->
            <button @click="activeTab = 'cashflow'"
              :class="[
                'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200',
                activeTab === 'cashflow'
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              ]">
              תזרים
            </button>

            <!-- Data management -->
            <button @click="activeTab = 'data'"
              :class="[
                'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200',
                activeTab === 'data'
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              ]">
              נתונים
            </button>

            <!-- Attendance -->
            <button @click="activeTab = 'attendance'"
              :class="[
                'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200',
                activeTab === 'attendance'
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              ]">
              נוכחות
            </button>
          </nav>

          <!-- Right side: actions -->
          <div class="flex items-center gap-2 sm:gap-3 flex-shrink-0 mr-auto">
            <!-- New project button (hidden on mobile - available in hamburger menu) -->
            <button @click="showNewProjectModal = true"
              class="hidden md:flex items-center gap-1.5 px-3.5 py-2 bg-gray-900 text-white rounded-xl text-sm font-medium hover:bg-gray-800 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
              </svg>
              <span class="hidden lg:inline">פרויקט חדש</span>
            </button>

            <!-- Alerts bell (always visible) -->
            <button @click="showAlertsModal = !showAlertsModal" class="relative p-2 rounded-xl hover:bg-gray-100 transition-colors">
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
              <span v-if="alertCount > 0" class="absolute -top-1 -left-1 bg-red-500 text-white text-[11px] min-w-[20px] h-5 rounded-full flex items-center justify-center font-bold px-1">{{ alertCount }}</span>
            </button>

            <!-- User avatar (hidden on mobile - available in hamburger menu) -->
            <div class="hidden md:flex items-center gap-2.5 pr-3 border-r border-gray-200">
              <div class="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                <span class="text-emerald-800 font-bold text-xs">FM</span>
              </div>
              <div class="hidden lg:block">
                <div class="text-sm font-semibold text-gray-700 leading-tight">מנהל מערכת</div>
                <div class="text-[11px] text-gray-400">סנג'ר של לנה</div>
              </div>
              <button @click="logout()"
                class="p-2 rounded-xl hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                title="יציאה">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Mobile menu panel -->
    <transition name="slide-down">
      <div v-if="mobileMenuOpen" class="fixed inset-0 top-14 z-20 bg-white md:hidden overflow-y-auto" dir="rtl">
        <div class="p-4 space-y-1">
          <!-- Nav items -->
          <button @click="mobileNav('dashboard')"
            :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors', activeTab === 'dashboard' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100']">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            דשבורד
          </button>

          <!-- Projects section -->
          <div class="border-b border-gray-100 pb-2 mb-2">
            <div class="px-4 py-2 text-xs font-medium text-gray-400">פרויקטים</div>
            <button v-for="p in projects" :key="p" @click="selectProject(p)"
              :class="['w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm transition-colors', activeTab === 'pnl' && selectedProject === p ? 'bg-emerald-50 text-emerald-800 font-medium' : 'text-gray-600 hover:bg-gray-50']">
              <span class="w-2 h-2 rounded-full flex-shrink-0" :class="activeTab === 'pnl' && selectedProject === p ? 'bg-emerald-600' : 'bg-gray-300'"></span>
              {{ p }}
            </button>
          </div>

          <button @click="mobileNav('cashflow')"
            :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors', activeTab === 'cashflow' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100']">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
            תזרים
          </button>
          <button @click="mobileNav('data')"
            :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors', activeTab === 'data' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100']">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"/></svg>
            נתונים
          </button>
          <button @click="mobileNav('attendance')"
            :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors', activeTab === 'attendance' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100']">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            נוכחות
          </button>

          <!-- Divider -->
          <div class="border-t border-gray-100 pt-2 mt-2"></div>

          <!-- New project -->
          <button @click="showNewProjectModal = true; mobileMenuOpen = false"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium bg-gray-900 text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
            פרויקט חדש
          </button>

          <!-- Logout -->
          <button @click="logout(); mobileMenuOpen = false"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-500 hover:bg-red-50">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            יציאה
          </button>
        </div>
      </div>
    </transition>

    <!-- Page content -->
    <main class="p-3 sm:p-6 lg:p-8 max-w-[1440px] mx-auto">
      <Dashboard v-if="activeTab === 'dashboard'" />
      <PnlView v-else-if="activeTab === 'pnl'" :initialProject="selectedProject" />
      <CashFlowView v-else-if="activeTab === 'cashflow'" />
      <DataView v-else-if="activeTab === 'data'" />
      <AttendanceView v-else-if="activeTab === 'attendance'" />
    </main>

    <!-- New project modal -->
    <ProjectFormModal
      :show="showNewProjectModal"
      :new-project="true"
      project=""
      @close="showNewProjectModal = false"
      @saved="onProjectSaved"
    />

    <!-- Alerts modal -->
    <Teleport to="body">
      <div v-if="showAlertsModal" class="fixed inset-0 z-[90]" dir="rtl">
        <div class="absolute inset-0 bg-black/30" @click="showAlertsModal = false"></div>
        <div class="fixed top-16 sm:top-20 inset-x-2 sm:inset-x-auto sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-lg bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
          <!-- Header -->
          <div class="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-100">
            <h3 class="text-lg font-bold text-gray-800">התראות</h3>
            <div class="flex items-center gap-2">
              <button v-if="alerts.length > 0" @click="alerts = []; alertCount = 0"
                class="text-xs text-gray-400 hover:text-gray-600 transition">איפוס</button>
              <button @click="showAlertsModal = false" class="p-1 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
          <!-- Body -->
          <div class="max-h-[400px] overflow-y-auto">
            <div v-if="alerts.length === 0" class="py-12 text-center">
              <div class="text-3xl mb-3">&#9989;</div>
              <div class="text-sm font-medium text-gray-600">אין התראות</div>
              <div class="text-xs text-gray-400 mt-1">כל הפרויקטים פועלים בטווח התקין</div>
            </div>
            <button v-for="(alert, i) in alerts" :key="i"
              @click="goToAlertProject(alert.project)"
              class="w-full flex items-start gap-3 px-6 py-4 border-b border-gray-50 hover:bg-gray-50 transition-colors text-right">
              <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
                :class="alert.severity === 'high' ? 'bg-red-50 text-red-500' : 'bg-orange-50 text-orange-500'">
                <span class="text-base">&#9888;</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-0.5">
                  <span class="font-semibold text-gray-800 text-sm">{{ alert.project }}</span>
                  <span class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                    :class="alert.severity === 'high' ? 'bg-red-100 text-red-600' : 'bg-orange-100 text-orange-600'">
                    {{ alert.severity === 'high' ? 'גבוה' : 'בינוני' }}
                  </span>
                </div>
                <div class="text-sm text-gray-600">{{ alert.message }}</div>
                <div v-if="alert.detail" class="text-xs text-gray-400 mt-0.5">{{ alert.detail }}</div>
              </div>
              <svg class="w-4 h-4 text-gray-300 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Robot popup -->
    <Teleport to="body">
      <div v-if="showRobotMsg" class="fixed inset-0 z-[100] flex items-center justify-center" dir="rtl">
        <div class="absolute inset-0 bg-black/40" @click="showRobotMsg = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl p-8 max-w-sm mx-4 text-center transform animate-bounce-in">
          <div class="text-6xl mb-4">🤖</div>
          <div class="text-xl font-bold text-gray-800 mb-2">איזה כיף להיות הסנג'ר של לנה!</div>
          <div class="text-sm text-gray-500 mb-5">אני כאן כדי לעזור לך לנהל את הפיננסים</div>
          <button @click="showRobotMsg = false"
            class="px-6 py-2.5 bg-emerald-700 text-white rounded-xl font-medium hover:bg-emerald-800 transition">
            תודה! 💚
          </button>
        </div>
      </div>
    </Teleport>

    <!-- Chatbot FAB + Panel -->
    <div class="fixed bottom-4 left-4 sm:bottom-6 sm:left-6 z-50 flex flex-col items-start gap-3" dir="rtl">
      <!-- Chat panel -->
      <transition name="chat-panel">
        <div v-if="showChatbot" class="w-[calc(100vw-2rem)] sm:w-80 h-[420px] bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.12)] border border-gray-200/60 flex flex-col overflow-hidden">
          <!-- Chat header -->
          <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                <span class="text-sm">🤖</span>
              </div>
              <div>
                <div class="text-sm font-semibold text-gray-800">עוזר חכם</div>
                <div class="text-[10px] text-emerald-600">מחובר</div>
              </div>
            </div>
            <button @click="showChatbot = false" class="p-1 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <!-- Chat messages -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div class="flex gap-2">
              <div class="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span class="text-xs">🤖</span>
              </div>
              <div class="bg-gray-50 rounded-xl rounded-tr-none px-3 py-2 text-sm text-gray-700 max-w-[85%]">
                היי! אני העוזר החכם של סנג'ר. אפשר לשאול אותי שאלות על הנתונים הפיננסיים, פרויקטים, ותזרים מזומנים.
              </div>
            </div>
          </div>
          <!-- Chat input -->
          <div class="px-3 py-3 border-t border-gray-100">
            <div class="flex items-center gap-2">
              <input type="text" placeholder="שאל שאלה..." disabled
                class="flex-1 bg-gray-50 border border-transparent rounded-lg px-3 py-2 text-sm focus:outline-none focus:bg-white focus:border-gray-300 transition placeholder-gray-400" />
              <button disabled class="p-2 bg-emerald-800 text-white rounded-lg opacity-50 cursor-not-allowed">
                <svg class="w-4 h-4 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
              </button>
            </div>
            <div class="text-[10px] text-gray-300 mt-1 text-center">בקרוב — תכונה בפיתוח</div>
          </div>
        </div>
      </transition>
      <!-- FAB button -->
      <button @click="showChatbot = !showChatbot"
        class="w-12 h-12 bg-emerald-800 text-white rounded-full shadow-lg hover:bg-emerald-900 transition-all hover:scale-105 flex items-center justify-center">
        <svg v-if="!showChatbot" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import LoginPage from './components/LoginPage.vue'
import Dashboard from './components/Dashboard.vue'
import PnlView from './components/PnlView.vue'
import CashFlowView from './components/CashFlowView.vue'
import AlertsView from './components/AlertsView.vue'
import DataView from './components/DataView.vue'
import AttendanceView from './components/AttendanceView.vue'
import ProjectFormModal from './components/ProjectFormModal.vue'
import { getPnl, getProjects, getProjectsDetail } from './services/api'

const isLoggedIn = ref(!!localStorage.getItem('token'))
const activeTab = ref('dashboard')
const showRobotMsg = ref(false)
const showChatbot = ref(false)
const showNewProjectModal = ref(false)
const showAlertsModal = ref(false)
const alerts = ref([])
const alertCount = ref(0)
const mobileMenuOpen = ref(false)
const pnlOpen = ref(false)
const projects = ref([])
const projectsDetail = ref([])
const selectedProject = ref('')
const projectsBtn = ref(null)

const dropdownStyle = computed(() => {
  if (!projectsBtn.value) return {}
  const rect = projectsBtn.value.getBoundingClientRect()
  return {
    top: rect.bottom + 8 + 'px',
    right: (window.innerWidth - rect.right) + 'px',
  }
})

function logout() {
  localStorage.removeItem('token')
  isLoggedIn.value = false
}

function selectProject(name) {
  selectedProject.value = name
  activeTab.value = 'pnl'
  mobileMenuOpen.value = false
}

function mobileNav(tab) {
  activeTab.value = tab
  selectedProject.value = ''
  mobileMenuOpen.value = false
}

function goToAlertProject(projectName) {
  showAlertsModal.value = false
  selectProject(projectName)
}

function getProjectStatus(name) {
  const detail = projectsDetail.value.find(p => p.name === name)
  return detail?.status || 'active'
}

function onProjectSaved(projectName) {
  showNewProjectModal.value = false
  getProjects().then(list => {
    projects.value = list
    if (projectName) {
      selectProject(projectName)
    }
  }).catch(() => {})
}

function loadAppData() {
  getProjects().then(list => { projects.value = list }).catch(() => {})
  getProjectsDetail().then(list => { projectsDetail.value = list || [] }).catch(() => {})

  getPnl().then(data => {
    const list = []
    for (const [name, project] of Object.entries(data)) {
      if (project.summary.margin != null && project.summary.margin < 20) {
        list.push({
          project: name,
          severity: project.summary.margin < 10 ? 'high' : 'medium',
          message: `מרווח תפעולי שנתי נמוך: ${project.summary.margin}%`,
          detail: `הסף הנדרש: 20%. הפרש: ${(20 - project.summary.margin).toFixed(1)}%`,
        })
      }
      const negativeProfitMonths = project.months.filter(m => m.operating_profit < 0 && m.revenue > 0)
      if (negativeProfitMonths.length > 0) {
        list.push({
          project: name,
          severity: 'medium',
          message: `${negativeProfitMonths.length} חודשים עם הפסד תפעולי למרות הכנסות`,
          detail: `חודשים: ${negativeProfitMonths.map(m => m.month).join(', ')}`,
        })
      }
      const zeroMonths = project.months.filter(m => m.revenue === 0)
      if (zeroMonths.length > 6) {
        list.push({
          project: name,
          severity: 'medium',
          message: `${zeroMonths.length} חודשים ללא הכנסה`,
          detail: 'ייתכן שיש בעיה בגביה או בלוח זמנים',
        })
      }
    }
    alerts.value = list
    alertCount.value = list.length
  }).catch(() => {})
}

// Only load data if already logged in
if (isLoggedIn.value) {
  loadAppData()
}
</script>
