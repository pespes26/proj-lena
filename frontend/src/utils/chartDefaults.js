// Shared chart configuration — Midnight Green + Warm palette

const fontFamily = "'Heebo', system-ui, sans-serif"

export const tooltipConfig = {
  rtl: true,
  backgroundColor: 'rgba(255,255,255,0.97)',
  titleColor: '#1B1B1B',
  bodyColor: '#4B5563',
  borderColor: 'rgba(6,95,70,0.12)',
  borderWidth: 1,
  cornerRadius: 10,
  padding: 12,
  boxPadding: 4,
  usePointStyle: true,
  titleFont: { family: fontFamily, size: 13, weight: '600' },
  bodyFont: { family: fontFamily, size: 12 },
}

export const axisConfig = {
  x: {
    grid: { display: false },
    ticks: { font: { family: fontFamily, size: 11 }, color: '#9CA3AF' },
    border: { display: false },
  },
  y: {
    grid: { color: 'rgba(6,95,70,0.05)', drawBorder: false },
    ticks: {
      font: { family: fontFamily, size: 11 },
      color: '#9CA3AF',
      callback: v => v.toLocaleString('he-IL'),
    },
    border: { display: false },
  },
}

export const legendConfig = {
  position: 'top',
  rtl: true,
  labels: {
    font: { family: fontFamily, size: 12 },
    usePointStyle: true,
    pointStyle: 'circle',
    padding: 20,
    color: '#4B5563',
  },
}

export const COLORS = {
  primary: '#065F46',
  primaryLight: 'rgba(6,95,70,0.12)',
  primaryFill: 'rgba(6,95,70,0.06)',
  amber: '#D97706',
  amberLight: 'rgba(217,119,6,0.12)',
  orange: '#EA580C',
  orangeLight: 'rgba(234,88,12,0.12)',
  green: '#16A34A',
  greenLight: 'rgba(22,163,74,0.10)',
  greenFill: 'rgba(22,163,74,0.06)',
  red: '#DC2626',
  redLight: 'rgba(220,38,38,0.12)',
  purple: '#7C3AED',
  indigo: '#4F46E5',
  lime: '#84CC16',
  cyan: '#0891B2',
}

// Helper to create a tooltip label callback with he-IL formatting
export function hebrewLabelCallback(prefix) {
  return ctx => ` ${prefix || ctx.dataset.label}: ${Number(ctx.raw).toLocaleString('he-IL')}`
}

// Helper to create absolute value label callback (for negative expense bars)
export function absLabelCallback() {
  return ctx => `${ctx.dataset.label}: ${Math.abs(Number(ctx.raw)).toLocaleString('he-IL')}`
}
