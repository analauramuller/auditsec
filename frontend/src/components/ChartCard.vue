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
  percent: { type: Number, default: null },
})

const chartData = computed(() => ({
  labels: ['Conforme', 'Nao conforme', 'Em andamento', 'Nao aplica'],
  datasets: [{
    data: [props.conforme, props.naoConforme, props.emAndamento, props.naoAplica],
    backgroundColor: ['#22c55e', '#ef4444', '#eab308', '#94a3b8'],
  }],
}))

const chartOptions = {
  plugins: {
    tooltip: {
      callbacks: {
        label(context) {
          const total = context.dataset.data.reduce((sum, value) => sum + (value || 0), 0)
          const value = context.raw || 0
          const pct = total ? Math.round((value / total) * 100) : 0
          return `${pct}%`
        },
      },
    },
  },
}
</script>

<template>
  <article class="flex flex-col items-center rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <h4 class="mb-1 text-center text-sm font-semibold text-slate-800">{{ title }}</h4>
    <p v-if="percent !== null" class="mb-3 text-2xl font-bold text-blue-700">{{ percent }}%</p>
    <div class="mx-auto max-h-48 w-full max-w-xs">
      <Pie :data="chartData" :options="chartOptions" />
    </div>
  </article>
</template>
