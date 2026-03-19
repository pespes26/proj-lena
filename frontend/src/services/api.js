import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.response.use(
  res => res,
  err => {
    const msg = err.response?.data?.detail || 'שגיאה בתקשורת עם השרת'
    return Promise.reject(new Error(msg))
  }
)

export const getProjects = () => api.get('/projects').then(r => r.data.projects)
export const getPnl = (project) => api.get('/pnl', { params: { project } }).then(r => r.data.data)
export const getPnlSummary = () => api.get('/pnl/summary').then(r => r.data.data)
export const getCashflow = () => api.get('/cashflow').then(r => r.data.data)
export const getDashboard = () => api.get('/dashboard').then(r => r.data.data)
export const getProjectCashflow = (project) => api.get('/project-cashflow', { params: { project } }).then(r => r.data.data)
export const getDataStatus = () => api.get('/data/status').then(r => r.data)
export const uploadData = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/data/upload', form, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 30000 }).then(r => r.data)
}
export const getBackups = () => api.get('/data/backups').then(r => r.data.backups)
export const getReports = (project) => api.get('/reports', { params: { project } }).then(r => r.data.reports)
export const createReport = (data) => api.post('/reports', data).then(r => r.data)
export const getProjectForm = (project) => api.get(`/project-form/${encodeURIComponent(project)}`).then(r => r.data.data)
export const saveProjectForm = (project, data) => api.post(`/project-form/${encodeURIComponent(project)}`, data).then(r => r.data)
export const getAttendance = () => api.get('/attendance').then(r => r.data.data)
export const uploadAttendance = (file, hourlyRate) => {
  const f = new FormData(); f.append('file', file)
  return api.post(`/attendance/upload?hourly_rate=${hourlyRate}`, f, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 30000 }).then(r => r.data)
}
export const getAttendanceByProject = (project) => api.get('/attendance/by-project', { params: { project } }).then(r => r.data)

export const formatNumber = (val) => {
  if (val == null) return '-'
  return Number(val).toLocaleString('he-IL', { maximumFractionDigits: 0 })
}

export const formatPercent = (val) => {
  if (val == null) return '-'
  return val.toFixed(1) + '%'
}
