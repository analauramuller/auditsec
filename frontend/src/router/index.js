import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CompanyView from '../views/CompanyView.vue'
import CompaniesView from '../views/CompaniesView.vue'
import CompanyDetailView from '../views/CompanyDetailView.vue'
import ReportsCatalogView from '../views/ReportsCatalogView.vue'
import AuditWizardView from '../views/AuditWizardView.vue'
import DashboardView from '../views/DashboardView.vue'
import CompareView from '../views/CompareView.vue'
import ReportsView from '../views/ReportsView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/empresas', name: 'companies', component: CompaniesView },
  { path: '/empresas/:companyId', name: 'company-detail', component: CompanyDetailView },
  { path: '/relatorios', name: 'reports-catalog', component: ReportsCatalogView },
  { path: '/empresa', name: 'company', component: CompanyView },
  { path: '/auditoria', name: 'audit', component: AuditWizardView },
  { path: '/dashboard/:auditId', name: 'dashboard', component: DashboardView },
  { path: '/comparativo/:companyId', name: 'compare', component: CompareView },
  { path: '/relatorios/:auditId', name: 'reports', component: ReportsView },
]

export default createRouter({ history: createWebHistory(), routes })
