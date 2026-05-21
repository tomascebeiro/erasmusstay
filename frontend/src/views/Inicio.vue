<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const API_URL = import.meta.env.VITE_API_URL || 'https://erasmusstay-production.up.railway.app'
const router = useRouter()

// Variables para el buscador inicial
const searchFilters = ref({
  location: '',
  maxPrice: '',
  duration: '',
  wifi: false,
  terrace: false,
  garage: false
})

const featuredAccommodations = ref([])
const loading = ref(true)

// Función para redirigir al listado con los filtros aplicados en la URL
const handleSearch = () => {
  const queryParams = new URLSearchParams()
  
  if (searchFilters.value.location) queryParams.append('localizacion', searchFilters.value.location)
  if (searchFilters.value.maxPrice) queryParams.append('precio_max', searchFilters.value.maxPrice)
  if (searchFilters.value.wifi) queryParams.append('wifi', 'true')
  if (searchFilters.value.terrace) queryParams.append('terraza', 'true')
  if (searchFilters.value.garage) queryParams.append('garaje', 'true')

  // Redirigir a la vista de anuncios pasando los parámetros
  router.push(`/anuncios?${queryParams.toString()}`)
}

// Cargar unos cuantos alojamientos de muestra para la landing
const fetchFeatured = async () => {
  try {
    const response = await fetch(`${API_URL}/api/anuncios/`)
    if (response.ok) {
      const data = await response.json()
      // Filtramos solo los aprobados y cogemos los 3 primeros para la portada
      featuredAccommodations.value = (data.results || data)
        .filter(a => a.aprobado && a.publicado)
        .slice(0, 3)
    }
  } catch (error) {
    console.error("Error loading featured accommodations:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchFeatured()
})
</script>

<template>
  <main class="w-full">
    
    <section class="w-full bg-slate-50 border-b border-slate-200 py-20 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-3xl md:text-5xl font-bold text-slate-900 mb-10 tracking-tight">
          Find Erasmus housing in Malta
        </h1>

        <div class="bg-white rounded-lg shadow-sm border border-slate-200 p-6 md:p-8">
          <form @submit.prevent="handleSearch" class="flex flex-col gap-6">
            
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
              <div class="md:col-span-1 text-left">
                <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Location</label>
                <input 
                  v-model="searchFilters.location"
                  type="text" 
                  placeholder="e.g. Sliema" 
                  class="w-full border border-slate-300 rounded px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div class="md:col-span-1 text-left">
                <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Max Price</label>
                <input 
                  v-model="searchFilters.maxPrice"
                  type="number" 
                  placeholder="e.g. 600€" 
                  class="w-full border border-slate-300 rounded px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div class="md:col-span-1 text-left">
                <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Stay Duration</label>
                <input 
                  v-model="searchFilters.duration"
                  type="number" 
                  placeholder="Months" 
                  class="w-full border border-slate-300 rounded px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <div class="md:col-span-1">
                <button 
                  type="submit" 
                  class="w-full bg-slate-900 text-white font-medium py-2.5 rounded hover:bg-slate-800 transition"
                >
                  Search
                </button>
              </div>
            </div>

            <div class="flex flex-wrap items-center justify-center gap-6 pt-4 border-t border-slate-100">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="searchFilters.wifi" type="checkbox" class="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" />
                <span class="text-sm text-slate-600 font-medium">Wifi</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="searchFilters.terrace" type="checkbox" class="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" />
                <span class="text-sm text-slate-600 font-medium">Terrace</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="searchFilters.garage" type="checkbox" class="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" />
                <span class="text-sm text-slate-600 font-medium">Garage</span>
              </label>
            </div>

          </form>
        </div>
      </div>
    </section>

    <section class="max-w-7xl mx-auto px-4 py-16">
      <h2 class="text-xl font-bold text-slate-900 mb-8">Available Accommodations</h2>

      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="border border-slate-200 rounded animate-pulse">
          <div class="h-48 bg-slate-200"></div>
          <div class="p-4">
            <div class="h-4 bg-slate-200 w-2/3 mb-2"></div>
            <div class="h-3 bg-slate-200 w-1/2 mb-4"></div>
            <div class="flex justify-between items-center">
              <div class="h-5 bg-slate-200 w-1/3"></div>
              <div class="h-8 bg-slate-200 w-1/4 rounded"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="featuredAccommodations.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <article 
          v-for="anuncio in featuredAccommodations" 
          :key="anuncio.id"
          class="bg-white border border-slate-200 rounded overflow-hidden flex flex-col"
        >
          <div class="h-48 bg-[#d1d5db] flex items-center justify-center relative">
            <span class="absolute top-3 left-3 bg-white text-slate-700 text-xs font-bold px-2 py-1 rounded shadow-sm capitalize">
               {{ (anuncio.tipo_vivienda || '').replace('_', ' ') }}
            </span>
            <span class="text-slate-500 font-medium">Image Placeholder</span>
          </div>

          <div class="p-5 flex-1 flex flex-col justify-between">
            <div>
              <h3 class="font-bold text-slate-900 line-clamp-1 mb-1">{{ anuncio.titulo }}</h3>
              <p class="text-xs text-slate-500 mb-4 capitalize">
                {{ anuncio.localizacion }} • {{ (anuncio.tipo_vivienda || '').replace('_', ' ') }}
              </p>
            </div>

            <div class="flex items-center justify-between border-t border-slate-100 pt-4">
              <p class="font-bold text-slate-900">
                {{ anuncio.precio_mes }}€<span class="text-xs font-normal text-slate-500">/month</span>
              </p>
              
              <router-link 
                :to="`/anuncio/${anuncio.id}`"
                class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold py-2 px-4 rounded transition"
              >
                View details
              </router-link>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="text-center py-10 bg-slate-50 rounded border border-slate-200 text-slate-500">
        No accommodations available at the moment.
      </div>
    </section>

  </main>
</template>