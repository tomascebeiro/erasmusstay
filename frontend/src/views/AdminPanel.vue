<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuth } from '../composables/useAuth'

/**
 * Panel de administración principal.
 *
 * Permite al administrador:
 * - revisar, aprobar, desaprobar, editar y eliminar anuncios;
 * - activar o bloquear usuarios;
 * - moderar comentarios y valoraciones;
 * - revisar solicitudes de contacto.
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const { getAuthHeaders } = useAuth()

const pestañaActiva = ref('anuncios')
const filtroEstadoAnuncios = ref('todos')

const cargando = ref(false)
const error = ref('')
const mensajeExito = ref('')

const anuncios = ref([])
const usuarios = ref([])
const comentarios = ref([])
const solicitudes = ref([])

/**
 * DRF puede devolver una lista directa o una respuesta paginada.
 * Esta función normaliza ambos casos.
 */
const normalizarLista = (data) => {
  return Array.isArray(data) ? data : (data.results || [])
}

/**
 * Realiza una petición autenticada al backend.
 */
const peticionAutenticada = async (url, options = {}) => {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...getAuthHeaders(),
    },
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || data.error || 'No se pudo completar la operación.')
  }

  return data
}

/**
 * Carga todos los datos necesarios para el panel.
 */
const cargarDatos = async () => {
  cargando.value = true
  error.value = ''

  try {
    const [
      anunciosData,
      usuariosData,
      comentariosData,
      solicitudesData,
    ] = await Promise.all([
      peticionAutenticada(`${API_URL}/api/anuncios/`),
      peticionAutenticada(`${API_URL}/api/admin/usuarios/`),
      peticionAutenticada(`${API_URL}/api/valoraciones/`),
      peticionAutenticada(`${API_URL}/api/solicitudes/`),
    ])

    anuncios.value = normalizarLista(anunciosData)
    usuarios.value = normalizarLista(usuariosData)
    comentarios.value = normalizarLista(comentariosData)
    solicitudes.value = normalizarLista(solicitudesData)
  } catch (err) {
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

/**
 * Filtra los anuncios según el estado seleccionado.
 */
const anunciosFiltrados = computed(() => {
  if (filtroEstadoAnuncios.value === 'pendientes') {
    return anuncios.value.filter((anuncio) => !anuncio.aprobado)
  }

  if (filtroEstadoAnuncios.value === 'aprobados') {
    return anuncios.value.filter((anuncio) => anuncio.aprobado)
  }

  return anuncios.value
})

/**
 * Devuelve el número de comentarios pendientes de moderación.
 */
const comentariosPendientes = computed(() => {
  return comentarios.value.filter((comentario) => !comentario.aprobado).length
})

/**
 * Devuelve el número de anuncios pendientes de aprobación.
 */
const anunciosPendientes = computed(() => {
  return anuncios.value.filter((anuncio) => !anuncio.aprobado).length
})

/**
 * Actualiza el estado de aprobación de un anuncio.
 */
const cambiarEstadoAnuncio = async (anuncio, aprobado) => {
  error.value = ''
  mensajeExito.value = ''

  try {
    await peticionAutenticada(`${API_URL}/api/anuncios/${anuncio.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        aprobado,
      }),
    })

    mensajeExito.value = aprobado
      ? `El anuncio "${anuncio.titulo}" ha sido aprobado correctamente.`
      : `El anuncio "${anuncio.titulo}" ha vuelto a quedar pendiente.`

    await cargarDatos()
  } catch (err) {
    error.value = err.message
  }
}

/**
 * Elimina un anuncio.
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
    await cargarDatos()
  } catch (err) {
    error.value = err.message
  }
}

/**
 * Activa o bloquea una cuenta de usuario.
 */
const cambiarEstadoUsuario = async (usuario) => {
  error.value = ''
  mensajeExito.value = ''

  try {
    const data = await peticionAutenticada(`${API_URL}/api/admin/usuarios/${usuario.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        activo: !usuario.activo,
      }),
    })

    mensajeExito.value = data.activo
      ? `El usuario "${usuario.username}" ha sido activado.`
      : `El usuario "${usuario.username}" ha sido bloqueado.`

    await cargarDatos()
  } catch (err) {
    error.value = err.message
  }
}

