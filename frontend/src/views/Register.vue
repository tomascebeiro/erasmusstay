<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

/**
 * Vista de registro.
 *
 * Responsabilidades:
 * - Crear una nueva cuenta de estudiante o propietario.
 * - Validar datos básicos antes de enviar.
 * - Enviar los datos al endpoint de registro del backend.
 * - Redirigir al login tras crear la cuenta.
 *
 * Nota:
 * Los valores internos del rol se mantienen como los espera el backend:
 * - estudiante
 * - propietario
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const router = useRouter()

const username = ref('')
const email = ref('')
const telefono = ref('')
const password = ref('')
const password2 = ref('')
const rol = ref('estudiante')

const loading = ref(false)
const error = ref('')
const success = ref('')

/**
 * Valida el formulario y registra la cuenta en el backend.
 */
const handleSubmit = async () => {
  error.value = ''
  success.value = ''

  if (!username.value || !email.value || !password.value || !password2.value) {
    error.value = 'Completa todos los campos obligatorios.'
    return
  }

  if (password.value !== password2.value) {
    error.value = 'Las contraseñas introducidas no coinciden.'
    return
  }

  if (password.value.length < 8) {
    error.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }

  loading.value = true

  try {
    const response = await fetch(`${API_URL}/api/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        telefono: telefono.value,
        password: password.value,
        rol: rol.value,
      }),
    })

    let data = {}

    try {
      data = await response.json()
    } catch {
      data = {}
    }

    if (!response.ok) {
      throw new Error(
        data.error ||
        data.detail ||
        data.username?.[0] ||
        data.email?.[0] ||
        data.password?.[0] ||
        'No se pudo completar el registro.'
      )
    }

    success.value = 'Cuenta creada correctamente. Redirigiendo al inicio de sesión...'

    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    error.value = err.message || 'Se produjo un error al crear la cuenta.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-slate-50 px-4 py-12">
    <div class="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:p-8">
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-extrabold tracking-tight text-slate-900">
          Crear cuenta
        </h1>

        <p class="mt-2 text-sm text-slate-500">
          Regístrate en ErasmusStay para buscar alojamientos o publicar tus propiedades.
        </p>
      </div>

      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div>
          <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
            Usuario
          </label>

          <input
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="Ej. estudiante123"
            required
            class="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-700 focus:border-slate-900 focus:outline-none disabled:opacity-50"
            :disabled="loading"
          >
        </div>

        <div>
          <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
            Correo electrónico
          </label>

          <input
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="nombre@example.com"
            required
            class="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-700 focus:border-slate-900 focus:outline-none disabled:opacity-50"
            :disabled="loading"
          >
        </div>

        <div>
          <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
            Teléfono
          </label>

          <input
            v-model="telefono"
            type="tel"
            autocomplete="tel"
            placeholder="+356 9999 9999"
            class="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-700 focus:border-slate-900 focus:outline-none disabled:opacity-50"
            :disabled="loading"
          >

          <p class="mt-1 text-xs text-slate-400">
            Si eres propietario, este teléfono será el que se muestre en tus anuncios.
          </p>
        </div>

        <div>
          <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
            Tipo de cuenta
          </label>

          <select
            v-model="rol"
            required
            class="w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 focus:border-slate-900 focus:outline-none disabled:opacity-50"
            :disabled="loading"
          >
            <option value="estudiante">
              Estudiante Erasmus - busco alojamiento
            </option>

            <option value="propietario">
              Propietario - quiero publicar alojamientos
            </option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
            Contraseña
          </label>

          <input
            v-model="password"
            type="password"
            autocomplete="new-password"
            placeholder="••••••••"
            required
            class="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-700 focus:border-slate-900 focus:outline-none disabled:opacity-50"
            :disabled="loading"
          >
        </div>

        <div>
          <label class="mb-2 block text-xs font-semibold uppercase text-slate-500">
            Confirmar contraseña
          </label>

          <input
            v-model="password2"
            type="password"
            autocomplete="new-password"
            placeholder="••••••••"
            required
            class="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-700 focus:border-slate-900 focus:outline-none disabled:opacity-50"
            :disabled="loading"
          >
        </div>

        <div
          v-if="error"
          class="rounded border border-red-200 bg-red-50 p-3 text-xs text-red-600"
        >
          {{ error }}
        </div>

        <div
          v-if="success"
          class="rounded border border-green-200 bg-green-50 p-3 text-xs font-medium text-green-700"
        >
          {{ success }}
        </div>

        <button
          type="submit"
          class="mt-2 w-full rounded bg-slate-900 py-2.5 text-sm font-bold text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="loading"
        >
          {{ loading ? 'Creando cuenta...' : 'Registrarme' }}
        </button>
      </form>

      <div class="mt-6 flex flex-col gap-2 border-t border-slate-200 pt-6 text-center">
        <p class="text-sm text-slate-500">
          ¿Ya tienes una cuenta?

          <router-link
            to="/login"
            class="ml-1 font-bold text-blue-600 transition-colors hover:text-blue-700"
          >
            Inicia sesión aquí
          </router-link>
        </p>
      </div>
    </div>
  </main>
</template>