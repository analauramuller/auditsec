import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuditStore = defineStore('audit', () => {
  const module = ref(null)
  const company = ref(null)
  const audit = ref(null)
  const controls = ref([])

  function setModule(m) { module.value = m }
  function setCompany(c) { company.value = c }
  function setAudit(a) { audit.value = a }
  function setControls(list) { controls.value = list }
  function reset() {
    module.value = null
    company.value = null
    audit.value = null
    controls.value = []
  }

  return { module, company, audit, controls, setModule, setCompany, setAudit, setControls, reset }
})
