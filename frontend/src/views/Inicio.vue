<script setup>
import { onMounted, ref } from 'vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const loading = ref(false)
const error = ref('')
const featuredAccommodations = ref([])

const searchFilters = ref({
  location: '',
  maxPrice: '',
  duration: '',
  wifi: false,
  terrace: false,
  garage: false,
})

const normalizeList = (data) => Array.isArray(data) ? data : (data.results || [])

const getImage = (anuncio) => {
  const first = anuncio.imagenes?.[0]

  if (!first) {
    return ''
  }

  return first.url || first.imagen || first.imagen_url || ''
}

const fetchFeatured = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_URL}/api/anuncios/`)

    if (!response.ok) {
      throw new Error('No se pudieron cargar los alojamientos.')
    }

    const data = normalizeList(await response.json())

    featuredAccommodations.value = data.slice(0, 3)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const submitSearch = () => {
  const params = new URLSearchParams()

  if (searchFilters.value.location) {
    params.append('localizacion', searchFilters.value.location)
  }

  if (searchFilters.value.maxPrice) {
    params.append('precio_max', searchFilters.value.maxPrice)
  }

  if (searchFilters.value.wifi) {
    params.append('wifi', 'true')
  }

  if (searchFilters.value.terrace) {
    params.append('terraza', 'true')
  }

  if (searchFilters.value.garage) {
    params.append('garaje', 'true')
  }

  window.location.href = `/anuncios?${params.toString()}`
}

onMounted(() => {
  fetchFeatured()
})
</script>

<template>
  <main class="bg-[#f8fafc] text-slate-900">
    <section class="border-b border-slate-200 bg-white">
      <div class="mx-auto max-w-7xl px-4 py-20 text-center">
        <p class="text-sm font-bold uppercase tracking-wide text-blue-700">
          ErasmusStay
        </p>

        <h1 class="mt-4 text-4xl font-black tracking-tight text-slate-950 md:text-6xl">
          Encuentra alojamiento de confianza para tu Erasmus.
        </h1>

        <p class="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
          Busca habitaciones, estudios y pisos para estancias temporales en Malta.
        </p>

        <form
          @submit.prevent="submitSearch"
          class="mx-auto mt-10 max-w-5xl rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div class="text-left">
              <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
                Ubicación
              </label>

              <input
                v-model="searchFilters.location"
                type="text"
                placeholder="Ej. Sliema"
                class="w-full rounded border border-slate-300 px-3 py-2.5 text-sm focus:border-blue-500 focus:outline-none"
              >
            </div>

            <div class="text-left">
              <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
                Precio máximo
              </label>

              <input
                v-model="searchFilters.maxPrice"
                type="number"
                placeholder="Ej. 600"
                class="w-full rounded border border-slate-300 px-3 py-2.5 text-sm focus:border-blue-500 focus:outline-none"
              >
            </div>

            <div class="text-left">
              <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
                Duración
              </label>

              <input
                v-model="searchFilters.duration"
                type="number"
                placeholder="Meses"
                class="w-full rounded border border-slate-300 px-3 py-2.5 text-sm focus:border-blue-500 focus:outline-none"
              >
            </div>

            <div class="flex items-end">
              <button
                type="submit"
                class="w-full rounded bg-slate-900 py-2.5 font-medium text-white transition hover:bg-slate-800"
              >
                Buscar
              </button>
            </div>
          </div>

          <div class="mt-5 flex flex-wrap items-center justify-center gap-6 border-t border-slate-100 pt-4">
            <label class="flex cursor-pointer items-center gap-2">
              <input v-model="searchFilters.wifi" type="checkbox" class="h-4 w-4 rounded border-slate-300">
              <span class="text-sm font-medium text-slate-600">WiFi</span>
            </label>

            <label class="flex cursor-pointer items-center gap-2">
              <input v-model="searchFilters.terrace" type="checkbox" class="h-4 w-4 rounded border-slate-300">
              <span class="text-sm font-medium text-slate-600">Terraza</span>
            </label>

            <label class="flex cursor-pointer items-center gap-2">
              <input v-model="searchFilters.garage" type="checkbox" class="h-4 w-4 rounded border-slate-300">
              <span class="text-sm font-medium text-slate-600">Garaje</span>
            </label>
          </div>
        </form>
      </div>
    </section>

    <section class="mx-auto max-w-7xl px-4 py-16">
      <div class="mb-8 flex items-end justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold text-slate-900">
            Alojamientos disponibles
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Últimos anuncios aprobados.
          </p>
        </div>

        <router-link to="/anuncios" class="text-sm font-bold text-blue-700 hover:text-blue-900">
          Ver todos →
        </router-link>
      </div>

      <div v-if="loading" class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div v-for="i in 3" :key="i" class="animate-pulse rounded border border-slate-200 bg-white">
          <div class="h-48 bg-slate-200"></div>
          <div class="p-4">
            <div class="mb-2 h-4 w-2/3 bg-slate-200"></div>
            <div class="mb-4 h-3 w-1/2 bg-slate-200"></div>
            <div class="flex items-center justify-between">
              <div class="h-5 w-1/3 bg-slate-200"></div>
              <div class="h-8 w-1/4 rounded bg-slate-200"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-red-700">
        {{ error }}
      </div>

      <div v-else-if="featuredAccommodations.length > 0" class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <article
          v-for="anuncio in featuredAccommodations"
          :key="anuncio.id"
          class="flex flex-col overflow-hidden rounded border border-slate-200 bg-white"
        >
          <div class="relative h-48 bg-slate-200">
            <span class="absolute left-3 top-3 z-10 rounded bg-white px-2 py-1 text-xs font-bold capitalize text-slate-700 shadow-sm">
              {{ (anuncio.tipo_vivienda || '').replace('_', ' ') }}
            </span>

            <img
              v-if="getImage(anuncio)"
              :src="getImage(anuncio)"
              :alt="anuncio.titulo"
              class="h-full w-full object-cover"
            >

            <div v-else class="flex h-full w-full items-center justify-center font-medium text-slate-500">
              Sin imagen disponible
            </div>
          </div>

          <div class="flex flex-1 flex-col justify-between p-5">
            <div>
              <h3 class="mb-1 line-clamp-1 font-bold text-slate-900">
                {{ anuncio.titulo }}
              </h3>

              <p class="mb-4 text-xs capitalize text-slate-500">
                {{ anuncio.localizacion }} • {{ (anuncio.tipo_vivienda || '').replace('_', ' ') }}
              </p>
            </div>

            <div class="flex items-center justify-between border-t border-slate-100 pt-4">
              <p class="font-bold text-slate-900">
                {{ anuncio.precio_mes }}€<span class="text-xs font-normal text-slate-500">/mes</span>
              </p>

              <router-link
                :to="`/anuncio/${anuncio.id}`"
                class="rounded bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-200"
              >
                Ver detalle
              </router-link>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="rounded border border-slate-200 bg-slate-50 py-10 text-center text-slate-500">
        No hay alojamientos disponibles en este momento.
      </div>
    </section>
  </main>
</template>