// ═══════════════════════════════════════════════════════════════════
// Shared Chart.js configuration — IFMLogiX Executive Cockpit
// Modern fintech SaaS palette: slate ink + emerald accent
// ═══════════════════════════════════════════════════════════════════

import { Chart as ChartJS } from 'chart.js'

// Unified font stack — DM Sans for Latin, Rubik for Hebrew
export const CHART_FONT = "'DM Sans', 'Rubik', -apple-system, BlinkMacSystemFont, system-ui, sans-serif"

// Slate + emerald tokens — mirrored from style.css
const INK = '#0f172a'          // slate-900
const INK_MUTED = '#475569'     // slate-600
const INK_FAINT = '#94a3b8'     // slate-400
const SURFACE = '#ffffff'
const SURFACE_MUTED = '#f1f5f9' // slate-100
const BORDER = '#e2e8f0'        // slate-200
const BORDER_STRONG = '#cbd5e1' // slate-300

// Dark tokenized tooltip — emerald-600 accent line, slate-900 body
export const tooltipConfig = {
  rtl: true,
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  titleColor: '#ffffff',
  bodyColor: '#ffffff',
  borderColor: '#334155',
  borderWidth: 1,
  cornerRadius: 10,
  padding: 10,
  boxPadding: 6,
  usePointStyle: true,
  titleFont: { family: CHART_FONT, size: 12, weight: '600' },
  bodyFont: { family: CHART_FONT, size: 12, weight: '500' },
  displayColors: true,
}

export const axisConfig = {
  x: {
    grid: { display: false, drawBorder: false },
    ticks: {
      font: { family: CHART_FONT, size: 11, weight: '500' },
      color: INK_MUTED,
    },
    border: { display: false },
  },
  y: {
    grid: {
      color: BORDER,
      drawBorder: false,
      drawTicks: false,
    },
    ticks: {
      font: { family: CHART_FONT, size: 11, weight: '500' },
      color: INK_MUTED,
      padding: 10,
      callback: v => Number(v).toLocaleString('he-IL'),
    },
    border: { display: false },
  },
}

export const legendConfig = {
  position: 'top',
  align: 'start',
  rtl: true,
  labels: {
    font: { family: CHART_FONT, size: 12, weight: '500' },
    usePointStyle: true,
    pointStyle: 'rectRounded',
    padding: 18,
    color: INK_MUTED,
    boxWidth: 10,
    boxHeight: 10,
  },
}

// Chart palette — slate primary, emerald positive, rose negative
export const COLORS = {
  primary: '#0f172a',            // slate-900 — neutral bars/lines
  primaryLight: 'rgba(15, 23, 42, 0.12)',
  primaryFill: 'rgba(15, 23, 42, 0.06)',

  accent: '#059669',             // emerald-600
  accentLight: 'rgba(5, 150, 105, 0.14)',
  accentFill: 'rgba(5, 150, 105, 0.08)',

  amber: '#d97706',              // amber-600
  amberLight: 'rgba(217, 119, 6, 0.14)',

  orange: '#ea580c',             // orange-600
  orangeLight: 'rgba(234, 88, 12, 0.14)',

  green: '#059669',              // emerald-600 (alias)
  greenLight: 'rgba(5, 150, 105, 0.14)',
  greenFill: 'rgba(5, 150, 105, 0.08)',

  red: '#e11d48',                // rose-600
  redLight: 'rgba(225, 29, 72, 0.14)',
  redFill: 'rgba(225, 29, 72, 0.08)',

  blue: '#2563eb',               // blue-600
  blueLight: 'rgba(37, 99, 235, 0.14)',

  purple: '#7c3aed',             // violet-600
  indigo: '#4f46e5',             // indigo-600
  lime: '#84cc16',               // lime-500
  cyan: '#0891b2',               // cyan-600

  // Editorial tokens (kept for backward compat with any chart referencing them)
  ink: INK,
  inkMuted: INK_MUTED,
  inkFaint: INK_FAINT,
  paperLight: SURFACE,
  rule: BORDER,
  ruleStrong: BORDER_STRONG,
}

// Called once from main.js — sets Chart.js global defaults
export function applyEditorialDefaults() {
  ChartJS.defaults.font.family = CHART_FONT
  ChartJS.defaults.font.size = 12
  ChartJS.defaults.font.weight = '500'
  ChartJS.defaults.color = INK_MUTED
  ChartJS.defaults.borderColor = BORDER
  ChartJS.defaults.animation.duration = 700
  ChartJS.defaults.animation.easing = 'easeOutCubic'
  // Smoother data-update transitions
  if (ChartJS.defaults.transitions) {
    ChartJS.defaults.transitions.active = { animation: { duration: 300 } }
  }
  if (ChartJS.defaults.elements && ChartJS.defaults.elements.bar) {
    ChartJS.defaults.elements.bar.borderRadius = 6
    ChartJS.defaults.elements.bar.borderSkipped = false
  }
  if (ChartJS.defaults.elements && ChartJS.defaults.elements.line) {
    ChartJS.defaults.elements.line.tension = 0.3
    ChartJS.defaults.elements.line.borderWidth = 2.5
  }
  if (ChartJS.defaults.elements && ChartJS.defaults.elements.point) {
    ChartJS.defaults.elements.point.radius = 0
    ChartJS.defaults.elements.point.hoverRadius = 5
    ChartJS.defaults.elements.point.hitRadius = 10
  }
}

// Alias for future-proofing
export const applyDashboardDefaults = applyEditorialDefaults

// Helper: tooltip label callback with he-IL formatting
export function hebrewLabelCallback(prefix) {
  return ctx => ` ${prefix || ctx.dataset.label}: ${Number(ctx.raw).toLocaleString('he-IL')}`
}

// Helper: absolute value label callback (for negative expense bars)
export function absLabelCallback() {
  return ctx => `${ctx.dataset.label}: ${Math.abs(Number(ctx.raw)).toLocaleString('he-IL')}`
}
