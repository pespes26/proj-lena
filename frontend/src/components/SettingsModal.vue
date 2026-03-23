<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-[80] flex items-center justify-center" dir="rtl">
      <div class="absolute inset-0 bg-black/40" @click="$emit('close')"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 class="text-lg font-bold text-gray-800">הגדרות</h2>
          <button @click="$emit('close')" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 px-6 pt-4 border-b border-gray-100">
          <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
            :class="['px-4 py-2.5 text-sm font-medium rounded-t-lg transition -mb-px', activeTab === tab.key ? 'bg-white border border-gray-100 border-b-white text-gray-900' : 'text-gray-500 hover:text-gray-700']">
            {{ tab.label }}
          </button>
        </div>

        <!-- Content -->
        <div class="px-6 py-5">

          <!-- Users Tab -->
          <div v-if="activeTab === 'users'">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-semibold text-gray-700">משתמשים רשומים</h3>
              <button @click="showAddUser = !showAddUser" class="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 transition">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                הוסף משתמש
              </button>
            </div>

            <!-- Add user form -->
            <div v-if="showAddUser" class="bg-gray-50 rounded-xl p-4 mb-4 space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">שם משתמש *</label>
                  <input v-model="newUser.username" type="text" class="w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">סיסמה *</label>
                  <input v-model="newUser.password" type="password" class="w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">שם מלא</label>
                  <input v-model="newUser.full_name" type="text" class="w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">אימייל</label>
                  <input v-model="newUser.email" type="email" dir="ltr" class="w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-left focus:outline-none focus:ring-2 focus:ring-emerald-300" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">תפקיד</label>
                  <select v-model="newUser.role" class="w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300">
                    <option value="מנהל">מנהל</option>
                    <option value="צופה">צופה</option>
                  </select>
                </div>
              </div>
              <div class="flex justify-end gap-2">
                <button @click="showAddUser = false" class="px-4 py-2 text-xs font-medium text-gray-500 hover:bg-gray-100 rounded-lg transition">ביטול</button>
                <button @click="handleCreateUser" :disabled="saving" class="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 disabled:opacity-50 transition">צור משתמש</button>
              </div>
            </div>

            <!-- Users table -->
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-gray-100">
                    <th class="text-right py-2.5 px-3 text-xs font-semibold text-gray-500">שם משתמש</th>
                    <th class="text-right py-2.5 px-3 text-xs font-semibold text-gray-500">שם מלא</th>
                    <th class="text-right py-2.5 px-3 text-xs font-semibold text-gray-500">אימייל</th>
                    <th class="text-right py-2.5 px-3 text-xs font-semibold text-gray-500">תפקיד</th>
                    <th class="text-right py-2.5 px-3 text-xs font-semibold text-gray-500">הרשאות</th>
                    <th class="py-2.5 px-3"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in users" :key="u.username" class="border-b border-gray-50 hover:bg-gray-50/50">
                    <td class="py-3 px-3 font-medium text-gray-800">{{ u.username }}</td>
                    <td class="py-3 px-3 text-gray-600">{{ u.full_name || '-' }}</td>
                    <td class="py-3 px-3 text-gray-600" dir="ltr">{{ u.email || '-' }}</td>
                    <td class="py-3 px-3">
                      <span :class="['px-2.5 py-1 rounded-full text-xs font-medium', u.role === 'מנהל' ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-600']">{{ u.role || 'מנהל' }}</span>
                    </td>
                    <td class="py-3 px-3">
                      <span class="text-xs text-gray-400">בקרוב</span>
                    </td>
                    <td class="py-3 px-3">
                      <button @click="handleDeleteUser(u.username)" class="p-1.5 rounded-lg hover:bg-red-50 text-gray-300 hover:text-red-500 transition" title="מחק">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- General Settings Tab -->
          <div v-if="activeTab === 'general'" class="space-y-6">
            <div>
              <h3 class="text-sm font-semibold text-gray-700 mb-3">שפה</h3>
              <div class="flex items-center gap-3 bg-gray-50 rounded-xl p-4">
                <span class="text-sm text-gray-600">עברית</span>
                <span class="text-xs text-gray-400">(ברירת מחדל)</span>
              </div>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-gray-700 mb-3">ברירות מחדל — תנאי תשלום</h3>
              <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-400">בקרוב — הגדרת תנאי תשלום ברירת מחדל לפרויקטים חדשים</div>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-gray-700 mb-3">קטגוריות הוצאות</h3>
              <div class="bg-gray-50 rounded-xl p-4 text-sm text-gray-400">בקרוב — ניהול וקסטום של קטגוריות הוצאות</div>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div v-if="message" :class="['mx-6 mb-4 text-sm px-4 py-2.5 rounded-lg', messageType === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600']">{{ message }}</div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { getUsers, createUser, deleteUser } from '../services/api'

const props = defineProps({ show: Boolean })
defineEmits(['close'])

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
const newUser = reactive({ username: '', password: '', full_name: '', email: '', role: 'צופה' })

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
  saving.value = true; message.value = ''
  try {
    await createUser({ ...newUser })
    message.value = `משתמש '${newUser.username}' נוצר`; messageType.value = 'success'
    newUser.username = ''; newUser.password = ''; newUser.full_name = ''; newUser.email = ''; newUser.role = 'צופה'
    showAddUser.value = false
    users.value = await getUsers()
  } catch (e) { message.value = e.message; messageType.value = 'error' }
  saving.value = false
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
