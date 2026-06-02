<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

/**
 * Vista para crear y editar anuncios.
 *
 * Esta vista se reutiliza para dos rutas:
 * - /crear-anuncio
 * - /editar-anuncio/:id
 *
 * Responsabilidades:
 * - Crear anuncios como propietario o administrador.
 * - Cargar un anuncio existente si se entra en modo edición.
 * - Enviar datos como multipart/form-data para permitir subida de imágenes.
 * - Mostrar imágenes actuales y vista previa de nuevas imágenes.
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const route = useRoute()
const router = useRouter()

const { user, getAuthHeaders } = useAuth()

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')

const imagePreviews = ref([])
const existingImages = ref([])

/**
 * La vista está en modo edición cuando la ruta contiene un id.
 */
const isEditMode = computed(() => Boolean(route.params.id))

const form = ref({
  titulo: '',
  descripcion: '',
  precio_mes: '',
  localizacion: '',
  tipo_vivienda: 'habitacion',
  duracion_min_meses: 3,
  duracion_max_meses: 6,
  wifi: true,
  terraza: false,
  garaje: false,
  imagenes: [],
})

/**
 * Comprueba si el usuario puede crear o editar anuncios.
 */
const role = computed(() => {
  return (user.value?.rol || '').toLowerCase()
})

const canPublish = computed(() => {
  return role.value === 'propietario' || role.value === 'administrador' || user.value?.username === 'admin'
})

/**
 * Obtiene la URL válida de una imagen.
 * Soporta imágenes subidas y URLs antiguas.
 */
const getImage = (image) => {
  return image.url || image.imagen || image.imagen_url || ''
}

/**
 * Recoge las imágenes seleccionadas y genera previsualizaciones locales.
 */
const handleImages = (event) => {
  const files = Array.from(event.target.files || [])

  form.value.imagenes = files

  imagePreviews.value.forEach((url) => URL.revokeObjectURL(url))
  imagePreviews.value = files.map((file) => URL.createObjectURL(file))
}

/**
 * Carga los datos del anuncio cuando se está editando.
 */