/**
 * Aprueba u oculta un comentario.
 */
const moderarComentario = async (comentario, aprobado) => {
  error.value = ''
  mensajeExito.value = ''

  try {
    await peticionAutenticada(`${API_URL}/api/valoraciones/${comentario.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        aprobado,
      }),
    })

    mensajeExito.value = aprobado
      ? 'Comentario aprobado correctamente.'
      : 'Comentario ocultado correctamente.'

    await cargarDatos()
  } catch (err) {
    error.value = err.message
  }
}

/**
 * Elimina definitivamente un comentario.
 */
const eliminarComentario = async (comentario) => {
  if (!confirm('¿Seguro que quieres eliminar este comentario?')) {
    return
  }

  error.value = ''
  mensajeExito.value = ''

  try {
    const response = await fetch(`${API_URL}/api/valoraciones/${comentario.id}/`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeaders(),
      },
    })

    if (!response.ok && response.status !== 204) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.detail || data.error || 'No se pudo eliminar el comentario.')
    }

    mensajeExito.value = 'Comentario eliminado correctamente.'
    await cargarDatos()
  } catch (err) {
    error.value = err.message
  }
}

/**
 * Cambia el estado de una solicitud de contacto.
 */
const actualizarSolicitud = async (solicitud, estado) => {
  error.value = ''
  mensajeExito.value = ''

  try {
    await peticionAutenticada(`${API_URL}/api/solicitudes/${solicitud.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        estado,
      }),
    })

    mensajeExito.value = 'Solicitud actualizada correctamente.'
    await cargarDatos()
  } catch (err) {
    error.value = err.message
  }
}

onMounted(() => {
  cargarDatos()
})
</script>

