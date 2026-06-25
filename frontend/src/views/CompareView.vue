<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import ChartCard from '../components/ChartCard.vue'
import PageLayout from '../components/PageLayout.vue'
import { formatAuditDate } from '../utils/format'

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend)

const route = useRoute()
const store = useAuditStore()
const comparison = ref(null)
const chartData = ref(null)
const categoryChartData = ref(null)
const error = ref(null)
const selectedModule = ref(route.query.module || store.module || 'ISO27001')

const selectClass =
  'rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'

const categoryLabels = computed(() => {
  const first = comparison.value?.audits?.[0]
  return first?.by_category?.map((c) => c.label) ?? []
})

const comparisonDatesDisplay = computed(() =>
  comparison.value?.audits?.map((a) => formatAuditDate(a.audit_date)).join(', ') ?? '',
)

function formatDelta(delta) {
  if (delta === null || delta === undefined) return '—'
  const sign = delta > 0 ? '+' : ''
  return `${sign}${delta}%`
}

function deltaClass(delta) {
  if (delta === null || delta === undefined) return 'text-slate-400'
  if (delta > 0) return 'text-green-600'
  if (delta < 0) return 'text-red-600'
  return 'text-slate-500'
}

const CATEGORY_COLORS = ['#2563eb', '#16a34a', '#d97706', '#9333ea', '#0891b2', '#dc2626']

async function loadComparison() {
  error.value = null
  try {
    comparison.value = await api.getComparison(route.params.companyId, selectedModule.value)
    const audits = comparison.value.audits
    chartData.value = {
      labels: audits.map((a) => formatAuditDate(a.audit_date)),
      datasets: [{
        label: 'Evolucao % conformidade geral',
        data: audits.map((a) => a.percent_conformidade),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.2,
        fill: true,
      }],
    }

    const labels = categoryLabels.value
    if (labels.length && audits.length > 1) {
      categoryChartData.value = {
        labels: audits.map((a) => formatAuditDate(a.audit_date)),
        datasets: labels.map((label, i) => ({
          label,
          data: audits.map((a) => {
            const cat = a.by_category?.find((c) => c.label === label)
            return cat?.percent_conformidade ?? 0
          }),
          borderColor: CATEGORY_COLORS[i % CATEGORY_COLORS.length],
          tension: 0.2,
        })),
      }
    } else {
      categoryChartData.value = null
    }
  } catch (e) {
    error.value = e.message
    comparison.value = null
    chartData.value = null
    categoryChartData.value = null
  }
}

onMounted(loadComparison)
watch(selectedModule, loadComparison)
</script>

<template>
  <PageLayout title="Comparativo de auditorias" subtitle="Ultimas 3 auditorias finalizadas por modulo" wide>
    <div class="mb-6 flex justify-center">
      <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
        Modulo
        <select v-model="selectedModule" :class="selectClass">
          <option value="ISO27001">NBR ISO/IEC 27001</option>
          <option value="ISO27701">NBR ISO/IEC 27701</option>
        </select>
      </label>
    </div>

    <p v-if="error" class="mb-4 rounded-lg bg-red-50 px-4 py-3 text-center text-red-700">{{ error }}</p>

    <div
      v-if="comparisonDatesDisplay"
      class="mb-4 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-center text-sm text-blue-900"
    >
      <strong>Auditorias comparadas:</strong> {{ comparisonDatesDisplay }}
    </div>

    <div v-if="comparison?.audits?.length" class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table class="w-full text-left text-sm">
        <thead class="bg-slate-100 text-slate-700">
          <tr>
            <th class="px-4 py-3 font-semibold">Data</th>
            <th class="px-4 py-3 font-semibold text-right">% Conformidade</th>
            <th class="px-4 py-3 font-semibold text-right">Variacao</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="a in comparison.audits"
            :key="a.audit_id"
            class="border-t border-slate-100 hover:bg-slate-50"
          >
            <td class="px-4 py-3">{{ formatAuditDate(a.audit_date) }}</td>
            <td class="px-4 py-3 text-right font-medium text-blue-700">{{ a.percent_conformidade }}%</td>
            <td class="px-4 py-3 text-right font-medium" :class="deltaClass(a.delta_percent)">
              {{ formatDelta(a.delta_percent) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else-if="!error" class="text-center text-slate-500">
      Nenhuma auditoria finalizada neste modulo para comparar. Inicie uma nova auditoria na ficha da empresa.
    </p>

    <template v-if="comparison?.audits?.length">
      <h2 class="mb-4 mt-8 text-center text-base font-semibold text-slate-800">
        Graficos de conformidade (comparativo)
      </h2>
      <article
        v-for="audit in comparison.audits"
        :key="`pies-${audit.audit_id}`"
        class="mb-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      >
        <h3 class="mb-4 text-center text-sm font-semibold text-slate-800">
          {{ formatAuditDate(audit.audit_date) }} — {{ audit.percent_conformidade }}% de conformidade
        </h3>
        <div class="grid gap-4 sm:grid-cols-2">
          <ChartCard
            title="Visao geral"
            :conforme="audit.conforme"
            :nao-conforme="audit.nao_conforme"
            :em-andamento="audit.em_andamento"
            :nao-aplica="audit.nao_aplica"
            :percent="audit.percent_conformidade"
          />
          <ChartCard
            v-for="cat in audit.by_category"
            :key="`${audit.audit_id}-${cat.category}`"
            :title="cat.label"
            :conforme="cat.conforme"
            :nao-conforme="cat.nao_conforme"
            :em-andamento="cat.em_andamento"
            :nao-aplica="cat.nao_aplica"
            :percent="cat.percent_conformidade"
          />
        </div>
      </article>
    </template>

    <article v-if="chartData" class="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="mb-4 text-center text-sm font-semibold text-slate-800">Evolucao da conformidade geral</h3>
      <div class="mx-auto max-h-72 w-full">
        <Line :data="chartData" />
      </div>
    </article>

    <article v-if="categoryChartData" class="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="mb-4 text-center text-sm font-semibold text-slate-800">Evolucao por tipo de controle</h3>
      <div class="mx-auto max-h-80 w-full">
        <Line :data="categoryChartData" :options="{ plugins: { legend: { position: 'bottom' } } }" />
      </div>
    </article>

    <p class="mt-8 text-center">
      <router-link
        :to="`/empresas/${route.params.companyId}`"
        class="text-sm font-medium text-blue-600 hover:text-blue-800"
      >
        Voltar a empresa
      </router-link>
    </p>
  </PageLayout>
</template>
