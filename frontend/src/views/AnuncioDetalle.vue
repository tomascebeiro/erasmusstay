<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

/*
|--------------------------------------------------------------------------
| Vista de detalle de anuncio
|--------------------------------------------------------------------------
|
| Esta vista muestra toda la información de un alojamiento concreto:
| imágenes, precio, localización, características, propietario, contacto y
| valoraciones aprobadas.
|
| El número de teléfono del propietario solo se muestra a usuarios que hayan
| iniciado sesión. Así se fuerza a que una persona se registre o acceda a su
| cuenta antes de poder contactar directamente con el propietario.
|
| Además, solo las cuentas con rol estudiante pueden solicitar contacto y dejar
| valoraciones.
|
*/

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const route = useRoute()
const router = useRouter()
const { user, isAuthenticated, getAuthHeaders } = useAuth()

const anuncio = ref(null)
const loading = ref(false)
const error = ref('')
const selectedImage = ref('')

const ratingForm = ref({
  puntuacion: 5,
  comentario: '',
})

const loadingRating = ref(false)
const ratingError = ref('')
const ratingSuccess = ref('')

/*
|--------------------------------------------------------------------------
| Cargar detalle del anuncio
|--------------------------------------------------------------------------
|
| Recupera desde la API la información completa del anuncio usando el id que
| llega en la URL. También selecciona por defecto la primera imagen de la
| galería, si existe.
|
*/
const fetchAnuncio = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_URL}/api/anuncios/${route.params.id}/`, {
      headers: {
        ...getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error('No se pudo recuperar la información detallada del alojamiento.')
    }

    anuncio.value = await response.json()
    selectedImage.value = anuncio.value?.imagenes?.[0]?.url || ''
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

/*
|--------------------------------------------------------------------------
| Permiso para valorar
|--------------------------------------------------------------------------
|
| Solo las cuentas autenticadas con rol estudiante pueden dejar valoraciones.
| Los propietarios y administradores no usan este formulario público.
|
*/
const canReview = computed(() => {
  if (!isAuthenticated.value) return false

  const rol = (user.value?.rol || '').toLowerCase()
  return rol === 'estudiante'
})

/*
|--------------------------------------------------------------------------
| Permiso para solicitar contacto
|--------------------------------------------------------------------------
|
| Solo los estudiantes autenticados pueden abrir una solicitud de contacto.
| Si el usuario no ha iniciado sesión, se le muestra una llamada a login/registro.
|
*/
const canRequestContact = computed(() => {
  if (!isAuthenticated.value) return false

  const rol = (user.value?.rol || '').toLowerCase()
  return rol === 'estudiante'
})

/*
|--------------------------------------------------------------------------
| Enviar valoración
|--------------------------------------------------------------------------
|
| Envía una valoración al backend. La valoración no se publica directamente:
| queda pendiente de aprobación por parte del administrador.
|
*/
const submitRating = async () => {
  if (!ratingForm.value.comentario.trim()) {
    ratingError.value = 'Escribe un comentario para enviar tu reseña.'
    return
  }

  loadingRating.value = true
  ratingError.value = ''
  ratingSuccess.value = ''

  try {
    const payload = {
      anuncio: anuncio.value.id,
      puntuacion: Number(ratingForm.value.puntuacion),
      comentario: ratingForm.value.comentario.trim(),
    }

    const response = await fetch(`${API_URL}/api/valoraciones/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(payload),
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || 'Error al guardar la valoración.')
    }

    ratingForm.value.comentario = ''
    ratingForm.value.puntuacion = 5
    ratingSuccess.value = 'Valoración enviada. Será visible cuando un administrador la apruebe.'

    await fetchAnuncio()
  } catch (err) {
    ratingError.value = err.message
  } finally {
    loadingRating.value = false
  }
}

/*
|--------------------------------------------------------------------------
| Ir al flujo de contacto
|--------------------------------------------------------------------------
|
| Si el usuario no está autenticado, se redirige al login guardando la ruta
| actual como redirect. Si ya ha iniciado sesión, se abre la pantalla de
| contacto asociada al anuncio.
|
*/
const goToContact = () => {
  if (!isAuthenticated.value) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }

  router.push({ name: 'contacto', params: { id: anuncio.value.id } })
}

/*
|--------------------------------------------------------------------------
| Ir a login
|--------------------------------------------------------------------------
|
| Redirige al login y guarda la ruta actual para volver al anuncio después.
|
*/
const goToLogin = () => {
  router.push({ name: 'login', query: { redirect: route.fullPath } })
}

