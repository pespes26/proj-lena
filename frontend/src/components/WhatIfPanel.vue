<template>
  <div class="space-y-8" dir="rtl">
    <!-- Controls -->
    <section class="ed-section-top">
      <div class="ed-eyebrow mb-1">סימולציה</div>
      <h2 class="font-sans font-semibold text-ink text-2xl mb-5 leading-none">פרמטרים</h2>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-6">
        <div>
          <label class="ed-label flex items-center justify-between" for="whatif-rev">
            <span>שינוי הכנסות</span>
            <span class="font-sans font-semibold text-sm ed-num" :class="revChange >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
              <bdi>{{ revChange > 0 ? '+' : '' }}{{ revChange }}%</bdi>
            </span>
          </label>
          <input id="whatif-rev" type="range" v-model.number="revChange" min="-50" max="50" step="5" class="ed-range" />
          <div class="flex justify-between ed-eyebrow mt-1" style="font-size: 0.625rem;"><span>−50%</span><span>0</span><span>+50%</span></div>
        </div>

        <div>
          <label class="ed-label flex items-center justify-between" for="whatif-cost">
            <span>שינוי הוצאות</span>
            <span class="font-sans font-semibold text-sm ed-num" :class="expChange <= 0 ? 'ed-tone-positive' : 'ed-tone-negative'">
              <bdi>{{ expChange > 0 ? '+' : '' }}{{ expChange }}%</bdi>
            </span>
          </label>
          <input id="whatif-cost" type="range" v-model.number="expChange" min="-30" max="30" step="5" class="ed-range" />
          <div class="flex justify-between ed-eyebrow mt-1" style="font-size: 0.625rem;"><span>−30%</span><span>0</span><span>+30%</span></div>
        </div>

        <div>
          <label class="ed-label" for="whatif-delay">הארכת פרויקט (חודשים)</label>
          <input id="whatif-delay" type="number" v-model.number="extendMonths" min="0" max="6" step="1" class="ed-input ed-num" />
        </div>

        <div class="flex items-end">
          <button @click="runSimulation" :disabled="loading" class="ed-btn ed-btn-primary">
            {{ loading ? 'מחשב…' : 'הרץ סימולציה' }} →
          </button>
        </div>
      </div>
    </section>

    <!-- Results -->
    <section v-if="result" class="ed-section">
      <div class="ed-eyebrow mb-1">תוצאות</div>
      <h2 class="font-sans font-semibold text-ink text-2xl mb-5 leading-none">השוואת תרחישים</h2>

      <table class="ed-table">
        <thead>
          <tr>
            <th>מדד</th>
            <th class="num">מקור</th>
            <th class="num">סימולציה</th>
            <th class="num">שינוי</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>הכנסות</td>
            <td class="num"><bdi class="ed-num">{{ fmt(result.original.summary.total_revenue) }}</bdi></td>
            <td class="num"><bdi class="ed-num">{{ fmt(result.simulated.summary.total_revenue) }}</bdi></td>
            <td class="num" :class="diffTone(result.diff.revenue_change)">
              <bdi class="ed-num">{{ diffLabel(result.diff.revenue_change) }}</bdi>
            </td>
          </tr>
          <tr>
            <td>הוצאות</td>
            <td class="num"><bdi class="ed-num">{{ fmt(result.original.summary.total_op_expenses) }}</bdi></td>
            <td class="num"><bdi class="ed-num">{{ fmt(result.simulated.summary.total_op_expenses) }}</bdi></td>
            <td class="num" :class="diffTone(-result.diff.expense_change)">
              <bdi class="ed-num">{{ diffLabel(result.diff.expense_change) }}</bdi>
            </td>
          </tr>
          <tr>
            <td class="font-sans font-semibold">רווח תפעולי</td>
            <td class="num" :class="result.original.summary.total_operating_profit >= 0 ? '' : 'ed-tone-negative'">
              <bdi class="ed-num">{{ fmt(result.original.summary.total_operating_profit) }}</bdi>
            </td>
            <td class="num" :class="result.simulated.summary.total_operating_profit >= 0 ? '' : 'ed-tone-negative'">
              <bdi class="ed-num">{{ fmt(result.simulated.summary.total_operating_profit) }}</bdi>
            </td>
            <td class="num" :class="diffTone(result.diff.profit_change)">
              <bdi class="ed-num">{{ diffLabel(result.diff.profit_change) }}</bdi>
            </td>
          </tr>
          <tr>
            <td>מרווח</td>
            <td class="num"><bdi class="ed-num">{{ result.original.summary.margin != null ? result.original.summary.margin + '%' : '—' }}</bdi></td>
            <td class="num"><bdi class="ed-num">{{ result.simulated.summary.margin != null ? result.simulated.summary.margin + '%' : '—' }}</bdi></td>
            <td class="num" :class="diffTone(result.diff.margin_change)">
              <bdi class="ed-num">{{ result.diff.margin_change > 0 ? '+' : '' }}{{ result.diff.margin_change }}%</bdi>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <p v-if="error" class="font-sans text-sm ed-tone-negative text-center">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { runWhatIf, formatNumber } from '../services/api'

const props = defineProps({
  project: { type: String, required: true }
})

const fmt = formatNumber
const revChange = ref(0)
const expChange = ref(0)
const extendMonths = ref(0)
const loading = ref(false)
const result = ref(null)
const error = ref(null)

async function runSimulation() {
  loading.value = true
  error.value = null
  try {
    const modifications = {}
    if (revChange.value !== 0) modifications.revenue_change_pct = revChange.value
    if (expChange.value !== 0) modifications.expense_change_pct = expChange.value
    if (extendMonths.value > 0) modifications.extend_months = extendMonths.value

    result.value = await runWhatIf(props.project, modifications)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function diffTone(val) {
  return val > 0 ? 'ed-tone-positive' : val < 0 ? 'ed-tone-negative' : 'ed-tone-muted'
}

function diffLabel(val) {
  if (val === 0) return '—'
  return (val > 0 ? '+' : '') + fmt(val)
}
</script>

<style scoped>
.ed-range {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 1px;
  background: var(--rule-strong);
  outline: none;
  cursor: pointer;
}
.ed-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 2px;
  height: 24px;
  background: var(--accent);
  cursor: pointer;
}
.ed-range::-moz-range-thumb {
  width: 2px;
  height: 24px;
  background: var(--accent);
  cursor: pointer;
  border: 0;
}
</style>
