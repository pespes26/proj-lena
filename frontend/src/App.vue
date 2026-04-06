<template>
  <!-- Login Gate -->
  <div v-if="!authReady" class="min-h-screen flex items-center justify-center bg-bg">
    <div class="flex items-center gap-3">
      <div class="ui-logo-mark"></div>
      <div class="ui-wordmark">IFMLogiX</div>
    </div>
  </div>
  <LoginPage v-else-if="!isLoggedIn" />

  <div v-else class="min-h-screen bg-bg text-ink" dir="rtl">
    <!-- ═══════════════════════════════════════════════════════════════
         TOP NAV BAR
         ═══════════════════════════════════════════════════════════════ -->
    <header class="ui-topbar sticky top-0 z-30 border-b border-border">
      <div class="max-w-app mx-auto px-4 sm:px-8">
        <div class="flex items-center gap-4 sm:gap-6 h-16">
          <!-- Brand -->
          <button @click="goHome" class="flex items-center gap-2.5 group flex-shrink-0" aria-label="IFMLogiX home">
            <div class="ui-logo-mark group-hover:scale-105 transition-transform"></div>
            <div class="hidden sm:block">
              <div class="font-sans font-semibold text-ink text-lg leading-none tracking-tight">IFMLogiX</div>
              <div class="text-[11px] text-ink-faint font-medium mt-0.5">ניהול פיננסי</div>
            </div>
          </button>

          <!-- Hamburger (mobile) -->
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden ms-auto p-3 -me-3 rounded-lg text-ink-muted hover:text-ink hover:bg-surface-muted transition-colors">
            <svg v-if="!mobileMenuOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>

          <!-- Divider -->
          <div class="hidden md:block w-px h-8 bg-border"></div>

          <!-- Nav tabs -->
          <nav class="hidden md:flex items-center gap-1.5 overflow-x-auto flex-nowrap flex-1 min-w-0">
            <SectionMarker label="דשבורד" :active="activeTab === 'dashboard'" @click="activeTab = 'dashboard'; selectedProject = ''" />
            <SectionMarker v-if="isAdmin" label="תפעול" :active="activeTab === 'operations'" @click="activeTab = 'operations'; selectedProject = ''" />
            <SectionMarker v-if="userProfile?.role === 'project_manager'" label="הפרויקטים שלי" :active="activeTab === 'my-projects'" @click="activeTab = 'my-projects'; selectedProject = ''" />
            <SectionMarker label="תזרים מזומנים" :active="activeTab === 'cashflow'" @click="activeTab = 'cashflow'" />

            <!-- Projects dropdown trigger -->
            <div class="relative" ref="projectsBtn">
              <SectionMarker label="פרויקטים" :active="activeTab === 'pnl'" @click="pnlOpen = !pnlOpen" />
            </div>

            <Teleport to="body">
              <div v-if="pnlOpen" class="ui-dropdown-backdrop" @click="pnlOpen = false"></div>
              <div v-if="pnlOpen" dir="rtl"
                class="ui-dropdown ed-fade-up"
                :style="dropdownStyle">
                <div class="px-4 pb-2 mb-1 border-b border-slate-200">
                  <span class="text-xs font-semibold text-slate-600">רשימת פרויקטים</span>
                </div>
                <button
                  v-for="p in projects" :key="p"
                  @click="selectProject(p); pnlOpen = false"
                  :class="[
                    'w-full flex items-center gap-2.5 px-4 py-2.5 transition-colors text-[14px]',
                    activeTab === 'pnl' && selectedProject === p
                      ? 'bg-emerald-50 text-emerald-700 font-semibold'
                      : 'text-slate-900 hover:bg-slate-50'
                  ]">
                  <span class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                    :class="activeTab === 'pnl' && selectedProject === p ? 'bg-emerald-600' : 'bg-slate-300'"></span>
                  <span class="flex-1 truncate text-right font-medium">{{ p }}</span>
                  <span v-if="getProjectStatus(p) === 'completed'" class="ui-pill ui-pill-neutral text-[10px]">הושלם</span>
                  <span v-else-if="getProjectStatus(p) === 'on-hold'" class="ui-pill ui-pill-warning text-[10px]">מושהה</span>
                </button>
              </div>
            </Teleport>
          </nav>

          <!-- Right-side actions -->
          <div class="hidden md:flex items-center gap-2 flex-shrink-0">
            <!-- Alerts bell -->
            <div class="relative" ref="alertsBtn">
              <button @click="showAlertsModal = !showAlertsModal" class="relative p-2.5 rounded-lg text-ink-muted hover:text-ink hover:bg-surface-muted transition-colors" aria-label="התראות">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                </svg>
                <span v-if="alertCount > 0" class="absolute top-1 left-1 min-w-[16px] h-4 px-1 bg-negative text-white text-[10px] font-bold rounded-full flex items-center justify-center ui-num">{{ alertCount }}</span>
              </button>
            </div>

            <!-- New project -->
            <button v-if="canEdit" @click="showNewProjectModal = true"
              class="ui-btn ui-btn-primary text-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" d="M12 4v16m8-8H4"/></svg>
              <span>פרויקט חדש</span>
            </button>

            <!-- User menu -->
            <div class="relative ms-1">
              <button @click="showUserMenu = !showUserMenu" class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-surface-muted transition-colors">
                <div class="w-8 h-8 rounded-full bg-accent-soft flex items-center justify-center overflow-hidden ring-1 ring-border">
                  <img v-if="userProfile.avatar" :src="userProfile.avatar" class="w-full h-full object-cover" alt="" />
                  <span v-else class="font-sans font-semibold text-xs text-accent">{{ userInitials }}</span>
                </div>
                <div class="hidden lg:block text-right">
                  <div class="font-display font-semibold text-[13px] text-ink leading-tight">{{ userDisplayName }}</div>
                  <div class="text-[11px] text-ink-faint leading-tight mt-0.5">{{ userRoleLabel }}</div>
                </div>
                <svg class="w-3.5 h-3.5 text-ink-faint hidden lg:block" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-if="showUserMenu" class="fixed inset-0 z-40" @click="showUserMenu = false"></div>
              <div v-if="showUserMenu" class="absolute left-0 top-full mt-2 bg-surface border border-border rounded-xl shadow-lg py-1.5 min-w-[220px] z-50 ed-fade-up" dir="rtl">
                <button @click="showUserProfile = true; showUserMenu = false" class="w-full text-right px-4 py-2.5 text-sm text-ink hover:bg-surface-muted transition-colors flex items-center gap-3 font-medium">
                  <svg class="w-4 h-4 text-ink-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                  פרטי משתמש
                </button>
                <button v-if="isAdmin" @click="showSettings = true; showUserMenu = false" class="w-full text-right px-4 py-2.5 text-sm text-ink hover:bg-surface-muted transition-colors flex items-center gap-3 font-medium">
                  <svg class="w-4 h-4 text-ink-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                  הגדרות
                </button>
                <hr class="border-border my-1" />
                <button @click="logout(); showUserMenu = false" class="w-full text-right px-4 py-2.5 text-sm text-negative hover:bg-negative-soft transition-colors flex items-center gap-3 font-medium">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                  התנתקות
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Mobile menu -->
    <transition name="slide-down">
      <div v-if="mobileMenuOpen" class="fixed inset-0 top-16 z-20 bg-bg md:hidden overflow-y-auto" dir="rtl">
        <div class="max-w-app mx-auto px-6 py-5 flex flex-col gap-1.5 ui-safe-bottom">
          <button @click="mobileNav('dashboard')" class="ui-mobile-nav-item" :class="{ 'is-active': activeTab === 'dashboard' }">דשבורד</button>
          <button v-if="isAdmin" @click="mobileNav('operations')" class="ui-mobile-nav-item" :class="{ 'is-active': activeTab === 'operations' }">תפעול</button>
          <button v-if="userProfile?.role === 'project_manager'" @click="mobileNav('my-projects')" class="ui-mobile-nav-item" :class="{ 'is-active': activeTab === 'my-projects' }">הפרויקטים שלי</button>
          <button @click="mobileNav('cashflow')" class="ui-mobile-nav-item" :class="{ 'is-active': activeTab === 'cashflow' }">תזרים מזומנים</button>

          <div class="text-xs font-semibold text-ink-faint uppercase tracking-wider mt-4 mb-1 px-2">פרויקטים</div>
          <button v-for="p in projects" :key="p" @click="selectProject(p)"
            class="ui-mobile-nav-item text-sm"
            :class="{ 'is-active': activeTab === 'pnl' && selectedProject === p }">
            {{ p }}
          </button>

          <hr class="border-border my-4" />

          <button v-if="canEdit" @click="showNewProjectModal = true; mobileMenuOpen = false" class="ui-btn ui-btn-primary self-start">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" d="M12 4v16m8-8H4"/></svg>
            פרויקט חדש
          </button>
          <button @click="showUserProfile = true; mobileMenuOpen = false" class="ui-mobile-nav-item">פרטי משתמש</button>
          <button v-if="isAdmin" @click="showSettings = true; mobileMenuOpen = false" class="ui-mobile-nav-item">הגדרות</button>
          <button @click="logout(); mobileMenuOpen = false" class="ui-mobile-nav-item ui-mobile-nav-item--danger">יציאה</button>
        </div>
      </div>
    </transition>

    <!-- Page content -->
    <main class="px-4 sm:px-8 py-6 sm:py-10 max-w-app mx-auto">
      <Transition name="view-fade" mode="out-in">
        <KeepAlive :max="5">
          <ExecutiveDashboard v-if="activeTab === 'dashboard' && userProfile?.role === 'admin'"
            :key="'exec'"
            @switch-to-operations="activeTab = 'operations'"
            @new-project="showNewProjectModal = true" />
          <Dashboard v-else-if="activeTab === 'dashboard' || activeTab === 'operations'" :key="'dash'" />
          <MyProjectsView v-else-if="activeTab === 'my-projects'" :key="'myproj'"
            @select-project="(p) => { selectedProject = p; activeTab = 'pnl' }" />
          <CashFlowView v-else-if="activeTab === 'cashflow'" :key="'cf'" />
          <PnlView v-else-if="activeTab === 'pnl'" :key="'pnl-' + selectedProject" :initialProject="selectedProject" />
        </KeepAlive>
      </Transition>
    </main>

    <!-- Footer -->
    <footer class="max-w-app mx-auto px-4 sm:px-8 py-8 mt-8">
      <hr class="border-border" />
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-5 text-[12px] text-ink-faint font-medium">
        <div>IFMLogiX · ניהול פיננסי חכם · © {{ new Date().getFullYear() }}</div>
        <div>{{ userRoleLabel }} · {{ userDisplayName }}</div>
      </div>
    </footer>

    <!-- Modals -->
    <ProjectFormModal
      :show="showNewProjectModal"
      :new-project="true"
      project=""
      @close="showNewProjectModal = false"
      @saved="onProjectSaved"
    />
    <UserProfileModal :show="showUserProfile" @close="showUserProfile = false; getProfile().then(p => userProfile = p).catch(() => {})" />
    <SettingsModal :show="showSettings" @close="showSettings = false" />

    <!-- Toast notifications -->
    <Teleport to="body">
      <div class="fixed top-5 left-1/2 -translate-x-1/2 z-[200] flex flex-col gap-2.5 w-full max-w-sm px-4" dir="rtl">
        <TransitionGroup name="toast">
          <div v-for="t in toasts" :key="t.id"
            class="ui-toast"
            :class="'ui-toast--' + t.type"
            @click="dismissToast(t.id)">
            <div class="flex items-start gap-2.5">
              <svg v-if="t.type === 'success'" class="w-4.5 h-4.5 text-accent mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              <svg v-else-if="t.type === 'error'" class="w-4.5 h-4.5 text-negative mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              <svg v-else-if="t.type === 'warning'" class="w-4.5 h-4.5 text-warning mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              <svg v-else class="w-4.5 h-4.5 text-ink-muted mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              <span class="font-sans text-sm font-medium text-ink leading-snug">{{ t.message }}</span>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showAlertsModal" class="ui-dropdown-backdrop" @click="showAlertsModal = false"></div>
      <div v-if="showAlertsModal" dir="rtl"
        class="ui-alerts-panel ed-fade-up"
        :style="alertsPanelStyle">
        <div class="flex items-center justify-between px-5 py-4 border-b border-border">
          <div>
            <h3 class="font-sans font-semibold text-ink text-base leading-tight">התראות</h3>
            <p class="text-[11px] text-ink-muted mt-0.5">{{ alerts.length }} התראות פעילות</p>
          </div>
          <div class="flex items-center gap-3">
            <button v-if="alerts.length > 0" @click="alerts = []; alertCount = 0" class="text-[11px] text-ink-muted hover:text-ink font-medium transition-colors">נקה הכל</button>
            <button @click="showAlertsModal = false" class="text-ink-muted hover:text-ink transition-colors" aria-label="סגור">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="ui-alerts-panel__body">
          <div v-if="alerts.length === 0" class="py-14 text-center px-6">
            <div class="w-11 h-11 bg-accent-soft rounded-full flex items-center justify-center mx-auto mb-3">
              <svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
            </div>
            <h4 class="font-sans font-semibold text-ink text-sm">הכל תקין</h4>
            <p class="text-[12px] text-ink-muted mt-1">כל הפרויקטים פועלים בטווח הצפוי</p>
          </div>
          <button v-for="(alert, i) in alerts" :key="i"
            @click="goToAlertProject(alert.project)"
            class="w-full text-right px-5 py-3.5 border-b border-border hover:bg-surface-muted transition-colors group flex items-start gap-3">
            <div class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5"
              :class="alert.severity === 'high' ? 'bg-negative-soft text-negative' : 'bg-warning-soft text-warning'">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline gap-2 mb-0.5 flex-wrap">
                <span class="font-sans font-semibold text-ink text-[13px] group-hover:text-accent transition-colors">{{ alert.project }}</span>
                <span class="ui-pill" :class="alert.severity === 'high' ? 'ui-pill-negative' : 'ui-pill-warning'">
                  {{ alert.severity === 'high' ? 'חמור' : 'בינוני' }}
                </span>
              </div>
              <div class="text-[12px] text-ink-muted leading-snug">{{ alert.message }}</div>
              <div v-if="alert.detail" class="text-[10.5px] text-ink-faint mt-1">{{ alert.detail }}</div>
            </div>
          </button>
        </div>
      </div>
    </Teleport>

    <AiChat />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { auth } from './firebase'
