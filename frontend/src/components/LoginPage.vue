<template>
  <div class="ui-login-shell" dir="rtl">
    <!-- Subtle gradient backdrop -->
    <div class="ui-login-gradient" aria-hidden="true"></div>

    <div class="relative w-full max-w-[440px]">
      <!-- Brand bar -->
      <div class="flex items-center justify-center gap-3 mb-8 animate-fade-up">
        <div class="ui-logo-mark"></div>
        <div>
          <div class="ui-brand-title">IFMLogiX</div>
          <div class="ui-brand-sub">ניהול פיננסי חכם</div>
        </div>
      </div>

      <!-- Card -->
      <div class="ui-card ui-login-card ed-fade-up-delay-1">
        <!-- Step 1: email + password -->
        <form v-if="step === 'login'" @submit.prevent="handleLogin" class="flex flex-col gap-5">
          <div class="text-center mb-1">
            <h1 class="ui-login-title">כניסה למערכת</h1>
            <p class="ui-login-hint">הזן את פרטי המשתמש שלך להמשך</p>
          </div>

          <div>
            <label for="email" class="ui-form-label">אימייל</label>
            <input
              id="email"
              v-model="email"
              type="email"
              :class="['ui-input', { 'is-error': !!errorMsg }]"
              placeholder="name@company.com"
              autofocus
              dir="ltr"
            />
          </div>

          <div>
            <label for="password" class="ui-form-label">סיסמה</label>
            <input
              id="password"
              v-model="password"
              type="password"
              :class="['ui-input', { 'is-error': !!errorMsg }]"
              placeholder="••••••••"
            />
          </div>

          <div v-if="errorMsg" class="ui-field-error ui-field-error--animate" role="alert">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M5.062 19h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <span>{{ errorMsg }}</span>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="ed-btn ed-btn-primary w-full mt-1 ui-login-submit"
          >
            {{ loading ? 'מתחבר…' : 'כניסה' }}
            <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 16l-4-4m0 0l4-4m-4 4h18"/>
            </svg>
          </button>
        </form>

        <!-- Step 2: TOTP -->
        <div v-else-if="step === 'totp'" class="flex flex-col gap-5 animate-fade-up">
          <div class="text-center">
            <div class="ui-totp-icon">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
            <h1 class="ui-login-title">אימות דו-שלבי</h1>
            <p class="ui-login-hint">הזן את הקוד מאפליקציית ה-Authenticator</p>
          </div>

          <div>
            <label for="totp" class="ui-form-label text-center">קוד אימות</label>
            <input
              id="totp"
              v-model="totpCode"
              type="text"
              inputmode="numeric"
              maxlength="6"
              :class="['ui-input', 'ui-num', 'ui-totp-input', { 'is-error': !!errorMsg }]"
              placeholder="000000"
              autofocus
              @keyup.enter="verifyTotp"
              dir="ltr"
            />
          </div>

          <div v-if="errorMsg" class="ui-field-error ui-field-error--animate" role="alert">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M5.062 19h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <span>{{ errorMsg }}</span>
          </div>

          <button
            @click="verifyTotp"
            :disabled="loading || totpCode.length < 6"
            class="ed-btn ed-btn-primary w-full ui-login-submit"
          >
            {{ loading ? 'מאמת…' : 'אימות' }}
            <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 16l-4-4m0 0l4-4m-4 4h18"/>
            </svg>
          </button>
          <button
            type="button"
            @click="step = 'login'; errorMsg = ''"
            class="ed-link text-sm self-center"
          >
            ← חזרה לכניסה
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="ui-login-footer ed-fade-up-delay-2">
        IFMLogiX · © {{ new Date().getFullYear() }} · FM Group
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// TODO Phase E: replace this entire flow with MSAL.js (Entra External ID).
// Phase 0 stub — any submission stores the DEV token and emits 'login'.
// The TOTP step is kept in the template but is unreachable until real auth lands.

const emit = defineEmits(['login'])

const step = ref('login')
const email = ref('')
const password = ref('')
const totpCode = ref('')
const errorMsg = ref('')
const loading = ref(false)

const DEV_TOKEN = 'dev-admin-local'

async function handleLogin() {
  errorMsg.value = ''
  if (!email.value || !password.value) {
    errorMsg.value = 'יש למלא אימייל וסיסמה'
    return
  }
  localStorage.setItem('auth_token', DEV_TOKEN)
  emit('login')
}

async function verifyTotp() {
  // Unreachable in Phase 0 — kept so the template still compiles.
  localStorage.setItem('auth_token', DEV_TOKEN)
  emit('login')
}
</script>

<style scoped>
/* Page shell */
.ui-login-shell {
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
}
@media (min-width: 640px) {
  .ui-login-shell { padding: 1.5rem; }
}

/* Subtle radial gradient backdrop */
.ui-login-gradient {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 800px 400px at 50% -10%, rgba(5, 150, 105, 0.08), transparent 60%),
    radial-gradient(ellipse 600px 300px at 50% 110%, rgba(15, 23, 42, 0.04), transparent 60%);
  z-index: 0;
}

/* Card overrides — the primitive .ui-card gives surface/border/radius/shadow,
   here we only tune padding and shadow intensity for the login card. */
.ui-login-card {
  padding: clamp(1.75rem, 4vw, 2.5rem);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-2xl);
}

.ui-brand-title {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--ink);
  font-size: 1.25rem;
  line-height: 1;
  letter-spacing: -0.01em;
}
.ui-brand-sub {
  font-size: 0.75rem;
  color: var(--ink-muted);
  font-weight: 500;
  margin-top: 0.25rem;
}

.ui-login-title {
  font-family: var(--font-sans);
  font-weight: 600;
  color: var(--ink);
  font-size: 1.5rem;
  line-height: 1.2;
  letter-spacing: -0.01em;
}
.ui-login-hint {
  font-size: 0.875rem;
  color: var(--ink-muted);
  margin-top: 0.375rem;
}

/* Primary submit — a bit larger than default ed-btn */
.ui-login-submit {
  padding-block: 0.875rem;
  font-size: 1rem;
}

/* TOTP icon puck */
.ui-totp-icon {
  width: 3rem;
  height: 3rem;
  border-radius: var(--radius-lg);
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.75rem;
}

/* TOTP code input — large, spaced digits */
.ui-totp-input {
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: 0.35em;
  padding-block: 0.875rem;
  text-align: center;
}

.ui-login-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--ink-faint);
}

/* Brand mark — identical to top nav logo mark */
.ui-logo-mark {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--ink) 100%);
  box-shadow: 0 4px 14px rgba(5, 150, 105, 0.28), 0 1px 3px rgba(15, 23, 42, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.15);
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
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 22px;
  letter-spacing: -0.02em;
}
</style>
