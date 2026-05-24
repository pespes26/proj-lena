<template>
  <Teleport to="body">
    <div v-if="show" class="ui-modal-layer" dir="rtl">
      <div class="ui-modal-backdrop" @click="$emit('close')"></div>
      <div ref="modalCard" class="ui-modal-card" style="max-width: 48rem;">
        <!-- Header -->
        <header class="px-7 pt-6 pb-4">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="ui-label mb-1">מערכת</div>
              <h2 class="ui-modal-title">הגדרות</h2>
            </div>
            <button @click="$emit('close')" class="ui-icon-btn" aria-label="סגור">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <hr class="ui-divider mt-4" />

          <!-- Tabs (ed-link style — keyboard/click, no animation) -->
          <div class="flex gap-x-6 mt-4">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              type="button"
              class="ed-link text-sm"
              :class="{ 'is-active': activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
        </header>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-7 py-6">

          <!-- Users Tab -->
          <div v-if="activeTab === 'users'">
            <div class="flex items-center justify-between mb-5">
              <h3 class="ui-section-title">משתמשים רשומים</h3>
              <button type="button" @click="showAddUser = !showAddUser" class="ui-btn">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" d="M12 4v16m8-8H4"/></svg>
                הוסף משתמש
              </button>
            </div>

            <!-- Add user form -->
            <div v-if="showAddUser" class="ui-inset-card mb-6">
              <div class="ui-label mb-4">משתמש חדש</div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                <div>
                  <label class="ui-form-label" for="settings-username">שם משתמש *</label>
                  <input id="settings-username" v-model="newUser.username" type="text" class="ui-input" />
                </div>
                <div>
                  <label class="ui-form-label" for="settings-password">סיסמה *</label>
                  <input id="settings-password" v-model="newUser.password" type="password" class="ui-input" />
                </div>
                <div>
                  <label class="ui-form-label" for="settings-fullname">שם מלא</label>
                  <input id="settings-fullname" v-model="newUser.full_name" type="text" class="ui-input" />
                </div>
                <div>
                  <label class="ui-form-label" for="settings-email">אימייל</label>
                  <input id="settings-email" v-model="newUser.email" type="email" dir="ltr" class="ui-input" />
                </div>
                <div>
                  <label class="ui-form-label" for="settings-role">הרשאה</label>
                  <select id="settings-role" v-model="newUser.role" class="ui-select">
                    <option value="admin">מנהל מערכת</option>
                    <option value="economist">כלכלנית</option>
                    <option value="viewer">צופה מלא</option>
                    <option value="project_manager">מנהל פרויקט</option>
                  </select>
                </div>
                <div v-if="newUser.role === 'project_manager'">
                  <label class="ui-form-label" for="settings-manager">מנהל משויך *</label>
                  <select id="settings-manager" v-model="newUser.linked_manager" class="ui-select">
                    <option value="" disabled>בחר מנהל</option>
                    <option value="אלון">אלון</option>
                    <option value="אתי">אתי</option>
                    <option value="אריאל">אריאל</option>
                  </select>
                </div>
              </div>
              <div class="flex justify-end gap-3 mt-6">
                <button type="button" @click="showAddUser = false" class="ui-btn">ביטול</button>
                <button type="button" @click="handleCreateUser" :disabled="saving" class="ui-btn ui-btn-dark">
                  {{ saving ? 'יוצר…' : 'צור משתמש' }}
                </button>
              </div>
            </div>

            <!-- Users table -->
            <div class="overflow-x-auto">
              <table class="ui-table">
                <thead>
                  <tr>
                    <th>שם משתמש</th>
                    <th>שם מלא</th>
                    <th>הרשאה</th>
                    <th>מנהל משויך</th>
                    <th style="width: 120px;">פעולות</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in users" :key="u.username">
                    <td class="font-semibold">{{ u.username }}</td>
                    <td>
                      <template v-if="editingUser === u.username">
                        <input v-model="editForm.full_name" type="text" class="ui-input" aria-label="שם מלא" />
                      </template>
                      <template v-else>{{ u.full_name || '—' }}</template>
                    </td>
                    <td>
                      <template v-if="editingUser === u.username">
                        <select v-model="editForm.role" class="ui-select" aria-label="הרשאה">
                          <option value="admin">מנהל מערכת</option>
                          <option value="economist">כלכלנית</option>
                          <option value="viewer">צופה מלא</option>
                          <option value="project_manager">מנהל פרויקט</option>
                        </select>
                      </template>
                      <template v-else>
                        <span class="ui-pill" :class="rolePillClass(u.role)">{{ roleLabel(u.role) }}</span>
                      </template>
                    </td>
                    <td>
                      <template v-if="editingUser === u.username && editForm.role === 'project_manager'">
                        <select v-model="editForm.linked_manager" class="ui-select" aria-label="מנהל משויך">
                          <option value="">בחר</option>
                          <option value="אלון">אלון</option>
                          <option value="אתי">אתי</option>
                          <option value="אריאל">אריאל</option>
                        </select>
                      </template>
                      <template v-else>{{ u.linked_manager || '—' }}</template>
                    </td>
                    <td>
                      <div class="flex items-center gap-2">
                        <template v-if="editingUser === u.username">
                          <button type="button" @click="handleSaveUser" class="ui-icon-btn ed-tone-positive" title="שמור" aria-label="שמור">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                          </button>
                          <button type="button" @click="editingUser = ''" class="ui-icon-btn" title="ביטול" aria-label="ביטול">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                          </button>
                        </template>
                        <template v-else>
                          <button type="button" @click="startEdit(u)" class="ui-icon-btn" title="ערוך" aria-label="ערוך">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                          </button>
                          <button type="button" @click="handleDeleteUser(u.username)" class="ui-icon-btn ed-tone-negative" title="מחק" aria-label="מחק">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                          </button>
                        </template>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- General Settings Tab -->
          <div v-if="activeTab === 'general'" class="space-y-8">
            <div>
              <div class="ui-label mb-2">שפה</div>
              <div class="ui-value-text">עברית</div>
              <p class="ui-help-text">ברירת מחדל של המערכת</p>
            </div>
            <hr class="ui-divider" />
            <div>
              <div class="ui-label mb-2">ברירות מחדל — תנאי תשלום</div>
              <p class="ui-help-text">בקרוב — הגדרת תנאי תשלום ברירת מחדל לפרויקטים חדשים.</p>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <p
          v-if="message"
          class="mx-7 mb-5 font-sans text-sm"
          :class="messageType === 'success' ? 'ed-tone-positive' : 'ed-tone-negative'"
        >
          {{ message }}
        </p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.ui-modal-title {
  font-family: var(--font-sans);
  font-weight: 600;
  color: var(--ink);
  font-size: clamp(1.5rem, 3vw, 1.875rem);
  line-height: 1.1;
  letter-spacing: -0.01em;
}
.ui-section-title {
  font-family: var(--font-sans);
  font-weight: 600;
  color: var(--ink);
  font-size: 1.125rem;
  letter-spacing: -0.005em;
}
.ui-inset-card {
  background: var(--surface-muted);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.25rem 1.25rem;
}
.ui-value-text {
  font-family: var(--font-sans);
  font-weight: 500;
  font-size: 1rem;
  color: var(--ink);
}
.ui-help-text {
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  color: var(--ink-muted);
  margin-top: 0.25rem;
}
</style>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { getUsers, createUser, deleteUser, updateUser } from '../services/api'
import { useToast } from '../composables/useToast'
import { useFocusTrap } from '../composables/useFocusTrap'