import { onAuthStateChanged, signOut } from 'firebase/auth'
import LoginPage from './components/LoginPage.vue'
import Dashboard from './components/Dashboard.vue'
import ExecutiveDashboard from './components/ExecutiveDashboard.vue'
import MyProjectsView from './components/MyProjectsView.vue'
import PnlView from './components/PnlView.vue'
import CashFlowView from './components/CashFlowView.vue'
import { SectionMarker } from './components/editorial'
import { getPnl, getProjects, getProjectsDetail, getProfile } from './services/api'
import { createToastProvider, setGlobalToast } from './composables/useToast'

const ProjectFormModal = defineAsyncComponent(() => import('./components/ProjectFormModal.vue'))
const UserProfileModal = defineAsyncComponent(() => import('./components/UserProfileModal.vue'))
const SettingsModal = defineAsyncComponent(() => import('./components/SettingsModal.vue'))
const AiChat = defineAsyncComponent(() => import('./components/AiChat.vue'))

const isLoggedIn = ref(false)
const authReady = ref(false)

onMounted(() => {
  onAuthStateChanged(auth, async (user) => {
    if (user) {
      try {
        await user.getIdToken(true)
      } catch {
        await signOut(auth)
        isLoggedIn.value = false
        authReady.value = true
        return
      }
      isLoggedIn.value = true
      authReady.value = true
      loadAppData()
      getProfile().then(p => {
        if (p.role === 'project_manager') {
          activeTab.value = 'my-projects'
        }
      }).catch(() => {})
    } else {
      isLoggedIn.value = false
      authReady.value = true
    }
  })
})

