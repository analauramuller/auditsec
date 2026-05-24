<script setup>
import { ref, watch } from 'vue'
import { categoryLabel } from '../utils/labels'

const props = defineProps({
  control: { type: Object, required: true },
  savedStatus: { type: String, default: null },
  missing: { type: Boolean, default: false },
})
const emit = defineEmits(['save'])

const status = ref(props.savedStatus)
const workInProgress = ref(false)

const baseBtn =
  'rounded-lg border-2 px-4 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-1'

watch(
  () => props.savedStatus,
  (v) => {
    status.value = v
    if (v === 'EM_ANDAMENTO') {
      status.value = 'NAO_CONFORME'
      workInProgress.value = true
    }
  },
  { immediate: true },
)

function select(newStatus) {
  status.value = newStatus
  if (newStatus !== 'NAO_CONFORME') workInProgress.value = false
  emit('save', {
    control_id: props.control.id,
    status: newStatus,
    work_in_progress: newStatus === 'NAO_CONFORME' && workInProgress.value,
  })
}

function toggleWork() {
  workInProgress.value = !workInProgress.value
  if (status.value === 'NAO_CONFORME') {
    emit('save', {
      control_id: props.control.id,
      status: 'NAO_CONFORME',
      work_in_progress: workInProgress.value,
    })
  }
}

function btnClass(option) {
  const idle = `${baseBtn} border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-300`
  if (status.value !== option) return idle
  if (option === 'CONFORME') {
    return `${baseBtn} border-green-600 bg-green-100 text-green-800 ring-green-500`
  }
  if (option === 'NAO_CONFORME') {
    return `${baseBtn} border-red-600 bg-red-100 text-red-800 ring-red-500`
  }
  return `${baseBtn} border-slate-500 bg-slate-200 text-slate-800 ring-slate-400`
}
</script>

<template>
  <article
    class="mb-4 rounded-xl border bg-white p-5 shadow-sm transition"
    :class="missing ? 'border-red-500 ring-2 ring-red-200' : 'border-slate-200'"
  >
    <p v-if="missing" class="mb-2 text-sm font-semibold text-red-600">
      Resposta obrigatoria — selecione uma opcao abaixo
    </p>
    <p class="font-semibold text-slate-900">
      <span class="text-blue-700">{{ control.code }}</span> — {{ control.title }}
    </p>
    <p class="mt-1 text-xs uppercase tracking-wide text-slate-500">
      {{ categoryLabel(control.category) }}
    </p>
    <p
      v-if="control.description"
      class="mt-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm leading-relaxed text-slate-600"
    >
      {{ control.description }}
    </p>
    <div class="mt-4 flex flex-wrap justify-center gap-2 sm:justify-start">
      <button type="button" :class="btnClass('CONFORME')" @click="select('CONFORME')">Conforme</button>
      <button type="button" :class="btnClass('NAO_CONFORME')" @click="select('NAO_CONFORME')">
        Nao conforme
      </button>
      <button type="button" :class="btnClass('NAO_APLICA')" @click="select('NAO_APLICA')">Nao aplica</button>
    </div>
    <label
      v-if="status === 'NAO_CONFORME'"
      class="mt-4 flex cursor-pointer items-center justify-center gap-2 text-sm text-slate-700 sm:justify-start"
    >
      <input
        type="checkbox"
        class="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
        :checked="workInProgress"
        @change="toggleWork"
      />
      Existe trabalho em andamento?
    </label>
  </article>
</template>
