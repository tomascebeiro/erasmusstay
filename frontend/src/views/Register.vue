<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const API_URL = import.meta.env.VITE_API_URL || 'https://erasmusstay-production.up.railway.app'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')
// We keep the exact backend values ('estudiante', 'propietario') to avoid breaking the DB, 
// but we display them in English in the template.
const rol = ref('estudiante')

const loading = ref(false)
const error = ref('')
const success = ref('')

const handleSubmit = async () => {
  error.value = ''
  success.value = ''

  if (!username.value || !email.value || !password.value || !password2.value) {
    error.value = 'Please fill in all required fields.'
    return
  }

  if (password.value !== password2.value) {
    error.value = 'The passwords entered do not match.'
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
        password: password.value,
        rol: rol.value 
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
        'Error processing registration in the system.'
      )
    }

    success.value = 'Registration successful. Redirecting to login...'

    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    error.value = err.message || 'An error occurred while trying to create the account.'
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
          Create an account
        </h1>
        <p class="text-sm text-slate-500 mt-2">
          Register for ErasmusStay to access housing management.
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
            placeholder="e.g. student123"
            required
            class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 disabled:opacity-50"
            :disabled="loading"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">
            Email address
          </label>
          <input
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="name@example.com"
            required
            class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 disabled:opacity-50"
            :disabled="loading"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">
            Account Type
          </label>
          <select
            v-model="rol"
            required
            class="w-full border border-slate-300 bg-white rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 disabled:opacity-50"
            :disabled="loading"
          >
            <option value="estudiante">Erasmus Student (Looking for housing)</option>
            <option value="propietario">Property Owner (Listing housing)</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">
            Password
          </label>
          <input
            v-model="password"
            type="password"
            autocomplete="new-password"
            placeholder="••••••••"
            required
            class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 disabled:opacity-50"
            :disabled="loading"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">
            Confirm Password
          </label>
          <input
            v-model="password2"
            type="password"
            autocomplete="new-password"
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

        <div
          v-if="success"
          class="bg-green-50 border border-green-200 text-green-700 rounded p-3 text-xs font-medium"
        >
          {{ success }}
        </div>

        <button
          type="submit"
          class="w-full bg-slate-900 text-white text-sm font-bold py-2.5 rounded hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
          :disabled="loading"
        >
          {{ loading ? 'Creating account...' : 'Register' }}
        </button>
      </form>

      <div class="mt-6 pt-6 border-t border-slate-200 flex flex-col gap-2 text-center">
        <p class="text-sm text-slate-500">
          Already have an active account? 
          <router-link
            to="/login"
            class="text-blue-600 hover:text-blue-700 font-bold transition-colors ml-1"
          >
            Log in here
          </router-link>
        </p>
      </div>
    </div>
  </main>
</template>