const props = defineProps({ show: Boolean })
defineEmits(['close'])
const toast = useToast()
const modalCard = ref(null)
const { activate, deactivate } = useFocusTrap(modalCard)
watch(() => props.show, async (val) => {
  if (val) { await nextTick(); activate() } else { deactivate() }
})

const ROLE_MAP = {
  admin: 'מנהל מערכת',
  economist: 'כלכלנית',
  viewer: 'צופה מלא',
  project_manager: 'מנהל פרויקט',
}

function roleLabel(role) { return ROLE_MAP[role] || role || '—' }

const ROLE_PILL = {
  admin: 'ui-pill-positive',
  economist: 'ui-pill-positive',
  project_manager: 'ui-pill-warning',
  viewer: 'ui-pill-neutral',
}
function rolePillClass(role) { return ROLE_PILL[role] || 'ui-pill-neutral' }

const tabs = [
  { key: 'users', label: 'ניהול משתמשים' },
  { key: 'general', label: 'הגדרות כלליות' },
]
const activeTab = ref('users')
const users = ref([])
const showAddUser = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')
const newUser = reactive({ username: '', password: '', full_name: '', email: '', role: 'viewer', linked_manager: '' })
const editingUser = ref('')
const editForm = reactive({ full_name: '', role: '', linked_manager: '' })

watch(() => props.show, async (val) => {
  if (val) {
    message.value = ''
    showAddUser.value = false
    try { users.value = await getUsers() } catch (e) { message.value = e.message; messageType.value = 'error' }
  }
})

async function handleCreateUser() {
  if (!newUser.username || !newUser.password) {
    message.value = 'שם משתמש וסיסמה הם שדות חובה'; messageType.value = 'error'; return
  }
  if (newUser.role === 'project_manager' && !newUser.linked_manager) {
    message.value = 'יש לבחור מנהל משויך עבור מנהל פרויקט'; messageType.value = 'error'; return
  }
  saving.value = true; message.value = ''
  try {
    await createUser({ ...newUser })
    message.value = `משתמש '${newUser.username}' נוצר`; messageType.value = 'success'; toast.success(`משתמש '${newUser.username}' נוצר`)
    Object.assign(newUser, { username: '', password: '', full_name: '', email: '', role: 'viewer', linked_manager: '' })
    showAddUser.value = false
    users.value = await getUsers()
  } catch (e) { message.value = e.message; messageType.value = 'error' }
  saving.value = false
}

function startEdit(u) {
  editingUser.value = u.username
  editForm.full_name = u.full_name || ''
  editForm.role = u.role || 'viewer'
  editForm.linked_manager = u.linked_manager || ''
}

async function handleSaveUser() {
  message.value = ''
  try {
    await updateUser(editingUser.value, {
      full_name: editForm.full_name,
      role: editForm.role,
      linked_manager: editForm.role === 'project_manager' ? editForm.linked_manager : '',
    })
    editingUser.value = ''
    users.value = await getUsers()
    message.value = 'המשתמש עודכן'; messageType.value = 'success'; toast.success('המשתמש עודכן')
  } catch (e) { message.value = e.message; messageType.value = 'error' }
}

async function handleDeleteUser(username) {
  if (!confirm(`למחוק את המשתמש '${username}'?`)) return
  try {
    await deleteUser(username)
    users.value = await getUsers()
    message.value = `משתמש '${username}' נמחק`; messageType.value = 'success'; toast.success(`משתמש '${username}' נמחק`)
  } catch (e) { message.value = e.message; messageType.value = 'error' }
}
</script>
