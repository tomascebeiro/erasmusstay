<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

/**
 * Listado público de anuncios.
 *
 * Permite:
 * - listar alojamientos aprobados;
 * - filtrar por ubicación, tipo, precio y servicios;
 * - mostrar imágenes reales;
 * - permitir editar o eliminar anuncios si el usuario es propietario del anuncio;
 * - permitir administrar anuncios si el usuario es administrador.
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const route = useRoute()
const { user, getAuthHeaders, isAuthenticated } = useAuth()

const anuncios = ref([])
const cargando = ref(false)
const error = ref('')
const mensajeExito = ref('')

const filtros = ref({
  busqueda: route.query.localizacion || '',
  tipo_vivienda: route.query.tipo_vivienda || '',
  precio_min: route.query.precio_min || '',
  precio_max: route.query.precio_max || route.query.maxPrice || '',
  wifi: route.query.wifi === 'true',
  terraza: route.query.terraza === 'true',
  garaje: route.query.garaje === 'true',
})

/**
 * Normaliza una respuesta paginada o una lista directa.
 */
const normalizarLista = (data) => {
  return Array.isArray(data) ? data : (data.results || [])
}

const rol = computed(() => {
  return (user.value?.rol || '').toLowerCase()
})

const esPropietario = computed(() => {
  return rol.value === 'propietario'
})

const esAdmin = computed(() => {
  return rol.value === 'administrador' || user.value?.username === 'admin'
})

/**
 * Comprueba si el usuario puede gestionar un anuncio concreto.
 */
const puedeGestionar = (anuncio) => {
  if (!isAuthenticated.value) return false
  if (esAdmin.value) return true

  return esPropietario.value && anuncio.propietario === user.value?.id
}

/**
 * Obtiene la primera imagen disponible del anuncio.
 */
const obtenerImagen = (anuncio) => {
  const primera = anuncio.imagenes?.[0]

  if (!primera) {
    return ''
  }

  return primera.url || primera.imagen || primera.imagen_url || ''
}

/**
 * Construye la query de filtros para el backend.
 */
const construirQuery = () => {
  const params = new URLSearchParams()

  if (filtros.value.busqueda) {
    params.append('localizacion', filtros.value.busqueda)
  }

  if (filtros.value.tipo_vivienda) {
    params.append('tipo_vivienda', filtros.value.tipo_vivienda)
  }

  if (filtros.value.precio_min) {
    params.append('precio_min', filtros.value.precio_min)
  }

  if (filtros.value.precio_max) {
    params.append('precio_max', filtros.value.precio_max)
  }

  if (filtros.value.wifi) {
    params.append('wifi', 'true')
  }

  if (filtros.value.terraza) {
    params.append('terraza', 'true')
  }

  if (filtros.value.garaje) {
    params.append('garaje', 'true')
  }

  return params.toString()
}

/**
 * Carga los anuncios desde la API.
 */
const cargarAnuncios = async () => {
  cargando.value = true
  error.value = ''

  try {
    const query = construirQuery()
    const url = query ? `${API_URL}/api/anuncios/?${query}` : `${API_URL}/api/anuncios/`

    const response = await fetch(url, {
      headers: {
        ...getAuthHeaders(),
      },
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'No se pudieron cargar los anuncios.')
    }

    anuncios.value = normalizarLista(data)
  } catch (err) {
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

/**
 * Elimina un anuncio si el usuario tiene permisos.
 */
const eliminarAnuncio = async (anuncio) => {
  if (!confirm(`¿Seguro que quieres eliminar el anuncio "${anuncio.titulo}"?`)) {
    return
  }

  error.value = ''
  mensajeExito.value = ''

  try {
    const response = await fetch(`${API_URL}/api/anuncios/${anuncio.id}/`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeaders(),
      },
    })

    if (!response.ok && response.status !== 204) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.detail || data.error || 'No se pudo eliminar el anuncio.')
    }

    mensajeExito.value = 'Anuncio eliminado correctamente.'
    await cargarAnuncios()
  } catch (err) {
    error.value = err.message
  }
}

