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

export const getProjects = () => api.get('/projects').then(r => r.data.projects)
export const getProjectsDetail = () => api.get('/projects').then(r => r.data.projects_detail)
export const getPnl = (project) => api.get('/pnl', { params: { project } }).then(r => r.data.data)
export const getPnlSummary = () => api.get('/pnl/summary').then(r => r.data.data)
export const getCashflow = () => api.get('/cashflow').then(r => r.data.data)
export const getDashboard = () => api.get('/dashboard').then(r => r.data.data)
export const getProjectCashflow = (project) => api.get('/project-cashflow', { params: { project } }).then(r => r.data.data)
export const getReports = (project) => api.get('/reports', { params: { project } }).then(r => r.data.reports)
export const createReport = (data) => api.post('/reports', data).then(r => r.data)
export const getProjectForm = (project) => api.get(`/project-form/${encodeURIComponent(project)}`).then(r => r.data.data)
export const saveProjectForm = (project, data) => api.post(`/project-form/${encodeURIComponent(project)}`, data).then(r => r.data)
export const saveProjectActuals = (project, data) => api.post(`/project-form/${encodeURIComponent(project)}/actuals`, data).then(r => r.data)
export const importExcelProject = (project) => api.post(`/import-excel-project/${encodeURIComponent(project)}`).then(r => r.data)
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
