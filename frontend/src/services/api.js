const BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '')

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      credentials: 'include',
      ...options,
    })
  } catch {
    throw new Error(
      'Nao foi possivel conectar a API. Verifique se os containers estao rodando (docker compose up) ou se o backend esta em http://localhost:8000.',
    )
  }
  if (!res.ok) {
    if (res.status === 401) throw new Error('Nao autenticado')
    const err = await res.json().catch(() => ({}))
    const detail = err.detail
    let message = 'Erro na requisicao'
    if (typeof detail === 'string') message = detail
    else if (Array.isArray(detail) && detail[0]?.msg) message = detail[0].msg
    throw new Error(message)
  }
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('text/html')) return res.text()
  return res.json()
}

export const api = {
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  me: () => request('/auth/me'),
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  getModules: () => request('/modules'),
  getControls: (module) => request(`/controls?module=${module}`),
  listCompanies: () => request('/companies'),
  checkCompanyDuplicate: (name, cnpj) => {
    const params = new URLSearchParams({ name })
    if (cnpj) params.set('cnpj', cnpj)
    return request(`/companies/check-duplicate?${params}`)
  },
  getCompany: (id) => request(`/companies/${id}`),
  startAuditForCompany: (companyId, data) =>
    request(`/companies/${companyId}/audits`, { method: 'POST', body: JSON.stringify(data) }),
  listCompanyAudits: (companyId, module) => {
    const q = module ? `?module=${module}` : ''
    return request(`/companies/${companyId}/audits${q}`)
  },
  listReportsCatalog: () => request('/audits/reports/catalog'),
  getAuditResponses: (auditId) => request(`/audits/${auditId}/responses`),
  createCompany: (data) => request('/companies', { method: 'POST', body: JSON.stringify(data) }),
  getAudit: (id) => request(`/audits/${id}`),
  createAudit: (data) => request('/audits', { method: 'POST', body: JSON.stringify(data) }),
  registerResponse: (auditId, data) =>
    request(`/audits/${auditId}/responses`, { method: 'PATCH', body: JSON.stringify(data) }),
  finishAudit: (auditId) => request(`/audits/${auditId}/finish`, { method: 'POST' }),
  getDashboard: (auditId) => request(`/audits/${auditId}/dashboard`),
  getComparison: (companyId, module) =>
    request(`/audits/company/${companyId}/comparison?module=${module}`),
  getReportUrl: (auditId, type, mode, companyId) => {
    const params = new URLSearchParams({ type, mode })
    if (companyId) params.set('company_id', companyId)
    return `${BASE}/audits/${auditId}/reports?${params}`
  },
}
