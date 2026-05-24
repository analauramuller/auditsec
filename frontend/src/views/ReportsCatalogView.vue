<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import PageLayout from '../components/PageLayout.vue'

const router = useRouter()
const store = useAuditStore()
const reports = ref([])
const error = ref(null)

const btnPrimary =
  'rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700'
const btnSecondary =
  'rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50'

onMounted(async () => {
  try {
    reports.value = await api.listReportsCatalog()
  } catch (e) {
    error.value = e.message
  }
})

function openReport(item) {
  store.setCompany({ id: item.company_id, name: item.company_name })
  store.setModule(item.module)
  router.push(`/relatorios/${item.audit_id}`)
}

function openDashboard(item) {
  router.push(`/dashboard/${item.audit_id}`)
}
</script>

<template>
  <PageLayout title="Relatorios cadastrados" subtitle="Auditorias finalizadas com relatorio disponivel">
    <p v-if="error" class="mb-4 rounded-lg bg-red-50 px-4 py-3 text-center text-red-700">{{ error }}</p>
    <p v-if="!reports.length && !error" class="text-center text-slate-500">Nenhum relatorio disponivel ainda.</p>

    <div class="space-y-4">
      <article
        v-for="item in reports"
        :key="item.audit_id"
        class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      >
        <h3 class="font-semibold text-slate-900">{{ item.company_name }}</h3>
        <p class="mt-1 text-sm text-slate-600">
          <span class="font-medium text-blue-700">{{ item.module }}</span> — {{ item.audit_date }}
        </p>
        <p v-if="item.finished_at" class="mt-1 text-xs text-slate-500">
          Finalizada: {{ new Date(item.finished_at).toLocaleString('pt-BR') }}
        </p>
        <div class="mt-4 flex flex-wrap justify-center gap-2">
          <button type="button" :class="btnPrimary" @click="openDashboard(item)">Dashboard</button>
          <button type="button" :class="btnSecondary" @click="openReport(item)">Gerar relatorio</button>
        </div>
      </article>
    </div>
  </PageLayout>
</template>
