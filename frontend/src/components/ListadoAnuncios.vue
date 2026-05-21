<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'erasmusstay-production.up.railway.app'

// Instancias y rutas
const route = useRoute()
const { user, isAuthenticated } = useAuth()

const anuncios = ref([])
const loading = ref(false)
const error = ref('')

const currentPage = ref(1)
const totalPages = ref(1)
const nextUrl = ref(null)
const previousUrl = ref(null)

// Filtros inicializados con soporte para query params de la URL
const filters = ref({
  search: route.query.localizacion || '',
  tipo_vivienda: '',
  precioMin: '',
  precioMax: route.query.precio_max || '',
  wifi: route.query.wifi === 'true',
  terraza: route.query.terraza === 'true',
  garaje: route.query.garaje === 'true',
  duracion: '' // Placeholder visual para seguir el wireframe
})

const anunciosFiltrados = computed(() => {
  if (user.value?.rol === 'administrador') return anuncios.value
  return anuncios.value.filter(anuncio => anuncio.aprobado && anuncio.publicado)
})

const buildQuery = () => {
  const params = new URLSearchParams()
  if (filters.value.search) params.append('localizacion', filters.value.search)
  if (filters.value.tipo_vivienda) params.append('tipo_vivienda', filters.value.tipo_vivienda)
  if (filters.value.precioMin) params.append('precio_min', filters.value.precioMin)
  if (filters.value.precioMax) params.append('precio_max', filters.value.precioMax)
  if (filters.value.wifi) params.append('wifi', 'true')
  if (filters.value.terraza) params.append('terraza', 'true')
  if (filters.value.garaje) params.append('garaje', 'true')
  params.append('page', currentPage.value)
  return params.toString()
}

