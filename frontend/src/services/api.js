import axios from 'axios'
import { auth } from '../firebase'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Attach Firebase ID token to every request
api.interceptors.request.use(async config => {
  const user = auth.currentUser
  if (user) {
    try {
      const token = await user.getIdToken()
      config.headers.Authorization = `Bearer ${token}`
    } catch {
      // Token refresh failed — will get 401
    }
  }
  return config
})

// Handle errors + auto-logout on 401
let ignoreNextUnauth = false
export function suppressNextUnauth() { ignoreNextUnauth = true; setTimeout(() => { ignoreNextUnauth = false }, 5000) }

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      // Don't auto-logout during initial load — let onAuthStateChanged handle it
      console.warn('401 from API:', err.config?.url)
    }
    const msg = err.response?.data?.detail || 'שגיאה בתקשורת עם השרת'
    return Promise.reject(new Error(msg))
  }
)

// Simple in-memory TTL cache for GET requests
const _cache = new Map()
const DEFAULT_TTL = 60_000 // 1 minute

function cachedGet(key, fetcher, ttl = DEFAULT_TTL) {
  const hit = _cache.get(key)
  if (hit && Date.now() - hit.ts < ttl) return Promise.resolve(hit.data)
  return fetcher().then(data => {
    _cache.set(key, { data, ts: Date.now() })
    return data
  })
}

export function invalidateCache(prefix) {
  if (!prefix) { _cache.clear(); return }
  for (const key of _cache.keys()) {
    if (key.startsWith(prefix)) _cache.delete(key)
  }
}

export const getProjects = () => cachedGet('projects', () => api.get('/projects').then(r => r.data.projects))
export const getProjectsDetail = () => cachedGet('projects_detail', () => api.get('/projects').then(r => r.data.projects_detail))
export const getPnl = (project) => cachedGet(`pnl:${project || ''}`, () => api.get('/pnl', { params: { project } }).then(r => r.data.data))
export const getPnlSummary = () => cachedGet('pnl_summary', () => api.get('/pnl/summary').then(r => r.data.data))
export const getCashflow = () => cachedGet('cashflow', () => api.get('/cashflow').then(r => r.data.data))
export const getDashboard = () => cachedGet('dashboard', () => api.get('/dashboard').then(r => r.data.data))
export const getProjectCashflow = (project) => cachedGet(`proj_cf:${project}`, () => api.get('/project-cashflow', { params: { project } }).then(r => r.data.data))
export const getReports = (project) => api.get('/reports', { params: { project } }).then(r => r.data.reports)
export const createReport = (data) => api.post('/reports', data).then(r => { invalidateCache(); return r.data })
export const getProjectForm = (project) => api.get(`/project-form/${encodeURIComponent(project)}`).then(r => r.data.data)
export const saveProjectForm = (project, data) => api.post(`/project-form/${encodeURIComponent(project)}`, data).then(r => { invalidateCache(); return r.data })
export const saveProjectActuals = (project, data) => api.post(`/project-form/${encodeURIComponent(project)}/actuals`, data).then(r => { invalidateCache(); return r.data })
export const importExcelProject = (project) => api.post(`/import-excel-project/${encodeURIComponent(project)}`).then(r => { invalidateCache(); return r.data })
export const uploadSubcontractorContract = (project, subIndex, file) => {
  const f = new FormData(); f.append('file', file)
  return api.post(`/project-form/${encodeURIComponent(project)}/upload-contract?sub_index=${subIndex}`, f, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
}

// Auth & Users (Firebase-based)
export const getProfile = () => api.get('/auth/profile').then(r => r.data)
export const updateProfile = (data) => api.put('/auth/profile', data).then(r => r.data)
export const getUsers = () => api.get('/auth/users').then(r => r.data.users)
export const createUser = (data) => api.post('/auth/users', data).then(r => r.data)
export const updateUser = (uid, data) => api.put(`/auth/users/${encodeURIComponent(uid)}`, data).then(r => r.data)
export const deleteUser = (uid) => api.delete(`/auth/users/${encodeURIComponent(uid)}`).then(r => r.data)
export const setupFirstAdmin = (data) => api.post('/auth/setup', data).then(r => r.data)

// AI Chat (streaming)
export async function sendAiChatStream(messages, message, onToken) {
  const user = auth.currentUser
  let token = ''
  if (user) token = await user.getIdToken()

  const response = await fetch('/api/ai/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ messages, message }),
  })

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let fullText = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const chunk = decoder.decode(value, { stream: true })
    const lines = chunk.split('\n')
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.token) {
            fullText += data.token
            onToken(fullText)
          }
        } catch {}
      }
    }
  }
  return fullText
}

// Financial Calculator
export const runWhatIf = (projectName, modifications) =>
  api.post('/ai/whatif', { project_name: projectName, modifications }).then(r => r.data)
export const getRiskScores = () => api.get('/ai/risk-scores').then(r => r.data.scores)
export const getRiskScore = (project) => api.get(`/ai/risk-score/${encodeURIComponent(project)}`).then(r => r.data)
export const getBudgetVsActual = (project) => api.get(`/ai/budget-vs-actual/${encodeURIComponent(project)}`).then(r => r.data)

export const formatNumber = (val) => {
  if (val == null) return '-'
  return Number(val).toLocaleString('he-IL', { maximumFractionDigits: 0 })
}

export const formatPercent = (val) => {
  if (val == null) return '-'
  return val.toFixed(1) + '%'
}
