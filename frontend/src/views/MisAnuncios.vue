<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const { user, getAuthHeaders } = useAuth()

const loading = ref(false)
const error = ref('')
const success = ref('')
const anuncios = ref([])

const role = computed(() => (user.value?.rol || '').toLowerCase())
const isOwnerOrAdmin = computed(() => {
  return ['propietario', 'administrador'].includes(role.value) || user.value?.username === 'admin'
})

const normalizeList = (data) => Array.isArray(data) ? data : (data.results || [])

const getImage = (anuncio) => {
  const first = anuncio.imagenes?.[0]

  if (!first) {
    return ''
  }

  return first.url || first.imagen || first.imagen_url || ''
}

const fetchMisAnuncios = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await fetch(`${API_URL}/api/anuncios/?mine=true`, {
      headers: {
        ...getAuthHeaders(),
      },
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'No se pudieron cargar tus anuncios.')
    }

    anuncios.value = normalizeList(data)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const eliminarAnuncio = async (anuncio) => {
  if (!confirm(`¿Seguro que quieres eliminar el anuncio "${anuncio.titulo}"?`)) {
    return
  }

  error.value = ''
  success.value = ''

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

    success.value = 'Anuncio eliminado correctamente.'
    await fetchMisAnuncios()
  } catch (err) {
    error.value = err.message
  }
}

onMounted(() => {
  fetchMisAnuncios()
})
</script>

<template>
  <main class="min-h-screen bg-slate-50 py-10">
    <div class="mx-auto max-w-7xl px-4">
      <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-sm font-bold uppercase tracking-wide text-blue-700">
            Panel de propietario
          </p>

          <h1 class="mt-2 text-3xl font-black text-slate-900 md:text-4xl">
            Mis anuncios
          </h1>

          <p class="mt-3 text-slate-600">
            Desde aquí puedes revisar, editar o eliminar los alojamientos que has publicado.
          </p>
        </div>

        <router-link
          to="/crear-anuncio"
          class="rounded bg-slate-900 px-5 py-3 font-bold text-white hover:bg-slate-700"
        >
          Crear nuevo anuncio
        </router-link>
      </div>

      <div
        v-if="!isOwnerOrAdmin"
        class="rounded border border-red-200 bg-red-50 p-4 text-red-700"
      >
        Solo las cuentas de propietario pueden acceder a esta sección.
      </div>

      <template v-else>
        <div
          v-if="error"
          class="mb-6 rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700"
        >
          {{ error }}
        </div>

        <div
          v-if="success"
          class="mb-6 rounded border border-green-200 bg-green-50 p-4 text-sm text-green-700"
        >
          {{ success }}
        </div>

        <div v-if="loading" class="text-slate-500">
          Cargando tus anuncios...
        </div>

        <div
          v-else-if="anuncios.length === 0"
          class="rounded border border-slate-200 bg-white p-10 text-center"
        >
          <h2 class="text-xl font-black text-slate-900">
            Todavía no tienes anuncios publicados
          </h2>

          <p class="mt-2 text-slate-500">
            Crea tu primer alojamiento para que pueda ser revisado por administración.
          </p>

          <router-link
            to="/crear-anuncio"
            class="mt-6 inline-flex rounded bg-slate-900 px-5 py-3 font-bold text-white hover:bg-slate-700"
          >
            Crear anuncio
          </router-link>
        </div>

        <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="anuncio in anuncios"
            :key="anuncio.id"
            class="overflow-hidden rounded border border-slate-200 bg-white shadow-sm"
          >
            <div class="relative h-48 bg-slate-200">
              <img
                v-if="getImage(anuncio)"
                :src="getImage(anuncio)"
                :alt="anuncio.titulo"
                class="h-full w-full object-cover"
              >

              <div
                v-else
                class="flex h-full w-full items-center justify-center font-medium text-slate-400"
              >
                Sin imagen
              </div>

              <span
                class="absolute left-3 top-3 rounded px-2 py-1 text-[10px] font-black uppercase tracking-wide"
                :class="anuncio.aprobado ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
              >
                {{ anuncio.aprobado ? 'Aprobado' : 'Pendiente' }}
              </span>
            </div>

            <div class="p-5">
              <div class="mb-3 flex items-start justify-between gap-4">
                <div>
                  <h2 class="text-lg font-black text-slate-900">
                    {{ anuncio.titulo }}
                  </h2>

                  <p class="mt-1 text-sm text-slate-500">
                    {{ anuncio.localizacion }}
                  </p>
                </div>

                <p class="whitespace-nowrap text-lg font-black text-slate-900">
                  {{ anuncio.precio_mes }} €
                </p>
              </div>

              <p class="line-clamp-3 text-sm leading-6 text-slate-600">
                {{ anuncio.descripcion }}
              </p>

              <div class="mt-5 flex flex-wrap gap-2">
                <span
                  v-if="anuncio.wifi"
                  class="rounded bg-slate-100 px-2 py-1 text-xs font-bold text-slate-700"
                >
                  WiFi
                </span>

                <span
                  v-if="anuncio.terraza"
                  class="rounded bg-slate-100 px-2 py-1 text-xs font-bold text-slate-700"
                >
                  Terraza
                </span>

                <span
                  v-if="anuncio.garaje"
                  class="rounded bg-slate-100 px-2 py-1 text-xs font-bold text-slate-700"
                >
                  Garaje
                </span>
              </div>

              <div class="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
                <router-link
                  :to="`/anuncio/${anuncio.id}`"
                  class="text-xs font-bold text-blue-700 hover:text-blue-900"
                >
                  Ver detalle
                </router-link>

                <div class="flex items-center gap-4">
                  <router-link
                    :to="{ name: 'editar-anuncio', params: { id: anuncio.id } }"
                    class="text-xs font-bold text-slate-700 hover:text-slate-900"
                  >
                    Editar
                  </router-link>

                  <button
                    type="button"
                    @click="eliminarAnuncio(anuncio)"
                    class="text-xs font-bold text-red-700 hover:text-red-900"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </template>
    </div>
  </main>
</template>