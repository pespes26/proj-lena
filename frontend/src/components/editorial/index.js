// IFMLogiX UI primitives — Modern fintech SaaS dashboard
// Import via: import { HeroNumber, SectionHeader, ... } from './editorial'

export { default as HeroNumber } from './HeroNumber.vue'
export { default as SectionHeader } from './SectionHeader.vue'
export { default as RuledSection } from './RuledSection.vue'
export { default as DataTable } from './DataTable.vue'
export { default as PullQuote } from './PullQuote.vue'
export { default as SectionMarker } from './SectionMarker.vue'
export { default as Dateline } from './Dateline.vue'
export { default as FootnoteSource } from './FootnoteSource.vue'
export { default as EpigraphCaption } from './EpigraphCaption.vue'
export { default as SkeletonLoader } from './SkeletonLoader.vue'

// Utility: current Hebrew month label — "אפריל 2026"
const HEBREW_MONTHS = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']
export function currentHebrewDate() {
  const d = new Date()
  return `${HEBREW_MONTHS[d.getMonth()]} ${d.getFullYear()}`
}
// Legacy export — returns empty string; views no longer display issue numbers
export function currentIssueNumber() {
  return ''
}
