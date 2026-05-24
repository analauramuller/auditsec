<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import PageLayout from '../components/PageLayout.vue'

const router = useRouter()
const store = useAuditStore()
const modules = ref([])
const error = ref(null)

onMounted(async () => {
  try {
    modules.value = await api.getModules()
  } catch (e) {
    error.value = e.message
  }
})

function selectModule(mod) {
  store.reset()
  store.setModule(mod.id)
  router.push('/empresa')
}
</script>

<template>
  <PageLayout
    title="AuditaSecIFC"
    subtitle="Diagnostico NBR ISO/IEC 27001 (27002:2022) e NBR ISO/IEC 27701 (Anexos A1/A2)"
  >
    <p v-if="error" class="mb-6 rounded-lg bg-red-50 px-4 py-3 text-center text-red-700">{{ error }}</p>
    <h2 class="mb-4 text-center text-lg font-semibold text-slate-800">Selecione o modulo</h2>
    <div class="grid gap-4 sm:grid-cols-2">
      <button
        v-for="mod in modules"
        :key="mod.id"
        type="button"
        class="rounded-xl border border-slate-200 bg-white p-6 text-left shadow-sm transition hover:border-blue-400 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        @click="selectModule(mod)"
      >
        <h3 class="text-lg font-semibold text-blue-700">{{ mod.name }}</h3>
        <p class="mt-2 text-sm text-slate-600">{{ mod.description }}</p>
        <p class="mt-2 text-xs text-slate-500">Catalogo: {{ mod.catalog_ref }}</p>
      </button>
    </div>
  </PageLayout>
</template>
