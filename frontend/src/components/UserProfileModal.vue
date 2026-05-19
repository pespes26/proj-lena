<template>
  <Teleport to="body">
    <div v-if="show" class="ui-modal-layer" dir="rtl">
      <div class="ui-modal-backdrop" @click="$emit('close')"></div>
      <div class="ui-modal-card" style="max-width: 36rem;">
        <!-- Header -->
        <header class="px-7 pt-6 pb-4">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="ui-label mb-1">פרופיל אישי</div>
              <h2 class="ui-modal-title">פרטי משתמש</h2>
            </div>
            <button @click="$emit('close')" class="ui-icon-btn" aria-label="סגור">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <hr class="ui-divider mt-4" />
        </header>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-7 py-5 space-y-8">
          <!-- Avatar -->
          <div class="flex flex-col items-center gap-3">
            <div class="ui-avatar-uploader" @click="$refs.avatarInput.click()" role="button" tabindex="0" @keydown.enter.prevent="$refs.avatarInput.click()">
              <div class="ui-avatar-ring">
                <img v-if="form.avatar" :src="form.avatar" class="w-full h-full object-cover" alt="" />
                <span v-else class="ui-avatar-initials">{{ initials }}</span>
              </div>
              <div class="ui-avatar-overlay">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              </div>
            </div>
            <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
            <span class="ui-label">לחץ לשינוי תמונה</span>
          </div>

          <!-- Fields -->
          <div class="space-y-5">
            <div>
              <label class="ui-form-label">שם משתמש</label>
              <input :value="form.username" disabled class="ui-input ui-input--readonly" />
            </div>
            <div>
              <label class="ui-form-label">שם מלא</label>
              <input v-model="form.full_name" type="text" placeholder="השם המלא שלך" class="ui-input" />
            </div>
            <div>
              <label class="ui-form-label">אימייל</label>
              <input v-model="form.email" type="email" placeholder="name@example.com" dir="ltr" class="ui-input" />
            </div>
            <div>
              <label class="ui-form-label">הרשאה</label>
              <div class="ui-role-display">
                {{ roleLabels[form.role] || form.role }}
              </div>
              <p class="ui-help-text">שינוי הרשאה מתבצע רק דרך הגדרות מערכת</p>
            </div>
          </div>

          <!-- TODO Phase E: password reset flows through Entra External ID. -->

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
        <footer class="px-7 py-5 border-t border-[color:var(--border)] flex justify-between gap-4">
          <button @click="$emit('close')" class="ui-btn">ביטול</button>
          <button @click="handleSave" :disabled="saving" class="ui-btn ui-btn-dark">
            {{ saving ? 'שומר…' : 'שמירה' }}
          </button>
        </footer>
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

/* Avatar uploader — circular with subtle hover */
.ui-avatar-uploader {
  position: relative;
  cursor: pointer;
  border-radius: 9999px;
  outline: none;
}
.ui-avatar-uploader:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.ui-avatar-ring {
  width: 7rem;
  height: 7rem;
  border-radius: 9999px;
  background: var(--surface-muted);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: transform var(--dur-press) var(--ease-out), border-color 180ms var(--ease-out);
}
.ui-avatar-uploader:active .ui-avatar-ring { transform: scale(0.97); }
.ui-avatar-initials {
  font-family: var(--font-sans);
  font-weight: 600;
  font-size: 1.875rem;
  color: var(--ink);
}
.ui-avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: rgba(15, 23, 42, 0.45);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 180ms var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .ui-avatar-uploader:hover .ui-avatar-overlay { opacity: 1; }
  .ui-avatar-uploader:hover .ui-avatar-ring { border-color: var(--border-strong); }
}

/* Disabled / readonly input */
.ui-input--readonly {
  color: var(--ink-faint);
  background: var(--surface-muted);
  cursor: not-allowed;
}

.ui-role-display {
  font-family: var(--font-sans);
  font-weight: 500;
  color: var(--ink);
  padding: 0.625rem 0.875rem;
  background: var(--surface-muted);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.ui-help-text {
  font-family: var(--font-sans);
  font-size: 0.75rem;
  color: var(--ink-faint);
  margin-top: 0.375rem;
}

.ui-password-section {
  border-top: 1px solid var(--border);
  padding-top: 1.5rem;
}
</style>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { getProfile, updateProfile } from '../services/api'
import { useToast } from '../composables/useToast'

const props = defineProps({ show: Boolean })
defineEmits(['close'])
const toast = useToast()

const roleLabels = { admin: 'מנהל מערכת', economist: 'כלכלנית', viewer: 'צופה מלא', project_manager: 'מנהל פרויקט' }
const form = reactive({ username: '', full_name: '', email: '', role: '', avatar: '' })
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

// TODO Phase E: password change moves to Entra External ID self-service.
</script>
