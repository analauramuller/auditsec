import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  async function init() {
    if (initialized.value) return
    initialized.value = true
    try {
      user.value = await api.me()
    } catch {
      user.value = null
    }
  }

  async function login(login, password) {
    loading.value = true
    try {
      user.value = await api.login({ login, password })
      return user.value
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await api.logout()
    } finally {
      user.value = null
    }
  }

  return { user, loading, isAuthenticated, init, login, logout }
})

