import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Attach JWT token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle errors + auto-logout on 401
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401 && localStorage.getItem('token')) {
      // Token expired — clear and reload to show login
      localStorage.removeItem('token')
      window.location.reload()
      return new Promise(() => {}) // prevent further handling
    }
    const msg = err.response?.data?.detail || 'שגיאה בתקשורת עם השרת'
    return Promise.reject(new Error(msg))
  }
)

export const login = (username, password) =>
  api.post('/auth/login', { username, password }).then(r => r.data)

export const getProjects = () => api.get('/projects').then(r => r.data.projects)
export const getProjectsDetail = () => api.get('/projects').then(r => r.data.projects_detail)
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
export const saveProjectActuals = (project, data) => api.post(`/project-form/${encodeURIComponent(project)}/actuals`, data).then(r => r.data)
export const importExcelProject = (project) => api.post(`/import-excel-project/${encodeURIComponent(project)}`).then(r => r.data)
export const uploadSubcontractorContract = (project, subIndex, file) => {
  const f = new FormData(); f.append('file', file)
  return api.post(`/project-form/${encodeURIComponent(project)}/upload-contract?sub_index=${subIndex}`, f, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
}

// Auth & Users
export const getProfile = () => api.get('/auth/profile').then(r => r.data)
export const updateProfile = (data) => api.put('/auth/profile', data).then(r => r.data)
export const changePassword = (data) => api.put('/auth/password', data).then(r => r.data)
export const getUsers = () => api.get('/auth/users').then(r => r.data.users)
export const createUser = (data) => api.post('/auth/users', data).then(r => r.data)
export const deleteUser = (username) => api.delete(`/auth/users/${encodeURIComponent(username)}`).then(r => r.data)

export const formatNumber = (val) => {
  if (val == null) return '-'
  return Number(val).toLocaleString('he-IL', { maximumFractionDigits: 0 })
}

export const formatPercent = (val) => {
  if (val == null) return '-'
  return val.toFixed(1) + '%'
}