const activeTab = ref('dashboard')
const showNewProjectModal = ref(false)
const showUserMenu = ref(false)
const showUserProfile = ref(false)
const showSettings = ref(false)
const { toasts, toast, dismiss: dismissToast } = createToastProvider()
setGlobalToast(toast)
const showAlertsModal = ref(false)
const userProfile = ref({ username: '', full_name: '', role: '', avatar: '' })
const alerts = ref([])
const alertCount = ref(0)
const mobileMenuOpen = ref(false)
const pnlOpen = ref(false)
const projects = ref([])
const projectsDetail = ref([])
const selectedProject = ref('')
const projectsBtn = ref(null)
const alertsBtn = ref(null)

const userDisplayName = computed(() => userProfile.value.full_name || userProfile.value.username || 'משתמש')
const userInitials = computed(() => {
  const name = userProfile.value.full_name || userProfile.value.username || ''
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || 'U'
})

const ROLE_LABELS = { admin: 'מנהל מערכת', economist: 'כלכלנית', viewer: 'צופה מלא', project_manager: 'מנהל פרויקט' }
const userRoleLabel = computed(() => ROLE_LABELS[userProfile.value.role] || userProfile.value.role || 'IFMLogiX')
const isAdmin = computed(() => userProfile.value.role === 'admin')
const isEditor = computed(() => ['admin', 'economist'].includes(userProfile.value.role))
const canEdit = computed(() => isEditor.value)

