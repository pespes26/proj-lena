<template>
  <Teleport to="body">
    <div v-if="show" class="ui-modal-layer" dir="rtl">
      <div class="ui-modal-backdrop" @click="$emit('close')"></div>
      <div class="ui-modal-card ed-fade-up" style="max-width: 36rem;">
        <!-- Header -->
        <header class="px-7 pt-6 pb-4">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="ed-eyebrow mb-1">פרופיל אישי</div>
              <h2 class="font-sans font-semibold text-ink leading-none" style="font-size: clamp(1.75rem, 3vw, 2.25rem);">פרטי משתמש</h2>
            </div>
            <button @click="$emit('close')" class="p-2 -m-2 rounded-lg text-ink-muted hover:text-accent hover:bg-surface-muted transition-colors" aria-label="סגור">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="square" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <hr class="ed-rule mt-4" />
        </header>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-7 py-5 space-y-8">
          <!-- Avatar -->
          <div class="flex flex-col items-center gap-3">
            <div class="relative group cursor-pointer" @click="$refs.avatarInput.click()">
              <div class="w-28 h-28 bg-paper-light border border-rule-strong flex items-center justify-center overflow-hidden">
                <img v-if="form.avatar" :src="form.avatar" class="w-full h-full object-cover" alt="" />
                <span v-else class="font-sans font-semibold text-3xl text-ink">{{ initials }}</span>
              </div>
              <div class="absolute inset-0 bg-ink/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                <span class="font-sans text-paper text-sm">שינוי תמונה</span>
              </div>
            </div>
            <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
            <span class="ed-eyebrow">לחץ לשינוי תמונה</span>
          </div>

          <!-- Fields -->
          <div class="space-y-6">
            <div>
              <label class="ed-label">שם משתמש</label>
              <input :value="form.username" disabled class="ed-input" style="color: var(--ink-faint); border-bottom-style: dashed;" />
            </div>
            <div>
              <label class="ed-label">שם מלא</label>
              <input v-model="form.full_name" type="text" placeholder="השם המלא שלך" class="ed-input" />
            </div>
            <div>
              <label class="ed-label">אימייל</label>
              <input v-model="form.email" type="email" placeholder="name@example.com" dir="ltr" class="ed-input" />
            </div>
            <div>
              <label class="ed-label">הרשאה</label>
              <div class="font-display text-ink pt-2.5 pb-2.5 border-b border-rule-strong" style="border-bottom-style: dashed;">
                {{ roleLabels[form.role] || form.role }}
              </div>
              <p class="font-sans text-ink-faint text-xs mt-1.5">שינוי הרשאה מתבצע רק דרך הגדרות מערכת</p>
            </div>
          </div>

          <!-- Change password -->
          <div class="border-t border-rule pt-6">
            <button @click="showPasswordSection = !showPasswordSection" class="ed-link text-sm">
              {{ showPasswordSection ? 'ביטול שינוי סיסמה ←' : 'שינוי סיסמה →' }}
            </button>
            <div v-if="showPasswordSection" class="mt-5 space-y-5 ed-fade-up">
              <div>
                <label class="ed-label">סיסמה נוכחית</label>
                <input v-model="passwords.current" type="password" class="ed-input" />
              </div>
              <div>
                <label class="ed-label">סיסמה חדשה</label>
                <input v-model="passwords.new_password" type="password" class="ed-input" />
              </div>
              <div>
                <label class="ed-label">אישור סיסמה חדשה</label>
                <input v-model="passwords.confirm" type="password" class="ed-input" />
              </div>
              <button @click="handleChangePassword" :disabled="saving" class="ed-btn ed-btn-primary">
                שנה סיסמה →
              </button>
            </div>
          </div>

          <!-- Messages -->
          <p
            v-if="message"
            class="font-sans text-sm"
            :class="messageType === 'success' ? 'ed-tone-positive' : 'ed-tone-negative'"
          >
            {{ message }}
          </p>
        </div>

        <!-- Footer -->
        <footer class="px-7 py-5 border-t border-rule-strong flex justify-between gap-4">
          <button @click="$emit('close')" class="ed-link text-sm">ביטול</button>
          <button @click="handleSave" :disabled="saving" class="ed-btn ed-btn-primary">
            {{ saving ? 'שומר…' : 'שמירה' }} →
          </button>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { getProfile, updateProfile } from '../services/api'
import { auth } from '../firebase'
import { updatePassword, EmailAuthProvider, reauthenticateWithCredential } from 'firebase/auth'
import { useToast } from '../composables/useToast'

const props = defineProps({ show: Boolean })
defineEmits(['close'])
const toast = useToast()

const roleLabels = { admin: 'מנהל מערכת', economist: 'כלכלנית', viewer: 'צופה מלא', project_manager: 'מנהל פרויקט' }
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
    message.value = 'הפרטים נשמרו בהצלחה'; messageType.value = 'success'; toast.success('הפרטים נשמרו')
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
    const user = auth.currentUser
    const credential = EmailAuthProvider.credential(user.email, passwords.current)
    await reauthenticateWithCredential(user, credential)
    await updatePassword(user, passwords.new_password)
    message.value = 'הסיסמה שונתה בהצלחה'; messageType.value = 'success'
    showPasswordSection.value = false
    passwords.current = ''; passwords.new_password = ''; passwords.confirm = ''
  } catch (e) { message.value = e.message; messageType.value = 'error' }
  saving.value = false
}
</script>