<template>
  <main class="min-h-screen bg-slate-50 py-10">
    <div class="mx-auto max-w-7xl px-4">
      <!-- Cabecera -->
      <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-sm font-bold uppercase tracking-wide text-blue-700">
            Administración
          </p>

          <h1 class="mt-2 text-3xl font-black text-slate-900 md:text-4xl">
            Panel de control
          </h1>

          <p class="mt-3 text-slate-600">
            Gestiona anuncios, usuarios, comentarios y solicitudes de contacto.
          </p>
        </div>

        <button
          type="button"
          class="rounded bg-slate-900 px-5 py-3 font-bold text-white hover:bg-slate-700"
          @click="cargarDatos"
        >
          Recargar datos
        </button>
      </div>

      <!-- Mensajes -->
      <div
        v-if="error"
        class="mb-6 rounded border border-red-200 bg-red-50 p-4 text-red-700"
      >
        {{ error }}
      </div>

      <div
        v-if="mensajeExito"
        class="mb-6 rounded border border-green-200 bg-green-50 p-4 text-green-700"
      >
        {{ mensajeExito }}
      </div>

      <!-- Resumen -->
      <div class="mb-8 grid gap-4 md:grid-cols-4">
        <div class="rounded border border-slate-200 bg-white p-5">
          <p class="text-xs font-bold uppercase tracking-wide text-slate-500">
            Anuncios
          </p>
          <p class="mt-2 text-3xl font-black text-slate-900">
            {{ anuncios.length }}
          </p>
        </div>

        <div class="rounded border border-slate-200 bg-white p-5">
          <p class="text-xs font-bold uppercase tracking-wide text-slate-500">
            Pendientes
          </p>
          <p class="mt-2 text-3xl font-black text-yellow-600">
            {{ anunciosPendientes }}
          </p>
        </div>

        <div class="rounded border border-slate-200 bg-white p-5">
          <p class="text-xs font-bold uppercase tracking-wide text-slate-500">
            Usuarios
          </p>
          <p class="mt-2 text-3xl font-black text-slate-900">
            {{ usuarios.length }}
          </p>
        </div>

        <div class="rounded border border-slate-200 bg-white p-5">
          <p class="text-xs font-bold uppercase tracking-wide text-slate-500">
            Comentarios pendientes
          </p>
          <p class="mt-2 text-3xl font-black text-blue-700">
            {{ comentariosPendientes }}
          </p>
        </div>
      </div>

      <!-- Pestañas -->
      <div class="mb-6 flex flex-wrap gap-2">
        <button
          type="button"
          class="rounded border border-slate-200 px-4 py-2 text-sm font-bold"
          :class="pestañaActiva === 'anuncios' ? 'bg-slate-900 text-white' : 'bg-white text-slate-700 hover:bg-slate-100'"
          @click="pestañaActiva = 'anuncios'"
        >
          Anuncios
        </button>

        <button
          type="button"
          class="rounded border border-slate-200 px-4 py-2 text-sm font-bold"
          :class="pestañaActiva === 'usuarios' ? 'bg-slate-900 text-white' : 'bg-white text-slate-700 hover:bg-slate-100'"
          @click="pestañaActiva = 'usuarios'"
        >
          Usuarios
        </button>

        <button
          type="button"
          class="rounded border border-slate-200 px-4 py-2 text-sm font-bold"
          :class="pestañaActiva === 'comentarios' ? 'bg-slate-900 text-white' : 'bg-white text-slate-700 hover:bg-slate-100'"
          @click="pestañaActiva = 'comentarios'"
        >
          Comentarios
          <span
            v-if="comentariosPendientes"
            class="ml-2 rounded bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700"
          >
            {{ comentariosPendientes }}
          </span>
        </button>

        <button
          type="button"
          class="rounded border border-slate-200 px-4 py-2 text-sm font-bold"
          :class="pestañaActiva === 'solicitudes' ? 'bg-slate-900 text-white' : 'bg-white text-slate-700 hover:bg-slate-100'"
          @click="pestañaActiva = 'solicitudes'"
        >
          Solicitudes
        </button>
      </div>

      <div v-if="cargando" class="text-slate-500">
        Cargando información del panel...
      </div>

      <!-- Anuncios -->
      <section
        v-else-if="pestañaActiva === 'anuncios'"
        class="rounded border border-slate-200 bg-white"
      >
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-5">
          <h2 class="text-xl font-black text-slate-900">
            Gestión de anuncios
          </h2>

          <div class="flex gap-2">
            <button
              type="button"
              class="rounded px-3 py-2 text-xs font-bold"
              :class="filtroEstadoAnuncios === 'todos' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700'"
              @click="filtroEstadoAnuncios = 'todos'"
            >
              Todos
            </button>

            <button
              type="button"
              class="rounded px-3 py-2 text-xs font-bold"
              :class="filtroEstadoAnuncios === 'pendientes' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700'"
              @click="filtroEstadoAnuncios = 'pendientes'"
            >
              Pendientes
            </button>

            <button
              type="button"
              class="rounded px-3 py-2 text-xs font-bold"
              :class="filtroEstadoAnuncios === 'aprobados' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700'"
              @click="filtroEstadoAnuncios = 'aprobados'"
            >
              Aprobados
            </button>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th class="px-5 py-4">Anuncio</th>
                <th class="px-5 py-4">Propietario</th>
                <th class="px-5 py-4">Estado</th>
                <th class="px-5 py-4 text-right">Acciones</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="anuncio in anunciosFiltrados"
                :key="anuncio.id"
                class="hover:bg-slate-50"
              >
                <td class="px-5 py-4">
                  <p class="font-bold text-slate-900">
                    {{ anuncio.titulo }}
                  </p>
                  <p class="mt-1 text-xs text-slate-500">
                    {{ anuncio.localizacion }} · {{ anuncio.precio_mes }} €/mes
                  </p>
                </td>

                <td class="px-5 py-4">
                  {{ anuncio.propietario_nombre || 'Sin propietario' }}
                </td>

                <td class="px-5 py-4">
                  <span
                    class="rounded px-2 py-1 text-[10px] font-black uppercase tracking-wide"
                    :class="anuncio.aprobado ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                  >
                    {{ anuncio.aprobado ? 'Aprobado' : 'Pendiente' }}
                  </span>
                </td>

                <td class="px-5 py-4 text-right">
                  <div class="flex flex-wrap justify-end gap-3">
                    <router-link
                      :to="`/anuncio/${anuncio.id}`"
                      class="text-xs font-bold text-blue-700 hover:text-blue-900"
                    >
                      Ver
                    </router-link>

                    <router-link
                      :to="{ name: 'editar-anuncio', params: { id: anuncio.id } }"
                      class="text-xs font-bold text-slate-700 hover:text-slate-900"
                    >
                      Editar
                    </router-link>

                    <button
                      v-if="!anuncio.aprobado"
                      type="button"
                      class="text-xs font-bold text-green-700 hover:text-green-900"
                      @click="cambiarEstadoAnuncio(anuncio, true)"
                    >
                      Aprobar
                    </button>

                    <button
                      v-else
                      type="button"
                      class="text-xs font-bold text-yellow-700 hover:text-yellow-900"
                      @click="cambiarEstadoAnuncio(anuncio, false)"
                    >
                      Desaprobar
                    </button>

                    <button
                      type="button"
                      class="text-xs font-bold text-red-700 hover:text-red-900"
                      @click="eliminarAnuncio(anuncio)"
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="anunciosFiltrados.length === 0">
                <td colspan="4" class="px-5 py-10 text-center text-slate-500">
                  No hay anuncios para este filtro.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Usuarios -->
      <section
        v-else-if="pestañaActiva === 'usuarios'"
        class="rounded border border-slate-200 bg-white"
      >
        <div class="border-b border-slate-200 p-5">
          <h2 class="text-xl font-black text-slate-900">
            Gestión de usuarios
          </h2>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th class="px-5 py-4">Usuario</th>
                <th class="px-5 py-4">Rol</th>
                <th class="px-5 py-4">Teléfono</th>
                <th class="px-5 py-4">Estado</th>
                <th class="px-5 py-4 text-right">Acciones</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="usuario in usuarios"
                :key="usuario.id"
                class="hover:bg-slate-50"
              >
                <td class="px-5 py-4">
                  <p class="font-bold text-slate-900">
                    {{ usuario.username }}
                  </p>
                  <p class="mt-1 text-xs text-slate-500">
                    {{ usuario.email }}
                  </p>
                </td>

                <td class="px-5 py-4 capitalize">
                  {{ usuario.rol }}
                </td>

                <td class="px-5 py-4">
                  {{ usuario.telefono || 'No indicado' }}
                </td>

                <td class="px-5 py-4">
                  <span
                    class="rounded px-2 py-1 text-[10px] font-black uppercase tracking-wide"
                    :class="usuario.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
                  >
                    {{ usuario.activo ? 'Activo' : 'Bloqueado' }}
                  </span>
                </td>

                <td class="px-5 py-4 text-right">
                  <button
                    type="button"
                    class="text-xs font-bold"
                    :class="usuario.activo ? 'text-red-700 hover:text-red-900' : 'text-green-700 hover:text-green-900'"
                    @click="cambiarEstadoUsuario(usuario)"
                  >
                    {{ usuario.activo ? 'Bloquear' : 'Activar' }}
                  </button>
                </td>
              </tr>

              <tr v-if="usuarios.length === 0">
                <td colspan="5" class="px-5 py-10 text-center text-slate-500">
                  No hay usuarios registrados.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Comentarios -->
      <section
        v-else-if="pestañaActiva === 'comentarios'"
        class="rounded border border-slate-200 bg-white"
      >
        <div class="border-b border-slate-200 p-5">
          <h2 class="text-xl font-black text-slate-900">
            Moderación de comentarios
          </h2>

          <p class="mt-1 text-sm text-slate-500">
            Los comentarios nuevos quedan pendientes hasta que un administrador los aprueba.
          </p>
        </div>

        <div class="divide-y divide-slate-100">
          <article
            v-for="comentario in comentarios"
            :key="comentario.id"
            class="p-5"
          >
            <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div>
                <div class="flex flex-wrap items-center gap-3">
                  <p class="font-bold text-slate-900">
                    {{ comentario.usuario_nombre || 'Usuario' }}
                  </p>

                  <span class="text-sm font-bold text-yellow-600">
                    {{ comentario.puntuacion }}/5
                  </span>

                  <span
                    class="rounded px-2 py-1 text-[10px] font-black uppercase tracking-wide"
                    :class="comentario.aprobado ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                  >
                    {{ comentario.aprobado ? 'Aprobado' : 'Pendiente' }}
                  </span>
                </div>

                <p class="mt-2 text-sm text-slate-500">
                  Anuncio ID: {{ comentario.anuncio }}
                </p>

                <p class="mt-3 leading-6 text-slate-700">
                  {{ comentario.comentario }}
                </p>
              </div>

              <div class="flex flex-wrap gap-3">
                <button
                  v-if="!comentario.aprobado"
                  type="button"
                  class="rounded bg-green-50 px-3 py-2 text-xs font-bold text-green-700 hover:bg-green-100"
                  @click="moderarComentario(comentario, true)"
                >
                  Aprobar
                </button>

                <button
                  v-else
                  type="button"
                  class="rounded bg-yellow-50 px-3 py-2 text-xs font-bold text-yellow-700 hover:bg-yellow-100"
                  @click="moderarComentario(comentario, false)"
                >
                  Ocultar
                </button>

                <button
                  type="button"
                  class="rounded bg-red-50 px-3 py-2 text-xs font-bold text-red-700 hover:bg-red-100"
                  @click="eliminarComentario(comentario)"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </article>

          <div
            v-if="comentarios.length === 0"
            class="p-10 text-center text-slate-500"
          >
            No hay comentarios registrados.
          </div>
        </div>
      </section>

      <!-- Solicitudes -->
      <section
        v-else-if="pestañaActiva === 'solicitudes'"
        class="rounded border border-slate-200 bg-white"
      >
        <div class="border-b border-slate-200 p-5">
          <h2 class="text-xl font-black text-slate-900">
            Solicitudes de contacto
          </h2>
        </div>

        <div class="divide-y divide-slate-100">
          <article
            v-for="solicitud in solicitudes"
            :key="solicitud.id"
            class="p-5"
          >
            <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div>
                <h3 class="font-black text-slate-900">
                  {{ solicitud.anuncio_titulo }}
                </h3>

                <p class="mt-1 text-sm text-slate-500">
                  Estudiante: {{ solicitud.estudiante_nombre }}
                </p>

                <p class="mt-1 text-sm text-slate-500">
                  Teléfono del propietario:
                  {{ solicitud.telefono_propietario_snapshot || 'No indicado' }}
                </p>

                <p
                  v-if="solicitud.mensaje"
                  class="mt-3 leading-6 text-slate-700"
                >
                  {{ solicitud.mensaje }}
                </p>
              </div>

              <div class="flex flex-col gap-2 md:items-end">
                <span
                  class="rounded px-2 py-1 text-[10px] font-black uppercase tracking-wide"
                  :class="{
                    'bg-yellow-100 text-yellow-700': solicitud.estado === 'pendiente',
                    'bg-green-100 text-green-700': solicitud.estado === 'respondida',
                    'bg-slate-100 text-slate-700': solicitud.estado === 'cerrada'
                  }"
                >
                  {{ solicitud.estado }}
                </span>

                <div class="flex gap-2">
                  <button
                    type="button"
                    class="rounded bg-green-50 px-3 py-2 text-xs font-bold text-green-700"
                    @click="actualizarSolicitud(solicitud, 'respondida')"
                  >
                    Marcar respondida
                  </button>

                  <button
                    type="button"
                    class="rounded bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700"
                    @click="actualizarSolicitud(solicitud, 'cerrada')"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            </div>
          </article>

          <div
            v-if="solicitudes.length === 0"
            class="p-10 text-center text-slate-500"
          >
            No hay solicitudes registradas.
          </div>
        </div>
      </section>
    </div>
  </main>
</template>