<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import ControlRow from '../components/ControlRow.vue'
import PageLayout from '../components/PageLayout.vue'

const PAGE_SIZE = 5
const router = useRouter()
const store = useAuditStore()
const responses = ref({})
const error = ref(null)
const pageError = ref(null)
const missingIds = ref(new Set())
const finishing = ref(false)
const currentPage = ref(0)

const totalCount = computed(() => store.controls.length)
const totalPages = computed(() => Math.ceil(totalCount.value / PAGE_SIZE) || 1)
const answeredCount = computed(() => Object.keys(responses.value).length)
const progressPercent = computed(() =>
  totalCount.value ? Math.round((answeredCount.value / totalCount.value) * 100) : 0,
)

const pageControls = computed(() => {
  const start = currentPage.value * PAGE_SIZE
  return store.controls.slice(start, start + PAGE_SIZE)
})

function isAnswered(controlId) {
  return Boolean(responses.value[controlId])
}

onMounted(async () => {
  if (!store.audit) {
    router.replace('/')
    return
  }
  try {
    const existing = await api.getAuditResponses(store.audit.id)
    for (const r of existing) {
      responses.value[r.control_id] = r.status
    }
  } catch {
    /* nova */
  }
})

async function saveResponse(data) {
  try {
    const saved = await api.registerResponse(store.audit.id, data)
    responses.value[data.control_id] = saved.status
    missingIds.value.delete(data.control_id)
    pageError.value = null
  } catch (e) {
    error.value = e.message
  }
}

function validateCurrentPage() {
  const missing = pageControls.value.filter((c) => !isAnswered(c.id))
  if (!missing.length) {
    missingIds.value = new Set()
    pageError.value = null
    return true
  }
  missingIds.value = new Set(missing.map((c) => c.id))
  const codes = missing.map((c) => c.code).join(', ')
  pageError.value = `Responda todos os controles desta pagina antes de continuar. Pendentes: ${codes}`
  return false
}

function prevPage() {
  if (currentPage.value > 0) {
    currentPage.value--
    pageError.value = null
    missingIds.value = new Set()
  }
}

function nextPage() {
  if (!validateCurrentPage()) return
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
    pageError.value = null
    missingIds.value = new Set()
  }
}

function validateAllPages() {
  const missing = store.controls.filter((c) => !isAnswered(c.id))
  if (!missing.length) return true
  missingIds.value = new Set(missing.map((c) => c.id))
  const firstMissing = missing[0]
  const pageIndex = store.controls.findIndex((c) => c.id === firstMissing.id)
  currentPage.value = Math.floor(pageIndex / PAGE_SIZE)
  pageError.value = `Ainda ha ${missing.length} controle(s) sem resposta. Revise a pagina atual.`
  return false
}

async function finish() {
  if (!validateCurrentPage() || !validateAllPages()) return
  finishing.value = true
  error.value = null
  try {
    await api.finishAudit(store.audit.id)
    router.push(`/dashboard/${store.audit.id}`)
  } catch (e) {
    error.value = e.message
  } finally {
    finishing.value = false
  }
}

const btnNav =
  'rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40'
</script>

<template>
  <PageLayout
    title="Auditoria em andamento"
    :subtitle="`${store.company?.name} — ${store.module}`"
    wide
  >
    <div class="mb-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-2 flex justify-between text-sm text-slate-600">
        <span>Progresso do formulario</span>
        <span class="font-medium text-slate-800">
          {{ answeredCount }} / {{ totalCount }} ({{ progressPercent }}%)
        </span>
      </div>
      <div class="h-3 overflow-hidden rounded-full bg-slate-200">
        <div
          class="h-full rounded-full bg-gradient-to-r from-blue-600 to-blue-400 transition-all duration-300"
          :style="{ width: progressPercent + '%' }"
        />
      </div>
    </div>

    <p v-if="error" class="mb-4 rounded-lg bg-red-50 px-4 py-3 text-center text-red-700">{{ error }}</p>
    <p v-if="pageError" class="mb-4 rounded-lg bg-amber-50 px-4 py-3 text-center text-amber-800">{{ pageError }}</p>

    <ControlRow
      v-for="control in pageControls"
      :key="control.id"
      :control="control"
      :saved-status="responses[control.id]"
      :missing="missingIds.has(control.id)"
      @save="saveResponse"
    />

    <div class="mt-6 flex flex-wrap items-center justify-center gap-3">
      <button type="button" :class="btnNav" :disabled="currentPage === 0" @click="prevPage">Anterior</button>
      <span class="text-sm text-slate-600">Pagina {{ currentPage + 1 }} de {{ totalPages }}</span>
      <button type="button" :class="btnNav" :disabled="currentPage >= totalPages - 1" @click="nextPage">
        Proxima
      </button>
    </div>

    <div class="mt-8 rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
      <button
        type="button"
        class="w-full rounded-lg bg-green-600 px-4 py-3 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-50 sm:w-auto sm:min-w-[240px]"
        :disabled="finishing"
        @click="finish"
      >
        Finalizar diagnostico
      </button>
      <p class="mt-3 text-sm text-slate-500">
        Todas as paginas devem estar completas para finalizar e gerar comparativo das ultimas 3 auditorias.
      </p>
    </div>
  </PageLayout>
</template>
