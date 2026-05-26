import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomeView from '../views/HomeView.vue'
import CompanyView from '../views/CompanyView.vue'
import CompaniesView from '../views/CompaniesView.vue'
import CompanyDetailView from '../views/CompanyDetailView.vue'
import ReportsCatalogView from '../views/ReportsCatalogView.vue'
import AuditWizardView from '../views/AuditWizardView.vue'
import DashboardView from '../views/DashboardView.vue'
import CompareView from '../views/CompareView.vue'
import ReportsView from '../views/ReportsView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/', name: 'home', component: HomeView, meta: { requiresAuth: true } },
  { path: '/empresas', name: 'companies', component: CompaniesView, meta: { requiresAuth: true } },
  { path: '/empresas/:companyId', name: 'company-detail', component: CompanyDetailView, meta: { requiresAuth: true } },
  { path: '/relatorios', name: 'reports-catalog', component: ReportsCatalogView, meta: { requiresAuth: true } },
  { path: '/empresa', name: 'company', component: CompanyView, meta: { requiresAuth: true } },
  { path: '/auditoria', name: 'audit', component: AuditWizardView, meta: { requiresAuth: true } },
  { path: '/dashboard/:auditId', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/comparativo/:companyId', name: 'compare', component: CompareView, meta: { requiresAuth: true } },
  { path: '/relatorios/:auditId', name: 'reports', component: ReportsView, meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.init()

  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) return { path: '/' }

  if (to.meta?.requiresAuth && !auth.isAuthenticated) {
    return { path: '/login', query: { next: to.fullPath } }
  }

  return true
})

export default router