/**
 * Limpia todos los filtros.
 */
const limpiarFiltros = () => {
  filtros.value = {
    busqueda: '',
    tipo_vivienda: '',
    precio_min: '',
    precio_max: '',
    wifi: false,
    terraza: false,
    garaje: false,
  }

  cargarAnuncios()
}

onMounted(() => {
  cargarAnuncios()
})
</script>

<template>
  <main class="min-h-screen bg-slate-50 py-10">
    <div class="mx-auto max-w-7xl px-4">
      <!-- Cabecera -->
      <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-sm font-bold uppercase tracking-wide text-blue-700">
            Alojamientos
          </p>

          <h1 class="mt-2 text-2xl font-black text-slate-900 md:text-4xl">
            Alojamientos disponibles
          </h1>

          <p class="mt-2 text-slate-500">
            Mostrando {{ anuncios.length }} resultados.
          </p>
        </div>

        <router-link
          v-if="esPropietario || esAdmin"
          to="/crear-anuncio"
          class="rounded bg-slate-900 px-5 py-3 font-bold text-white hover:bg-slate-700"
        >
          Publicar anuncio
        </router-link>
      </div>

      <!-- Mensajes -->
      <div
        v-if="error"
        class="mb-6 rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700"
      >
        {{ error }}
      </div>

      <div
        v-if="mensajeExito"
        class="mb-6 rounded border border-green-200 bg-green-50 p-4 text-sm text-green-700"
      >
        {{ mensajeExito }}
      </div>

      <div class="grid gap-8 lg:grid-cols-[260px_1fr]">
        <!-- Filtros -->
        <aside class="h-fit rounded border border-slate-200 bg-white p-5">
          <h2 class="mb-5 font-black text-slate-900">
            Filtros
          </h2>

          <div class="space-y-5">
            <div>
              <label class="mb-2 block text-sm font-bold text-slate-700">
                Ubicación
              </label>

              <input
                v-model="filtros.busqueda"
                type="text"
                placeholder="Buscar por ubicación..."
                class="w-full rounded border border-slate-300 px-4 py-2 text-sm"
              >
            </div>

            <div>
              <label class="mb-2 block text-sm font-bold text-slate-700">
                Tipo de vivienda
              </label>

              <select
                v-model="filtros.tipo_vivienda"
                class="w-full rounded border border-slate-300 px-4 py-2 text-sm"
              >
                <option value="">Todos</option>
                <option value="habitacion">Habitación</option>
                <option value="piso_completo">Piso completo</option>
                <option value="estudio">Estudio</option>
              </select>
            </div>

            <div>
              <label class="mb-2 block text-sm font-bold text-slate-700">
                Precio mínimo
              </label>

              <input
                v-model="filtros.precio_min"
                type="number"
                class="w-full rounded border border-slate-300 px-4 py-2 text-sm"
              >
            </div>

            <div>
              <label class="mb-2 block text-sm font-bold text-slate-700">
                Precio máximo
              </label>

              <input
                v-model="filtros.precio_max"
                type="number"
                class="w-full rounded border border-slate-300 px-4 py-2 text-sm"
              >
            </div>

            <div class="space-y-3">
              <label class="flex cursor-pointer items-center gap-3">
                <input v-model="filtros.wifi" type="checkbox">
                <span class="text-sm text-slate-700">WiFi</span>
              </label>

              <label class="flex cursor-pointer items-center gap-3">
                <input v-model="filtros.terraza" type="checkbox">
                <span class="text-sm text-slate-700">Terraza</span>
              </label>

              <label class="flex cursor-pointer items-center gap-3">
                <input v-model="filtros.garaje" type="checkbox">
                <span class="text-sm text-slate-700">Garaje</span>
              </label>
            </div>

            <button
              type="button"
              class="w-full rounded bg-slate-900 py-2.5 font-bold text-white"
              @click="cargarAnuncios"
            >
              Aplicar filtros
            </button>

            <button
              type="button"
              class="w-full rounded bg-slate-100 py-2.5 text-xs font-bold text-slate-700 transition hover:bg-slate-200"
              @click="limpiarFiltros"
            >
              Limpiar filtros
            </button>
          </div>
        </aside>

        <!-- Resultados -->
        <section>
          <div
            v-if="cargando"
            class="grid grid-cols-1 gap-6 lg:grid-cols-2"
          >
            <div
              v-for="i in 4"
              :key="i"
              class="animate-pulse rounded border border-slate-200 bg-white"
            >
              <div class="h-48 bg-slate-200"></div>

              <div class="p-5">
                <div class="mb-3 h-4 w-1/4 bg-slate-200"></div>
                <div class="mb-2 h-5 w-3/4 bg-slate-200"></div>
                <div class="mb-6 h-4 w-1/2 bg-slate-200"></div>

                <div class="flex justify-between">
                  <div class="h-6 w-1/3 bg-slate-200"></div>
                  <div class="h-8 w-1/4 rounded bg-slate-200"></div>
                </div>
              </div>
            </div>
          </div>

          <div
            v-else-if="anuncios.length"
            class="grid grid-cols-1 gap-6 lg:grid-cols-2"
          >
            <article
              v-for="anuncio in anuncios"
              :key="anuncio.id"
              class="flex flex-col overflow-hidden rounded border border-slate-200 bg-white"
            >
              <div class="h-48 bg-slate-200">
                <img
                  v-if="obtenerImagen(anuncio)"
                  :src="obtenerImagen(anuncio)"
                  :alt="anuncio.titulo"
                  class="h-full w-full object-cover"
                >

                <div
                  v-else
                  class="flex h-full w-full items-center justify-center text-slate-400"
                >
                  Sin imagen disponible
                </div>
              </div>

              <div class="flex flex-1 flex-col justify-between p-5">
                <div>
                  <div class="mb-2 flex items-center justify-between">
                    <span class="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                      {{ (anuncio.tipo_vivienda || '').replace('_', ' ') }}
                    </span>

                    <span
                      v-if="puedeGestionar(anuncio)"
                      class="rounded px-2 py-0.5 text-[10px] font-bold uppercase"
                      :class="anuncio.aprobado ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                    >
                      {{ anuncio.aprobado ? 'Aprobado' : 'Pendiente' }}
                    </span>
                  </div>

                  <h3 class="mb-1 line-clamp-1 text-lg font-bold text-slate-900">
                    {{ anuncio.titulo }}
                  </h3>

                  <p class="mb-5 text-xs text-slate-500">
                    {{ anuncio.localizacion }}
                  </p>
                </div>

                <div class="mt-auto border-t border-slate-100 pt-4">
                  <div class="flex items-center justify-between">
                    <p class="text-xl font-bold text-slate-900">
                      {{ anuncio.precio_mes }}€
                      <span class="text-xs font-normal text-slate-500">/mes</span>
                    </p>

                    <router-link
                      :to="`/anuncio/${anuncio.id}`"
                      class="rounded bg-slate-100 px-4 py-2 text-xs font-bold text-slate-700 transition hover:bg-slate-200"
                    >
                      Ver detalle
                    </router-link>
                  </div>

                  <div
                    v-if="puedeGestionar(anuncio)"
                    class="mt-4 flex items-center justify-end gap-3"
                  >
                    <router-link
                      :to="{ name: 'editar-anuncio', params: { id: anuncio.id } }"
                      class="text-xs font-bold text-blue-700 hover:text-blue-900"
                    >
                      Editar
                    </router-link>

                    <button
                      type="button"
                      class="text-xs font-bold text-red-700 hover:text-red-900"
                      @click="eliminarAnuncio(anuncio)"
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              </div>
            </article>
          </div>

          <div
            v-else
            class="rounded border border-slate-200 bg-white py-20 text-center"
          >
            <h3 class="text-lg font-bold text-slate-700">
              No se han encontrado alojamientos
            </h3>

            <p class="mt-1 text-sm text-slate-500">
              Prueba a modificar los filtros de búsqueda.
            </p>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>