<template>
  <div class="flex min-h-screen flex-col">
    <header class="sticky top-0 z-10 border-b border-slate-200 bg-white shadow-sm">
      <nav class="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <router-link
          to="/"
          class="text-lg font-bold text-blue-700 hover:text-blue-800"
        >
          AuditaSecIFC
        </router-link>
        <ul class="flex flex-wrap items-center justify-center gap-1 sm:gap-2">
          <li>
            <router-link
              to="/"
              class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
              active-class="!bg-blue-50 !text-blue-700"
            >
              Nova auditoria
            </router-link>
          </li>
          <li>
            <router-link
              to="/empresas"
              class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
              active-class="!bg-blue-50 !text-blue-700"
            >
              Empresas
            </router-link>
          </li>
          <li>
            <router-link
              to="/relatorios"
              class="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
              active-class="!bg-blue-50 !text-blue-700"
            >
              Relatorios
            </router-link>
          </li>
        </ul>
      </nav>
    </header>
    <main class="flex-1 px-4 py-8 sm:px-6">
      <router-view />
    </main>
    <footer class="border-t border-slate-200 bg-white py-4 text-center text-sm text-slate-500">
      AuditaSecIFC — NBR ISO/IEC 27001 e 27701
    </footer>
  </div>
</template>
