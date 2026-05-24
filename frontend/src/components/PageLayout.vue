<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  wide: { type: Boolean, default: false },
})
</script>

<template>
  <div :class="wide ? 'mx-auto w-full max-w-5xl' : 'mx-auto w-full max-w-3xl'">
    <header v-if="title" class="mb-8 text-center">
      <h1 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{{ title }}</h1>
      <p v-if="subtitle" class="mt-2 text-slate-600">{{ subtitle }}</p>
    </header>
    <slot />
  </div>
</template>
