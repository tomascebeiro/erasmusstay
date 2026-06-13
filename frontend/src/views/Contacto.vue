<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const route = useRoute()
const { user, getAuthHeaders } = useAuth()

const anuncio = ref(null)
const solicitudes = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  mensaje: '',
})

const role = computed(() => (user.value?.rol || '').toLowerCase())
const isStudent = computed(() => role.value === 'estudiante')
const isOwner = computed(() => role.value === 'propietario')
const isAdmin = computed(() => role.value === 'administrador')

const normalizeList = (data) => Array.isArray(data) ? data : (data.results || [])

const fetchAnuncio = async () => {
  if (!route.params.id) return

  const response = await fetch(`${API_URL}/api/anuncios/${route.params.id}/`, {
    headers: {
      ...getAuthHeaders(),
    },
  })

  if (!response.ok) {
    throw new Error('No se pudo cargar el anuncio.')
  }

  anuncio.value = await response.json()
}

const fetchSolicitudes = async () => {
  const response = await fetch(`${API_URL}/api/solicitudes/`, {
    headers: {
      ...getAuthHeaders(),
    },
  })

  if (!response.ok) {
    throw new Error('No se pudo cargar el historial de solicitudes.')
  }

  solicitudes.value = normalizeList(await response.json())
}

const loadData = async () => {
  loading.value = true
  error.value = ''

  try {
    await Promise.all([
      fetchAnuncio(),
      fetchSolicitudes(),
    ])
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const submitSolicitud = async () => {
  if (!route.params.id) {
    error.value = 'Selecciona un anuncio para solicitar contacto.'
    return
  }

  error.value = ''
  success.value = ''

  try {
    const response = await fetch(`${API_URL}/api/solicitudes/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        anuncio: Number(route.params.id),
        mensaje: form.value.mensaje,
      }),
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || 'No se pudo registrar la solicitud.')
    }

    form.value.mensaje = ''
    success.value = 'Solicitud registrada correctamente.'
    await fetchSolicitudes()
  } catch (err) {
    error.value = err.message
  }
}

const updateEstado = async (solicitud, estado) => {
  error.value = ''

  try {
    const response = await fetch(`${API_URL}/api/solicitudes/${solicitud.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ estado }),
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || 'No se pudo actualizar la solicitud.')
    }

    await fetchSolicitudes()
  } catch (err) {
    error.value = err.message
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <main class="bg-slate-50 min-h-screen py-10">
    <div class="max-w-5xl mx-auto px-4">
      <div class="mb-8">
        <p class="text-sm font-bold text-blue-700 uppercase tracking-wide">
          Contacto
        </p>
        <h1 class="text-3xl md:text-4xl font-black text-slate-900 mt-2">
          Historial de solicitudes
        </h1>
        <p class="text-slate-600 mt-3">
          Revisa las solicitudes realizadas o recibidas y su estado.
        </p>
      </div>

      <div v-if="loading" class="text-slate-500">
        Cargando...
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">
        {{ error }}
      </div>

      <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 rounded-lg p-4 mb-6">
        {{ success }}
      </div>

      <section v-if="route.params.id && anuncio && isStudent" class="bg-white border border-slate-200 rounded-xl p-6 mb-8">
        <h2 class="text-2xl font-black text-slate-900">
          Solicitar contacto por este anuncio
        </h2>

        <div class="mt-4 bg-slate-50 border border-slate-200 rounded-lg p-4">
          <strong>{{ anuncio.titulo }}</strong>
          <p class="text-slate-600">{{ anuncio.localizacion }} · {{ anuncio.precio_mes }} €/mes</p>
          <p class="text-slate-600 mt-2">
            Teléfono propietario:
            <strong>{{ anuncio.propietario_telefono || 'No configurado' }}</strong>
          </p>
        </div>

        <form @submit.prevent="submitSolicitud" class="mt-5">
          <label class="block text-sm font-bold text-slate-700 mb-2">
            Mensaje opcional
          </label>
          <textarea
            v-model="form.mensaje"
            rows="4"
            class="w-full border border-slate-300 rounded-lg px-4 py-3"
            placeholder="Hola, estoy interesado en este alojamiento..."
          ></textarea>

          <button type="submit" class="mt-4 bg-slate-900 text-white font-bold px-5 py-3 rounded-lg">
            Registrar solicitud
          </button>
        </form>
      </section>

      <section class="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div class="p-6 border-b border-slate-200">
          <h2 class="text-2xl font-black text-slate-900">
            {{ isOwner ? 'Solicitudes recibidas' : isAdmin ? 'Todas las solicitudes' : 'Mis solicitudes realizadas' }}
          </h2>
        </div>

        <div v-if="solicitudes.length === 0" class="p-8 text-center text-slate-500">
          No hay solicitudes registradas.
        </div>

        <div v-else class="divide-y divide-slate-200">
          <article v-for="solicitud in solicitudes" :key="solicitud.id" class="p-6">
            <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div>
                <h3 class="font-black text-slate-900">
                  {{ solicitud.anuncio_titulo }}
                </h3>

                <p class="text-sm text-slate-500 mt-1">
                  {{ solicitud.anuncio_localizacion }}
                </p>

                <p class="text-sm text-slate-600 mt-3" v-if="solicitud.mensaje">
                  “{{ solicitud.mensaje }}”
                </p>

                <p class="text-sm text-slate-500 mt-3">
                  Estudiante: <strong>{{ solicitud.estudiante_nombre }}</strong>
                </p>

                <p class="text-sm text-slate-500">
                  Teléfono propietario en el momento de solicitud:
                  <strong>{{ solicitud.telefono_propietario_snapshot || 'No configurado' }}</strong>
                </p>
              </div>

              <div class="flex flex-col gap-2 md:items-end">
                <span class="text-xs font-black uppercase tracking-wide px-3 py-1 rounded-full"
                      :class="{
                        'bg-yellow-100 text-yellow-700': solicitud.estado === 'pendiente',
                        'bg-green-100 text-green-700': solicitud.estado === 'respondida',
                        'bg-slate-100 text-slate-700': solicitud.estado === 'cerrada'
                      }">
                  {{ solicitud.estado }}
                </span>

                <div v-if="isOwner || isAdmin" class="flex gap-2 mt-2">
                  <button @click="updateEstado(solicitud, 'respondida')" class="text-xs font-bold bg-green-50 text-green-700 px-3 py-2 rounded">
                    Respondida
                  </button>
                  <button @click="updateEstado(solicitud, 'cerrada')" class="text-xs font-bold bg-slate-100 text-slate-700 px-3 py-2 rounded">
                    Cerrar
                  </button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </main>
</template>