const loadAnuncio = async () => {
  if (!isEditMode.value) {
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_URL}/api/anuncios/${route.params.id}/`, {
      headers: {
        ...getAuthHeaders(),
      },
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'No se pudo cargar el anuncio.')
    }

    form.value.titulo = data.titulo || ''
    form.value.descripcion = data.descripcion || ''
    form.value.precio_mes = data.precio_mes || ''
    form.value.localizacion = data.localizacion || ''
    form.value.tipo_vivienda = data.tipo_vivienda || 'habitacion'
    form.value.duracion_min_meses = data.duracion_min_meses || 3
    form.value.duracion_max_meses = data.duracion_max_meses || 6
    form.value.wifi = Boolean(data.wifi)
    form.value.terraza = Boolean(data.terraza)
    form.value.garaje = Boolean(data.garaje)

    existingImages.value = data.imagenes || []
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

/**
 * Construye el FormData que se enviará al backend.
 */
const buildPayload = () => {
  const payload = new FormData()

  payload.append('titulo', form.value.titulo.trim())
  payload.append('descripcion', form.value.descripcion.trim())
  payload.append('precio_mes', form.value.precio_mes)
  payload.append('localizacion', form.value.localizacion.trim())
  payload.append('tipo_vivienda', form.value.tipo_vivienda)
  payload.append('duracion_min_meses', form.value.duracion_min_meses)
  payload.append('duracion_max_meses', form.value.duracion_max_meses)
  payload.append('wifi', form.value.wifi ? 'true' : 'false')
  payload.append('terraza', form.value.terraza ? 'true' : 'false')
  payload.append('garaje', form.value.garaje ? 'true' : 'false')

  form.value.imagenes.forEach((file) => {
    payload.append('uploaded_images', file)
  })

  return payload
}

/**
 * Valida y envía el formulario.
 */
const submit = async () => {
  if (!canPublish.value) {
    error.value = 'Solo propietarios o administradores pueden guardar anuncios.'
    return
  }

  if (!form.value.titulo.trim() || !form.value.descripcion.trim() || !form.value.precio_mes || !form.value.localizacion.trim()) {
    error.value = 'Completa todos los campos obligatorios.'
    return
  }

  saving.value = true
  error.value = ''
  success.value = ''

  try {
    const url = isEditMode.value
      ? `${API_URL}/api/anuncios/${route.params.id}/`
      : `${API_URL}/api/anuncios/`

    const method = isEditMode.value ? 'PATCH' : 'POST'

    const response = await fetch(url, {
      method,
      headers: {
        ...getAuthHeaders(),
      },
      body: buildPayload(),
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || data.error || JSON.stringify(data) || 'No se pudo guardar el anuncio.')
    }

    success.value = isEditMode.value
      ? 'Anuncio actualizado correctamente.'
      : 'Anuncio creado correctamente. Quedará pendiente de aprobación.'

    router.push({ name: 'anuncio-detalle', params: { id: data.id } })
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadAnuncio()
})
</script>

<template>
  <main class="min-h-screen bg-slate-50 py-10">
    <div class="mx-auto max-w-4xl px-4">
      <div class="mb-8">
        <p class="text-sm font-bold uppercase tracking-wide text-blue-700">
          {{ isEditMode ? 'Editar anuncio' : 'Publicar anuncio' }}
        </p>

        <h1 class="mt-2 text-3xl font-black text-slate-900 md:text-4xl">
          {{ isEditMode ? 'Editar alojamiento' : 'Crear nuevo anuncio' }}
        </h1>

        <p class="mt-3 text-slate-600">
          El teléfono visible en el anuncio será el que tengas configurado en tu cuenta de propietario.
        </p>
      </div>

      <div v-if="loading" class="text-slate-500">
        Cargando anuncio...
      </div>

      <div
        v-else-if="!canPublish"
        class="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700"
      >
        Solo propietarios o administradores pueden crear o editar anuncios.
      </div>

      <form
        v-else
        class="space-y-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm md:p-8"
        @submit.prevent="submit"
      >
        <div
          v-if="error"
          class="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"
        >
          {{ error }}
        </div>

        <div
          v-if="success"
          class="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700"
        >
          {{ success }}
        </div>

        <div class="grid gap-5 md:grid-cols-2">
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-bold text-slate-700">
              Título *
            </label>

            <input
              v-model="form.titulo"
              type="text"
              class="w-full rounded-lg border border-slate-300 px-4 py-3"
              required
            >
          </div>

          <div>
            <label class="mb-2 block text-sm font-bold text-slate-700">
              Precio mensual *
            </label>

            <input
              v-model="form.precio_mes"
              type="number"
              min="1"
              step="0.01"
              class="w-full rounded-lg border border-slate-300 px-4 py-3"
              required
            >
          </div>

          <div>
            <label class="mb-2 block text-sm font-bold text-slate-700">
              Ubicación *
            </label>

            <input
              v-model="form.localizacion"
              type="text"
              class="w-full rounded-lg border border-slate-300 px-4 py-3"
              required
            >
          </div>

          <div>
            <label class="mb-2 block text-sm font-bold text-slate-700">
              Tipo de vivienda *
            </label>

            <select
              v-model="form.tipo_vivienda"
              class="w-full rounded-lg border border-slate-300 px-4 py-3"
            >
              <option value="habitacion">Habitación</option>
              <option value="piso_completo">Piso completo</option>
              <option value="estudio">Estudio</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="mb-2 block text-sm font-bold text-slate-700">
                Mín. meses
              </label>

              <input
                v-model="form.duracion_min_meses"
                type="number"
                min="1"
                class="w-full rounded-lg border border-slate-300 px-4 py-3"
              >
            </div>

            <div>
              <label class="mb-2 block text-sm font-bold text-slate-700">
                Máx. meses
              </label>

              <input
                v-model="form.duracion_max_meses"
                type="number"
                min="1"
                class="w-full rounded-lg border border-slate-300 px-4 py-3"
              >
            </div>
          </div>

          <div class="md:col-span-2">
            <label class="mb-2 block text-sm font-bold text-slate-700">
              Descripción *
            </label>

            <textarea
              v-model="form.descripcion"
              rows="5"
              class="w-full rounded-lg border border-slate-300 px-4 py-3"
              required
            ></textarea>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 p-5">
          <h2 class="mb-3 font-bold text-slate-900">
            Servicios
          </h2>

          <div class="flex flex-wrap gap-4">
            <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input v-model="form.wifi" type="checkbox">
              WiFi
            </label>

            <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input v-model="form.terraza" type="checkbox">
              Terraza
            </label>

            <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input v-model="form.garaje" type="checkbox">
              Garaje
            </label>
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 p-5">
          <h2 class="mb-2 font-bold text-slate-900">
            Imágenes
          </h2>

          <p class="mb-4 text-sm text-slate-500">
            Si seleccionas imágenes nuevas al editar, se enviarán como nueva galería.
          </p>

          <div
            v-if="existingImages.length && !imagePreviews.length"
            class="mb-5"
          >
            <p class="mb-3 text-sm font-bold text-slate-700">
              Imágenes actuales
            </p>

            <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
              <img
                v-for="image in existingImages"
                :key="image.id"
                :src="getImage(image)"
                alt="Imagen actual"
                class="aspect-video rounded-lg border border-slate-200 object-cover"
              >
            </div>
          </div>

          <input
            type="file"
            multiple
            accept="image/*"
            class="block w-full text-sm text-slate-600"
            @change="handleImages"
          >

          <div
            v-if="imagePreviews.length"
            class="mt-5 grid grid-cols-2 gap-3 md:grid-cols-4"
          >
            <img
              v-for="preview in imagePreviews"
              :key="preview"
              :src="preview"
              alt="Vista previa"
              class="aspect-video rounded-lg border border-slate-200 object-cover"
            >
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <router-link
            to="/anuncios"
            class="rounded-lg bg-slate-100 px-6 py-3 font-bold text-slate-700"
          >
            Cancelar
          </router-link>

          <button
            type="submit"
            class="rounded-lg bg-slate-900 px-6 py-3 font-bold text-white disabled:opacity-60"
            :disabled="saving"
          >
            {{ saving ? 'Guardando...' : isEditMode ? 'Guardar cambios' : 'Publicar anuncio' }}
          </button>
        </div>
      </form>
    </div>
  </main>
</template>