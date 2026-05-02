<template>
  <div class="fixed bottom-6 left-6 z-50" dir="rtl">
    <!-- Floating launcher — pill with icon + label -->
    <button
      v-if="!isOpen"
      @click="isOpen = true"
      class="ui-chat-launcher ui-press"
      aria-label="פתח עוזר פיננסי"
    >
      <div class="ui-chat-launcher__icon">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
        </svg>
      </div>
      <div class="ui-chat-launcher__text">
        <div class="ui-chat-launcher__eyebrow">IFMLogiX AI</div>
        <div class="ui-chat-launcher__label">עוזר פיננסי</div>
      </div>
    </button>

    <!-- Chat Panel -->
    <div v-if="isOpen" class="ui-chat-panel">
      <!-- Header -->
      <header class="ui-chat-header">
        <div class="flex items-center gap-2.5">
          <div class="ui-chat-header__mark">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>
          <div>
            <div class="font-sans font-semibold text-sm leading-none" style="color: #ffffff;">IFMLogiX AI</div>
            <div class="text-[11px] font-medium mt-0.5" style="color: rgba(255, 255, 255, 0.65);">עוזר פיננסי חכם</div>
          </div>
        </div>
        <div class="flex items-center gap-1">
          <button @click="clearChat" class="ui-chat-header__btn ui-press" title="נקה שיחה" aria-label="נקה">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
          <button @click="isOpen = false" class="ui-chat-header__btn ui-press" aria-label="סגור">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </header>

      <!-- Messages -->
      <div ref="messagesContainer" class="ui-chat-messages">
        <!-- Welcome -->
        <div v-if="messages.length === 0" class="py-4">
          <div class="ui-chat-welcome-mark">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" style="color: var(--accent);">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>
          <h4 class="font-sans font-semibold text-base leading-tight" style="color: var(--ink);">שלום 👋</h4>
          <p class="text-sm mt-1.5 leading-relaxed" style="color: var(--ink-muted);">
            אני IFMLogiX AI — העוזר הפיננסי שלך. שאל אותי על הפרויקטים, התזרים, או הרווחיות של הקבוצה.
          </p>
          <div class="mt-5 space-y-1.5">
            <div class="ed-eyebrow mb-2">שאלות נפוצות</div>
            <button
              v-for="q in quickQuestions"
              :key="q"
              @click="sendMessage(q)"
              class="ui-chat-quick ui-press"
            >
              {{ q }}
            </button>
          </div>
        </div>

        <!-- Message bubbles -->
        <div v-for="(msg, i) in messages" :key="i" class="ui-chat-bubble" :class="`ui-chat-bubble--${msg.role}`">
          <div v-if="msg.role === 'user'" class="ui-chat-bubble__body-user">{{ msg.content }}</div>
          <div v-else class="ui-chat-bubble__body-ai ai-message" v-html="renderMarkdown(msg.content)"></div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="ui-chat-bubble ui-chat-bubble--assistant">
          <div class="ui-chat-bubble__body-ai flex items-center gap-1">
            <span class="ui-chat-dot" style="animation-delay: 0ms"></span>
            <span class="ui-chat-dot" style="animation-delay: 150ms"></span>
            <span class="ui-chat-dot" style="animation-delay: 300ms"></span>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="ui-chat-input-wrap">
        <div class="relative">
          <input
            v-model="input"
            ref="chatInput"
            @keyup.enter="sendMessage()"
            :disabled="loading"
            class="ui-input"
            style="padding-inline-end: 3rem;"
            placeholder="שאל שאלה…"
          />
          <button
            @click="sendMessage()"
            :disabled="loading || !input.trim()"
            class="ui-chat-send ui-press"
            aria-label="שלח"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import { sendAiChatStream } from '../services/api'

marked.setOptions({ breaks: true, gfm: true })

function renderMarkdown(text) {
  return marked.parse(text || '')
}

const isOpen = ref(false)
const input = ref('')
const messages = ref([])
const loading = ref(false)
const messagesContainer = ref(null)
const chatInput = ref(null)

const quickQuestions = [
  'תן לי סיכום של כל הפרויקטים',
  'איזה פרויקט הכי רווחי ולמה?',
  'האם יש פרויקטים בסיכון?',
  'כמה כסף צפוי להיכנס החודש הבא?',
]

async function sendMessage(text) {
  const msg = text || input.value.trim()
  if (!msg) return

  input.value = ''
  messages.value.push({ role: 'user', content: msg })
  await scrollToBottom()

  loading.value = true
  messages.value.push({ role: 'assistant', content: '' })
  const assistantIdx = messages.value.length - 1
  try {
    const history = messages.value.slice(0, -2).map(m => ({ role: m.role, content: m.content }))
    await sendAiChatStream(history, msg, (partialText) => {
      messages.value[assistantIdx].content = partialText
      scrollToBottom()
    })
  } catch (err) {
    messages.value[assistantIdx].content = `שגיאה: ${err.message}`
  } finally {
    loading.value = false
    await scrollToBottom()
    chatInput.value?.focus()
  }
}

