<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-900 via-emerald-800 to-gray-900" dir="rtl">
    <div class="w-full max-w-md mx-4">
      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-2xl p-8">
        <!-- Logo -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-emerald-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-800">סנג'ר של לנה</h1>
          <p class="text-sm text-gray-400 mt-1">ניהול פיננסי</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">שם משתמש</label>
            <input
              v-model="username"
              type="text"
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
              placeholder="הזן שם משתמש"
              autofocus
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">סיסמה</label>
            <input
              v-model="password"
              type="password"
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
              placeholder="הזן סיסמה"
            />
          </div>

          <p v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-emerald-800 text-white rounded-xl font-medium text-sm hover:bg-emerald-900 transition-colors mt-2 disabled:opacity-50"
          >
            {{ loading ? 'מתחבר...' : 'כניסה' }}
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-emerald-200/50 text-xs mt-6">© 2026 סנג'ר של לנה — ניהול פיננסי</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { login } from '../services/api'

const emit = defineEmits(['login'])
const username = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function handleLogin() {
  errorMsg.value = ''
  if (!username.value || !password.value) {
    errorMsg.value = 'יש למלא שם משתמש וסיסמה'
    return
  }
  loading.value = true
  try {
    const data = await login(username.value, password.value)
    localStorage.setItem('token', data.access_token)
    emit('login')
  } catch (err) {
    errorMsg.value = err.message || 'שגיאה בהתחברות'
  } finally {
    loading.value = false
  }
}
</script>
