<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'erasmusstay-production.up.railway.app'
const { user, getAuthHeaders, login } = useAuth()

const loading = ref(false)
const error = ref('')
const success = ref('')

// Variables vinculadas al modelo de Django (User + PerfilUsuario)
const profileForm = ref({
  username: '',
  email: '',
  rol: ''
})

const fetchCurrentProfile = async () => {
  try {
    const response = await fetch(`${API_URL}/api/me/`, {
      method: 'GET',
      headers: getAuthHeaders()
    })
    if (response.ok) {
      const data = await response.json()
      profileForm.value.username = data.username || ''
      profileForm.value.email = data.email || ''
      profileForm.value.rol = data.rol || data.perfil?.rol || user.value?.rol || 'User'
    }
  } catch (err) {
    console.error("Failed to load user profile metadata:", err)
  }
}

const handleUpdateProfile = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const response = await fetch(`${API_URL}/api/me/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({
        email: profileForm.value.email
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.email?.[0] || 'Could not update profile records.')
    }

    success.value = 'Your personal settings have been saved successfully.'
    
    // Actualizamos la sesión en el cliente (localStorage)
    login(localStorage.getItem('token'), { ...user.value, email: profileForm.value.email })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (user.value) {
    profileForm.value.username = user.value.username || ''
    profileForm.value.email = user.value.email || ''
    profileForm.value.rol = user.value.rol || ''
  }
  fetchCurrentProfile()
})
</script>

<template>
  <main class="max-w-xl mx-auto px-4 py-12">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">Account Settings</h1>
      <p class="text-sm text-slate-500 mt-2">Manage your core user credentials and profile records below.</p>
    </div>

    <form @submit.prevent="handleUpdateProfile" class="bg-white border border-slate-200 rounded-lg p-6 space-y-6 shadow-sm">
      
      <div>
        <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Username</label>
        <input 
          v-model="profileForm.username" 
          type="text" 
          disabled 
          class="w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-sm text-slate-400 cursor-not-allowed outline-none" 
        />
        <p class="text-[11px] text-slate-400 mt-1">User identifiers cannot be modified once set during registration.</p>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Assigned Profile Type</label>
        <div class="w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-sm text-slate-500 font-medium capitalize select-none">
          {{ profileForm.rol || 'Student' }}
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Email Address *</label>
        <input 
          v-model="profileForm.email" 
          type="email" 
          required
          :disabled="loading"
          placeholder="name@example.com"
          class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 disabled:opacity-50" 
        />
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 rounded p-3 text-xs">
        {{ error }}
      </div>

      <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 rounded p-3 text-xs font-medium">
        {{ success }}
      </div>

      <div class="pt-4 border-t border-slate-100 text-right">
        <button 
          type="submit" 
          :disabled="loading"
          class="bg-slate-900 text-white text-sm font-medium px-5 py-2 rounded hover:bg-slate-800 transition disabled:opacity-50"
        >
          {{ loading ? 'Saving Records...' : 'Save Settings' }}
        </button>
      </div>

    </form>
  </main>
</template>