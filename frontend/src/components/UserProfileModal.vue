<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-[80] flex items-center justify-center" dir="rtl">
      <div class="absolute inset-0 bg-black/40" @click="$emit('close')"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 class="text-lg font-bold text-gray-800">פרטי משתמש</h2>
          <button @click="$emit('close')" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Content -->
        <div class="px-6 py-5 space-y-6">
          <!-- Avatar -->
          <div class="flex flex-col items-center gap-3">
            <div class="relative group cursor-pointer" @click="$refs.avatarInput.click()">
              <div class="w-24 h-24 rounded-full bg-emerald-100 flex items-center justify-center overflow-hidden border-4 border-white shadow-lg">
                <img v-if="form.avatar" :src="form.avatar" class="w-full h-full object-cover" />
                <span v-else class="text-emerald-800 font-bold text-2xl">{{ initials }}</span>
              </div>
              <div class="absolute inset-0 rounded-full bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              </div>
            </div>
            <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
            <span class="text-xs text-gray-400">לחץ לשינוי תמונה</span>
          </div>

          <!-- Fields -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">שם משתמש</label>
              <input :value="form.username" disabled class="w-full bg-gray-100 border border-gray-200 rounded-lg px-4 py-2.5 text-sm text-gray-500 cursor-not-allowed" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">שם מלא</label>
              <input v-model="form.full_name" type="text" placeholder="השם המלא שלך" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">אימייל</label>
              <input v-model="form.email" type="email" placeholder="email@example.com" dir="ltr" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition text-left" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">תפקיד</label>
              <input v-model="form.role" type="text" placeholder="מנהל / צופה" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition" />
            </div>
          </div>

          <!-- Change password -->
          <div class="border-t border-gray-100 pt-5">
            <button @click="showPasswordSection = !showPasswordSection" class="text-sm font-medium text-emerald-600 hover:text-emerald-700 transition">
              {{ showPasswordSection ? 'ביטול שינוי סיסמה' : 'שינוי סיסמה' }}
            </button>
            <div v-if="showPasswordSection" class="mt-4 space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">סיסמה נוכחית</label>
                <input v-model="passwords.current" type="password" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">סיסמה חדשה</label>
                <input v-model="passwords.new_password" type="password" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">אישור סיסמה חדשה</label>
                <input v-model="passwords.confirm" type="password" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition" />
              </div>
              <button @click="handleChangePassword" :disabled="saving" class="w-full py-2.5 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition">
                שנה סיסמה
              </button>
            </div>
          </div>

          <!-- Messages -->
          <div v-if="message" :class="['text-sm px-4 py-2.5 rounded-lg', messageType === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600']">{{ message }}</div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
          <button @click="$emit('close')" class="px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition">ביטול</button>
          <button @click="handleSave" :disabled="saving" class="px-5 py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 disabled:opacity-50 transition">
            {{ saving ? 'שומר...' : 'שמירה' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { getProfile, updateProfile, changePassword } from '../services/api'

const props = defineProps({ show: Boolean })
const emit = defineEmits(['close'])

const form = reactive({ username: '', full_name: '', email: '', role: '', avatar: '' })
const passwords = reactive({ current: '', new_password: '', confirm: '' })
const showPasswordSection = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')

const initials = computed(() => {
  if (form.full_name) return form.full_name.split(' ').map(w => w[0]).join('').slice(0, 2)
  return form.username ? form.username.slice(0, 2).toUpperCase() : 'FM'
})

watch(() => props.show, async (val) => {
  if (val) {
    message.value = ''
    showPasswordSection.value = false
    passwords.current = ''; passwords.new_password = ''; passwords.confirm = ''
    try {
      const data = await getProfile()
      Object.assign(form, data)
    } catch (e) { message.value = e.message; messageType.value = 'error' }
  }
})

function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => { form.avatar = reader.result }
  reader.readAsDataURL(file)
}

async function handleSave() {
  saving.value = true; message.value = ''
  try {
    await updateProfile({ full_name: form.full_name, email: form.email, role: form.role, avatar: form.avatar })
    message.value = 'הפרטים נשמרו בהצלחה'; messageType.value = 'success'
  } catch (e) { message.value = e.message; messageType.value = 'error' }
  saving.value = false
}

async function handleChangePassword() {
  if (passwords.new_password !== passwords.confirm) {
    message.value = 'הסיסמאות לא תואמות'; messageType.value = 'error'; return
  }
  if (passwords.new_password.length < 4) {
    message.value = 'סיסמה חייבת להכיל לפחות 4 תווים'; messageType.value = 'error'; return
  }
  saving.value = true; message.value = ''
  try {
    await changePassword({ current_password: passwords.current, new_password: passwords.new_password })
    message.value = 'הסיסמה שונתה בהצלחה'; messageType.value = 'success'
    showPasswordSection.value = false
    passwords.current = ''; passwords.new_password = ''; passwords.confirm = ''
  } catch (e) { message.value = e.message; messageType.value = 'error' }
  saving.value = false
}
</script>
