<template>
  <div>
    <h2 class="text-xl font-bold text-gray-800 mb-6">התראות</h2>

    <div v-if="loading" class="text-center py-20 text-gray-400">טוען נתונים...</div>

    <template v-if="!loading">
      <div v-if="alerts.length === 0"
        class="bg-white rounded-2xl p-12 shadow-sm border border-gray-100 text-center">
        <div class="text-4xl mb-4">&#9989;</div>
        <div class="text-lg font-semibold text-gray-700 mb-2">אין התראות</div>
        <div class="text-sm text-gray-400">כל הפרויקטים פועלים בטווח התקין</div>
      </div>

      <div v-else class="space-y-4">
        <div v-for="(alert, i) in alerts" :key="i"
          class="bg-white rounded-2xl p-5 shadow-sm border flex items-start gap-4 transition-colors"
          :class="alert.severity === 'high' ? 'border-red-200' : 'border-orange-200'">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            :class="alert.severity === 'high' ? 'bg-red-50 text-red-500' : 'bg-orange-50 text-orange-500'">
            <span class="text-lg">&#9888;</span>
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-semibold text-gray-800">{{ alert.project }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                :class="alert.severity === 'high' ? 'bg-red-100 text-red-600' : 'bg-orange-100 text-orange-600'">
                {{ alert.severity === 'high' ? 'גבוה' : 'בינוני' }}
              </span>
            </div>
            <div class="text-sm text-gray-600">{{ alert.message }}</div>
            <div v-if="alert.detail" class="text-xs text-gray-400 mt-1">{{ alert.detail }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPnl } from '../services/api'

const alerts = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await getPnl()
    for (const [name, project] of Object.entries(data)) {
      // Check margin alerts
      if (project.summary.margin != null && project.summary.margin < 20) {
        alerts.value.push({
          project: name,
          severity: project.summary.margin < 10 ? 'high' : 'medium',
          message: `מרווח תפעולי שנתי נמוך: ${project.summary.margin}%`,
          detail: `הסף הנדרש: 20%. הפרש: ${(20 - project.summary.margin).toFixed(1)}%`,
        })
      }

      // Check months with negative operating profit
      const negativeProfitMonths = project.months.filter(m => m.operating_profit < 0 && m.revenue > 0)
      if (negativeProfitMonths.length > 0) {
        alerts.value.push({
          project: name,
          severity: 'medium',
          message: `${negativeProfitMonths.length} חודשים עם הפסד תפעולי למרות הכנסות`,
          detail: `חודשים: ${negativeProfitMonths.map(m => m.month).join(', ')}`,
        })
      }

      // Months with no revenue
      const zeroRevenueMonths = project.months.filter(m => m.revenue === 0)
      if (zeroRevenueMonths.length > 6) {
        alerts.value.push({
          project: name,
          severity: 'medium',
          message: `${zeroRevenueMonths.length} חודשים ללא הכנסה`,
          detail: 'ייתכן שיש בעיה בגביה או בלוח זמנים',
        })
      }
    }
  } catch (e) {
    alerts.value.push({ project: 'מערכת', severity: 'high', message: `שגיאה בטעינת נתונים: ${e.message}` })
  } finally {
    loading.value = false
  }
})
</script>