/*
|--------------------------------------------------------------------------
| Ir a registro
|--------------------------------------------------------------------------
|
| Redirige al registro. También se guarda la ruta actual para poder volver al
| anuncio después si se gestiona el redirect tras el registro/login.
|
*/
const goToRegister = () => {
  router.push({ name: 'register', query: { redirect: route.fullPath } })
}

onMounted(() => {
  fetchAnuncio()
})
</script>

<template>
  <main class="bg-slate-50 min-h-screen py-10">
    <div class="max-w-6xl mx-auto px-4">
      <button
        @click="router.back()"
        class="text-sm font-bold text-blue-700 hover:text-blue-900 mb-6"
      >
        ← Volver
      </button>

      <div v-if="loading" class="text-slate-500">
        Cargando anuncio...
      </div>

      <div
        v-else-if="error"
        class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4"
      >
        {{ error }}
      </div>

      <article v-else-if="anuncio" class="grid lg:grid-cols-2 gap-8">
        <section class="bg-white rounded-xl border border-slate-200 p-5">
          <div class="aspect-video bg-slate-100 rounded-xl overflow-hidden flex items-center justify-center">
            <img
              v-if="selectedImage"
              :src="selectedImage"
              :alt="anuncio.titulo"
              class="w-full h-full object-cover"
            >

            <span v-else class="text-slate-400 font-bold">
              Sin imágenes
            </span>
          </div>

          <div v-if="anuncio.imagenes?.length" class="grid grid-cols-4 gap-3 mt-4">
            <button
              v-for="img in anuncio.imagenes"
              :key="img.id"
              type="button"
              @click="selectedImage = img.url"
              class="aspect-video rounded-lg overflow-hidden border"
              :class="selectedImage === img.url ? 'border-blue-600' : 'border-slate-200'"
            >
              <img
                :src="img.url"
                :alt="anuncio.titulo"
                class="w-full h-full object-cover"
              >
            </button>
          </div>
        </section>

        <section class="bg-white rounded-xl border border-slate-200 p-6 md:p-8">
          <div class="flex flex-wrap gap-2 mb-4">
            <span
              v-if="anuncio.aprobado"
              class="bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full"
            >
              Aprobado
            </span>

            <span class="bg-blue-100 text-blue-700 text-xs font-bold px-3 py-1 rounded-full">
              {{ anuncio.tipo_vivienda }}
            </span>
          </div>

          <h1 class="text-3xl md:text-4xl font-black text-slate-900">
            {{ anuncio.titulo }}
          </h1>

          <p class="mt-3 text-xl font-bold text-blue-700">
            {{ anuncio.precio_mes }} €/mes
          </p>

          <p class="mt-2 text-slate-500">
            {{ anuncio.localizacion }}
          </p>

          <p class="mt-6 text-slate-700 leading-relaxed">
            {{ anuncio.descripcion }}
          </p>

          <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mt-6">
            <div class="bg-slate-50 border border-slate-200 rounded-lg p-3">
              <span class="block text-xs text-slate-500 font-bold">Duración</span>
              <span class="font-bold">
                {{ anuncio.duracion_min_meses }}-{{ anuncio.duracion_max_meses }} meses
              </span>
            </div>

            <div class="bg-slate-50 border border-slate-200 rounded-lg p-3">
              <span class="block text-xs text-slate-500 font-bold">WiFi</span>
              <span class="font-bold">{{ anuncio.wifi ? 'Sí' : 'No' }}</span>
            </div>

            <div class="bg-slate-50 border border-slate-200 rounded-lg p-3">
              <span class="block text-xs text-slate-500 font-bold">Terraza</span>
              <span class="font-bold">{{ anuncio.terraza ? 'Sí' : 'No' }}</span>
            </div>

            <div class="bg-slate-50 border border-slate-200 rounded-lg p-3">
              <span class="block text-xs text-slate-500 font-bold">Garaje</span>
              <span class="font-bold">{{ anuncio.garaje ? 'Sí' : 'No' }}</span>
            </div>

            <div class="bg-slate-50 border border-slate-200 rounded-lg p-3 col-span-2">
              <span class="block text-xs text-slate-500 font-bold">Propietario</span>
              <span class="font-bold">{{ anuncio.propietario_nombre }}</span>
            </div>
          </div>

          <div class="mt-8 bg-blue-50 border border-blue-100 rounded-xl p-5">
            <h2 class="font-bold text-slate-900">
              Contacto
            </h2>

            <p class="text-sm text-slate-600 mt-1">
              El teléfono procede de la cuenta del propietario, no del anuncio.
            </p>

            <template v-if="isAuthenticated">
              <p class="mt-3 text-lg font-black text-slate-900">
                {{ anuncio.propietario_telefono || 'Teléfono no configurado' }}
              </p>

              <button
                v-if="canRequestContact"
                type="button"
                @click="goToContact"
                class="mt-4 bg-slate-900 text-white font-bold px-5 py-3 rounded-lg hover:bg-slate-700"
              >
                Solicitar contacto
              </button>

              <p v-else class="mt-4 text-sm text-slate-600">
                Solo las cuentas de estudiante pueden solicitar contacto con el propietario.
              </p>
            </template>

            <template v-else>
              <div class="mt-4 bg-white border border-blue-100 rounded-lg p-4">
                <p class="font-bold text-slate-900">
                  Inicia sesión para ver el teléfono del propietario.
                </p>

                <p class="text-sm text-slate-600 mt-1">
                  Para proteger los datos de contacto, el número solo está disponible para usuarios registrados.
                </p>

                <div class="flex flex-col sm:flex-row gap-3 mt-4">
                  <button
                    type="button"
                    @click="goToLogin"
                    class="bg-slate-900 text-white font-bold px-5 py-3 rounded-lg hover:bg-slate-700"
                  >
                    Iniciar sesión
                  </button>

                  <button
                    type="button"
                    @click="goToRegister"
                    class="bg-white border border-slate-300 text-slate-900 font-bold px-5 py-3 rounded-lg hover:bg-slate-50"
                  >
                    Crear cuenta
                  </button>
                </div>
              </div>
            </template>
          </div>
        </section>

        <section class="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 md:p-8">
          <h2 class="text-2xl font-black text-slate-900 mb-5">
            Valoraciones aprobadas
          </h2>

          <div v-if="anuncio.valoraciones?.length" class="space-y-4">
            <article
              v-for="valoracion in anuncio.valoraciones"
              :key="valoracion.id"
              class="border border-slate-200 rounded-lg p-4"
            >
              <div class="flex justify-between gap-4">
                <strong>{{ valoracion.usuario_nombre }}</strong>
                <span class="font-bold text-yellow-600">
                  {{ valoracion.puntuacion }}/5
                </span>
              </div>

              <p class="text-slate-600 mt-2">
                {{ valoracion.comentario }}
              </p>
            </article>
          </div>

          <p v-else class="text-slate-500">
            Aún no hay valoraciones aprobadas.
          </p>

          <form
            v-if="canReview"
            @submit.prevent="submitRating"
            class="mt-8 border-t border-slate-200 pt-6"
          >
            <h3 class="text-xl font-black text-slate-900 mb-4">
              Dejar valoración
            </h3>

            <div
              v-if="ratingError"
              class="bg-red-50 border border-red-200 text-red-700 rounded p-3 text-sm mb-4"
            >
              {{ ratingError }}
            </div>

            <div
              v-if="ratingSuccess"
              class="bg-green-50 border border-green-200 text-green-700 rounded p-3 text-sm mb-4"
            >
              {{ ratingSuccess }}
            </div>

            <div class="grid md:grid-cols-[160px_1fr] gap-4">
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">
                  Puntuación
                </label>

                <select
                  v-model="ratingForm.puntuacion"
                  class="w-full border border-slate-300 rounded-lg px-3 py-2"
                >
                  <option :value="5">5</option>
                  <option :value="4">4</option>
                  <option :value="3">3</option>
                  <option :value="2">2</option>
                  <option :value="1">1</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-bold text-slate-700 mb-2">
                  Comentario
                </label>

                <textarea
                  v-model="ratingForm.comentario"
                  rows="3"
                  class="w-full border border-slate-300 rounded-lg px-3 py-2"
                ></textarea>
              </div>
            </div>

            <button
              :disabled="loadingRating"
              class="mt-4 bg-blue-700 text-white font-bold px-5 py-3 rounded-lg disabled:opacity-50"
            >
              {{ loadingRating ? 'Enviando...' : 'Enviar valoración' }}
            </button>
          </form>

          <div v-else class="mt-6 text-sm text-slate-500">
            Solo las cuentas de estudiante pueden dejar valoraciones.
          </div>
        </section>
      </article>
    </div>
  </main>
</template>