const fetchAnuncios = async (url = null) => {
  loading.value = true
  error.value = ''

  try {
    const endpoint = url || `${API_URL}/api/anuncios/?${buildQuery()}`
    const response = await fetch(endpoint)
    if (!response.ok) throw new Error('No se pudieron cargar los alojamientos disponibles')

    const data = await response.json()
    anuncios.value = data.results || data
    nextUrl.value = data.next || null
    previousUrl.value = data.previous || null

    totalPages.value = data.count ? Math.ceil(data.count / 10) : 1
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Watcher para aplicar los filtros automáticamente como en el wireframe
watch(filters, () => {
  currentPage.value = 1
  fetchAnuncios()
}, { deep: true })

const clearFilters = () => {
  filters.value = {
    search: '',
    tipo_vivienda: '',
    precioMin: '',
    precioMax: '',
    wifi: false,
    terraza: false,
    garaje: false,
    duracion: ''
  }
}

const goNext = () => {
  if (!nextUrl.value) return
  currentPage.value += 1
  fetchAnuncios(nextUrl.value)
}

const goPrevious = () => {
  if (!previousUrl.value) return
  currentPage.value -= 1
  fetchAnuncios(previousUrl.value)
}

onMounted(() => {
  fetchAnuncios()
})
</script>

<template>
  <main class="max-w-7xl mx-auto px-4 py-8 md:py-12">
    
    <div class="flex flex-col md:flex-row gap-8 items-start">
      
      <aside class="w-full md:w-64 flex-shrink-0 bg-white rounded border border-slate-200 p-6 md:sticky md:top-24">
        
        <div class="mb-8">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Price Range</h3>
          <div class="flex items-center justify-between gap-2">
            <input 
              v-model="filters.precioMin" 
              type="number" 
              placeholder="Min €" 
              class="w-1/2 border border-slate-300 rounded px-2 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-slate-500"
            />
            <span class="text-slate-400">-</span>
            <input 
              v-model="filters.precioMax" 
              type="number" 
              placeholder="Max €" 
              class="w-1/2 border border-slate-300 rounded px-2 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-slate-500"
            />
          </div>
        </div>

        <div class="mb-8">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Property Type</h3>
          <div class="space-y-3">
            <label class="flex items-center gap-3 cursor-pointer">
              <input type="radio" v-model="filters.tipo_vivienda" value="habitacion" class="w-4 h-4 text-slate-900 border-slate-300 focus:ring-slate-900" />
              <span class="text-sm text-slate-700">Room</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input type="radio" v-model="filters.tipo_vivienda" value="piso_completo" class="w-4 h-4 text-slate-900 border-slate-300 focus:ring-slate-900" />
              <span class="text-sm text-slate-700">Full Flat</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input type="radio" v-model="filters.tipo_vivienda" value="estudio" class="w-4 h-4 text-slate-900 border-slate-300 focus:ring-slate-900" />
              <span class="text-sm text-slate-700">Studio</span>
            </label>
          </div>
        </div>

        <div class="mb-8">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Services</h3>
          <div class="space-y-3">
            <label class="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" v-model="filters.wifi" class="w-4 h-4 rounded text-slate-900 border-slate-300 focus:ring-slate-900" />
              <span class="text-sm text-slate-700">Wifi</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" v-model="filters.terraza" class="w-4 h-4 rounded text-slate-900 border-slate-300 focus:ring-slate-900" />
              <span class="text-sm text-slate-700">Terrace</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" v-model="filters.garaje" class="w-4 h-4 rounded text-slate-900 border-slate-300 focus:ring-slate-900" />
              <span class="text-sm text-slate-700">Garage</span>
            </label>
          </div>
        </div>

        <button 
          @click="clearFilters"
          class="w-full bg-slate-100 text-slate-700 text-xs font-bold py-2.5 rounded hover:bg-slate-200 transition"
        >
          Clear All Filters
        </button>
      </aside>

      <section class="flex-1 w-full">
        
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h1 class="text-2xl font-bold text-slate-900">
              Available Housing <span v-if="filters.search">in {{ filters.search }}</span>
            </h1>
            <p class="text-sm text-slate-500 mt-1">
              Showing {{ anunciosFiltrados.length }} results for your search
            </p>
          </div>
          
          <div class="w-full sm:w-48 relative">
            <input 
              v-model="filters.search"
              type="text" 
              placeholder="Search by location..." 
              class="w-full border border-slate-300 rounded pl-4 pr-10 py-2 text-sm text-slate-700 focus:outline-none focus:border-blue-500"
            />
            <div class="absolute right-3 top-2.5 text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            </div>
          </div>
        </div>

        <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-for="i in 4" :key="i" class="border border-slate-200 rounded animate-pulse">
            <div class="h-48 bg-slate-200"></div>
            <div class="p-5">
              <div class="h-4 bg-slate-200 w-1/4 mb-3"></div>
              <div class="h-5 bg-slate-200 w-3/4 mb-2"></div>
              <div class="h-4 bg-slate-200 w-1/2 mb-6"></div>
              <div class="flex justify-between">
                <div class="h-6 bg-slate-200 w-1/3"></div>
                <div class="h-8 bg-slate-200 w-1/4 rounded"></div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded border border-red-200 text-sm">
          {{ error }}
        </div>

        <div v-else-if="anunciosFiltrados.length" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <article 
            v-for="anuncio in anunciosFiltrados" 
            :key="anuncio.id"
            class="bg-white border border-slate-200 rounded overflow-hidden flex flex-col"
          >
            <div class="h-48 bg-[#e5e7eb] flex items-center justify-center">
              <svg class="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            </div>

            <div class="p-5 flex-1 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider bg-slate-100 px-2 py-0.5 rounded">
                    {{ (anuncio.tipo_vivienda || '').replace('_', ' ') }}
                  </span>
                  <div class="flex items-center gap-1 text-sm font-bold text-slate-800">
                    <span class="text-slate-900">★</span> 
                    {{ anuncio.valoraciones?.length ? (anuncio.valoraciones.reduce((acc, val) => acc + val.puntuacion, 0) / anuncio.valoraciones.length).toFixed(1) : 'Nuevo' }}
                  </div>
                </div>
                
                <h3 class="text-lg font-bold text-slate-900 mb-1 line-clamp-1">{{ anuncio.titulo }}</h3>
                <p class="text-xs text-slate-500 flex items-center gap-1 mb-5">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                  {{ anuncio.localizacion }}
                </p>
              </div>

              <div class="flex items-center justify-between border-t border-slate-100 pt-4 mt-auto">
                <p class="text-xl font-bold text-slate-900">
                  {{ anuncio.precio_mes }}€ <span class="text-xs font-normal text-slate-500">/month</span>
                </p>
                <router-link 
                  :to="`/anuncio/${anuncio.id}`"
                  class="bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-bold py-2 px-4 rounded transition"
                >
                  View details
                </router-link>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="text-center py-20 bg-white border border-slate-200 rounded">
          <svg class="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <h3 class="text-lg font-bold text-slate-700">No properties found</h3>
          <p class="text-sm text-slate-500 mt-1">Try adjusting your search filters.</p>
        </div>

        <div v-if="totalPages > 1" class="flex justify-center items-center gap-2 mt-10">
          <button 
            @click="goPrevious" 
            :disabled="!previousUrl"
            class="w-8 h-8 flex items-center justify-center rounded border border-slate-300 text-slate-600 disabled:opacity-30 transition hover:bg-slate-50"
          >
            &lt;
          </button>
          
          <span class="w-8 h-8 flex items-center justify-center rounded bg-slate-900 text-white font-medium text-sm">
            {{ currentPage }}
          </span>
          <span class="text-slate-400 text-sm px-1">of</span>
          <span class="text-slate-600 font-medium text-sm px-1">{{ totalPages }}</span>

          <button 
            @click="goNext" 
            :disabled="!nextUrl"
            class="w-8 h-8 flex items-center justify-center rounded border border-slate-300 text-slate-600 disabled:opacity-30 transition hover:bg-slate-50"
          >
            &gt;
          </button>
        </div>

      </section>
    </div>
  </main>
</template>