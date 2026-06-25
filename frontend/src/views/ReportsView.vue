<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import PageLayout from '../components/PageLayout.vue'

const route = useRoute()
const store = useAuditStore()
const reportType = ref('full')
const mode = ref('current')
const reportHtml = ref(null)
const error = ref(null)
const auditFinished = ref(false)
const loading = ref(true)

const selectClass =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'

onMounted(async () => {
  try {
    const audit = await api.getAudit(route.params.auditId)
    auditFinished.value = audit.status === 'FINISHED'
    if (!store.company?.id) {
      const company = await api.getCompany(audit.company_id)
      store.setCompany(company)
    }
    if (!store.module) {
      store.setModule(audit.module)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function loadReport() {
  if (!auditFinished.value) {
    error.value = 'Relatorio disponivel apenas apos finalizacao da auditoria.'
    return
  }
  error.value = null
  reportHtml.value = null
  try {
    const companyId = store.company?.id
    const url = api.getReportUrl(
      route.params.auditId,
      reportType.value,
      mode.value,
      companyId,
    )
    const res = await fetch(url, { credentials: 'include' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Erro ao gerar relatorio')
    }
    reportHtml.value = await res.text()
  } catch (e) {
    error.value = e.message
  }
}

function openPrint() {
  const w = window.open('', '_blank')
  w.document.write(reportHtml.value)
  w.document.close()
  w.print()
}
</script>

<template>
  <PageLayout title="Relatorios" subtitle="Disponivel apos finalizacao da auditoria">
    <p v-if="loading" class="text-center text-slate-500">Carregando...</p>

    <div
      v-else-if="!auditFinished"
      class="rounded-xl border border-amber-200 bg-amber-50 p-6 text-center text-amber-900"
    >
      <p class="font-medium">Auditoria ainda nao finalizada</p>
      <p class="mt-2 text-sm">Finalize o diagnostico para gerar relatorios.</p>
      <router-link
        :to="`/auditoria/${route.params.auditId}`"
        class="mt-4 inline-block text-sm font-medium text-blue-600 hover:text-blue-800"
      >
        Voltar a auditoria
      </router-link>
    </div>

    <template v-else>
      <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block text-sm font-medium text-slate-700">
            Tipo
            <select v-model="reportType" :class="selectClass">
              <option value="full">Completo</option>
              <option value="by_category">Por tipos de controle</option>
            </select>
          </label>
          <label class="block text-sm font-medium text-slate-700">
            Modo
            <select v-model="mode" :class="selectClass">
              <option value="current">Atual</option>
              <option value="comparative">Comparativo</option>
            </select>
          </label>
        </div>
        <div class="mt-6 flex flex-wrap justify-center gap-3">
          <button
            type="button"
            class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
            @click="loadReport"
          >
            Gerar relatorio
          </button>
          <button
            v-if="reportHtml"
            type="button"
            class="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            @click="openPrint"
          >
            Imprimir
          </button>
        </div>
      </div>

      <p v-if="error" class="mt-4 rounded-lg bg-red-50 px-4 py-3 text-center text-red-700">{{ error }}</p>
      <iframe
        v-if="reportHtml"
        :srcdoc="reportHtml"
        class="mt-6 h-[600px] w-full rounded-xl border border-slate-200 bg-white shadow-sm"
      />
    </template>

    <p class="mt-8 text-center">
      <router-link
        :to="`/dashboard/${route.params.auditId}`"
        class="text-sm font-medium text-blue-600 hover:text-blue-800"
      >
        Voltar ao dashboard
      </router-link>
    </p>
  </PageLayout>
</template>