const dropdownStyle = computed(() => {
  if (!projectsBtn.value) return {}
  const rect = projectsBtn.value.getBoundingClientRect()
  return {
    top: rect.bottom + 8 + 'px',
    right: (window.innerWidth - rect.right) + 'px',
  }
})

const alertsPanelStyle = computed(() => {
  if (!alertsBtn.value) return {}
  const rect = alertsBtn.value.getBoundingClientRect()
  return {
    top: rect.bottom + 10 + 'px',
    right: Math.max(8, window.innerWidth - rect.right - 4) + 'px',
  }
})

function goHome() {
  activeTab.value = 'dashboard'
  selectedProject.value = ''
}

function logout() {
  signOut(auth)
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
  getProfile().then(p => { userProfile.value = p }).catch(() => {})
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
      const startMonth = project.meta?.start_month || 1
      const endMonth = project.meta?.end_month || 12
      const projectMonths = project.months.filter(m => m.month >= startMonth && m.month <= endMonth)
      const zeroMonths = projectMonths.filter(m => m.revenue === 0)
      if (zeroMonths.length > 0 && zeroMonths.length >= projectMonths.length / 2) {
        list.push({
          project: name,
          severity: 'medium',
          message: `${zeroMonths.length} חודשים ללא הכנסה (מתוך ${projectMonths.length} חודשי פרויקט)`,
          detail: `חודשים: ${zeroMonths.map(m => m.month).join(', ')}`,
        })
      }
    }
    alerts.value = list
    alertCount.value = list.length
  }).catch(() => {})
}
</script>

