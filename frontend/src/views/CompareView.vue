<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import PageLayout from '../components/PageLayout.vue'

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend)

const route = useRoute()
const store = useAuditStore()
const comparison = ref(null)
const chartData = ref(null)
const error = ref(null)
const selectedModule = ref(route.query.module || store.module || 'ISO27001')

const selectClass =
  'rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'

async function loadComparison() {
  error.value = null
  try {
    comparison.value = await api.getComparison(route.params.companyId, selectedModule.value)
    chartData.value = {
      labels: comparison.value.audits.map((a) => a.audit_date),
      datasets: [{
        label: 'Evolucao % conformidade',
        data: comparison.value.audits.map((a) => a.percent_conformidade),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.2,
        fill: true,
      }],
    }
  } catch (e) {
    error.value = e.message
    comparison.value = null
    chartData.value = null
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

    <div v-if="comparison?.audits?.length" class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table class="w-full text-left text-sm">
        <thead class="bg-slate-100 text-slate-700">
          <tr>
            <th class="px-4 py-3 font-semibold">Data</th>
            <th class="px-4 py-3 font-semibold text-right">% Conformidade</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="a in comparison.audits"
            :key="a.audit_id"
            class="border-t border-slate-100 hover:bg-slate-50"
          >
            <td class="px-4 py-3">{{ a.audit_date }}</td>
            <td class="px-4 py-3 text-right font-medium text-blue-700">{{ a.percent_conformidade }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else-if="!error" class="text-center text-slate-500">
      Nenhuma auditoria finalizada neste modulo para comparar. Inicie uma nova auditoria na ficha da empresa.
    </p>

    <article v-if="chartData" class="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mx-auto max-h-72 w-full">
        <Line :data="chartData" />
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
