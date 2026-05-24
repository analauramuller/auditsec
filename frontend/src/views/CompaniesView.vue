<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'
import PageLayout from '../components/PageLayout.vue'

const router = useRouter()
const companies = ref([])
const error = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    companies.value = await api.listCompanies()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

function openCompany(id) {
  router.push(`/empresas/${id}`)
}
</script>

<template>
  <PageLayout title="Empresas cadastradas" subtitle="Selecione uma empresa para ver as auditorias">
    <p v-if="loading" class="text-center text-slate-500">Carregando...</p>
    <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-center text-red-700">{{ error }}</p>
    <p v-if="!loading && !companies.length" class="text-center text-slate-500">
      Nenhuma empresa cadastrada ainda.
    </p>
    <div class="grid gap-4 sm:grid-cols-2">
      <button
        v-for="company in companies"
        :key="company.id"
        type="button"
        class="rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:border-blue-400 hover:shadow-md"
        @click="openCompany(company.id)"
      >
        <h3 class="font-semibold text-slate-900">{{ company.name }}</h3>
        <p v-if="company.cnpj" class="mt-1 text-sm text-slate-600">CNPJ: {{ company.cnpj }}</p>
        <p class="mt-2 text-xs text-slate-500">
          Cadastro: {{ new Date(company.created_at).toLocaleDateString('pt-BR') }}
        </p>
      </button>
    </div>
  </PageLayout>
</template>
