<script setup>
import { computed } from 'vue'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  title: String,
  conforme: Number,
  naoConforme: Number,
  emAndamento: Number,
  naoAplica: Number,
})

const chartData = computed(() => ({
  labels: ['Conforme', 'Nao conforme', 'Em andamento', 'Nao aplica'],
  datasets: [{
    data: [props.conforme, props.naoConforme, props.emAndamento, props.naoAplica],
    backgroundColor: ['#22c55e', '#ef4444', '#eab308', '#94a3b8'],
  }],
}))
</script>

<template>
  <article class="flex flex-col items-center rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <h4 class="mb-3 text-center text-sm font-semibold text-slate-800">{{ title }}</h4>
    <div class="mx-auto max-h-48 w-full max-w-xs">
      <Pie :data="chartData" />
    </div>
  </article>
</template>
