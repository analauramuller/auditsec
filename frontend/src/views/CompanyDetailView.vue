<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import PageLayout from '../components/PageLayout.vue'

const route = useRoute()
const router = useRouter()
const store = useAuditStore()
const company = ref(null)
const audits = ref([])
const modules = ref([])
const error = ref(null)
const newModule = ref('ISO27001')
const newAuditDate = ref(new Date().toISOString().slice(0, 10))
const starting = ref(false)

const statusLabel = {
  FINISHED: 'Finalizada',
  IN_PROGRESS: 'Em andamento',
  DRAFT: 'Rascunho',
}

function statusBadgeClass(status) {
  if (status === 'FINISHED') return 'bg-green-100 text-green-800'
  if (status === 'IN_PROGRESS') return 'bg-amber-100 text-amber-800'
  return 'bg-slate-100 text-slate-700'
}

const btnPrimary =
  'rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700'
const btnSecondary =
  'rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50'

const selectClass =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'

onMounted(async () => {
  const id = Number(route.params.companyId)
  try {
    company.value = await api.getCompany(id)
    audits.value = await api.listCompanyAudits(id)
    modules.value = await api.getModules()
  } catch (e) {
    error.value = e.message
  }
})

function openDashboard(auditId) {
  router.push(`/dashboard/${auditId}`)
}

function openReports(auditId) {
  store.setCompany(company.value)
  router.push(`/relatorios/${auditId}`)
}

function openCompare(module) {
  router.push({ path: `/comparativo/${company.value.id}`, query: { module } })
}

async function resumeAudit(audit) {
  try {
    store.setCompany(company.value)
    store.setModule(audit.module)
    store.setAudit(audit)
    store.setControls(await api.getControls(audit.module))
    router.push('/auditoria')
  } catch (e) {
    error.value = e.message
  }
}

async function startNewAudit() {
  starting.value = true
  error.value = null
  try {
    const inProgress = audits.value.find(
      (a) => a.module === newModule.value && a.status === 'IN_PROGRESS',
    )
    if (inProgress) {
      error.value = 'Ja existe auditoria em andamento neste modulo. Continue-a ou finalize antes de iniciar outra.'
      return
    }
    const audit = await api.startAuditForCompany(company.value.id, {
      module: newModule.value,
      audit_date: newAuditDate.value,
    })
    store.setCompany(company.value)
    store.setModule(newModule.value)
    store.setAudit(audit)
    store.setControls(await api.getControls(newModule.value))
    router.push('/auditoria')
  } catch (e) {
    error.value = e.message
  } finally {
    starting.value = false
  }
}

const finishedModules = () => [...new Set(audits.value.filter((a) => a.status === 'FINISHED').map((a) => a.module))]
</script>

<template>
  <PageLayout v-if="company" :title="company.name" :subtitle="company.cnpj ? `CNPJ: ${company.cnpj}` : ''" wide>
    <p v-if="error" class="mb-4 rounded-lg bg-red-50 px-4 py-3 text-center text-red-700">{{ error }}</p>

    <article class="mb-8 rounded-xl border border-blue-200 bg-blue-50 p-6 shadow-sm">
      <h2 class="text-lg font-semibold text-blue-900">Nova auditoria (empresa cadastrada)</h2>
      <p class="mt-1 text-sm text-blue-800">
        Gere um novo diagnostico para comparar com as ultimas 3 auditorias finalizadas do mesmo modulo.
      </p>
      <div class="mt-4 grid gap-4 sm:grid-cols-2">
        <label class="block text-sm font-medium text-slate-700">
          Modulo
          <select v-model="newModule" :class="selectClass">
            <option v-for="mod in modules" :key="mod.id" :value="mod.id">{{ mod.name }}</option>
          </select>
        </label>
        <label class="block text-sm font-medium text-slate-700">
          Data da auditoria
          <input v-model="newAuditDate" type="date" :class="selectClass" />
        </label>
      </div>
      <button
        type="button"
        class="mt-4 w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50 sm:w-auto"
        :disabled="starting"
        @click="startNewAudit"
      >
        {{ starting ? 'Iniciando...' : 'Iniciar nova auditoria' }}
      </button>
    </article>

    <h2 class="mb-4 text-center text-lg font-semibold text-slate-800">Historico de auditorias</h2>
    <p v-if="!audits.length" class="text-center text-slate-500">Nenhuma auditoria para esta empresa.</p>

    <div class="space-y-4">
      <article
        v-for="audit in audits"
        :key="audit.id"
        class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h3 class="font-semibold text-blue-700">{{ audit.module }}</h3>
          <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="statusBadgeClass(audit.status)">
            {{ statusLabel[audit.status] || audit.status }}
          </span>
        </div>
        <p class="mt-2 text-sm text-slate-600">Data: {{ audit.audit_date }}</p>
        <div class="mt-4 flex flex-wrap justify-center gap-2">
          <button v-if="audit.status === 'FINISHED'" type="button" :class="btnPrimary" @click="openDashboard(audit.id)">
            Dashboard
          </button>
          <button v-if="audit.status === 'FINISHED'" type="button" :class="btnSecondary" @click="openReports(audit.id)">
            Relatorio
          </button>
          <button v-if="audit.status === 'IN_PROGRESS'" type="button" :class="btnPrimary" @click="resumeAudit(audit)">
            Continuar
          </button>
        </div>
      </article>
    </div>

    <div class="mt-8 flex flex-col items-center gap-3">
      <template v-for="mod in finishedModules()" :key="mod">
        <button type="button" :class="btnSecondary" @click="openCompare(mod)">
          Comparativo — {{ mod }} (ultimas 3)
        </button>
      </template>
      <router-link to="/empresas" class="text-sm font-medium text-blue-600 hover:text-blue-800">
        Voltar para empresas
      </router-link>
    </div>
  </PageLayout>
</template>
