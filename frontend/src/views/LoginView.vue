<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PageLayout from '../components/PageLayout.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const login = ref('')
const password = ref('')
const error = ref(null)

const canSubmit = computed(() => login.value.trim() && password.value)

function validatePassword(pw) {
  if (pw.length < 4 || pw.length > 12) return 'Senha deve ter entre 4 e 12 caracteres.'
  if (!/[A-Za-z]/.test(pw)) return 'Senha deve conter ao menos uma letra.'
  return null
}

async function submit() {
  error.value = null
  const pwError = validatePassword(password.value)
  if (pwError) {
    error.value = pwError
    return
  }
  try {
    await auth.login(login.value.trim(), password.value)
    const next = typeof route.query.next === 'string' ? route.query.next : '/'
    router.replace(next)
  } catch (e) {
    error.value = e?.message || 'Falha no login.'
  }
}
</script>

<template>
  <PageLayout title="Entrar" subtitle="Acesse o AuditaSecIFC com seu login e senha.">
    <div class="mx-auto w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <p
        v-if="error"
        class="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700"
      >
        {{ error }}
      </p>

      <form class="space-y-4" @submit.prevent="submit">
        <label class="block">
          <span class="text-sm font-medium text-slate-700">Login</span>
          <input
            v-model="login"
            type="text"
            autocomplete="username"
            class="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            placeholder="admin"
          />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-slate-700">Senha</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            class="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            placeholder="••••"
          />
          <p class="mt-2 text-xs text-slate-500">4–12 caracteres e ao menos 1 letra.</p>
        </label>

        <button
          type="submit"
          :disabled="!canSubmit || auth.loading"
          class="inline-flex w-full items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {{ auth.loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <p class="mt-4 text-center text-sm text-slate-600">
        Nao possui conta?
        <router-link to="/register" class="text-blue-600 hover:underline">Criar conta</router-link>
      </p>
    </div>
  </PageLayout>
</template>

