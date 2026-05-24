<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'
import { useAuditStore } from '../stores/audit'
import PageLayout from '../components/PageLayout.vue'

const router = useRouter()
const store = useAuditStore()
const name = ref('')
const cnpj = ref('')
const auditDate = ref(new Date().toISOString().slice(0, 10))
const error = ref(null)
const loading = ref(false)

const inputClass =
  'mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20'

async function startAudit() {
  if (!name.value.trim()) {
    error.value = 'Informe o nome da empresa'
    return
  }
  loading.value = true
  error.value = null
  try {
    const check = await api.checkCompanyDuplicate(name.value, cnpj.value || null)
    if (!check.available) {
      error.value = check.message || 'Empresa ja cadastrada'
      return
    }
    const company = await api.createCompany({ name: name.value, cnpj: cnpj.value || null })
    store.setCompany(company)
    const audit = await api.createAudit({
      company_id: company.id,
      module: store.module,
      audit_date: auditDate.value,
    })
    store.setAudit(audit)
    const controls = await api.getControls(store.module)
    store.setControls(controls)
    router.push('/auditoria')
  } catch (e) {
    error.value = typeof e.message === 'string' ? e.message : 'Nao foi possivel cadastrar a empresa'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <PageLayout title="Nova auditoria" :subtitle="`Modulo ${store.module}`">
    <form class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm" @submit.prevent="startAudit">
      <p class="mb-4 text-sm text-slate-600">
        Nome e CNPJ devem ser unicos no sistema. Empresas ja cadastradas podem receber nova auditoria pelo menu Empresas.
      </p>
      <div class="space-y-4">
        <label class="block text-sm font-medium text-slate-700">
          Nome da empresa
          <input v-model="name" required :class="inputClass" />
        </label>
        <label class="block text-sm font-medium text-slate-700">
          CNPJ (opcional, 14 digitos)
          <input v-model="cnpj" placeholder="00.000.000/0000-00" :class="inputClass" />
        </label>
        <label class="block text-sm font-medium text-slate-700">
          Data da auditoria
          <input v-model="auditDate" type="date" :class="inputClass" />
        </label>
      </div>
      <p v-if="error" class="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>
      <button
        type="submit"
        class="mt-6 w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
        :disabled="loading"
      >
        {{ loading ? 'Verificando...' : 'Iniciar auditoria' }}
      </button>
    </form>
    <p class="mt-6 text-center">
      <router-link to="/" class="text-sm font-medium text-blue-600 hover:text-blue-800">Voltar</router-link>
    </p>
  </PageLayout>
</template>