<style scoped>
/* Brand mark — small rounded square with emerald-to-ink gradient */
.ui-logo-mark {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: linear-gradient(135deg, #059669 0%, #0f172a 100%);
  box-shadow: 0 2px 6px rgba(5, 150, 105, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  position: relative;
  flex-shrink: 0;
}
.ui-logo-mark::after {
  content: "L";
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 15px;
  letter-spacing: -0.02em;
}

/* Mobile nav item */
.ui-mobile-nav-item {
  display: block;
  width: 100%;
  text-align: right;
  padding: 0.75rem 1rem;
  font-family: var(--font-sans);
  font-size: 1rem;
  font-weight: 500;
  color: var(--ink);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}
.ui-mobile-nav-item:hover {
  background: var(--surface-muted);
}
.ui-mobile-nav-item.is-active {
  background: var(--ink);
  color: #ffffff;
  font-weight: 600;
}
.ui-mobile-nav-item--danger {
  color: var(--negative);
}
.ui-mobile-nav-item--danger:hover {
  background: var(--negative-soft);
}

/* Top nav bar — fully opaque, never translucent */
.ui-topbar {
  background: #ffffff;
  -webkit-backdrop-filter: none;
  backdrop-filter: none;
}

/* Dropdown (projects picker) */
.ui-dropdown-backdrop {
  position: fixed;
  inset: 0;
  z-index: 90;
}
.ui-dropdown {
  position: fixed;
  z-index: 100;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 0.5rem 0;
  min-width: 280px;
  max-height: 20rem;
  overflow-y: auto;
}

/* Alerts panel — anchored dropdown beneath the bell */
.ui-alerts-panel {
  position: fixed;
  z-index: 100;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: min(380px, calc(100vw - 16px));
  max-height: min(560px, calc(100vh - 120px));
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.ui-alerts-panel__body {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

/* Toast notifications */
.ui-toast {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-inline-start: 3px solid var(--ink-muted);
}
.ui-toast--success { border-inline-start-color: var(--accent); }
.ui-toast--error   { border-inline-start-color: var(--negative); }
.ui-toast--warning { border-inline-start-color: var(--warning); }

.toast-enter-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.toast-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.toast-move { transition: transform 0.25s ease; }
.toast-enter-from { opacity: 0; transform: translateY(-12px) scale(0.95); }
.toast-leave-to   { opacity: 0; transform: translateY(-8px) scale(0.97); }

/* View transition (tab switching) */
.view-fade-enter-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.view-fade-leave-active { transition: opacity 0.1s ease; }
.view-fade-enter-from { opacity: 0; transform: translateY(6px); }
.view-fade-leave-to   { opacity: 0; }
</style>
