<template>
  <Teleport to="body">
    <div v-if="show" class="ui-modal-layer" dir="rtl">
      <div class="ui-modal-backdrop" @click="$emit('close')"></div>
      <div class="ui-modal-card ed-fade-up" style="max-width: 48rem;">
        <!-- Header -->
        <header class="px-7 pt-6 pb-4">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="ed-eyebrow mb-1">מערכת</div>
              <h2 class="font-sans font-semibold text-ink leading-none" style="font-size: clamp(1.75rem, 3vw, 2.25rem);">הגדרות</h2>
            </div>
            <button @click="$emit('close')" class="text-ink-muted hover:text-accent transition-colors" aria-label="סגור">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="square" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <hr class="ed-rule mt-4" />

          <!-- Tabs via section markers -->
          <div class="flex gap-x-8 mt-4">
            <SectionMarker
              v-for="tab in tabs"
              :key="tab.key"
              :label="tab.label"
              :active="activeTab === tab.key"
              @click="activeTab = tab.key"
            />
          </div>
        </header>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-7 py-6">

          <!-- Users Tab -->
          <div v-if="activeTab === 'users'">
            <div class="flex items-center justify-between mb-5">
              <h3 class="font-sans font-semibold text-ink text-xl">משתמשים רשומים</h3>
              <button @click="showAddUser = !showAddUser" class="ed-link text-sm">
                + הוסף משתמש
              </button>
            </div>

            <!-- Add user form -->
            <div v-if="showAddUser" class="bg-paper-dark/30 border-t border-b border-rule-strong py-5 px-5 mb-6 ed-fade-up">
              <div class="ed-eyebrow mb-4">משתמש חדש</div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                <div>
                  <label class="ed-label">שם משתמש *</label>
                  <input v-model="newUser.username" type="text" class="ed-input" />
                </div>
                <div>
                  <label class="ed-label">סיסמה *</label>
                  <input v-model="newUser.password" type="password" class="ed-input" />
                </div>
                <div>
                  <label class="ed-label">שם מלא</label>
                  <input v-model="newUser.full_name" type="text" class="ed-input" />
                </div>
                <div>
                  <label class="ed-label">אימייל</label>
                  <input v-model="newUser.email" type="email" dir="ltr" class="ed-input" />
                </div>
                <div>
                  <label class="ed-label">הרשאה</label>
                  <select v-model="newUser.role" class="ed-select">
                    <option value="admin">מנהל מערכת</option>
                    <option value="economist">כלכלנית</option>
                    <option value="viewer">צופה מלא</option>
                    <option value="project_manager">מנהל פרויקט</option>
                  </select>
                </div>
                <div v-if="newUser.role === 'project_manager'">
                  <label class="ed-label">מנהל משויך *</label>
                  <select v-model="newUser.linked_manager" class="ed-select">
                    <option value="" disabled>בחר מנהל</option>
                    <option value="אלון">אלון</option>
                    <option value="אתי">אתי</option>
                    <option value="אריאל">אריאל</option>
                  </select>
                </div>
              </div>
              <div class="flex justify-end gap-6 mt-6">
                <button @click="showAddUser = false" class="ed-link text-sm">ביטול</button>
                <button @click="handleCreateUser" :disabled="saving" class="ed-btn ed-btn-primary">
                  צור משתמש →
                </button>
              </div>
            </div>

            <!-- Users table -->
            <div class="overflow-x-auto">
              <table class="ed-table">
                <thead>
                  <tr>
                    <th>שם משתמש</th>
                    <th>שם מלא</th>
                    <th>הרשאה</th>
                    <th>מנהל משויך</th>
                    <th style="width: 100px;">פעולות</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in users" :key="u.username">
                    <td class="font-sans font-semibold">{{ u.username }}</td>
                    <td>
                      <template v-if="editingUser === u.username">
                        <input v-model="editForm.full_name" type="text" class="ed-input" />
                      </template>
                      <template v-else>{{ u.full_name || '—' }}</template>
                    </td>
                    <td>
                      <template v-if="editingUser === u.username">
                        <select v-model="editForm.role" class="ed-select">
                          <option value="admin">מנהל מערכת</option>
                          <option value="economist">כלכלנית</option>
                          <option value="viewer">צופה מלא</option>
                          <option value="project_manager">מנהל פרויקט</option>
                        </select>
                      </template>
                      <template v-else>
                        <span class="ed-eyebrow">{{ roleLabel(u.role) }}</span>
                      </template>
                    </td>
                    <td>
                      <template v-if="editingUser === u.username && editForm.role === 'project_manager'">
                        <select v-model="editForm.linked_manager" class="ed-select">
                          <option value="">בחר</option>
                          <option value="אלון">אלון</option>
                          <option value="אתי">אתי</option>
                          <option value="אריאל">אריאל</option>
                        </select>
                      </template>
                      <template v-else>{{ u.linked_manager || '—' }}</template>
                    </td>
                    <td>
                      <div class="flex items-center gap-3">
                        <template v-if="editingUser === u.username">
                          <button @click="handleSaveUser" class="ed-link text-xs ed-tone-positive" title="שמור">שמור</button>
                          <button @click="editingUser = ''" class="ed-link text-xs" title="ביטול">בטל</button>
                        </template>
                        <template v-else>
                          <button @click="startEdit(u)" class="ed-link text-xs" title="ערוך">ערוך</button>
                          <button @click="handleDeleteUser(u.username)" class="ed-link text-xs ed-tone-negative" title="מחק">מחק</button>
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
              <div class="ed-eyebrow mb-3">שפה</div>
              <div class="font-display text-ink text-lg">עברית</div>
              <p class="font-sans text-ink-muted text-sm mt-1">ברירת מחדל של המערכת</p>
            </div>
            <hr class="ed-rule" />
            <div>
              <div class="ed-eyebrow mb-3">ברירות מחדל — תנאי תשלום</div>
              <p class="font-sans text-ink-muted text-sm">בקרוב — הגדרת תנאי תשלום ברירת מחדל לפרויקטים חדשים.</p>
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

<script setup>
import { ref, reactive, watch } from 'vue'
import { getUsers, createUser, deleteUser, updateUser } from '../services/api'
import { SectionMarker } from './editorial'

const props = defineProps({ show: Boolean })
defineEmits(['close'])

const ROLE_MAP = {
  admin: 'מנהל מערכת',
  economist: 'כלכלנית',
  viewer: 'צופה מלא',
  project_manager: 'מנהל פרויקט',
}

function roleLabel(role) { return ROLE_MAP[role] || role || '—' }

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
    message.value = `משתמש '${newUser.username}' נוצר`; messageType.value = 'success'
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
    message.value = 'המשתמש עודכן'; messageType.value = 'success'
  } catch (e) { message.value = e.message; messageType.value = 'error' }
}

async function handleDeleteUser(username) {
  if (!confirm(`למחוק את המשתמש '${username}'?`)) return
  try {
    await deleteUser(username)
    users.value = await getUsers()
    message.value = `משתמש '${username}' נמחק`; messageType.value = 'success'
  } catch (e) { message.value = e.message; messageType.value = 'error' }
}
</script>
