<template>
  <Teleport to="body">
    <div v-if="show" class="ui-modal-layer" dir="rtl">
      <div class="ui-modal-backdrop" @click="handleClose()"></div>

      <div ref="modalCard" class="ui-modal-card ed-fade-up" style="max-width: 56rem; max-height: 90vh; display: flex; flex-direction: column; padding: 0;">
        <!-- Header + Stepper -->
        <div class="px-5 sm:px-10 pt-6 sm:pt-8 pb-4 sm:pb-5">
          <div class="flex items-start justify-between mb-5 gap-4">
            <div>
              <div class="ed-eyebrow mb-1">{{ newProject ? 'פרויקט חדש' : 'עריכת פרויקט' }}</div>
              <h3 class="ui-display" style="font-size: clamp(1.75rem, 3vw, 2.25rem); line-height: 1;">
                {{ newProject ? 'פרויקט חדש' : project }}
              </h3>
              <p class="ed-eyebrow mt-1.5">שלב <bdi class="ed-num">{{ step + 1 }}</bdi> מתוך <bdi class="ed-num">{{ steps.length }}</bdi></p>
            </div>
            <button @click="handleClose()" class="ui-icon-btn" aria-label="סגור">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="square" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <hr class="ed-rule" />
          <!-- Step markers -->
          <div class="flex items-center gap-x-3 sm:gap-x-7 gap-y-2 overflow-x-auto mt-3 flex-nowrap sm:flex-wrap scrollbar-hide">
            <button v-for="(s, i) in steps" :key="i"
              @click="step = i"
              class="ed-marker-step"
              :class="{ 'is-active': i === step }">
              <span class="ed-marker-step__num ed-num">{{ String(i + 1).padStart(2, '0') }}</span>
              <span class="ed-marker-step__label">{{ s }}</span>
            </button>
          </div>
        </div>

        <!-- Content (scrollable) -->
        <div class="flex-1 overflow-y-auto px-4 sm:px-8 py-4 sm:py-6">

          <!-- Step 1: Project Details -->
          <div v-if="step === 0" class="space-y-6">
            <!-- Project name + Priority ID + Recurring toggle -->
            <div class="flex flex-col sm:flex-row gap-4 sm:gap-3 sm:items-end">
              <div v-if="newProject" class="flex-[15]" data-field="project_name">
                <label class="ed-label" for="field-project-name">שם פרויקט *</label>
                <input id="field-project-name" v-model="form.project_name" type="text" placeholder="שם הפרויקט"
                  @blur="vf('project_name', form.project_name, { required: true, minLen: 2 })"
                  :class="['w-full ui-input', fc('project_name')]" />
                <div v-if="fe.project_name" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe.project_name }}</div>
              </div>
              <div class="flex-[4]" data-field="priority_id">
                <label class="ed-label" for="field-priority-id">מספר Priority *</label>
                <input id="field-priority-id" v-model="form.priority_id" type="text" placeholder="P-1001"
                  @blur="vf('priority_id', form.priority_id, { required: true, minLen: 2 })"
                  :class="['w-full ui-input ui-num', fc('priority_id')]" />
                <div v-if="fe.priority_id" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe.priority_id }}</div>
              </div>
            </div>
            <!-- Start date + End date -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
              <div>
                <label class="ed-label">תאריך התחלה *</label>
                <DatePicker v-model="form.start_date"
                  :input-class="'w-full ui-input ' + (fe.start_date ? 'is-error' : '')" />
                <div v-if="fe.start_date" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe.start_date }}</div>
              </div>
              <div>
                <label class="ed-label">צפי סיום פרויקט *</label>
                <DatePicker v-model="form.expected_end_date" :min-date="form.start_date"
                  :input-class="'w-full ui-input ' + (fe.expected_end_date ? 'is-error' : '')" />
                <div v-if="fe.expected_end_date" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe.expected_end_date }}</div>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
              <div>
                <label class="ed-label" for="field-manager">מנהל פרויקט *</label>
                <select id="field-manager" v-model="form.manager"
                  @change="vf('manager', form.manager, { required: true })"
                  :class="['w-full ui-select', fc('manager')]">
                  <option value="" disabled>בחר מנהל פרויקט</option>
                  <option v-for="m in managers" :key="m" :value="m">{{ m }}</option>
                </select>
                <div v-if="fe.manager" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe.manager }}</div>
              </div>
              <div>
                <label class="ed-label" for="field-client">שם המזמין *</label>
                <input id="field-client" v-model="form.client" type="text" placeholder="שם החברה/לקוח"
                  @blur="vf('client', form.client, { required: true, minLen: 2 })"
                  :class="['w-full ui-input', fc('client')]" />
                <div v-if="fe.client" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe.client }}</div>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-5">
              <div>
                <label class="ed-label" for="field-axis">ציר</label>
                <select id="field-axis" v-model="form.axis" class="w-full ui-select">
                  <option value="לוגי">לוגי</option>
                  <option value="מנרב">מנרב</option>
                  <option value="פיתוח עסקי">פיתוח עסקי</option>
                </select>
              </div>
              <div>
                <label class="ed-label" for="field-area">תחום</label>
                <select id="field-area" v-model="form.area" class="w-full ui-select">
                  <option value="מסחרי פרטי">מסחרי פרטי</option>
                  <option value="פרוייקטים">פרוייקטים</option>
                  <option value="מטה">מטה</option>
                  <option value="רכש">רכש</option>
                  <option value="זכיינות">זכיינות</option>
                </select>
              </div>
              <div>
                <label class="ed-label" for="field-status">סטטוס</label>
                <select id="field-status" v-model="form.status" class="w-full ui-select">
                  <option value="active">פעיל</option>
                  <option value="on-hold">מושהה</option>
                  <option value="completed">הושלם</option>
                </select>
              </div>
            </div>
            <div>
              <label class="ed-label" for="field-description">תיאור פרויקט *</label>
              <textarea id="field-description" v-model="form.description" rows="3" placeholder="תיאור כללי של הפרויקט..."
                @blur="vf('description', form.description, { required: true, minLen: 5 })"
                :class="['w-full ui-input resize-none', fc('description')]"></textarea>
              <div class="flex justify-between mt-0.5">
                <div v-if="fe.description" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe.description }}</div>
                <span v-else></span>
                <span class="ed-tone-faint text-xs">{{ (form.description || '').length }} תווים</span>
              </div>
            </div>
          </div>

          <!-- Step 2: Revenue -->
          <div v-if="step === 1" class="space-y-6">
            <div>
              <label class="ed-label" for="field-total-revenue">סך הכנסות הפרויקט (₪) *</label>
              <input id="field-total-revenue" :value="fmtNum(form.total_revenue)" @input="onNumInput(form, 'total_revenue', $event)" type="text" inputmode="numeric" placeholder="0"
                @blur="vf('total_revenue', form.total_revenue, { required: true, positive: true, max: 999999999 })"
                :class="['w-full ui-input ui-num', fc('total_revenue')]" />
              <div v-if="fe.total_revenue" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe.total_revenue }}</div>
            </div>

            <!-- Payment terms as dynamic table -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="ed-label" style="margin: 0;">תנאי תשלום הכנסה</label>
                <span class="ui-pill" :class="paymentTermsTotal === 100 ? 'ui-pill-positive' : 'ui-pill-warning'">
                  סה"כ: <span class="ui-num">{{ paymentTermsTotal }}</span>%
                </span>
              </div>
              <div class="space-y-2">
                <div v-for="(term, i) in form.revenue_payment_terms" :key="i"
                  class="ui-mini-card space-y-2">
                  <div class="flex flex-wrap items-center gap-2">
                    <select v-model="term.type" class="flex-1 ui-select" style="min-width: 140px;">
                      <option value="מקדמה">מקדמה</option>
                      <option value="שוטף+0">שוטף+0</option>
                      <option value="שוטף+30">שוטף+30</option>
                      <option value="שוטף+45">שוטף+45</option>
                      <option value="שוטף+60">שוטף+60</option>
                      <option value="שוטף+75">שוטף+75</option>
                      <option value="שוטף+90">שוטף+90</option>
                      <option value="פעימות תשלום">פעימות תשלום</option>
                    </select>
                    <div v-if="term.type !== 'פעימות תשלום'" class="flex items-center gap-1">
                      <input v-model.number="term.percent" @input="clampPaymentTerm(i)" type="number" min="0" max="100" placeholder="0"
                        class="ui-input ui-num" style="width: 4.5rem; text-align: center;" />
                      <span class="ed-tone-faint text-xs">%</span>
                    </div>
                    <div v-if="term.type !== 'פעימות תשלום'" class="flex items-center gap-1">
                      <input type="text" inputmode="numeric"
                        :value="fmtNum(termAmount(i))"
                        @input="onTermAmountInput(i, $event)"
                        placeholder="0"
                        class="ui-input ui-num" style="width: 7rem; text-align: center;" />
                      <span class="ed-tone-faint text-xs">₪</span>
                    </div>
                    <button v-if="form.revenue_payment_terms.length > 1" @click="form.revenue_payment_terms.splice(i, 1)"
                      class="ui-icon-btn ed-tone-negative" aria-label="מחק שורה">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                  </div>
                  <!-- Milestones sub-section when פעימות תשלום is selected -->
                  <div v-if="term.type === 'פעימות תשלום'" class="space-y-2 pr-2" style="border-inline-end: 2px solid var(--border);">
                    <div class="flex items-center justify-between">
                      <span class="ed-label" style="margin: 0;">פעימות</span>
                      <span v-if="form.payment_milestones.length" class="ui-pill"
                        :class="milestonesTotal <= 100 ? 'ui-pill-positive' : 'ui-pill-negative'">
                        <span class="ui-num">{{ milestonesTotal }}</span>%
                      </span>
                    </div>
                    <div v-for="(ms, mi) in form.payment_milestones" :key="mi"
                      class="flex flex-wrap items-center gap-2 ui-mini-card">
                      <div class="flex items-center gap-1">
                        <input v-model.number="ms.percent" @input="syncMilestoneFromPercent(mi)" type="number" min="0" max="100" placeholder="%"
                          class="ui-input ui-num" style="width: 3.75rem; text-align: center;" />
                        <span class="ed-tone-faint text-xs">%</span>
                      </div>
                      <div class="flex items-center gap-1">
                        <input :value="fmtNum(ms.amount)" @change="e => { ms.amount = parseNum(e.target.value); syncMilestoneFromAmount(mi) }" @blur="e => { ms.amount = parseNum(e.target.value); syncMilestoneFromAmount(mi) }" type="text" inputmode="numeric" placeholder="סכום"
                          class="ui-input ui-num" style="width: 6rem; text-align: center;" />
                        <span class="ed-tone-faint text-xs">₪</span>
                      </div>
                      <DatePicker v-model="ms.date" :min-date="form.start_date"
                        :input-class="'ui-input'" />
                      <input v-model="ms.description" type="text" placeholder="תיאור"
                        class="flex-1 ui-input" style="min-width: 5rem;" />
                      <button @click="form.payment_milestones.splice(mi, 1)"
                        class="ui-icon-btn ed-tone-negative" aria-label="מחק פעימה">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                      </button>
                    </div>
                    <button @click="form.payment_milestones.push({ percent: 0, amount: 0, date: '', description: '' })"
                      class="ui-btn w-full" style="border-style: dashed; justify-content: center; gap: 0.375rem;">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                      הוסף פעימה
                    </button>
                  </div>
                </div>
                <button @click="form.revenue_payment_terms.push({ type: 'שוטף+30', percent: 0 })"
                  class="ui-btn w-full" style="border-style: dashed; justify-content: center; gap: 0.375rem;">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                  הוסף שורת תשלום
                </button>
              </div>
            </div>

            <!-- Revenue forecast table -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="ed-label" style="margin: 0;">צפי הכנסות חודשי</label>
                <div class="flex items-center gap-2">
                  <span class="ed-tone-faint text-xs">סה"כ: <span class="ui-num">{{ manualForecastTotal.toLocaleString('he-IL') }}</span> ₪</span>
                  <span class="ui-pill" :class="manualForecastPct === 100 ? 'ui-pill-positive' : manualForecastPct > 100 ? 'ui-pill-negative' : 'ui-pill-neutral'">
                    <span class="ui-num">{{ manualForecastPct }}</span>%
                  </span>
                </div>
              </div>
              <div class="overflow-x-auto" style="border: 1px solid var(--border); border-radius: var(--radius-md);">
                <table class="w-full text-xs" dir="rtl">
                  <thead>
                    <tr style="background: var(--surface-muted);">
                      <th class="px-3 py-2 text-start ed-label" style="margin: 0; min-width: 72px;">חודש</th>
                      <th class="px-3 py-2 text-end ed-label" style="margin: 0; min-width: 90px;">הכנסה צפויה (₪)</th>
                      <th class="px-3 py-2 text-end ed-label" style="margin: 0; min-width: 72px;">אחוז מסה״כ</th>
                      <th class="px-3 py-2 text-end ed-label" style="margin: 0; min-width: 90px;">כניסת תשלום (₪)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="m in activeMonthsRange" :key="m" style="border-top: 1px solid var(--border);">
                      <td class="px-3 py-1.5 font-sans font-medium text-ink">{{ hebrewMonths[m] }}</td>
                      <td class="px-2 py-1">
                        <input
                          type="number"
                          :value="revenueAmountForMonth(m) || ''"
                          @input="onRevenueAmountInput(m, $event.target.value)"
                          class="w-full ui-input text-xs ui-num"
                          style="padding: 0.25rem 0.375rem; text-align: end;"
                          :class="revenueAmountForMonth(m) > 0 ? 'ed-tone-positive' : ''"
                          placeholder="0"
                          min="0"
                        />
                      </td>
                      <td class="px-3 py-1.5 text-end ui-num" :class="form.revenue_forecast[m] > 0 ? '' : 'ed-tone-faint'">
                        {{ form.revenue_forecast[m] ? Math.round(form.revenue_forecast[m]) + '%' : '—' }}
                      </td>
                      <td class="px-3 py-1.5 text-end ui-num" :class="cashInflowForMonth(m) > 0 ? 'ed-tone-positive' : 'ed-tone-faint'">
                        {{ cashInflowForMonth(m) ? cashInflowForMonth(m).toLocaleString('he-IL') : '—' }}
                      </td>
                    </tr>
                  </tbody>
                  <tfoot>
                    <tr style="background: var(--surface-muted); border-top: 2px solid var(--border-strong);">
                      <td class="px-3 py-2 font-sans font-semibold text-ink">סה״כ</td>
                      <td class="px-3 py-2 text-end ui-num font-semibold text-ink">
                        <bdi>{{ manualForecastTotal.toLocaleString('he-IL') }}</bdi>
                      </td>
                      <td class="px-3 py-2 text-end ui-num font-semibold"
                          :class="manualForecastPct === 100 ? 'ed-tone-positive' : manualForecastPct > 100 ? 'ed-tone-negative' : 'ed-tone-warning'">
                        {{ manualForecastPct }}%
                      </td>
                      <td class="px-3 py-2 text-end ui-num font-semibold text-ink">
                        <bdi>{{ totalCashInflow.toLocaleString('he-IL') }}</bdi>
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          </div>

          <!-- Step 3: Expenses -->
          <div v-if="step === 2" class="space-y-6">

            <!-- Default payment terms for expenses -->
            <div class="ui-card flex items-center gap-4" style="background: var(--accent-soft);">
              <label class="ed-label whitespace-nowrap" style="margin: 0;">תנאי תשלום ברירת מחדל</label>
              <select v-model="form.default_expense_payment_terms"
                @change="applyDefaultPaymentTerms()"
                class="ui-select flex-1" style="max-width: 200px;">
                <option value="מקדמה">מקדמה</option>
                <option value="שוטף+0">שוטף+0</option>
                <option value="שוטף+30">שוטף+30</option>
                <option value="שוטף+45">שוטף+45</option>
                <option value="שוטף+60">שוטף+60</option>
                <option value="שוטף+75">שוטף+75</option>
                <option value="שוטף+90">שוטף+90</option>
              </select>
              <span class="ed-tone-faint text-xs">יחול על כל ההוצאות</span>
            </div>

            <!-- Expense categories accordion -->
            <div class="space-y-2">
              <div class="ed-label mb-1">קטגוריות התחייבות לספקים</div>

              <!-- ספקים -->
              <div class="ui-card" style="padding: 0; overflow: hidden;">
                <button @click="toggleCategory('subcontractors')"
                  class="ui-press w-full flex items-center justify-between px-4 py-3 text-sm" style="font-weight: 500; color: var(--ink); background: transparent; border: 0;">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full" style="background: var(--positive);"></span>
                    ספקים
                    <span v-if="form.subcontractors.length" class="ui-pill ui-pill-positive">{{ form.subcontractors.length }}</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <span v-if="subcontractorsTotal > 0" class="text-xs font-semibold ed-tone-muted ui-num">{{ subcontractorsTotal.toLocaleString('he-IL') }} ₪</span>
                    <svg class="w-4 h-4 ed-tone-faint" :class="activeCategory === 'subcontractors' ? 'rotate-180' : ''" style="transition: transform 180ms var(--ease-out);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                  </div>
                </button>
                <div v-if="activeCategory === 'subcontractors'" class="p-4 space-y-3">
                  <div v-for="(sub, i) in form.subcontractors" :key="i"
                    class="ui-mini-card space-y-2">
                    <div class="flex items-center justify-between mb-1">
                      <span class="ed-label" style="margin: 0;">ספק {{ i + 1 }}</span>
                      <button @click="form.subcontractors.splice(i, 1)"
                        class="ui-icon-btn ed-tone-negative" aria-label="מחק ספק">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                      </button>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <div>
                        <label class="ed-label">שם ספק</label>
                        <input v-model="sub.name" type="text" placeholder="שם הספק"
                          @blur="vf(`sub_name_${i}`, sub.name, { required: true, minLen: 2 })"
                          :class="['w-full ui-input', fc(`sub_name_${i}`)]" />
                        <div v-if="fe[`sub_name_${i}`]" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe[`sub_name_${i}`] }}</div>
                      </div>
                      <div>
                        <label class="ed-label">סה"כ התחייבות (ש"ח)</label>
                        <input :value="fmtNum(sub.total_amount)" @input="onNumInput(sub, 'total_amount', $event)" type="text" inputmode="numeric" placeholder="0"
                          @blur="vf(`sub_amount_${i}`, sub.total_amount, { required: true, positive: true })"
                          :class="['w-full ui-input ui-num', fc(`sub_amount_${i}`)]" />
                        <div v-if="fe[`sub_amount_${i}`]" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe[`sub_amount_${i}`] }}</div>
                      </div>
                    </div>
                    <!-- פרטי ספק -->
                    <div style="border: 1px solid var(--border); border-radius: 0.5rem; overflow: hidden;">
                      <button @click="sub._showDetails = !sub._showDetails" type="button"
                        class="ui-press w-full flex items-center justify-between px-3 py-2 text-xs ed-tone-muted" style="background: var(--surface-muted); border: 0; font-weight: 500;">
                        <span>פרטי ספק</span>
                        <svg class="w-3.5 h-3.5 ed-tone-faint" :class="sub._showDetails ? 'rotate-180' : ''" style="transition: transform 180ms var(--ease-out);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                      </button>
                      <div v-if="sub._showDetails" class="p-3 space-y-2" style="background: var(--surface-muted);">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label class="ed-label">מספר ח.פ / ת"ז</label>
                            <input v-model="sub.tax_id" type="text" placeholder="ח.פ / ת.ז"
                              class="w-full ui-input ui-num" />
                          </div>
                          <div>
                            <label class="ed-label">סוג ספק</label>
                            <select v-model="sub.vendor_type" class="w-full ui-select">
                              <option value="">בחר...</option>
                              <option value="חברה בע״מ">חברה בע״מ</option>
                              <option value="עוסק מורשה">עוסק מורשה</option>
                              <option value="עוסק פטור">עוסק פטור</option>
                            </select>
                          </div>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label class="ed-label">שם איש קשר</label>
                            <input v-model="sub.contact_name" type="text" placeholder="שם איש קשר"
                              class="w-full ui-input" />
                          </div>
                          <div>
                            <label class="ed-label">תפקיד</label>
                            <input v-model="sub.contact_role" type="text" placeholder="תפקיד"
                              class="w-full ui-input" />
                          </div>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label class="ed-label">טלפון</label>
                            <input v-model="sub.phone" type="tel" placeholder="050-0000000" dir="ltr"
                              class="w-full ui-input ui-num" />
                          </div>
                          <div>
                            <label class="ed-label">דוא"ל</label>
                            <input v-model="sub.email" type="email" placeholder="email@example.com" dir="ltr"
                              class="w-full ui-input" />
                          </div>
                        </div>
                        <div>
                          <label class="ed-label">כתובת מלאה</label>
                          <input v-model="sub.address" type="text" placeholder="כתובת"
                            class="w-full ui-input" />
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div>
                            <label class="ed-label">איש קשר הנה"ח</label>
                            <input v-model="sub.accounting_contact" type="text" placeholder="שם"
                              class="w-full ui-input" />
                          </div>
                          <div>
                            <label class="ed-label">טלפון הנה"ח</label>
                            <input v-model="sub.accounting_phone" type="tel" placeholder="050-0000000" dir="ltr"
                              class="w-full ui-input ui-num" />
                          </div>
                        </div>
                        <div>
                          <label class="ed-label">מייל הנה"ח</label>
                          <input v-model="sub.accounting_email" type="email" placeholder="accounting@example.com" dir="ltr"
                            class="w-full ui-input" />
                        </div>
                      </div>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <div>
                        <label class="ed-label">תאריך התחלה</label>
                        <DatePicker v-model="sub.start_date" :min-date="form.start_date"
                          input-class="w-full ui-input" />
                      </div>
                      <div>
                        <label class="ed-label">תאריך סיום</label>
                        <DatePicker v-model="sub.end_date" :min-date="form.start_date"
                          input-class="w-full ui-input" />
                      </div>
                    </div>
                    <!-- Payment terms array (like revenue) -->
                    <div>
                      <label class="ed-label">תנאי תשלום</label>
                      <div class="space-y-1.5">
                        <div v-for="(term, ti) in sub.payment_terms" :key="ti" class="flex items-center gap-2 flex-wrap">
                          <select v-model="term.type" class="ui-select flex-1" style="min-width: 100px;">
                            <option value="מקדמה">מקדמה</option>
                            <option value="שוטף+0">שוטף+0</option>
                            <option value="שוטף+30">שוטף+30</option>
                            <option value="שוטף+45">שוטף+45</option>
                            <option value="שוטף+60">שוטף+60</option>
                            <option value="שוטף+75">שוטף+75</option>
                            <option value="שוטף+90">שוטף+90</option>
                          </select>
                          <div class="flex items-center gap-1">
                            <input type="text" inputmode="numeric"
                              :value="fmtNum(subTermAmount(sub, ti))"
                              @input="onSubTermAmountInput(sub, ti, $event)"
                              placeholder="0"
                              class="ui-input ui-num" style="width: 6rem; text-align: center;" />
                            <span class="ed-tone-faint text-xs">₪</span>
                          </div>
                          <span class="ed-tone-faint text-xs ui-num">{{ sub.total_amount && term.percent ? Math.round(term.percent * 10) / 10 + '%' : '' }}</span>
                          <button @click="sub.payment_terms.splice(ti, 1)" v-if="sub.payment_terms.length > 1"
                            class="ui-icon-btn ed-tone-negative" aria-label="מחק תנאי תשלום">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                          </button>
                        </div>
                      </div>
                      <div class="flex items-center justify-between mt-1.5">
                        <button @click="sub.payment_terms.push({ type: 'שוטף+30', percent: 0 })"
                          class="ed-link">+ הוסף שורת תשלום</button>
                        <span class="ui-pill" :class="subTermsTotal(sub) === 100 ? 'ui-pill-positive' : 'ui-pill-warning'">
                          סה"כ: <span class="ui-num">{{ subTermsTotal(sub) }}</span>%
                        </span>
                      </div>
                    </div>
                    <div>
                      <label class="ed-label">חוזה ספק</label>
                      <div class="flex items-center gap-2">
                        <label class="ui-btn flex-1" style="cursor: pointer; justify-content: flex-start; gap: 0.5rem;">
                          <svg class="w-4 h-4 ed-tone-faint" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13"/></svg>
                          <span class="ed-tone-muted">{{ sub.contract_filename || 'בחר קובץ חוזה...' }}</span>
                          <input type="file" accept=".pdf,.doc,.docx,.jpg,.png" class="hidden" @change="e => { sub.contract_filename = e.target.files[0]?.name || ''; sub.contract_file = e.target.files[0] }" />
                        </label>
                        <button v-if="sub.contract_filename" @click="sub.contract_filename = ''; sub.contract_file = null"
                          class="ui-icon-btn ed-tone-negative" aria-label="מחק קובץ">
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                      </div>
                    </div>
                  </div>
                  <button @click="addSubcontractor"
                    class="ui-btn w-full" style="border-style: dashed; justify-content: center; gap: 0.5rem; color: var(--positive);">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                    הוספת ספק חדש
                  </button>
                </div>
              </div>

              <!-- כוח אדם -->
              <div class="ui-card" style="padding: 0; overflow: hidden;">
                <button @click="toggleCategory('manpower')"
                  class="ui-press w-full flex items-center justify-between px-4 py-3 text-sm" style="font-weight: 500; color: var(--ink); background: transparent; border: 0;">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full" style="background: var(--accent);"></span>
                    כוח אדם
                    <span v-if="form.manpower_attendance_summary" class="ui-pill ui-pill-neutral">מנוכחות</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <span v-if="categoryTotal('manpower') > 0" class="text-xs font-semibold ed-tone-muted ui-num">{{ categoryTotal('manpower').toLocaleString('he-IL') }} ₪</span>
                    <svg class="w-4 h-4 ed-tone-faint" :class="activeCategory === 'manpower' ? 'rotate-180' : ''" style="transition: transform 180ms var(--ease-out);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                  </div>
                </button>
                <div v-if="activeCategory === 'manpower'" class="p-4 space-y-3">
                  <!-- Pull from attendance -->
                  <div class="ui-card" style="background: var(--accent-soft);">
                    <div class="ed-label mb-2" style="color: var(--accent);">משיכה משעון נוכחות רומי</div>
                    <div class="flex items-center gap-2">
                      <input v-model="form.priority_id" type="text" readonly
                        class="flex-1 ui-input ed-tone-muted" placeholder="מספר פרויקט" />
                      <button @click="pullAttendance" :disabled="loadingAttendance"
                        class="ui-btn ui-btn-accent disabled:opacity-50">
                        <svg v-if="loadingAttendance" class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                        משוך נוכחות
                      </button>
                    </div>
                    <div v-if="form.manpower_attendance_summary" class="mt-2 grid grid-cols-3 gap-2">
                      <div class="ui-mini-card text-center">
                        <div class="ui-display ui-num" style="color: var(--accent); font-size: 1.125rem;">{{ form.manpower_attendance_summary.total_hours?.toFixed(1) }}</div>
                        <div class="ed-label" style="margin: 0;">שעות</div>
                      </div>
                      <div class="ui-mini-card text-center">
                        <div class="ui-display ui-num" style="color: var(--accent); font-size: 1.125rem;">{{ form.manpower_attendance_summary.employees }}</div>
                        <div class="ed-label" style="margin: 0;">עובדים</div>
                      </div>
                      <div class="ui-mini-card text-center">
                        <div class="ui-display ui-num" style="color: var(--accent); font-size: 1.125rem;">{{ form.manpower_attendance_summary.total_cost?.toLocaleString('he-IL') }}</div>
                        <div class="ed-label" style="margin: 0;">עלות ש"ח</div>
                      </div>
                    </div>
                    <div v-if="attendanceError" class="mt-2 text-xs ed-tone-negative">{{ attendanceError }}</div>
                  </div>
                  <!-- Manual lines -->
                  <div class="space-y-3">
                    <div v-for="(line, i) in form.expense_lines_manpower" :key="i"
                      class="ui-mini-card space-y-2">
                      <div class="flex items-center justify-between mb-1">
                        <span class="ed-label" style="margin: 0;">שורה {{ i + 1 }}</span>
                        <button @click="form.expense_lines_manpower.splice(i, 1)" class="ui-icon-btn ed-tone-negative" aria-label="מחק שורה">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                      </div>
                      <div class="grid grid-cols-2 gap-2">
                        <div>
                          <label class="ed-label">פירוט</label>
                          <input v-model="line.name" type="text" placeholder="תיאור ההוצאה"
                            @blur="vf(`mp_name_${i}`, line.name, { required: true, minLen: 2 })"
                            :class="['w-full ui-input', fc(`mp_name_${i}`)]" />
                          <div v-if="fe[`mp_name_${i}`]" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe[`mp_name_${i}`] }}</div>
                        </div>
                        <div>
                          <label class="ed-label">התחייבות לספק (₪)</label>
                          <input :value="fmtNum(line.monthly_amount)" @input="onNumInput(line, 'monthly_amount', $event)" type="text" inputmode="numeric" placeholder="0"
                            @blur="vf(`mp_amount_${i}`, line.monthly_amount, { required: true, positive: true })"
                            :class="['w-full ui-input ui-num', fc(`mp_amount_${i}`)]" />
                          <div v-if="fe[`mp_amount_${i}`]" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe[`mp_amount_${i}`] }}</div>
                        </div>
                      </div>
                      <div class="grid grid-cols-2 gap-2">
                        <div>
                          <label class="ed-label">מחודש</label>
                          <select v-model.number="line.start_month" class="w-full ui-select">
                            <option v-for="m in 12" :key="m" :value="m">חודש {{ m }}</option>
                          </select>
                        </div>
                        <div>
                          <label class="ed-label">עד חודש</label>
                          <select v-model.number="line.end_month"
                            :class="['w-full ui-select', fc(`mp_end_${i}`)]">
                            <option v-for="m in 12" :key="m" :value="m">חודש {{ m }}</option>
                          </select>
                          <div v-if="fe[`mp_end_${i}`]" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe[`mp_end_${i}`] }}</div>
                        </div>
                      </div>
                      <!-- Line total preview -->
                      <div v-if="line.monthly_amount && line.start_month && line.end_month" class="ui-mini-card text-xs ed-tone-faint flex justify-between" style="padding: 0.5rem 0.75rem;">
                        <span><span class="ui-num">{{ line.end_month - line.start_month + 1 }}</span> חודשים</span>
                        <span class="ed-tone-muted ui-num">סה"כ: {{ (line.monthly_amount * (line.end_month - line.start_month + 1)).toLocaleString('he-IL') }} ₪</span>
                      </div>
                    </div>
                  </div>
                  <button @click="addExpenseLine('manpower')"
                    class="ui-btn w-full" style="border-style: dashed; justify-content: center; gap: 0.375rem;">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                    הוסף שורה ידנית
                  </button>
                </div>
              </div>

              <!-- Standard categories (supplier forms like subcontractors) -->
              <div v-for="cat in standardCategories" :key="cat.key" class="ui-card" style="padding: 0; overflow: hidden;">
                <button @click="toggleCategory(cat.key)"
                  class="ui-press w-full flex items-center justify-between px-4 py-3 text-sm" style="font-weight: 500; color: var(--ink); background: transparent; border: 0;">
                  <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full" :class="cat.color"></span>
                    {{ cat.label }}
                    <span v-if="form['expense_lines_' + cat.key]?.length" class="ui-pill ui-pill-neutral">{{ form['expense_lines_' + cat.key].length }}</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <span v-if="categoryTotal(cat.key) > 0" class="text-xs font-semibold ed-tone-muted ui-num">{{ categoryTotal(cat.key).toLocaleString('he-IL') }} ₪</span>
                    <svg class="w-4 h-4 ed-tone-faint" :class="activeCategory === cat.key ? 'rotate-180' : ''" style="transition: transform 180ms var(--ease-out);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                  </div>
                </button>
                <div v-show="activeCategory === cat.key" class="accordion-body">
                  <div class="p-4 space-y-3">
                    <!-- Empty state -->
                    <div v-if="!form['expense_lines_' + cat.key]?.length" class="text-center py-6">
                      <div class="text-2xl mb-1" style="opacity: 0.4;">📋</div>
                      <div class="text-xs ed-tone-faint">אין {{ cat.label }} בקטגוריה זו</div>
                      <div class="text-xs ed-tone-faint mt-0.5">לחץ למטה להוספה</div>
                    </div>
                    <!-- Supplier cards -->
                    <div v-for="(line, i) in form['expense_lines_' + cat.key]" :key="i"
                      class="ui-mini-card space-y-2">
                      <div class="flex items-center justify-between mb-1">
                        <span class="ed-label" style="margin: 0;">ספק {{ i + 1 }}</span>
                        <button @click="form['expense_lines_' + cat.key].splice(i, 1)" class="ui-icon-btn ed-tone-negative" aria-label="מחק ספק">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                        </button>
                      </div>
                      <div class="grid grid-cols-2 gap-2">
                        <div>
                          <label class="ed-label">שם ספק</label>
                          <input v-model="line.name" type="text" placeholder="שם הספק"
                            @blur="vf(`${cat.key}_name_${i}`, line.name, { required: true, minLen: 2 })"
                            :class="['w-full ui-input', fc(`${cat.key}_name_${i}`)]" />
                          <div v-if="fe[`${cat.key}_name_${i}`]" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe[`${cat.key}_name_${i}`] }}</div>
                        </div>
                        <div>
                          <label class="ed-label">התחייבות לספק (₪)</label>
                          <input :value="fmtNum(line.monthly_amount)" @input="onNumInput(line, 'monthly_amount', $event)" type="text" inputmode="numeric" placeholder="0"
                            @blur="vf(`${cat.key}_amount_${i}`, line.monthly_amount, { required: true, positive: true })"
                            :class="['w-full ui-input ui-num', fc(`${cat.key}_amount_${i}`)]" />
                          <div v-if="fe[`${cat.key}_amount_${i}`]" class="ui-field-error ui-field-error--animate"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>{{ fe[`${cat.key}_amount_${i}`] }}</div>
                        </div>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <div>
                          <label class="ed-label">תאריך התחלה</label>
                          <DatePicker v-model="line.start_date" :min-date="form.start_date"
                            input-class="w-full ui-input" />
                        </div>
                        <div>
                          <label class="ed-label">תאריך סיום</label>
                          <DatePicker v-model="line.end_date" :min-date="form.start_date"
                            input-class="w-full ui-input" />
                        </div>
                        <div>
                          <label class="ed-label">תנאי תשלום</label>
                          <select v-model="line.payment_terms"
                            class="w-full ui-select">
                            <option value="מקדמה">מקדמה</option>
                            <option value="שוטף+0">שוטף+0</option>
                            <option value="שוטף+30">שוטף+30</option>
                            <option value="שוטף+45">שוטף+45</option>
                            <option value="שוטף+60">שוטף+60</option>
                            <option value="שוטף+75">שוטף+75</option>
                            <option value="שוטף+90">שוטף+90</option>
                            <option value="פעימות תשלום">פעימות תשלום</option>
                          </select>
                        </div>
                      </div>
                      <!-- Expense milestones when פעימות תשלום is selected -->
                      <div v-if="line.payment_terms === 'פעימות תשלום'" class="space-y-2 pr-2" style="border-inline-end: 2px solid var(--border);">
                        <div class="flex items-center justify-between">
                          <span class="ed-label" style="margin: 0;">פעימות</span>
                          <span v-if="line.milestones?.length" class="ui-pill"
                            :class="lineMilestonesTotal(line) <= 100 ? 'ui-pill-positive' : 'ui-pill-negative'">
                            <span class="ui-num">{{ lineMilestonesTotal(line) }}</span>%
                          </span>
                        </div>
                        <div v-for="(ms, mi) in (line.milestones || [])" :key="mi"
                          class="flex flex-wrap items-center gap-2 ui-mini-card">
                          <div class="flex items-center gap-1">
                            <input v-model.number="ms.percent" @input="syncLineMilestoneFromPercent(line, mi)" type="number" min="0" max="100" placeholder="%"
                              class="ui-input ui-num" style="width: 3.75rem; text-align: center;" />
                            <span class="ed-tone-faint text-xs">%</span>
                          </div>
                          <div class="flex items-center gap-1">
                            <input :value="fmtNum(ms.amount)" @change="e => { ms.amount = parseNum(e.target.value); syncLineMilestoneFromAmount(line, mi) }" @blur="e => { ms.amount = parseNum(e.target.value); syncLineMilestoneFromAmount(line, mi) }" type="text" inputmode="numeric" placeholder="סכום"
                              class="ui-input ui-num" style="width: 6rem; text-align: center;" />
                            <span class="ed-tone-faint text-xs">₪</span>
                          </div>
                          <DatePicker v-model="ms.date" :min-date="form.start_date"
                            :input-class="'ui-input'" />
                          <input v-model="ms.description" type="text" placeholder="תיאור"
                            class="flex-1 ui-input" style="min-width: 5rem;" />
                          <button @click="line.milestones.splice(mi, 1)"
                            class="ui-icon-btn ed-tone-negative" aria-label="מחק פעימה">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                          </button>
                        </div>
                        <button @click="if(!line.milestones) line.milestones = []; line.milestones.push({ percent: 0, amount: 0, date: '', description: '' })"
                          class="ui-btn w-full" style="border-style: dashed; justify-content: center; gap: 0.375rem;">
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                          הוסף פעימה
                        </button>
                      </div>
                    </div>
                    <button @click="addSupplierLine(cat.key)"
                      class="ui-btn w-full" style="border-style: dashed; justify-content: center; gap: 0.375rem;">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                      הוסף {{ cat.label }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Total summary -->
            <div class="ui-mini-card">
              <div class="flex items-center justify-between">
                <span class="ed-label" style="margin: 0;">סה"כ התחייבויות:</span>
                <span class="ui-display ui-num" style="font-size: 1rem;">
                  {{ totalMonthlyExpenses.toLocaleString('he-IL') }} ₪
                </span>
              </div>
            </div>
          </div>

          <!-- Step 4: Summary / Overview -->
          <div v-if="step === 3" class="space-y-6">
            <!-- Project Details -->
            <div class="ui-card">
              <div class="flex items-center justify-between mb-4">
                <h4 class="ed-eyebrow-lg" style="margin: 0;">פרטי פרויקט</h4>
                <button @click="step = 0" class="ed-link">עריכה</button>
              </div>
              <div class="grid grid-cols-2 gap-x-8 gap-y-2.5 text-sm">
                <div v-if="newProject"><span class="ed-tone-faint">שם פרויקט: </span><span class="ed-tone-muted" style="font-weight: 500;">{{ form.project_name }}</span></div>
                <div><span class="ed-tone-faint">מספר Priority: </span><span class="ed-tone-muted ui-num" style="font-weight: 500;">{{ form.priority_id }}</span></div>
                <div><span class="ed-tone-faint">תאריך התחלה: </span><span class="ed-tone-muted ui-num" style="font-weight: 500;">{{ form.start_date }}</span></div>
                <div><span class="ed-tone-faint">צפי סיום: </span><span class="ed-tone-muted ui-num" style="font-weight: 500;">{{ form.expected_end_date }}</span></div>
                <div v-if="form.company_id"><span class="ed-tone-faint">ח.פ: </span><span class="ed-tone-muted ui-num" style="font-weight: 500;">{{ form.company_id }}</span></div>
                <div><span class="ed-tone-faint">מנהל פרויקט: </span><span class="ed-tone-muted" style="font-weight: 500;">{{ form.manager }}</span></div>
                <div><span class="ed-tone-faint">מזמין: </span><span class="ed-tone-muted" style="font-weight: 500;">{{ form.client }}</span></div>
                <div><span class="ed-tone-faint">תחום: </span><span class="ed-tone-muted" style="font-weight: 500;">{{ form.area }}</span></div>
                <div><span class="ed-tone-faint">ציר: </span><span class="ed-tone-muted" style="font-weight: 500;">{{ form.axis }}</span></div>
                <div><span class="ed-tone-faint">סטטוס: </span><span class="ed-tone-muted" style="font-weight: 500;">{{ form.status === 'active' ? 'פעיל' : form.status === 'on-hold' ? 'מושהה' : 'הושלם' }}</span></div>
              </div>
              <div v-if="form.description" class="mt-3 text-sm">
                <span class="ed-tone-faint">תיאור: </span><span class="ed-tone-muted">{{ form.description }}</span>
              </div>
            </div>

            <!-- Revenue -->
            <div class="ui-card">
              <div class="flex items-center justify-between mb-4">
                <h4 class="ed-eyebrow-lg" style="margin: 0;">צפי הכנסות</h4>
                <button @click="step = 1" class="ed-link">עריכה</button>
              </div>
              <div class="text-sm mb-3">
                <span class="ed-tone-faint">סך הכנסות: </span>
                <span class="ui-display ui-num" style="font-size: 1rem;">{{ form.total_revenue ? form.total_revenue.toLocaleString('he-IL') : '0' }} ₪</span>
              </div>
              <!-- Payment terms -->
              <div v-if="form.revenue_payment_terms?.length" class="mb-4">
                <div class="ed-label mb-2">תנאי תשלום:</div>
                <div class="flex flex-wrap gap-2">
                  <span v-for="(term, i) in form.revenue_payment_terms" :key="i"
                    class="ui-pill ui-pill-neutral">
                    <span class="ed-tone-muted">{{ term.type }}</span>
                    <span class="ed-tone-faint ui-num">{{ term.percent }}%</span>
                    <span v-if="form.total_revenue" class="ed-tone-faint">·</span>
                    <span v-if="form.total_revenue" class="ed-tone-faint ui-num">{{ Math.round(form.total_revenue * term.percent / 100).toLocaleString('he-IL') }} ₪</span>
                  </span>
                </div>
              </div>
              <!-- Revenue forecast mini table (auto-computed) -->
              <div>
                <div class="ed-label mb-2">תחזית כניסת הכנסות חודשית:</div>
                <div class="overflow-x-auto">
                <div class="grid grid-cols-12 gap-1 text-center min-w-[600px]">
                  <div v-for="m in 12" :key="m" class="text-xs">
                    <div class="ed-label" style="margin-bottom: 0.25rem;">{{ m }}</div>
                    <div class="py-1 rounded ui-num" :class="cashInflowForMonth(m) > 0 ? 'ed-tone-positive' : 'ed-tone-faint'" :style="cashInflowForMonth(m) > 0 ? 'background: var(--positive-soft); font-weight: 500;' : ''">
                      {{ cashInflowForMonth(m) ? cashInflowForMonth(m).toLocaleString('he-IL') : '-' }}
                    </div>
                  </div>
                </div>
                </div>
              </div>
              <!-- Payment milestones summary -->
              <div v-if="form.payment_milestones?.length" class="mb-4">
                <div class="ed-label mb-2">פעימות תשלום:</div>
                <div class="space-y-1">
                  <div v-for="(ms, i) in form.payment_milestones" :key="i"
                    class="ui-mini-card flex items-center justify-between text-xs">
                    <span class="ed-tone-muted" style="font-weight: 500;">{{ ms.description || 'פעימה ' + (i+1) }}</span>
                    <div class="flex items-center gap-3">
                      <span class="ed-tone-faint ui-num">{{ ms.percent }}%</span>
                      <span class="ed-tone-muted ui-num" style="font-weight: 500;">{{ (ms.amount || 0).toLocaleString('he-IL') }} ₪</span>
                      <span class="ed-tone-faint ui-num">{{ ms.date || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Expenses -->
            <div class="ui-card">
              <div class="flex items-center justify-between mb-4">
                <h4 class="ed-eyebrow-lg" style="margin: 0;">צפי הוצאות</h4>
                <button @click="step = 2" class="ed-link">עריכה</button>
              </div>
              <div class="grid grid-cols-2 gap-x-8 gap-y-2 text-sm mb-4">
                <div><span class="ed-tone-faint">סה"כ הוצאות: </span><span class="ui-display ui-num" style="font-size: 1rem;">{{ totalMonthlyExpenses.toLocaleString('he-IL') }} ₪</span></div>
              </div>
              <!-- Subcontractors -->
              <div v-if="form.subcontractors?.length" class="mb-3">
                <div class="ed-label mb-2 flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full" style="background: var(--positive);"></span> ספקים (<span class="ui-num">{{ form.subcontractors.length }}</span>)
                </div>
                <div class="space-y-1">
                  <div v-for="(sub, i) in form.subcontractors" :key="i"
                    class="ui-mini-card flex items-center justify-between text-xs">
                    <span class="ed-tone-muted" style="font-weight: 500;">{{ sub.name || 'ללא שם' }}</span>
                    <span class="ed-tone-muted ui-num">{{ (sub.total_amount || 0).toLocaleString('he-IL') }} ₪</span>
                  </div>
                </div>
              </div>
              <!-- Other categories -->
              <template v-for="cat in allExpenseCategories" :key="cat.key">
                <div v-if="form['expense_lines_' + cat.key]?.length" class="mb-3">
                  <div class="ed-label mb-2 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full" :class="cat.color"></span> {{ cat.label }} (<span class="ui-num">{{ form['expense_lines_' + cat.key].length }}</span>)
                  </div>
                  <div class="space-y-1">
                    <div v-for="(line, i) in form['expense_lines_' + cat.key]" :key="i"
                      class="ui-mini-card flex items-center justify-between text-xs">
                      <span class="ed-tone-muted" style="font-weight: 500;">{{ line.name || 'ללא שם' }}</span>
                      <span class="ed-tone-muted ui-num">{{ (line.monthly_amount || 0).toLocaleString('he-IL') }} ₪/חודש</span>
                    </div>
                  </div>
                </div>
              </template>
              <!-- Total -->
              <hr class="ui-divider" style="margin: 0.75rem 0;" />
              <div class="flex items-center justify-between text-sm">
                <span class="ed-tone-muted">סה"כ התחייבויות:</span>
                <span class="ui-display ui-num" style="font-size: 1rem;">
                  {{ totalMonthlyExpenses.toLocaleString('he-IL') }} ₪
                </span>
              </div>
            </div>

            <!-- Financial Summary KPIs -->
            <div class="ui-card">
              <h4 class="ed-eyebrow-lg mb-4" style="margin-top: 0;">סיכום כספי</h4>
              <div class="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div class="ed-label mb-1">סך הכנסות</div>
                  <div class="ui-display ui-num" style="font-size: 1.375rem;">{{ (form.total_revenue || 0).toLocaleString('he-IL') }}</div>
                  <div class="text-[10px] ed-tone-faint">₪</div>
                </div>
                <div>
                  <div class="ed-label mb-1">סך הוצאות</div>
                  <div class="ui-display ui-num ed-tone-warning" style="font-size: 1.375rem;">{{ totalMonthlyExpenses.toLocaleString('he-IL') }}</div>
                  <div class="text-[10px] ed-tone-faint">₪</div>
                </div>
                <div>
                  <div class="ed-label mb-1">רווח צפוי</div>
                  <div class="ui-display ui-num" :class="(form.total_revenue || 0) - totalMonthlyExpenses >= 0 ? 'ed-tone-positive' : 'ed-tone-negative'" style="font-size: 1.375rem;">
                    {{ ((form.total_revenue || 0) - totalMonthlyExpenses).toLocaleString('he-IL') }}
                  </div>
                  <div class="text-[10px] ed-tone-faint">₪</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Exit confirmation overlay -->
        <div v-if="showExitConfirm" class="absolute inset-0 z-10 flex items-center justify-center" style="background: rgba(255,255,255,0.92); border-radius: inherit;">
          <div class="text-center max-w-xs">
            <div class="text-3xl mb-3">💾</div>
            <h4 class="ui-display mb-2" style="font-size: 1rem;">הטופס לא הושלם</h4>
            <p class="text-sm ed-tone-muted mb-6">האם לשמור את המצב הנוכחי כטיוטא?</p>
            <div class="flex flex-col gap-2">
              <button @click="saveDraftAndClose" class="ui-btn ui-btn-accent w-full" style="justify-content: center;">שמור טיוטא</button>
              <button @click="discardAndClose" class="ui-btn w-full" style="justify-content: center;">צא ללא שמירה</button>
              <button @click="showExitConfirm = false" class="ed-link">המשך עריכה</button>
            </div>
          </div>
        </div>

        <!-- Validation errors overlay -->
        <div v-if="showValidationModal" class="absolute inset-0 z-10 flex items-center justify-center" style="background: rgba(255,255,255,0.92); border-radius: inherit;">
          <div class="text-center max-w-sm px-4">
            <div class="text-3xl mb-3">&#9888;&#65039;</div>
            <h4 class="ui-display mb-2" style="font-size: 1rem;">לא ניתן לשמור את הפרויקט</h4>
            <p class="text-sm ed-tone-muted mb-4">יש להשלים את השדות הבאים:</p>
            <div class="ui-mini-card mb-5 text-right max-h-[200px] overflow-y-auto">
              <ul class="space-y-1.5">
                <li v-for="(field, i) in validationErrorsList" :key="i" class="flex items-center gap-2 text-sm ed-tone-negative">
                  <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  {{ field }}
                </li>
              </ul>
            </div>
            <button @click="showValidationModal = false" class="ui-btn ui-btn-dark w-full" style="justify-content: center;">הבנתי, חזרה לעריכה</button>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-4 sm:px-8 py-4 sm:py-5 flex items-center justify-between" style="border-top: 1px solid var(--border); background: var(--surface);">
          <button v-if="step > 0" @click="step--" class="ui-btn" style="gap: 0.375rem;">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
            חזרה
          </button>
          <div v-else></div>

          <div class="flex items-center gap-3">
            <div v-if="error" class="ed-tone-negative text-xs" style="font-weight: 500;">{{ error }}</div>
            <button v-if="step < steps.length - 1" @click="nextStep" class="ui-btn ui-btn-dark" style="gap: 0.375rem;">
              הבא
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
            </button>
            <button v-else @click="save" :disabled="saving" class="ui-btn ui-btn-dark disabled:opacity-50" style="gap: 0.375rem;">
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
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { getProjectForm, saveProjectForm } from '../services/api'
import { useToast } from '../composables/useToast'
import { useFocusTrap } from '../composables/useFocusTrap'
import DatePicker from './DatePicker.vue'

// Format number with commas for display
function fmtNum(val) {
  if (val === null || val === undefined || val === '' || val === 0) return ''
  return Number(val).toLocaleString('he-IL')
}
// Parse formatted string back to number
function parseNum(str) {
  const cleaned = String(str).replace(/[,\s]/g, '')
  const num = parseFloat(cleaned)
  return isNaN(num) ? 0 : num
}
// Handle formatted number input: updates the reactive property
function onNumInput(obj, key, event) {
  const raw = parseNum(event.target.value)
  obj[key] = raw
  // Reformat the display value
  const el = event.target
  const pos = el.selectionStart
  const oldLen = el.value.length
  el.value = raw ? raw.toLocaleString('he-IL') : ''
  const newLen = el.value.length
  el.setSelectionRange(pos + newLen - oldLen, pos + newLen - oldLen)
}

const props = defineProps({
  show: Boolean,
  project: String,
  newProject: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'saved'])
const toast = useToast()
const modalCard = ref(null)
const { activate, deactivate } = useFocusTrap(modalCard)
watch(() => props.show, async (val) => {
  if (val) { await nextTick(); activate() } else { deactivate() }
})

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

const managers = ['אלון', 'אתי', 'אריאל']

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
  axis: 'לוגי',
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
  default_expense_payment_terms: 'שוטף+30',
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
  if (err) {
    const el = document.querySelector(`[data-field="${name}"]`)
    if (el) { el.classList.remove('ui-shake'); void el.offsetWidth; el.classList.add('ui-shake') }
  }
  return err
}

// Dynamic class for input border
function fc(name) {
  return fe[name] ? 'border-red-400! bg-paper-dark!' : ''
}

// Validate all step fields
function validateStep0() {
  const errs = []
  if (props.newProject) errs.push(vf('project_name', form.project_name, { required: true, minLen: 2 }))
  errs.push(vf('priority_id', form.priority_id, { required: true, minLen: 2 }))
  errs.push(vf('start_date', form.start_date, { required: true }))
  errs.push(vf('manager', form.manager, { required: true }))
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
  // subcontractors
  form.subcontractors.forEach((sub, i) => {
    if (sub.name || sub.total_amount) {
      errs.push(vf(`sub_name_${i}`, sub.name, { required: true, minLen: 2 }))
      errs.push(vf(`sub_amount_${i}`, sub.total_amount, { required: true, positive: true }))
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

const hebrewMonths = { 1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל', 5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט', 9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר' }

const activeMonthsRange = computed(() => {
  const result = []
  for (let m = startMonth.value; m <= endMonth.value; m++) result.push(m)
  return result
})

const totalCashInflow = computed(() =>
  activeMonthsRange.value.reduce((sum, m) => sum + cashInflowForMonth(m), 0)
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

// Revenue forecast helpers: amount ↔ percentage conversion
// Local amounts array — breaks the reactive loop so typing works freely
const revenueAmounts = reactive({})

function initRevenueAmounts() {
  for (let m = 1; m <= 12; m++) {
    const pct = Number(form.revenue_forecast[m]) || 0
    revenueAmounts[m] = (pct && form.total_revenue) ? Math.round(form.total_revenue * pct / 100) : 0
  }
}

function revenueAmountForMonth(m) {
  return revenueAmounts[m] || 0
}

function onRevenueAmountInput(m, rawValue) {
  const amount = Number(rawValue) || 0
  revenueAmounts[m] = amount
  if (!form.total_revenue || form.total_revenue <= 0) {
    form.revenue_forecast[m] = 0
    return
  }
  form.revenue_forecast[m] = (amount / form.total_revenue) * 100
}

const manualForecastTotal = computed(() => {
  let total = 0
  for (let m = 1; m <= 12; m++) total += revenueAmountForMonth(m)
  return total
})

const manualForecastPct = computed(() => {
  return Math.round(Object.values(form.revenue_forecast).reduce((a, v) => a + (Number(v) || 0), 0))
})

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
    } else if (term.type === 'פעימות תשלום') {
      // Milestones handled separately
    } else {
      // שוטף+X: invoice at project END, payment = end of end_month + X days
      const xDays = extractShotefDays(term.type)
      const invYear = em < sm ? startYear + 1 : startYear
      const payMonth = shotefPaymentMonth(em, invYear, xDays)
      if (payMonth === targetMonth) {
        total += Math.round(termAmount)
      }
    }
  }
  return total
}

const totalMonthlyExpenses = computed(() => {
  let total = 0
  for (const sub of form.subcontractors) total += Number(sub.total_amount) || 0
  for (const cat of ['manpower', 'equipment', 'insurance', 'consultants', 'financing', 'other']) {
    for (const line of form['expense_lines_' + cat] || []) total += Number(line.monthly_amount) || 0
  }
  return total
})

const subcontractorsTotal = computed(() => {
  return form.subcontractors.reduce((sum, sub) => sum + (Number(sub.total_amount) || 0), 0)
})

function subTermsTotal(sub) {
  if (!Array.isArray(sub.payment_terms)) return 0
  return sub.payment_terms.reduce((sum, t) => sum + (Number(t.percent) || 0), 0)
}

// Subcontractor term: derive amount from percent
function subTermAmount(sub, termIndex) {
  const pct = Number(sub.payment_terms[termIndex].percent) || 0
  return sub.total_amount ? Math.round(sub.total_amount * pct / 100) : 0
}

// Subcontractor term: type amount → auto-compute percent
function onSubTermAmountInput(sub, termIndex, event) {
  const el = event.target
  const raw = parseNum(el.value)
  // Format with commas + preserve cursor
  const pos = el.selectionStart
  const oldLen = el.value.length
  el.value = raw ? raw.toLocaleString('he-IL') : ''
  const newLen = el.value.length
  el.setSelectionRange(pos + newLen - oldLen, pos + newLen - oldLen)
  // Sync percent from amount
  if (!sub.total_amount || sub.total_amount <= 0) return
  const percent = (raw / sub.total_amount) * 100
  // Clamp so total doesn't exceed 100%
  const othersTotal = sub.payment_terms
    .filter((_, i) => i !== termIndex)
    .reduce((a, t) => a + (Number(t.percent) || 0), 0)
  const max = Math.max(0, 100 - othersTotal)
  sub.payment_terms[termIndex].percent = Math.min(Math.max(0, percent), max)
}

// Apply default payment terms to ALL existing expense lines + subcontractors
function applyDefaultPaymentTerms() {
  const val = form.default_expense_payment_terms || 'שוטף+30'
  const cats = ['manpower', 'equipment', 'insurance', 'consultants', 'financing', 'other']
  for (const cat of cats) {
    const lines = form['expense_lines_' + cat] || []
    for (const line of lines) {
      if (line.payment_terms !== 'פעימות תשלום') {
        line.payment_terms = val
      }
    }
  }
  for (const sub of form.subcontractors) {
    if (Array.isArray(sub.payment_terms)) {
      for (const term of sub.payment_terms) {
        term.type = val
      }
    }
  }
}

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
  form.subcontractors.push({
    name: '', total_amount: null,
    start_date: form.start_date || '', end_date: form.expected_end_date || '',
    payment_terms: [{ type: form.default_expense_payment_terms || 'שוטף+30', percent: 100 }],
    contract_filename: '',
    // Vendor details
    tax_id: '', vendor_type: '', contact_name: '', contact_role: '',
    phone: '', email: '', address: '',
    accounting_contact: '', accounting_phone: '', accounting_email: '',
    _showDetails: false,
  })
}

function addExpenseLine(cat) {
  form['expense_lines_' + cat].push({ name: '', monthly_amount: null, start_month: 1, end_month: 12 })
}

function addSupplierLine(cat) {
  const vendorFields = {
    tax_id: '', vendor_type: '', contact_name: '', contact_role: '',
    phone: '', email: '', address: '',
    accounting_contact: '', accounting_phone: '', accounting_email: '',
    _showDetails: false,
  }
  // Insurance: default to project end date with שוטף+0 (one-time payment at end)
  if (cat === 'insurance') {
    form['expense_lines_' + cat].push({
      name: '', monthly_amount: null,
      start_date: form.expected_end_date || '', end_date: form.expected_end_date || '',
      payment_terms: 'שוטף+0', ...vendorFields
    })
  } else {
    form['expense_lines_' + cat].push({
      name: '', monthly_amount: null,
      start_date: form.start_date || '', end_date: form.expected_end_date || '',
      payment_terms: form.default_expense_payment_terms || 'שוטף+30', ...vendorFields
    })
  }
}

async function pullAttendance() {
  attendanceError.value = 'פיצ׳ר נוכחות הוסר מהמערכת'
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
  // total_budget is now auto-calculated, no validation needed

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
  // Don't let total exceed 100%
  const othersTotal = form.revenue_payment_terms
    .filter((_, i) => i !== index)
    .reduce((a, t) => a + (Number(t.percent) || 0), 0)
  const max = Math.max(0, 100 - othersTotal)
  form.revenue_payment_terms[index].percent = Math.min(current, max)
}

// Term amount: derives ₪ from percentage
function termAmount(index) {
  const pct = Number(form.revenue_payment_terms[index].percent) || 0
  return form.total_revenue ? Math.round(form.total_revenue * pct / 100) : 0
}

// On typing in the ₪ field: format with commas + sync percentage live
function onTermAmountInput(index, event) {
  const el = event.target
  const raw = parseNum(el.value)
  // Format with commas and preserve cursor
  const pos = el.selectionStart
  const oldLen = el.value.length
  el.value = raw ? raw.toLocaleString('he-IL') : ''
  const newLen = el.value.length
  el.setSelectionRange(pos + newLen - oldLen, pos + newLen - oldLen)
  // Sync percentage
  if (!form.total_revenue || form.total_revenue <= 0) return
  const percent = (raw / form.total_revenue) * 100
  const othersTotal = form.revenue_payment_terms
    .filter((_, i) => i !== index)
    .reduce((a, t) => a + (Number(t.percent) || 0), 0)
  const max = Math.max(0, 100 - othersTotal)
  form.revenue_payment_terms[index].percent = Math.min(Math.max(0, percent), max)
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

// Expense line milestone helpers
function lineMilestonesTotal(line) {
  if (!line.milestones) return 0
  return line.milestones.reduce((sum, m) => sum + (Number(m.percent) || 0), 0)
}

function syncLineMilestoneFromPercent(line, i) {
  const ms = line.milestones[i]
  let pct = Number(ms.percent) || 0
  if (pct < 0) pct = 0
  if (pct > 100) pct = 100
  ms.percent = pct
  ms.amount = line.monthly_amount ? Math.round(line.monthly_amount * pct / 100) : 0
}

function syncLineMilestoneFromAmount(line, i) {
  const ms = line.milestones[i]
  let amt = Number(ms.amount) || 0
  if (amt < 0) amt = 0
  ms.amount = amt
  ms.percent = line.monthly_amount ? Math.round((amt / line.monthly_amount) * 1000) / 10 : 0
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
    toast.success(props.newProject ? 'הפרויקט נוצר בהצלחה' : 'הפרויקט נשמר')
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
    initRevenueAmounts()
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
    initRevenueAmounts()
    // Capture snapshot for dirty checking
    originalFormSnapshot.value = JSON.stringify(form)
  }
})
</script>

<style scoped>
.accordion-body {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 220ms var(--ease-out);
}
.accordion-body > div {
  overflow: hidden;
}
.accordion-body[style*="display: none"] {
  grid-template-rows: 0fr;
}
.accordion-body:not([style*="display: none"]) {
  grid-template-rows: 1fr;
}

/* Step marker for wizard stepper */
.ed-marker-step {
  display: inline-flex;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.5rem 0.25rem;
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--rule);
  cursor: pointer;
  font-family: var(--font-display);
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--ink-muted);
  transition: color 180ms var(--ease-out), border-color 180ms var(--ease-out);
  white-space: nowrap;
}
.ed-marker-step:hover { color: var(--ink); border-bottom-color: var(--ink-muted); }
.ed-marker-step.is-active {
  color: var(--ink);
  font-weight: 900;
  border-bottom: 2px solid var(--ink);
  padding-bottom: calc(0.5rem - 1px);
}
.ed-marker-step__num {
  font-family: var(--font-sans);
  font-size: 0.625rem;
  letter-spacing: 0.12em;
  color: var(--ink-faint);
}
.ed-marker-step.is-active .ed-marker-step__num { color: var(--accent); }

/* Scoped overrides so ed-* utilities work inside the modal */
:deep(.ed-input-compat) {
  display: block;
  width: 100%;
  font-family: var(--font-sans);
  font-size: 0.95rem;
  color: var(--ink);
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--rule-strong);
  padding: 0.6rem 0;
  outline: none;
  transition: border-color 0.2s ease;
  font-feature-settings: "lnum" 1, "tnum" 1;
}
:deep(.ed-input-compat::placeholder) { color: var(--ink-faint); }
:deep(.ed-input-compat:focus) {
  border-bottom: 2px solid var(--accent);
  padding-bottom: calc(0.6rem - 1px);
}
</style>