function clearChat() {
  messages.value = []
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
/* Floating launcher — pill with icon + label */
.ui-chat-launcher {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1rem 0.625rem 0.75rem;
  background: var(--ink);
  color: #ffffff;
  border: 0;
  border-radius: 999px;
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  transition: transform 180ms var(--ease-out), box-shadow 180ms var(--ease-out);
  font-family: var(--font-sans);
  transform-origin: center;
}
@media (hover: hover) and (pointer: fine) {
  .ui-chat-launcher:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
  }
}
.ui-chat-launcher:active {
  transform: scale(0.97);
}
.ui-chat-launcher__icon {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}
.ui-chat-launcher__text {
  text-align: right;
  padding-left: 0.25rem;
}
.ui-chat-launcher__eyebrow {
  font-size: 0.625rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.65);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  line-height: 1;
  margin-bottom: 0.25rem;
}
.ui-chat-launcher__label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  line-height: 1;
}

/* Chat panel — uses modal entrance */
.ui-chat-panel {
  width: 380px;
  height: 560px;
  max-height: 85vh;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform-origin: bottom right;
  animation: ui-modal-in 220ms var(--ease-out) both;
}

/* Header — branded dark (inverted) */
.ui-chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--border-strong);
  background: var(--ink);
  flex-shrink: 0;
}
.ui-chat-header__mark {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}
.ui-chat-header__btn {
  color: rgba(255, 255, 255, 0.72);
  background: transparent;
  border: 0;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: color 180ms var(--ease-out), background 180ms var(--ease-out), transform var(--dur-press) var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .ui-chat-header__btn:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.08);
  }
}
.ui-chat-header__btn:active {
  transform: scale(0.97);
}

/* Welcome state */
.ui-chat-welcome-mark {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  background: var(--accent-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

/* Quick-question buttons — editorial link-meets-button */
.ui-chat-quick {
  width: 100%;
  text-align: right;
  padding: 0.625rem 0.875rem;
  background: var(--surface);
  color: var(--ink);
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 500;
  line-height: 1.4;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background 180ms var(--ease-out), border-color 180ms var(--ease-out), color 180ms var(--ease-out), transform var(--dur-press) var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .ui-chat-quick:hover {
    background: var(--surface-muted);
    border-color: var(--border-strong);
    color: var(--accent);
  }
}
.ui-chat-quick:active {
  transform: scale(0.98);
}

/* Messages */
.ui-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.125rem;
  background: var(--surface);
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}
.ui-chat-bubble {
  display: flex;
}
.ui-chat-bubble--user {
  justify-content: flex-start;
}
.ui-chat-bubble--assistant {
  justify-content: flex-end;
}
.ui-chat-bubble__body-user {
  max-width: 85%;
  background: var(--ink);
  color: #ffffff;
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.55;
  padding: 0.625rem 0.875rem;
  border-radius: 14px 14px 4px 14px;
  word-wrap: break-word;
}
.ui-chat-bubble__body-ai {
  max-width: 88%;
  background: var(--surface-muted);
  color: var(--ink);
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.55;
  padding: 0.75rem 0.9375rem;
  border-radius: 14px 14px 14px 4px;
  border: 1px solid var(--border);
  word-wrap: break-word;
}

/* Loading dots — opacity + translateY only */
.ui-chat-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--ink-faint);
  animation: ui-chat-dot 1.2s infinite var(--ease-out);
}
@keyframes ui-chat-dot {
  0%, 80%, 100% { opacity: 0.3; transform: translateY(0); }
  40% { opacity: 1; transform: translateY(-2px); }
}

/* Input */
.ui-chat-input-wrap {
  padding: 0.875rem 1rem;
  border-top: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}
.ui-chat-send {
  position: absolute;
  left: 0.375rem;
  top: 50%;
  transform: translateY(-50%);
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-md);
  background: var(--ink);
  color: #ffffff;
  border: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 180ms var(--ease-out), transform var(--dur-press) var(--ease-out);
}
.ui-chat-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.ui-chat-send:not(:disabled):active {
  transform: translateY(-50%) scale(0.97);
}
</style>

<style>
/* AI message markdown — scoped to .ai-message only */
.ai-message h1, .ai-message h2, .ai-message h3 {
  font-family: 'DM Sans', 'Rubik', sans-serif;
  font-weight: 700;
  margin: 10px 0 4px;
  color: #0f172a;
}
.ai-message h2 { font-size: 0.9375rem; }
.ai-message h3 { font-size: 0.875rem; }
.ai-message p { margin: 4px 0; }
.ai-message ul, .ai-message ol { padding-right: 1.2em; margin: 4px 0; }
.ai-message li { margin: 2px 0; }
.ai-message strong { font-weight: 700; color: #0f172a; }
.ai-message table {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 0.8125rem;
  font-family: 'DM Sans', 'Rubik', sans-serif;
  font-feature-settings: "lnum" 1, "tnum" 1;
}
.ai-message th, .ai-message td {
  border-bottom: 1px solid #e2e8f0;
  padding: 5px 8px;
  text-align: right;
}
.ai-message th {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #475569;
  border-bottom-color: #cbd5e1;
  text-transform: none;
  letter-spacing: 0;
}
.ai-message code {
  background: #f1f5f9;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.8125rem;
  font-family: ui-monospace, monospace;
  color: #0f172a;
}
.ai-message hr { border: none; border-top: 1px solid #e2e8f0; margin: 10px 0; }
</style>
