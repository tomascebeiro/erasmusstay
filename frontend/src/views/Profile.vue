<script setup>
import { onMounted, ref } from 'vue'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const { user, getAuthHeaders, updateLocalUser, restoreSession } = useAuth()

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  username: '',
  email: '',
  rol: '',
  telefono: '',
})

const loadProfile = async () => {
  loading.value = true
  error.value = ''

  try {
    await restoreSession()

    form.value.username = user.value?.username || ''
    form.value.email = user.value?.email || ''
    form.value.rol = user.value?.rol || ''
    form.value.telefono = user.value?.telefono || ''
  } catch (err) {
    error.value = 'No se pudo cargar el perfil.'
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await fetch(`${API_URL}/api/me/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        email: form.value.email,
        telefono: form.value.telefono,
      }),
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || 'No se pudo actualizar el perfil.')
    }

    updateLocalUser(data)
    success.value = 'Perfil actualizado correctamente.'
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<template>
  <main class="bg-slate-50 min-h-screen py-10">
    <div class="max-w-3xl mx-auto px-4">
      <div class="mb-8">
        <p class="text-sm font-bold text-blue-700 uppercase tracking-wide">Mi cuenta</p>
        <h1 class="text-3xl md:text-4xl font-black text-slate-900 mt-2">
          Perfil de usuario
        </h1>
        <p class="text-slate-600 mt-3">
          Actualiza tus datos de contacto. Si eres propietario, este teléfono será el que se muestre en tus anuncios.
        </p>
      </div>

      <div v-if="loading" class="text-slate-500">
        Cargando perfil...
      </div>

      <form v-else @submit.prevent="saveProfile" class="bg-white border border-slate-200 rounded-xl p-6 md:p-8 space-y-6">
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
          {{ error }}
        </div>

        <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 rounded-lg p-4 text-sm">
          {{ success }}
        </div>

        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Usuario</label>
          <input v-model="form.username" disabled class="w-full border border-slate-200 bg-slate-100 rounded-lg px-4 py-3 text-slate-500">
        </div>

        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Rol</label>
          <input v-model="form.rol" disabled class="w-full border border-slate-200 bg-slate-100 rounded-lg px-4 py-3 text-slate-500">
        </div>

        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Email</label>
          <input v-model="form.email" type="email" class="w-full border border-slate-300 rounded-lg px-4 py-3">
        </div>

        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Teléfono</label>
          <input v-model="form.telefono" type="tel" class="w-full border border-slate-300 rounded-lg px-4 py-3" placeholder="+356 9999 9999">
          <p class="text-sm text-slate-500 mt-2">
            Este teléfono se mostrará automáticamente en tus anuncios si tienes rol de propietario.
          </p>
        </div>

        <div class="flex justify-end">
          <button :disabled="saving" class="bg-slate-900 text-white font-bold px-6 py-3 rounded-lg disabled:opacity-60">
            {{ saving ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </form>
    </div>
  </main>
</template>