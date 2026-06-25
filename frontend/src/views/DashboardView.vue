<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import ChartCard from '../components/ChartCard.vue'
import PageLayout from '../components/PageLayout.vue'
import { formatAuditDate } from '../utils/format'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const barChartOptions = {
  maintainAspectRatio: true,
  plugins: {
    tooltip: {
      callbacks: {
        label(context) {
          return `${Math.round(context.parsed.y)}%`
        },
      },
    },
  },
}

const route = useRoute()
const router = useRouter()
const store = useAuditStore()
const dashboard = ref(null)
const error = ref(null)
const barData = ref(null)

const btnPrimary =
  'rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700'
const btnSecondary =
  'rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50'

onMounted(async () => {
  try {
    if (!store.company?.id) {
      const audit = await api.getAudit(route.params.auditId)
      store.setModule(audit.module)
      const company = await api.getCompany(audit.company_id)
      store.setCompany(company)
    }
    dashboard.value = await api.getDashboard(route.params.auditId)
    barData.value = {
      labels: dashboard.value.by_category.map((c) => c.label),
      datasets: [{
        label: '% Conformidade',
        data: dashboard.value.by_category.map((c) => c.percent_conformidade),
        backgroundColor: '#2563eb',
      }],
    }
  } catch (e) {
    error.value = e.message
  }
})

function goCompare() {
  if (store.company?.id) {
    router.push({ path: `/comparativo/${store.company.id}`, query: { module: store.module } })
  }
}

function goReports() {
  router.push(`/relatorios/${route.params.auditId}`)
}
</script>

<template>
  <PageLayout
    v-if="dashboard"
    title="Dashboard de Conformidade"
    :subtitle="store.company?.name"
    wide
  >
    <div class="mb-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-center text-sm text-slate-700">
      <strong>Auditoria demonstrada:</strong> {{ formatAuditDate(dashboard.audit_date) }}
    </div>

    <div class="mb-6 rounded-xl border border-blue-200 bg-blue-50 p-6 text-center shadow-sm">
      <p class="text-sm font-medium uppercase tracking-wide text-blue-800">Conformidade geral</p>
      <p class="mt-1 text-4xl font-bold text-blue-900">{{ dashboard.percent_total }}%</p>
      <div class="mt-4 flex flex-wrap justify-center gap-4 text-sm text-slate-700">
        <span><strong class="text-green-700">{{ dashboard.conforme }}</strong> conformes</span>
        <span><strong class="text-red-700">{{ dashboard.nao_conforme }}</strong> NC</span>
        <span><strong class="text-amber-700">{{ dashboard.em_andamento }}</strong> andamento</span>
        <span><strong class="text-slate-500">{{ dashboard.nao_aplica }}</strong> N/A</span>
      </div>
    </div>

    <div class="mb-6 grid gap-4 sm:grid-cols-2">
      <ChartCard
        title="Visao geral"
        :conforme="dashboard.conforme"
        :nao-conforme="dashboard.nao_conforme"
        :em-andamento="dashboard.em_andamento"
        :nao-aplica="dashboard.nao_aplica"
        :percent="dashboard.percent_total"
      />
      <ChartCard
        v-for="cat in dashboard.by_category"
        :key="cat.category"
        :title="cat.label"
        :conforme="cat.conforme"
        :nao-conforme="cat.nao_conforme"
        :em-andamento="cat.em_andamento"
        :nao-aplica="cat.nao_aplica"
        :percent="cat.percent_conformidade"
      />
    </div>

    <article v-if="barData" class="mb-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="mb-4 text-center text-sm font-semibold text-slate-800">Conformidade por categoria</h3>
      <div class="mx-auto max-h-64 w-full">
        <Bar :data="barData" :options="barChartOptions" />
      </div>
    </article>

    <div class="flex flex-wrap justify-center gap-3">
      <button type="button" :class="btnPrimary" @click="goCompare">Ver comparativo</button>
      <button type="button" :class="btnSecondary" @click="goReports">Gerar relatorio</button>
    </div>

    <p class="mt-8 text-center text-sm">
      <router-link to="/" class="font-medium text-blue-600 hover:text-blue-800">Nova auditoria</router-link>
      <span v-if="store.company" class="text-slate-400"> · </span>
      <router-link
        v-if="store.company"
        :to="`/empresas/${store.company.id}`"
        class="font-medium text-blue-600 hover:text-blue-800"
      >
        Voltar a empresa
      </router-link>
    </p>
  </PageLayout>
  <p v-if="error" class="mx-auto max-w-3xl rounded-lg bg-red-50 px-4 py-3 text-center text-red-700">{{ error }}</p>
</template>
