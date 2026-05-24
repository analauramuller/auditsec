<script setup>
import { ref } from 'vue'
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

const selectClass =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'

async function loadReport() {
  error.value = null
  reportHtml.value = null
  try {
    const url = api.getReportUrl(
      route.params.auditId,
      reportType.value,
      mode.value,
      store.company?.id,
    )
    const res = await fetch(url)
    if (!res.ok) throw new Error('Erro ao gerar relatorio')
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
