<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'erasmusstay-production.up.railway.app'

const router = useRouter()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''

  if (!username.value || !password.value) {
    error.value = 'Please enter your username and password.'
    return
  }

  loading.value = true

  try {
    const response = await fetch(`${API_URL}/api/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
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
        data.detail ||
        data.error ||
        data.non_field_errors?.[0] ||
        'Invalid login credentials.'
      )
    }

    const token = data.token

    if (!token) {
      throw new Error('Authentication failed while processing the security token.')
    }

    login(token, data.user || {
      id: data.user?.id,
      username: username.value,
      email: data.user?.email || '',
      rol: data.user?.rol || 'estudiante',
    })

    router.push('/')
  } catch (err) {
    error.value = err.message || 'System error during login.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 bg-slate-50">
    <div class="bg-white border border-slate-200 rounded-lg p-6 md:p-8 max-w-md w-full shadow-sm">
      
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">
          Welcome back
        </h1>
        <p class="text-sm text-slate-500 mt-2">
          Sign in to ErasmusStay to manage your accommodations.
        </p>
      </div>

      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div>
          <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">
            Username
          </label>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="Your username"
            required
            class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 disabled:opacity-50"
            :disabled="loading"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">
            Password
          </label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
            class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 disabled:opacity-50"
            :disabled="loading"
          />
        </div>

        <div
          v-if="error"
          class="bg-red-50 border border-red-200 text-red-600 rounded p-3 text-xs"
        >
          {{ error }}
        </div>

        <button
          type="submit"
          class="w-full bg-slate-900 text-white text-sm font-bold py-2.5 rounded hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
          :disabled="loading"
        >
          {{ loading ? 'Verifying credentials...' : 'Sign in' }}
        </button>
      </form>

      <div class="mt-6 pt-6 border-t border-slate-200 flex flex-col gap-2 text-center">
        <p class="text-sm text-slate-500">
          Don't have an account yet? 
          <router-link
            to="/register"
            class="text-blue-600 hover:text-blue-700 font-bold transition-colors ml-1"
          >
            Register here
          </router-link>
        </p>
        
        <router-link
          to="/"
          class="text-sm font-medium text-slate-400 hover:text-slate-600 transition-colors mt-4 block"
        >
          ← Back to listings
        </router-link>
      </div>
    </div>
  </main>
</template>