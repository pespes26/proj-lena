<template>
  <div class="min-h-screen bg-bg text-ink flex items-center justify-center p-4 sm:p-6" dir="rtl">
    <!-- Subtle gradient backdrop -->
    <div class="ui-login-gradient" aria-hidden="true"></div>

    <div class="relative w-full max-w-[440px]">
      <!-- Brand bar -->
      <div class="flex items-center justify-center gap-3 mb-8 ed-fade-up">
        <div class="ui-logo-mark"></div>
        <div>
          <div class="font-sans font-semibold text-ink text-xl leading-none tracking-tight">IFMLogiX</div>
          <div class="text-[12px] text-ink-muted font-medium mt-1">ניהול פיננסי חכם</div>
        </div>
      </div>

      <!-- Card -->
      <div class="bg-surface border border-border rounded-2xl shadow-lg p-7 sm:p-9 ed-fade-up-delay-1">
        <!-- Step 1: email + password -->
        <form v-if="step === 'login'" @submit.prevent="handleLogin" class="flex flex-col gap-5">
          <div class="text-center mb-1">
            <h1 class="font-sans font-semibold text-ink text-2xl leading-tight">כניסה למערכת</h1>
            <p class="text-sm text-ink-muted mt-1.5">הזן את פרטי המשתמש שלך להמשך</p>
          </div>

          <div>
            <label for="email" class="ui-form-label">אימייל</label>
            <input
              id="email"
              v-model="email"
              type="email"
              class="ui-input"
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
              class="ui-input"
              placeholder="••••••••"
            />
          </div>

          <p v-if="errorMsg" class="text-sm font-medium text-negative text-center bg-negative-soft border border-negative/20 rounded-lg py-2 px-3 -mb-1">{{ errorMsg }}</p>

          <button
            type="submit"
            :disabled="loading"
            class="ui-btn ui-btn-accent w-full mt-1 py-3 text-base"
          >
            {{ loading ? 'מתחבר…' : 'כניסה' }}
            <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 16l-4-4m0 0l4-4m-4 4h18"/>
            </svg>
          </button>
        </form>

        <!-- Step 2: TOTP -->
        <div v-else-if="step === 'totp'" class="flex flex-col gap-5 ed-fade-up">
          <div class="text-center">
            <div class="w-12 h-12 rounded-xl bg-accent-soft flex items-center justify-center mx-auto mb-3">
              <svg class="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
            <h1 class="font-sans font-semibold text-ink text-xl leading-tight">אימות דו-שלבי</h1>
            <p class="text-sm text-ink-muted mt-1.5">הזן את הקוד מאפליקציית ה-Authenticator</p>
          </div>

          <div>
            <label for="totp" class="ui-form-label text-center">קוד אימות</label>
            <input
              id="totp"
              v-model="totpCode"
              type="text"
              inputmode="numeric"
              maxlength="6"
              class="ui-input text-center ui-num"
              style="font-size: 1.75rem; font-weight: 600; letter-spacing: 0.35em; padding-block: 0.875rem;"
              placeholder="000000"
              autofocus
              @keyup.enter="verifyTotp"
              dir="ltr"
            />
          </div>

          <p v-if="errorMsg" class="text-sm font-medium text-negative text-center bg-negative-soft border border-negative/20 rounded-lg py-2 px-3">{{ errorMsg }}</p>

          <button
            @click="verifyTotp"
            :disabled="loading || totpCode.length < 6"
            class="ui-btn ui-btn-accent w-full py-3 text-base"
          >
            {{ loading ? 'מאמת…' : 'אימות' }}
            <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 16l-4-4m0 0l4-4m-4 4h18"/>
            </svg>
          </button>
          <button
            @click="step = 'login'; errorMsg = ''"
            class="text-sm text-ink-muted hover:text-ink font-medium transition-colors self-center"
          >
            ← חזרה לכניסה
          </button>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center mt-6 text-[11px] text-ink-faint font-medium ed-fade-up-delay-2">
        IFMLogiX · © {{ new Date().getFullYear() }} · FM Group
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { auth } from '../firebase'
import {
  signInWithEmailAndPassword,
  TotpMultiFactorGenerator,
  getMultiFactorResolver,
} from 'firebase/auth'

const emit = defineEmits(['login'])

const step = ref('login')
const email = ref('')
const password = ref('')
const totpCode = ref('')
const errorMsg = ref('')
const loading = ref(false)

const mfaResolver = ref(null)

async function handleLogin() {
  errorMsg.value = ''
  if (!email.value || !password.value) {
    errorMsg.value = 'יש למלא אימייל וסיסמה'
    return
  }
  loading.value = true
  try {
    await signInWithEmailAndPassword(auth, email.value, password.value)
    emit('login')
  } catch (err) {
    if (err.code === 'auth/multi-factor-auth-required') {
      mfaResolver.value = getMultiFactorResolver(auth, err)
      step.value = 'totp'
      totpCode.value = ''
    } else if (err.code === 'auth/invalid-credential' || err.code === 'auth/wrong-password') {
      errorMsg.value = 'אימייל או סיסמה שגויים'
    } else if (err.code === 'auth/user-not-found') {
      errorMsg.value = 'משתמש לא נמצא'
    } else if (err.code === 'auth/too-many-requests') {
      errorMsg.value = 'יותר מדי ניסיונות. נסה שוב מאוחר יותר'
    } else {
      errorMsg.value = err.message || 'שגיאה בהתחברות'
    }
  } finally {
    loading.value = false
  }
}

async function verifyTotp() {
  errorMsg.value = ''
  loading.value = true
  try {
    const resolver = mfaResolver.value
    const totpHint = resolver.hints.find(h => h.factorId === TotpMultiFactorGenerator.FACTOR_ID)
    if (!totpHint) {
      errorMsg.value = 'לא נמצא אימות TOTP'
      return
    }
    const assertion = TotpMultiFactorGenerator.assertionForSignIn(totpHint.uid, totpCode.value)
    await resolver.resolveSignIn(assertion)
    emit('login')
  } catch (err) {
    if (err.code === 'auth/invalid-verification-code') {
      errorMsg.value = 'קוד שגוי. נסה שוב'
    } else {
      errorMsg.value = err.message || 'שגיאה באימות'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
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

.ui-logo-mark {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #059669 0%, #0f172a 100%);
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
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 22px;
  letter-spacing: -0.02em;
}
</style>
