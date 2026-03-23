<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center" dir="rtl">
      <div class="absolute inset-0 bg-black/25" @click="handleClose()"></div>

      <div class="relative bg-white shadow-[0_8px_30px_rgba(0,0,0,0.08)] w-full max-w-3xl mx-0 sm:mx-4 rounded-none sm:rounded-2xl max-h-[90vh] flex flex-col overflow-hidden border border-gray-200/60">
        <!-- Header + Stepper -->
        <div class="px-4 sm:px-8 pt-6 sm:pt-8 pb-4 sm:pb-6 border-b border-gray-100">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-xl font-bold text-gray-900">
                {{ newProject ? 'פרויקט חדש' : 'הגדרת פרויקט — ' + project }}
              </h3>
              <p class="text-sm text-gray-400 mt-0.5">שלב {{ step + 1 }} מתוך {{ steps.length }}</p>
            </div>
            <button @click="handleClose()" class="p-2 rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <!-- Step tabs -->
          <div class="flex items-center gap-3 sm:gap-8 overflow-x-auto mt-2">
            <button v-for="(s, i) in steps" :key="i"
              @click="step = i"
              :class="[
                'pb-3 text-xs sm:text-sm font-medium border-b-2 transition-all cursor-pointer',
                i === step ? 'text-gray-900 border-gray-900'
                  : 'text-gray-500 border-transparent hover:text-gray-700'
              ]">
              {{ s }}
            </button>
          </div>
        </div>

        <!-- Content (scrollable) -->
        <div class="flex-1 overflow-y-auto px-4 sm:px-8 py-4 sm:py-6">

          <!-- Step 1: Project Details -->
          <div v-if="step === 0" class="space-y-6">
            <!-- Project name field (only for new projects) -->
            <div v-if="newProject">
              <label class="block text-sm font-medium text-gray-700 mb-2">שם פרויקט *</label>
              <input v-model="form.project_name" type="text" placeholder="שם הפרויקט"
                @blur="vf('project_name', form.project_name, { required: true, minLen: 2 })"
                :class="['w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition', fc('project_name')]" />
              <span v-if="fe.project_name" class="text-red-500 text-xs mt-0.5 block">{{ fe.project_name }}</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">מספר Priority *</label>
                <input v-model="form.priority_id" type="text" placeholder="P-1001"
                  @blur="vf('priority_id', form.priority_id, { required: true, minLen: 2 })"
                  :class="['w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-emerald-300 transition', fc('priority_id')]" />
                <span v-if="fe.priority_id" class="text-red-500 text-xs mt-0.5 block">{{ fe.priority_id }}</span>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">תאריך התחלה *</label>
                <DatePicker v-model="form.start_date"
                  :input-class="'w-full bg-gray-50/70 border rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition ' + (fe.start_date ? 'border-red-400 bg-red-50' : 'border-gray-200')" />
                <span v-if="fe.start_date" class="text-red-500 text-xs mt-0.5 block">{{ fe.start_date }}</span>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">צפי סיום פרויקט *</label>
                <DatePicker v-model="form.expected_end_date" :min-date="form.start_date"
                  :input-class="'w-full bg-gray-50/70 border rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition ' + (fe.expected_end_date ? 'border-red-400 bg-red-50' : 'border-gray-200')" />
                <span v-if="fe.expected_end_date" class="text-red-500 text-xs mt-0.5 block">{{ fe.expected_end_date }}</span>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">ח.פ / מספר עוסק מורשה</label>
                <input v-model="form.company_id" type="text" placeholder="51-123456-7"
                  :class="['w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition font-mono']" />
              </div>
              <div class="flex items-end pb-1">
                <label class="flex items-center gap-3 cursor-pointer">
                  <div class="relative">
                    <input type="checkbox" v-model="form.is_recurring" class="sr-only peer" />
                    <div class="w-10 h-5 bg-gray-200 rounded-full peer-checked:bg-emerald-500 transition"></div>
                    <div class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-5"></div>
                  </div>
                  <span class="text-sm font-medium text-gray-700">פרויקט מחזורי</span>
                </label>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">שם מנהל פרויקט *</label>
                <input v-model="form.manager" type="text" placeholder="שם מלא"
                  @blur="vf('manager', form.manager, { required: true, minLen: 2 })"
                  :class="['w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition', fc('manager')]" />
                <span v-if="fe.manager" class="text-red-500 text-xs mt-0.5 block">{{ fe.manager }}</span>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">שם המזמין *</label>
                <input v-model="form.client" type="text" placeholder="שם החברה/לקוח"
                  @blur="vf('client', form.client, { required: true, minLen: 2 })"
                  :class="['w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition', fc('client')]" />
                <span v-if="fe.client" class="text-red-500 text-xs mt-0.5 block">{{ fe.client }}</span>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">תחום</label>
                <select v-model="form.area" class="w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition">
                  <option value="מסחרי פרטי">מסחרי פרטי</option>
                  <option value="פרוייקטים">פרוייקטים</option>
                  <option value="מטה">מטה</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">ציר</label>
                <select v-model="form.axis" class="w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition">
                  <option value="FM">FM</option>
                  <option value="אחר">אחר</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">סטטוס</label>
                <select v-model="form.status" class="w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition">
                  <option value="active">פעיל</option>
                  <option value="on-hold">מושהה</option>
                  <option value="completed">הושלם</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">תיאור פרויקט *</label>
              <textarea v-model="form.description" rows="3" placeholder="תיאור כללי של הפרויקט..."
                @blur="vf('description', form.description, { required: true, minLen: 5 })"
                :class="['w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition resize-none', fc('description')]"></textarea>
              <div class="flex justify-between mt-0.5">
                <span v-if="fe.description" class="text-red-500 text-xs">{{ fe.description }}</span>
                <span v-else></span>
                <span class="text-gray-400 text-xs">{{ (form.description || '').length }} תווים</span>
              </div>
            </div>
          </div>

          <!-- Step 2: Revenue -->
          <div v-if="step === 1" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">סך הכנסות הפרויקט (₪) *</label>
              <input v-model.number="form.total_revenue" type="number" placeholder="0" min="1"
                @blur="vf('total_revenue', form.total_revenue, { required: true, positive: true, max: 999999999 })"
                :class="['w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition', fc('total_revenue')]" />
              <span v-if="fe.total_revenue" class="text-red-500 text-xs mt-0.5 block">{{ fe.total_revenue }}</span>
            </div>

            <!-- Payment terms as dynamic table -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs font-medium text-gray-600">תנאי תשלום הכנסה</label>
                <span class="text-xs font-bold" :class="paymentTermsTotal === 100 ? 'text-emerald-700' : 'text-orange-500'">
                  סה"כ: {{ paymentTermsTotal }}%
                </span>
              </div>
              <div class="space-y-2">
                <div v-for="(term, i) in form.revenue_payment_terms" :key="i"
                  class="flex flex-wrap items-center gap-2 bg-gray-50/50 rounded-lg border border-gray-100 px-3 py-2.5">
                  <select v-model="term.type" class="flex-1 bg-white border border-gray-200 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0">
                    <option value="מזומן">מזומן</option>
                    <option value="מקדמה">מקדמה</option>
                    <option value="שוטף+0">שוטף+0</option>
                    <option value="שוטף+30">שוטף+30</option>
                    <option value="שוטף+45">שוטף+45</option>
                    <option value="שוטף+60">שוטף+60</option>
                    <option value="שוטף+90">שוטף+90</option>
                  </select>
                  <div class="flex items-center gap-1">
                    <input v-model.number="term.percent" @input="clampPaymentTerm(i)" type="number" min="0" max="100" placeholder="0"
                      class="w-16 bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs text-center focus:outline-none focus:border-gray-400 focus:ring-0" />
                    <span class="text-xs text-gray-400">%</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <input :value="form.total_revenue ? Math.round(form.total_revenue * (term.percent || 0) / 100) : 0"
                      @input="updateTermAmount(i, $event)" type="number" min="0" placeholder="0"
                      class="w-24 bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs text-center focus:outline-none focus:border-gray-400 focus:ring-0" />
                    <span class="text-xs text-gray-400">₪</span>
                  </div>
                  <button v-if="form.revenue_payment_terms.length > 1" @click="form.revenue_payment_terms.splice(i, 1)"
                    class="p-1 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </div>
                <button @click="form.revenue_payment_terms.push({ type: 'שוטף+30', percent: 0 })"
                  class="w-full py-2 border border-dashed border-gray-200 rounded-xl text-xs text-gray-500 hover:bg-gray-50 transition flex items-center justify-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                  הוסף שורת תשלום
                </button>
              </div>
            </div>

            <!-- Payment milestones -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs font-medium text-gray-600">פעימות תשלום</label>
                <span v-if="form.payment_milestones.length" class="text-xs font-bold"
                  :class="milestonesTotal <= 100 ? 'text-emerald-700' : 'text-red-500'">
                  סה"כ: {{ milestonesTotal }}%
                </span>
              </div>
              <div class="space-y-2">
                <div v-for="(ms, i) in form.payment_milestones" :key="i"
                  class="flex flex-wrap items-center gap-2 bg-gray-50/50 rounded-lg border border-gray-100 px-3 py-2.5">
                  <div class="flex items-center gap-1">
                    <input v-model.number="ms.percent" @input="syncMilestoneFromPercent(i)" type="number" min="0" max="100" placeholder="%"
                      class="w-14 bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs text-center focus:outline-none focus:border-gray-400 focus:ring-0" />
                    <span class="text-xs text-gray-400">%</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <input v-model.number="ms.amount" @input="syncMilestoneFromAmount(i)" type="number" min="0" placeholder="סכום"
                      class="w-24 bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs text-center focus:outline-none focus:border-gray-400 focus:ring-0" />
                    <span class="text-xs text-gray-400">₪</span>
                  </div>
                  <DatePicker v-model="ms.date" :min-date="form.start_date"
                    :input-class="'w-28 bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0'" />
                  <input v-model="ms.description" type="text" placeholder="תיאור"
                    class="flex-1 bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0" />
                  <button @click="form.payment_milestones.splice(i, 1)"
                    class="p-1 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                  </button>
                </div>
                <button @click="form.payment_milestones.push({ percent: 0, amount: 0, date: '', description: '' })"
                  class="w-full py-2 border border-dashed border-gray-200 rounded-xl text-xs text-gray-500 hover:bg-gray-50 transition flex items-center justify-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                  הוסף פעימת תשלום
                </button>
              </div>
            </div>

            <!-- Revenue forecast table (auto-computed) -->
            <div>
              <label class="text-xs font-medium text-gray-600 mb-2 block">תחזית כניסת הכנסות לפי תנאי תשלום</label>
              <div class="bg-gray-50/50 rounded-xl overflow-x-auto">
                <table class="w-full text-xs min-w-[600px]">
                  <thead>
                    <tr class="bg-gray-100/50">
                      <th v-for="m in 12" :key="m" class="px-1 py-2 text-center font-medium text-gray-500 w-[8.33%]">{{ m }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <!-- Cash inflow per month (auto-computed from payment terms) -->
                    <tr class="bg-emerald-50/50">
                      <td v-for="m in 12" :key="m" class="px-1 py-2 text-center text-xs font-medium"
                        :class="cashInflowForMonth(m) > 0 ? 'text-emerald-700' : 'text-gray-300'">
                        {{ cashInflowForMonth(m) ? cashInflowForMonth(m).toLocaleString('he-IL') : '-' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
                <!-- Legend -->
                <div class="flex items-center gap-4 px-3 py-2 border-t border-gray-200 text-xs text-gray-400">
                  <div class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-emerald-200"></span> כניסת תשלום בפועל</div>
                  <div class="text-gray-300">•</div>
                  <div>מקדמה: חודש התחלה · מזומן: פרוס על תקופת הפרויקט · שוטף+X: סוף חודש חשבונית + X ימים</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Expenses -->
          <div v-if="step === 2" class="space-y-6">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">סה"כ תקציב הוצאות (ש"ח) *</label>
                <input v-model.number="form.total_budget" type="number" placeholder="0" min="1"
                  @blur="vf('total_budget', form.total_budget, { required: true, positive: true })"
                  :class="['w-full bg-gray-50/70 border border-transparent rounded-lg px-4 py-3 text-sm focus:outline-none focus:bg-white focus:border-gray-300 focus:ring-0 transition', fc('total_budget')]" />
                <span v-if="fe.total_budget" class="text-red-500 text-xs mt-0.5 block">{{ fe.total_budget }}</span>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">תנאי תשלום הוצאות</label>
                <div class="flex gap-2">
                  <select v-model="form.payment_terms_expense.type" class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition">
                    <option value="מזומן">מזומן</option>
                    <option value="מקדמה">מקדמה</option>
                    <option value="שוטף+0">שוטף+0</option>
                    <option value="שוטף+30">שוטף+30</option>
                    <option value="שוטף+45">שוטף+45</option>
                    <option value="שוטף+60">שוטף+60</option>
                    <option value="שוטף+90">שוטף+90</option>
                  </select>
                  <input v-model="form.payment_terms_expense.notes" type="text" placeholder="הערות"
                    class="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300 transition" />
                </div>
              </div>
            </div>

            <!-- Expense categories accordion -->
            <div class="space-y-2">
              <div class="text-xs font-medium text-gray-500 mb-1">קטגוריות התחייבות לספקים</div>

              <!-- קבלני משנה -->
              <div class="border border-gray-100 rounded-xl overflow-hidden">
                <button @click="toggleCategory('subcontractors')"
                  class="w-full flex items-center justify-between px-4 py-3 bg-transparent hover:bg-gray-50 transition text-sm font-medium text-gray-700">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                    קבלני משנה
                    <span v-if="form.subcontractors.length" class="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full">{{ form.subcontractors.length }}</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <span v-if="subcontractorsTotal > 0" class="text-xs font-bold text-gray-500">{{ subcontractorsTotal.toLocaleString('he-IL') }} ₪</span>
                    <svg class="w-4 h-4 text-gray-400 transition-transform duration-200" :class="activeCategory === 'subcontractors' ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                  </div>
                </button>
                <div v-if="activeCategory === 'subcontractors'" class="p-4 space-y-3">
                  <div v-for="(sub, i) in form.subcontractors" :key="i"
                    class="bg-gray-50/50 rounded-lg border border-gray-100 p-3 space-y-2">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs font-medium text-gray-500">קבלן {{ i + 1 }}</span>
                      <button @click="form.subcontractors.splice(i, 1)"
                        class="p-1 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                      </button>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                      <div>
                        <label class="block text-xs text-gray-400 mb-1">שם קבלן</label>
                        <input v-model="sub.name" type="text" placeholder="שם הקבלן"
                          @blur="vf(`sub_name_${i}`, sub.name, { required: true, minLen: 2 })"
                          :class="['w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0', fc(`sub_name_${i}`)]" />
                        <span v-if="fe[`sub_name_${i}`]" class="text-red-500 text-xs">{{ fe[`sub_name_${i}`] }}</span>
                      </div>
                      <div>
                        <label class="block text-xs text-gray-400 mb-1">התחייבות לספק (ש"ח)</label>
                        <input v-model.number="sub.monthly_amount" type="number" placeholder="0" min="1"
                          @blur="vf(`sub_amount_${i}`, sub.monthly_amount, { required: true, positive: true })"
                          :class="['w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0', fc(`sub_amount_${i}`)]" />
                        <span v-if="fe[`sub_amount_${i}`]" class="text-red-500 text-xs">{{ fe[`sub_amount_${i}`] }}</span>
                      </div>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      <div>
                        <label class="block text-xs text-gray-400 mb-1">תאריך התחלה</label>
                        <DatePicker v-model="sub.start_date" :min-date="form.start_date"
                          input-class="w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0" />
                      </div>
                      <div>
                        <label class="block text-xs text-gray-400 mb-1">תאריך סיום</label>
                        <DatePicker v-model="sub.end_date" :min-date="form.start_date"
                          input-class="w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0" />
                      </div>
                      <div>
                        <label class="block text-xs text-gray-400 mb-1">תנאי תשלום</label>
                        <select v-model="sub.payment_terms"
                          class="w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0">
                          <option value="מזומן">מזומן</option>
                          <option value="מקדמה">מקדמה</option>
                          <option value="שוטף+0">שוטף+0</option>
                          <option value="שוטף+30">שוטף+30</option>
                          <option value="שוטף+45">שוטף+45</option>
                          <option value="שוטף+60">שוטף+60</option>
                          <option value="שוטף+90">שוטף+90</option>
                        </select>
                      </div>
                    </div>
                    <div class="col-span-2">
                      <label class="block text-xs text-gray-500 mb-1">חוזה קבלן</label>
                      <div class="flex items-center gap-2">
                        <label class="flex-1 flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition text-xs">
                          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13"/></svg>
                          <span class="text-gray-500">{{ sub.contract_filename || 'בחר קובץ חוזה...' }}</span>
                          <input type="file" accept=".pdf,.doc,.docx,.jpg,.png" class="hidden" @change="e => { sub.contract_filename = e.target.files[0]?.name || ''; sub.contract_file = e.target.files[0] }" />
                        </label>
                        <button v-if="sub.contract_filename" @click="sub.contract_filename = ''; sub.contract_file = null"
                          class="p-1.5 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition">
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                      </div>
                    </div>
                  </div>
                  <button @click="addSubcontractor"
                    class="w-full py-2.5 border border-dashed border-gray-200 rounded-xl text-sm text-emerald-700 font-medium hover:bg-emerald-50 transition flex items-center justify-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                    הוספת קבלן משנה חדש
                  </button>
                </div>
              </div>

              <!-- כוח אדם -->
              <div class="border border-gray-100 rounded-xl overflow-hidden">
                <button @click="toggleCategory('manpower')"
                  class="w-full flex items-center justify-between px-4 py-3 bg-transparent hover:bg-gray-50 transition text-sm font-medium text-gray-700">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-purple-400"></span>
                    כוח אדם
                    <span v-if="form.manpower_attendance_summary" class="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full">מנוכחות</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <span v-if="categoryTotal('manpower') > 0" class="text-xs font-bold text-gray-500">{{ categoryTotal('manpower').toLocaleString('he-IL') }} ₪</span>
                    <svg class="w-4 h-4 text-gray-400 transition-transform duration-200" :class="activeCategory === 'manpower' ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                  </div>
                </button>
                <div v-if="activeCategory === 'manpower'" class="p-4 space-y-3">
                  <!-- Pull from attendance -->
                  <div class="bg-purple-50 rounded-xl border border-purple-200 p-3">
                    <div class="text-xs font-medium text-purple-700 mb-2">משיכה משעון נוכחות רומי</div>
                    <div class="flex items-center gap-2">
                      <input v-model="form.priority_id" type="text" readonly
                        class="flex-1 bg-white border border-purple-200 rounded-lg px-2 py-1.5 text-xs text-gray-500" placeholder="מספר פרויקט" />
                      <button @click="pullAttendance" :disabled="loadingAttendance"
                        class="px-3 py-1.5 bg-purple-500 text-white text-xs font-medium rounded-lg hover:bg-purple-600 disabled:opacity-50 transition flex items-center gap-1">
                        <svg v-if="loadingAttendance" class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                        משוך נוכחות
                      </button>
                    </div>
                    <div v-if="form.manpower_attendance_summary" class="mt-2 grid grid-cols-3 gap-2">
                      <div class="bg-white rounded-lg p-2 text-center border border-purple-100">
                        <div class="text-lg font-bold text-purple-600">{{ form.manpower_attendance_summary.total_hours?.toFixed(1) }}</div>
                        <div class="text-xs text-gray-400">שעות</div>
                      </div>
                      <div class="bg-white rounded-lg p-2 text-center border border-purple-100">
                        <div class="text-lg font-bold text-purple-600">{{ form.manpower_attendance_summary.employees }}</div>
                        <div class="text-xs text-gray-400">עובדים</div>
                      </div>
                      <div class="bg-white rounded-lg p-2 text-center border border-purple-100">
                        <div class="text-lg font-bold text-purple-600">{{ form.manpower_attendance_summary.total_cost?.toLocaleString('he-IL') }}</div>
                        <div class="text-xs text-gray-400">עלות ש"ח</div>
                      </div>
                    </div>
                    <div v-if="attendanceError" class="mt-2 text-xs text-red-500">{{ attendanceError }}</div>
                  </div>
                  <!-- Manual lines -->
                  <div class="space-y-3">
                    <div v-for="(line, i) in form.expense_lines_manpower" :key="i"
                      class="bg-gray-50/50 rounded-lg border border-gray-100 p-3 space-y-2 hover:border-gray-300 transition-colors">
                      <div class="flex items-center justify-between mb-1">
                        <span class="text-xs font-medium text-gray-500">שורה {{ i + 1 }}</span>
                        <button @click="form.expense_lines_manpower.splice(i, 1)" class="p-1 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                      </div>
                      <div class="grid grid-cols-2 gap-2">
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">פירוט</label>
                          <input v-model="line.name" type="text" placeholder="תיאור ההוצאה"
                            @blur="vf(`mp_name_${i}`, line.name, { required: true, minLen: 2 })"
                            :class="['w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0', fc(`mp_name_${i}`)]" />
                          <span v-if="fe[`mp_name_${i}`]" class="text-red-500 text-xs">{{ fe[`mp_name_${i}`] }}</span>
                        </div>
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">התחייבות לספק (₪)</label>
                          <input v-model.number="line.monthly_amount" type="number" placeholder="0" min="1"
                            @blur="vf(`mp_amount_${i}`, line.monthly_amount, { required: true, positive: true })"
                            :class="['w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0', fc(`mp_amount_${i}`)]" />
                          <span v-if="fe[`mp_amount_${i}`]" class="text-red-500 text-xs">{{ fe[`mp_amount_${i}`] }}</span>
                        </div>
                      </div>
                      <div class="grid grid-cols-2 gap-2">
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">מחודש</label>
                          <select v-model.number="line.start_month" class="w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0">
                            <option v-for="m in 12" :key="m" :value="m">חודש {{ m }}</option>
                          </select>
                        </div>
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">עד חודש</label>
                          <select v-model.number="line.end_month"
                            :class="['w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0', fc(`mp_end_${i}`)]">
                            <option v-for="m in 12" :key="m" :value="m">חודש {{ m }}</option>
                          </select>
                          <span v-if="fe[`mp_end_${i}`]" class="text-red-500 text-xs">{{ fe[`mp_end_${i}`] }}</span>
                        </div>
                      </div>
                      <!-- Line total preview -->
                      <div v-if="line.monthly_amount && line.start_month && line.end_month" class="bg-white rounded-lg px-2 py-1.5 text-xs text-gray-400 flex justify-between">
                        <span>{{ line.end_month - line.start_month + 1 }} חודשים</span>
                        <span class="font-medium text-gray-600">סה"כ: {{ (line.monthly_amount * (line.end_month - line.start_month + 1)).toLocaleString('he-IL') }} ₪</span>
                      </div>
                    </div>
                  </div>
                  <button @click="addExpenseLine('manpower')"
                    class="w-full py-2.5 border border-dashed border-gray-200 rounded-xl text-xs text-gray-500 font-medium hover:bg-gray-50 hover:border-gray-400 transition flex items-center justify-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                    הוסף שורה ידנית
                  </button>
                </div>
              </div>

              <!-- Standard categories (supplier forms like subcontractors) -->
              <div v-for="cat in standardCategories" :key="cat.key" class="border border-gray-100 rounded-xl overflow-hidden">
                <button @click="toggleCategory(cat.key)"
                  class="w-full flex items-center justify-between px-4 py-3 bg-transparent hover:bg-gray-50 transition text-sm font-medium text-gray-700">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full" :class="cat.color"></span>
                    {{ cat.label }}
                    <span v-if="form['expense_lines_' + cat.key]?.length" class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">{{ form['expense_lines_' + cat.key].length }}</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <span v-if="categoryTotal(cat.key) > 0" class="text-xs font-bold text-gray-500">{{ categoryTotal(cat.key).toLocaleString('he-IL') }} ₪</span>
                    <svg class="w-4 h-4 text-gray-400 transition-transform duration-200" :class="activeCategory === cat.key ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                  </div>
                </button>
                <div v-show="activeCategory === cat.key" class="accordion-body">
                  <div class="p-4 space-y-3">
                    <!-- Empty state -->
                    <div v-if="!form['expense_lines_' + cat.key]?.length" class="text-center py-6">
                      <div class="text-2xl mb-1 opacity-40">📋</div>
                      <div class="text-xs text-gray-400">אין ספקים בקטגוריה זו</div>
                      <div class="text-xs text-gray-300 mt-0.5">לחץ למטה להוספת ספק</div>
                    </div>
                    <!-- Supplier cards -->
                    <div v-for="(line, i) in form['expense_lines_' + cat.key]" :key="i"
                      class="bg-gray-50/50 rounded-lg border border-gray-100 p-3 space-y-2 hover:border-gray-300 transition-colors">
                      <div class="flex items-center justify-between mb-1">
                        <span class="text-xs font-medium text-gray-500">ספק {{ i + 1 }}</span>
                        <button @click="form['expense_lines_' + cat.key].splice(i, 1)" class="p-1 rounded-lg text-red-400 hover:bg-red-50 hover:text-red-600 transition">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                      </div>
                      <div class="grid grid-cols-2 gap-2">
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">שם ספק</label>
                          <input v-model="line.name" type="text" placeholder="שם הספק"
                            @blur="vf(`${cat.key}_name_${i}`, line.name, { required: true, minLen: 2 })"
                            :class="['w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0', fc(`${cat.key}_name_${i}`)]" />
                          <span v-if="fe[`${cat.key}_name_${i}`]" class="text-red-500 text-xs">{{ fe[`${cat.key}_name_${i}`] }}</span>
                        </div>
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">התחייבות לספק (₪)</label>
                          <input v-model.number="line.monthly_amount" type="number" placeholder="0" min="1"
                            @blur="vf(`${cat.key}_amount_${i}`, line.monthly_amount, { required: true, positive: true })"
                            :class="['w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0', fc(`${cat.key}_amount_${i}`)]" />
                          <span v-if="fe[`${cat.key}_amount_${i}`]" class="text-red-500 text-xs">{{ fe[`${cat.key}_amount_${i}`] }}</span>
                        </div>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">תאריך התחלה</label>
                          <DatePicker v-model="line.start_date" :min-date="form.start_date"
                            input-class="w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0" />
                        </div>
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">תאריך סיום</label>
                          <DatePicker v-model="line.end_date" :min-date="form.start_date"
                            input-class="w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0" />
                        </div>
                        <div>
                          <label class="block text-xs text-gray-400 mb-1">תנאי תשלום</label>
                          <select v-model="line.payment_terms"
                            class="w-full bg-white border border-gray-200 rounded-lg px-2 py-2 text-xs focus:outline-none focus:border-gray-400 focus:ring-0">
                            <option value="מזומן">מזומן</option>
                            <option value="מקדמה">מקדמה</option>
                            <option value="שוטף+0">שוטף+0</option>
                            <option value="שוטף+30">שוטף+30</option>
                            <option value="שוטף+45">שוטף+45</option>
                            <option value="שוטף+60">שוטף+60</option>
                            <option value="שוטף+90">שוטף+90</option>
                          </select>
                        </div>
                      </div>
                    </div>
                    <button @click="addSupplierLine(cat.key)"
                      class="w-full py-2.5 border border-dashed border-gray-200 rounded-xl text-xs text-gray-500 font-medium hover:bg-gray-50 hover:border-gray-400 transition flex items-center justify-center gap-1.5">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                      הוסף ספק
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Budget utilization progress bar -->
            <div v-if="form.total_budget" class="space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-500">ניצול תקציב</span>
                <span class="text-xs font-bold" :class="budgetUtilization > 100 ? 'text-red-500' : budgetUtilization > 80 ? 'text-orange-500' : 'text-emerald-700'">
                  {{ budgetUtilization.toFixed(0) }}%
                </span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                <div class="h-full rounded-full transition-all duration-500"
                  :class="budgetUtilization > 100 ? 'bg-red-500' : budgetUtilization > 80 ? 'bg-orange-400' : 'bg-emerald-700'"
                  :style="{ width: Math.min(budgetUtilization, 100) + '%' }"></div>
              </div>
            </div>

            <!-- Total summary -->
            <div class="bg-gray-50/50 rounded-lg border border-gray-100 px-4 py-3">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-500">סה"כ התחייבויות חודשיות:</span>
                <span class="text-sm font-bold" :class="form.total_budget && totalMonthlyExpenses > form.total_budget ? 'text-red-500' : 'text-gray-700'">
                  {{ totalMonthlyExpenses.toLocaleString('he-IL') }} ₪
                </span>
              </div>
              <div v-if="form.total_budget" class="flex items-center justify-between mt-1">
                <span class="text-xs text-gray-400">תקציב מאושר:</span>
                <span class="text-xs text-gray-400">{{ form.total_budget.toLocaleString('he-IL') }} ₪</span>
              </div>
            </div>
          </div>

          <!-- Step 4: Summary / Overview -->
          <div v-if="step === 3" class="space-y-6">
            <!-- Project Details -->
            <div class="bg-gray-50/60 rounded-xl p-5">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-sm font-bold text-gray-700">פרטי פרויקט</h4>
                <button @click="step = 0" class="text-xs text-emerald-700 hover:text-emerald-800 font-medium">עריכה</button>
              </div>
              <div class="grid grid-cols-2 gap-x-8 gap-y-2.5 text-sm">
                <div v-if="newProject"><span class="text-gray-400">שם פרויקט: </span><span class="font-medium text-gray-800">{{ form.project_name }}</span></div>
                <div><span class="text-gray-400">מספר Priority: </span><span class="font-medium text-gray-800 font-mono">{{ form.priority_id }}</span></div>
                <div><span class="text-gray-400">תאריך התחלה: </span><span class="font-medium text-gray-800">{{ form.start_date }}</span></div>
                <div><span class="text-gray-400">צפי סיום: </span><span class="font-medium text-gray-800">{{ form.expected_end_date }}</span></div>
                <div v-if="form.company_id"><span class="text-gray-400">ח.פ: </span><span class="font-medium text-gray-800 font-mono">{{ form.company_id }}</span></div>
                <div v-if="form.is_recurring"><span class="text-gray-400">סוג: </span><span class="font-medium text-emerald-700">פרויקט מחזורי</span></div>
                <div><span class="text-gray-400">מנהל פרויקט: </span><span class="font-medium text-gray-800">{{ form.manager }}</span></div>
                <div><span class="text-gray-400">מזמין: </span><span class="font-medium text-gray-800">{{ form.client }}</span></div>
                <div><span class="text-gray-400">תחום: </span><span class="font-medium text-gray-800">{{ form.area }}</span></div>
                <div><span class="text-gray-400">ציר: </span><span class="font-medium text-gray-800">{{ form.axis }}</span></div>
                <div><span class="text-gray-400">סטטוס: </span><span class="font-medium text-gray-800">{{ form.status === 'active' ? 'פעיל' : form.status === 'on-hold' ? 'מושהה' : 'הושלם' }}</span></div>
              </div>
              <div v-if="form.description" class="mt-3 text-sm">
                <span class="text-gray-400">תיאור: </span><span class="text-gray-600">{{ form.description }}</span>
              </div>
            </div>

            <!-- Revenue -->
            <div class="bg-gray-50/60 rounded-xl p-5">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-sm font-bold text-gray-700">צפי הכנסות</h4>
                <button @click="step = 1" class="text-xs text-emerald-700 hover:text-emerald-800 font-medium">עריכה</button>
              </div>
              <div class="text-sm mb-3">
                <span class="text-gray-400">סך הכנסות: </span>
                <span class="font-bold text-gray-800">{{ form.total_revenue ? form.total_revenue.toLocaleString('he-IL') : '0' }} ₪</span>
              </div>
              <!-- Payment terms -->
              <div v-if="form.revenue_payment_terms?.length" class="mb-4">
                <div class="text-xs text-gray-400 mb-2">תנאי תשלום:</div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="(term, i) in form.revenue_payment_terms" :key="i"
                    class="inline-flex items-center gap-1.5 px-3 py-1 bg-white rounded-lg border border-gray-100 text-xs">
                    <span class="font-medium text-gray-700">{{ term.type }}</span>
                    <span class="text-gray-400">{{ term.percent }}%</span>
                    <span v-if="form.total_revenue" class="text-gray-300">·</span>
                    <span v-if="form.total_revenue" class="text-gray-400">{{ Math.round(form.total_revenue * term.percent / 100).toLocaleString('he-IL') }} ₪</span>
                  </span>
                </div>
              </div>
              <!-- Revenue forecast mini table (auto-computed) -->
              <div>
                <div class="text-xs text-gray-400 mb-2">תחזית כניסת הכנסות חודשית:</div>
                <div class="overflow-x-auto">
                <div class="grid grid-cols-12 gap-1 text-center min-w-[600px]">
                  <div v-for="m in 12" :key="m" class="text-xs">
                    <div class="text-gray-400 font-medium mb-1">{{ m }}</div>
                    <div :class="['py-1 rounded', cashInflowForMonth(m) > 0 ? 'bg-emerald-50 text-emerald-700 font-medium' : 'text-gray-300']">
                      {{ cashInflowForMonth(m) ? cashInflowForMonth(m).toLocaleString('he-IL') : '-' }}
                    </div>
                  </div>
                </div>
                </div>
              </div>
              <!-- Payment milestones summary -->
              <div v-if="form.payment_milestones?.length" class="mb-4">
                <div class="text-xs text-gray-400 mb-2">פעימות תשלום:</div>
                <div class="space-y-1">
                  <div v-for="(ms, i) in form.payment_milestones" :key="i"
                    class="flex items-center justify-between bg-white rounded-lg px-3 py-2 border border-gray-100 text-xs">
                    <span class="font-medium text-gray-700">{{ ms.description || 'פעימה ' + (i+1) }}</span>
                    <div class="flex items-center gap-3">
                      <span class="text-gray-400">{{ ms.percent }}%</span>
                      <span class="text-gray-500 font-medium">{{ (ms.amount || 0).toLocaleString('he-IL') }} ₪</span>
                      <span class="text-gray-400">{{ ms.date || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Expenses -->
            <div class="bg-gray-50/60 rounded-xl p-5">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-sm font-bold text-gray-700">צפי הוצאות</h4>
                <button @click="step = 2" class="text-xs text-emerald-700 hover:text-emerald-800 font-medium">עריכה</button>
              </div>
              <div class="grid grid-cols-2 gap-x-8 gap-y-2 text-sm mb-4">
                <div><span class="text-gray-400">תקציב הוצאות: </span><span class="font-bold text-gray-800">{{ form.total_budget ? form.total_budget.toLocaleString('he-IL') : '0' }} ₪</span></div>
                <div><span class="text-gray-400">תנאי תשלום: </span><span class="font-medium text-gray-800">{{ form.payment_terms_expense?.type || '-' }}</span></div>
              </div>
              <!-- Subcontractors -->
              <div v-if="form.subcontractors?.length" class="mb-3">
                <div class="text-xs text-gray-400 mb-2 flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-emerald-500"></span> קבלני משנה ({{ form.subcontractors.length }})
                </div>
                <div class="space-y-1">
                  <div v-for="(sub, i) in form.subcontractors" :key="i"
                    class="flex items-center justify-between bg-white rounded-lg px-3 py-2 border border-gray-100 text-xs">
                    <span class="font-medium text-gray-700">{{ sub.name || 'ללא שם' }}</span>
                    <span class="text-gray-500">{{ (sub.monthly_amount || 0).toLocaleString('he-IL') }} ₪/חודש</span>
                  </div>
                </div>
              </div>
              <!-- Other categories -->
              <template v-for="cat in allExpenseCategories" :key="cat.key">
                <div v-if="form['expense_lines_' + cat.key]?.length" class="mb-3">
                  <div class="text-xs text-gray-400 mb-2 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full" :class="cat.color"></span> {{ cat.label }} ({{ form['expense_lines_' + cat.key].length }})
                  </div>
                  <div class="space-y-1">
                    <div v-for="(line, i) in form['expense_lines_' + cat.key]" :key="i"
                      class="flex items-center justify-between bg-white rounded-lg px-3 py-2 border border-gray-100 text-xs">
                      <span class="font-medium text-gray-700">{{ line.name || 'ללא שם' }}</span>
                      <span class="text-gray-500">{{ (line.monthly_amount || 0).toLocaleString('he-IL') }} ₪/חודש</span>
                    </div>
                  </div>
                </div>
              </template>
              <!-- Total -->
              <div class="flex items-center justify-between pt-3 mt-3 border-t border-gray-200 text-sm">
                <span class="text-gray-500">סה"כ התחייבויות:</span>
                <span class="font-bold" :class="form.total_budget && totalMonthlyExpenses > form.total_budget ? 'text-red-500' : 'text-gray-800'">
                  {{ totalMonthlyExpenses.toLocaleString('he-IL') }} ₪
                </span>
              </div>
            </div>

            <!-- Financial Summary KPIs -->
            <div class="bg-emerald-50/60 rounded-xl p-5 border border-emerald-100">
              <h4 class="text-sm font-bold text-gray-700 mb-4">סיכום כספי</h4>
              <div class="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div class="text-xs text-gray-500 mb-1">סך הכנסות</div>
                  <div class="text-xl font-bold text-gray-800">{{ (form.total_revenue || 0).toLocaleString('he-IL') }}</div>
                  <div class="text-[10px] text-gray-400">₪</div>
                </div>
                <div>
                  <div class="text-xs text-gray-500 mb-1">סך הוצאות</div>
                  <div class="text-xl font-bold text-orange-600">{{ totalMonthlyExpenses.toLocaleString('he-IL') }}</div>
                  <div class="text-[10px] text-gray-400">₪</div>
                </div>
                <div>
                  <div class="text-xs text-gray-500 mb-1">רווח צפוי</div>
                  <div class="text-xl font-bold" :class="(form.total_revenue || 0) - totalMonthlyExpenses >= 0 ? 'text-emerald-700' : 'text-red-500'">
                    {{ ((form.total_revenue || 0) - totalMonthlyExpenses).toLocaleString('he-IL') }}
                  </div>
                  <div class="text-[10px] text-gray-400">₪</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Exit confirmation overlay -->
        <div v-if="showExitConfirm" class="absolute inset-0 z-10 bg-white/90 flex items-center justify-center rounded-2xl">
          <div class="text-center max-w-xs">
            <div class="text-3xl mb-3">💾</div>
            <h4 class="text-base font-bold text-gray-900 mb-2">הטופס לא הושלם</h4>
            <p class="text-sm text-gray-500 mb-6">האם לשמור את המצב הנוכחי כטיוטא?</p>
            <div class="flex flex-col gap-2">
              <button @click="saveDraftAndClose"
                class="w-full py-2.5 bg-emerald-800 text-white text-sm font-medium rounded-lg hover:bg-emerald-900 transition">שמור טיוטא</button>
              <button @click="discardAndClose"
                class="w-full py-2.5 bg-white border border-gray-200 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 transition">צא ללא שמירה</button>
              <button @click="showExitConfirm = false"
                class="w-full py-2 text-sm text-gray-400 hover:text-gray-600 transition">המשך עריכה</button>
            </div>
          </div>
        </div>

        <!-- Validation errors overlay -->
        <div v-if="showValidationModal" class="absolute inset-0 z-10 bg-white/90 flex items-center justify-center rounded-2xl">
          <div class="text-center max-w-sm px-4">
            <div class="text-3xl mb-3">&#9888;&#65039;</div>
            <h4 class="text-base font-bold text-gray-900 mb-2">לא ניתן לשמור את הפרויקט</h4>
            <p class="text-sm text-gray-500 mb-4">יש להשלים את השדות הבאים:</p>
            <div class="bg-red-50 rounded-xl p-4 mb-5 text-right max-h-[200px] overflow-y-auto">
              <ul class="space-y-1.5">
                <li v-for="(field, i) in validationErrorsList" :key="i" class="flex items-center gap-2 text-sm text-red-700">
                  <svg class="w-3.5 h-3.5 flex-shrink-0 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  {{ field }}
                </li>
              </ul>
            </div>
            <button @click="showValidationModal = false"
              class="w-full py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 transition">הבנתי, חזרה לעריכה</button>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-4 sm:px-8 py-4 sm:py-5 border-t border-gray-100 bg-white flex items-center justify-between">
          <button v-if="step > 0" @click="step--"
            class="px-4 py-2.5 text-sm font-medium text-gray-500 hover:text-gray-700 transition flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
            חזרה
          </button>
          <div v-else></div>

          <div class="flex items-center gap-3">
            <div v-if="error" class="text-red-500 text-xs font-medium">{{ error }}</div>
            <button v-if="step < steps.length - 1" @click="nextStep"
              class="px-5 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 transition flex items-center gap-1.5">
              הבא
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
            </button>
            <button v-else @click="save" :disabled="saving"
              class="px-8 py-3 bg-[#065F46] text-white text-sm font-semibold rounded-lg hover:bg-[#064E3B] disabled:opacity-50 transition flex items-center gap-2">
              <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
              {{ saving ? 'שומר...' : 'אשר ושמור' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { getProjectForm, saveProjectForm, getAttendanceByProject } from '../services/api'
import DatePicker from './DatePicker.vue'

const props = defineProps({
  show: Boolean,
  project: String,
  newProject: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'saved'])

const steps = ['פרטי פרויקט', 'צפי הכנסות', 'צפי הוצאות', 'סיכום']
const step = ref(0)
const saving = ref(false)
const error = ref(null)
const activeCategory = ref(null)
const loadingAttendance = ref(false)
const attendanceError = ref(null)
const showExitConfirm = ref(false)
const showValidationModal = ref(false)
const validationErrorsList = ref([])
const originalFormSnapshot = ref(null)

const isDirty = computed(() => {
  if (!originalFormSnapshot.value) return false
  return JSON.stringify(form) !== originalFormSnapshot.value
})

const standardCategories = [
  { key: 'equipment', label: 'ציוד וכלים', color: 'bg-orange-400' },
  { key: 'insurance', label: 'ביטוחים', color: 'bg-green-400' },
  { key: 'consultants', label: 'מתכננים ויועצים', color: 'bg-yellow-400' },
  { key: 'financing', label: 'הוצאות מימון', color: 'bg-red-400' },
  { key: 'other', label: 'אחר', color: 'bg-gray-400' },
]

const allExpenseCategories = [
  { key: 'manpower', label: 'כוח אדם', color: 'bg-purple-400' },
  ...standardCategories,
]

const defaultForm = () => ({
  project_name: '',
  priority_id: '',
  start_date: '',
  expected_end_date: '',
  company_id: '',
  is_recurring: false,
  payment_milestones: [],
  description: '',
  manager: '',
  client: '',
  area: 'מסחרי פרטי',
  axis: 'FM',
  payment_terms_revenue: { type: 'שוטף+60', notes: '' },
  revenue_payment_terms: [{ type: 'מקדמה', percent: 50 }, { type: 'שוטף+30', percent: 50 }],
  payment_terms_expense: { type: 'שוטף+30', notes: '' },
  total_revenue: null,
  revenue_forecast: Object.fromEntries(Array.from({ length: 12 }, (_, i) => [i + 1, 0])),
  total_budget: null,
  // Expense categories
  subcontractors: [],
  expense_lines_manpower: [],
  expense_lines_equipment: [],
  expense_lines_insurance: [],
  expense_lines_consultants: [],
  expense_lines_financing: [],
  expense_lines_other: [],
  manpower_attendance_summary: null,
  // Legacy
  expense_lines: [],
  // Unified data model
  status: 'active',
  actuals: Object.fromEntries(Array.from({ length: 12 }, (_, i) => [i + 1, { revenue: 0, op_expenses: 0, salary_expenses: 0, notes: '' }])),
  source: 'form',
  last_updated: '',
})

const form = reactive(defaultForm())
const fe = reactive({}) // field errors - { fieldName: 'error message' }

// Validate a single field, returns error string or ''
function vf(name, value, opts = {}) {
  let err = ''
  const v = typeof value === 'string' ? value.trim() : value
  if (opts.required && (v === '' || v === null || v === undefined)) err = 'שדה חובה'
  else if (opts.minLen && typeof v === 'string' && v.length > 0 && v.length < opts.minLen) err = `מינימום ${opts.minLen} תווים`
  else if (opts.maxLen && typeof v === 'string' && v.length > opts.maxLen) err = `מקסימום ${opts.maxLen} תווים`
  else if (opts.positive && typeof v === 'number' && v <= 0) err = 'חייב להיות מספר חיובי'
  else if (opts.min !== undefined && typeof v === 'number' && v < opts.min) err = `מינימום ${opts.min}`
  else if (opts.max !== undefined && typeof v === 'number' && v > opts.max) err = `מקסימום ${opts.max.toLocaleString('he-IL')}`
  else if (opts.positive && v !== null && v !== undefined && v !== '' && (isNaN(v) || Number(v) <= 0)) err = 'חייב להיות מספר חיובי'
  fe[name] = err
  return err
}

// Dynamic class for input border
function fc(name) {
  return fe[name] ? 'border-red-400! bg-red-50!' : ''
}

// Validate all step fields
function validateStep0() {
  const errs = []
  if (props.newProject) errs.push(vf('project_name', form.project_name, { required: true, minLen: 2 }))
  errs.push(vf('priority_id', form.priority_id, { required: true, minLen: 2 }))
  errs.push(vf('start_date', form.start_date, { required: true }))
  errs.push(vf('manager', form.manager, { required: true, minLen: 2 }))
  errs.push(vf('client', form.client, { required: true, minLen: 2 }))
  errs.push(vf('description', form.description, { required: true, minLen: 5 }))
  errs.push(vf('expected_end_date', form.expected_end_date, { required: true }))
  if (form.expected_end_date && form.start_date && form.expected_end_date < form.start_date) {
    fe.expected_end_date = 'צפי סיום חייב להיות אחרי תאריך ההתחלה'
    errs.push('err')
  }
  return errs.every(e => !e)
}

function validateStep1() {
  const errs = []
  errs.push(vf('total_revenue', form.total_revenue, { required: true, positive: true, max: 999999999 }))
  // payment terms percent validation
  form.revenue_payment_terms.forEach((t, i) => {
    const v = Number(t.percent) || 0
    if (v < 0 || v > 100) errs.push(vf(`pt_${i}`, v, { min: 0, max: 100 }))
    else fe[`pt_${i}`] = ''
  })
  if (milestonesTotal.value > 100) {
    error.value = 'סה"כ פעימות תשלום לא יכול לעלות על 100%'
    errs.push('err')
  }
  return errs.every(e => !e)
}

function validateStep2() {
  const errs = []
  errs.push(vf('total_budget', form.total_budget, { required: true, positive: true }))
  // subcontractors
  form.subcontractors.forEach((sub, i) => {
    if (sub.name || sub.monthly_amount) {
      errs.push(vf(`sub_name_${i}`, sub.name, { required: true, minLen: 2 }))
      errs.push(vf(`sub_amount_${i}`, sub.monthly_amount, { required: true, positive: true }))
      if (sub.start_date && sub.end_date && sub.end_date < sub.start_date) {
        fe[`sub_end_${i}`] = 'תאריך סיום חייב להיות אחרי ההתחלה'
        errs.push('err')
      } else { fe[`sub_end_${i}`] = '' }
    }
  })
  // manpower
  form.expense_lines_manpower.forEach((line, i) => {
    if (line.name || line.monthly_amount) {
      errs.push(vf(`mp_name_${i}`, line.name, { required: true, minLen: 2 }))
      errs.push(vf(`mp_amount_${i}`, line.monthly_amount, { required: true, positive: true }))
      if (line.start_month > line.end_month) {
        fe[`mp_end_${i}`] = 'חודש סיום חייב להיות אחרי ההתחלה'
        errs.push('err')
      } else { fe[`mp_end_${i}`] = '' }
    }
  })
  // standard categories
  for (const cat of standardCategories) {
    const lines = form['expense_lines_' + cat.key] || []
    lines.forEach((line, i) => {
      if (line.name || line.monthly_amount) {
        errs.push(vf(`${cat.key}_name_${i}`, line.name, { required: true, minLen: 2 }))
        errs.push(vf(`${cat.key}_amount_${i}`, line.monthly_amount, { required: true, positive: true }))
        if (line.start_date && line.end_date && line.end_date < line.start_date) {
          fe[`${cat.key}_end_${i}`] = 'תאריך סיום חייב להיות אחרי ההתחלה'
          errs.push('err')
        } else { fe[`${cat.key}_end_${i}`] = '' }
      }
    })
  }
  return errs.every(e => !e)
}

const forecastTotal = computed(() =>
  Object.values(form.revenue_forecast).reduce((a, v) => a + (Number(v) || 0), 0)
)

const paymentTermsTotal = computed(() =>
  (form.revenue_payment_terms || []).reduce((a, t) => a + (Number(t.percent) || 0), 0)
)

const startMonth = computed(() => {
  if (!form.start_date) return 1
  const parts = form.start_date.split('-')
  return parts.length >= 2 ? parseInt(parts[1], 10) : 1
})

const endMonth = computed(() => {
  if (!form.expected_end_date) return 12
  const parts = form.expected_end_date.split('-')
  return parts.length >= 2 ? parseInt(parts[1], 10) : 12
})

// Zero out forecast months before start date when start_date changes
watch(startMonth, (newStart) => {
  for (let m = 1; m < newStart; m++) {
    form.revenue_forecast[m] = 0
  }
})

// Extract X days from שוטף+X
function extractShotefDays(type) {
  if (!type) return 0
  if (type.includes('שוטף+90')) return 90
  if (type.includes('שוטף+60')) return 60
  if (type.includes('שוטף+45')) return 45
  if (type.includes('שוטף+30')) return 30
  if (type.includes('שוטף+0') || type === 'שוטף') return 0
  return 0
}

// Calculate payment month: end of invoice month + X days
function shotefPaymentMonth(invoiceMonth, invoiceYear, xDays) {
  const lastDay = new Date(invoiceYear, invoiceMonth, 0).getDate() // last day of month
  const endOfMonth = new Date(invoiceYear, invoiceMonth - 1, lastDay)
  const paymentDate = new Date(endOfMonth.getTime() + xDays * 86400000)
  return paymentDate.getMonth() + 1 // 1-based
}

// Calculate actual cash inflow per month based on שוטף+ logic
function cashInflowForMonth(targetMonth) {
  if (!form.total_revenue) return 0
  let total = 0
  const sm = startMonth.value
  const em = endMonth.value
  const projectMonths = Math.max(1, em - sm + 1)

  // Parse start year from start_date
  const startYear = form.start_date ? parseInt(form.start_date.split('-')[0]) || 2026 : 2026

  for (const term of (form.revenue_payment_terms || [])) {
    const termPct = Number(term.percent) || 0
    if (!termPct) continue
    const termAmount = form.total_revenue * termPct / 100

    if (term.type === 'מקדמה') {
      if (targetMonth === sm) total += Math.round(termAmount)
    } else if (term.type === 'מזומן') {
      const monthlyAmount = termAmount / projectMonths
      if (targetMonth >= sm && targetMonth <= em) {
        total += Math.round(monthlyAmount)
      }
    } else {
      // שוטף+X: invoices each month, payment = end of invoice month + X days
      const xDays = extractShotefDays(term.type)
      const monthlyInvoice = termAmount / projectMonths
      for (let invM = sm; invM <= em; invM++) {
        const invYear = invM < sm ? startYear + 1 : startYear
        const payMonth = shotefPaymentMonth(invM, invYear, xDays)
        if (payMonth === targetMonth) {
          total += Math.round(monthlyInvoice)
        }
      }
    }
  }
  return total
}

const totalMonthlyExpenses = computed(() => {
  let total = 0
  for (const sub of form.subcontractors) total += Number(sub.monthly_amount) || 0
  for (const cat of ['manpower', 'equipment', 'insurance', 'consultants', 'financing', 'other']) {
    for (const line of form['expense_lines_' + cat] || []) total += Number(line.monthly_amount) || 0
  }
  return total
})

const subcontractorsTotal = computed(() => {
  return form.subcontractors.reduce((sum, sub) => sum + (Number(sub.monthly_amount) || 0), 0)
})

function categoryTotal(catKey) {
  return (form['expense_lines_' + catKey] || []).reduce((sum, line) => sum + (Number(line.monthly_amount) || 0), 0)
}

const budgetUtilization = computed(() => {
  if (!form.total_budget || form.total_budget <= 0) return 0
  return (totalMonthlyExpenses.value / form.total_budget) * 100
})

function toggleCategory(key) {
  activeCategory.value = activeCategory.value === key ? null : key
}

function addSubcontractor() {
  form.subcontractors.push({ name: '', start_date: form.start_date || '', end_date: form.expected_end_date || '', payment_terms: 'שוטף+30', monthly_amount: null, contract_filename: '' })
}

function addExpenseLine(cat) {
  form['expense_lines_' + cat].push({ name: '', monthly_amount: null, start_month: 1, end_month: 12 })
}

function addSupplierLine(cat) {
  // Insurance: default to project end date with שוטף+0 (one-time payment at end)
  if (cat === 'insurance') {
    form['expense_lines_' + cat].push({
      name: '', monthly_amount: null,
      start_date: form.expected_end_date || '', end_date: form.expected_end_date || '',
      payment_terms: 'שוטף+0'
    })
  } else {
    form['expense_lines_' + cat].push({
      name: '', monthly_amount: null,
      start_date: form.start_date || '', end_date: form.expected_end_date || '',
      payment_terms: 'שוטף+30'
    })
  }
}

async function pullAttendance() {
  if (!form.priority_id) { attendanceError.value = 'יש להזין מספר Priority תחילה'; return }
  loadingAttendance.value = true
  attendanceError.value = null
  try {
    const data = await getAttendanceByProject(form.priority_id)
    if (data.summary) {
      form.manpower_attendance_summary = data.summary
    } else {
      attendanceError.value = 'לא נמצאו נתוני נוכחות עבור מספר פרויקט זה'
    }
  } catch {
    attendanceError.value = 'שגיאה במשיכת נתוני נוכחות'
  } finally {
    loadingAttendance.value = false
  }
}

function nextStep() {
  error.value = null
  step.value++
}

function validateAll() {
  error.value = null
  Object.keys(fe).forEach(k => delete fe[k])
  const emptyFields = []

  // Step 0 fields
  if (props.newProject && !form.project_name?.trim()) emptyFields.push('שם פרויקט')
  if (!form.priority_id?.trim()) emptyFields.push('מספר Priority')
  if (!form.start_date) emptyFields.push('תאריך התחלה')
  if (!form.expected_end_date) emptyFields.push('צפי סיום')
  if (!form.manager?.trim()) emptyFields.push('שם מנהל פרויקט')
  if (!form.client?.trim()) emptyFields.push('שם המזמין')
  if (!form.description?.trim()) emptyFields.push('תיאור פרויקט')

  // Step 1 fields
  if (!form.total_revenue || form.total_revenue <= 0) emptyFields.push('סך הכנסות')
  if (paymentTermsTotal.value !== 100) emptyFields.push('תנאי תשלום (סה"כ חייב להיות 100%)')
  if (milestonesTotal.value > 100) emptyFields.push('פעימות תשלום (מעל 100%)')

  // Step 2 fields
  if (!form.total_budget || form.total_budget <= 0) emptyFields.push('סך תקציב הוצאות')

  // Also run existing validation for field-level errors
  validateStep0()
  validateStep1()
  validateStep2()

  if (form.expected_end_date && form.start_date && form.expected_end_date < form.start_date) {
    emptyFields.push('צפי סיום חייב להיות אחרי תאריך ההתחלה')
  }

  return emptyFields
}

function clampForecast(month) {
  if (month < startMonth.value) { form.revenue_forecast[month] = 0; return }
  const current = Number(form.revenue_forecast[month]) || 0
  const othersTotal = Object.entries(form.revenue_forecast)
    .filter(([k]) => Number(k) !== month)
    .reduce((a, [, v]) => a + (Number(v) || 0), 0)
  const max = 100 - othersTotal
  if (current > max) form.revenue_forecast[month] = Math.max(0, max)
  if (current < 0) form.revenue_forecast[month] = 0
}

function clampPaymentTerm(index) {
  let current = Number(form.revenue_payment_terms[index].percent) || 0
  if (current < 0) current = 0
  if (current > 100) current = 100
  const othersTotal = form.revenue_payment_terms
    .filter((_, i) => i !== index)
    .reduce((a, t) => a + (Number(t.percent) || 0), 0)
  form.revenue_payment_terms[index].percent = Math.min(current, Math.max(0, 100 - othersTotal))
}

function updateTermAmount(index, event) {
  const amount = Number(event.target.value) || 0
  if (!form.total_revenue || form.total_revenue <= 0) return
  const percent = Math.round((amount / form.total_revenue) * 100)
  form.revenue_payment_terms[index].percent = Math.max(0, Math.min(100, percent))
  clampPaymentTerm(index)
}

const milestonesTotal = computed(() =>
  (form.payment_milestones || []).reduce((a, m) => a + (Number(m.percent) || 0), 0)
)

function syncMilestoneFromPercent(i) {
  const ms = form.payment_milestones[i]
  let pct = Number(ms.percent) || 0
  if (pct < 0) pct = 0
  if (pct > 100) pct = 100
  ms.percent = pct
  ms.amount = form.total_revenue ? Math.round(form.total_revenue * pct / 100) : 0
}

function syncMilestoneFromAmount(i) {
  const ms = form.payment_milestones[i]
  let amt = Number(ms.amount) || 0
  if (amt < 0) amt = 0
  ms.amount = amt
  ms.percent = form.total_revenue ? Math.round((amt / form.total_revenue) * 100 * 10) / 10 : 0
}

async function save() {
  const validationErrors = validateAll()
  if (validationErrors.length > 0) {
    showValidationModal.value = true
    validationErrorsList.value = validationErrors
    return
  }
  saving.value = true
  try {
    const projectKey = props.newProject ? form.project_name : props.project
    await saveProjectForm(projectKey, { ...form })
    const draftKey = `form_draft_${props.newProject ? '__draft__' : props.project}`
    localStorage.removeItem(draftKey)
    emit('saved', projectKey)
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

function handleClose() {
  if (isDirty.value) {
    showExitConfirm.value = true
  } else {
    emit('close')
  }
}

function saveDraftAndClose() {
  const projectKey = props.newProject ? (form.project_name || '__draft__') : props.project
  localStorage.setItem(`form_draft_${projectKey}`, JSON.stringify({ ...form, _draft_step: step.value }))
  showExitConfirm.value = false
  emit('close')
}

function discardAndClose() {
  showExitConfirm.value = false
  emit('close')
}

watch(() => props.show, async (val) => {
  if (val) {
    step.value = 0
    error.value = null
    activeCategory.value = null
    attendanceError.value = null
    Object.keys(fe).forEach(k => delete fe[k])
    Object.assign(form, defaultForm())
    if (!props.newProject) {
      try {
        const data = await getProjectForm(props.project)
        if (data) {
          Object.keys(data).forEach(k => {
            if (k in form) {
              if (typeof form[k] === 'object' && !Array.isArray(form[k]) && form[k] !== null) {
                Object.assign(form[k], data[k])
              } else {
                form[k] = data[k]
              }
            }
          })
        }
      } catch {}
    }
    // Restore draft if exists
    const draftKey = `form_draft_${props.newProject ? '__draft__' : props.project}`
    const draft = localStorage.getItem(draftKey)
    if (draft) {
      try {
        const parsed = JSON.parse(draft)
        Object.keys(parsed).forEach(k => {
          if (k in form && k !== '_draft_step') form[k] = parsed[k]
        })
        if (parsed._draft_step !== undefined) step.value = parsed._draft_step
      } catch {}
      localStorage.removeItem(draftKey)
    }
    // Capture snapshot for dirty checking
    originalFormSnapshot.value = JSON.stringify(form)
  }
})
</script>

<style scoped>
.accordion-body {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.25s ease;
}
.accordion-body > div {
  overflow: hidden;
}
.accordion-body[style*="display: none"] {
  grid-template-rows: 0fr;
}
/* v-show sets display:none when hidden, so override for visible */
.accordion-body:not([style*="display: none"]) {
  grid-template-rows: 1fr;
}
</style>
