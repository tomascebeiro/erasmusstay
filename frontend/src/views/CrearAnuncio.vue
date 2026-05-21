<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'erasmusstay-production.up.railway.app'

const router = useRouter()
const { getAuthHeaders, user } = useAuth()

const loading = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  titulo: '',
  descripcion: '',
  precio_mes: '',
  localizacion: '',
  tipo_vivienda: '',
  duracion_min_meses: '',
  duracion_max_meses: '',
  telefono_contacto: '',
  email_contacto: user.value?.email || '',
  wifi: false,
  terraza: false,
  garaje: false,
})

const handleSubmit = async () => {
  error.value = ''
  success.value = ''

  if (!form.value.titulo || !form.value.descripcion || !form.value.precio_mes || !form.value.localizacion) {
    error.value = 'Please fill in all required fields (Title, Description, Price, and Location).'
    return
  }

  loading.value = true

  try {
    // We use pure JSON because your Django AnuncioSerializer expects JSON, not FormData
    const payload = {
      titulo: form.value.titulo,
      descripcion: form.value.descripcion,
      precio_mes: Number(form.value.precio_mes),
      localizacion: form.value.localizacion,
      tipo_vivienda: form.value.tipo_vivienda || 'habitacion',
      duracion_min_meses: form.value.duracion_min_meses ? Number(form.value.duracion_min_meses) : 3,
      duracion_max_meses: form.value.duracion_max_meses ? Number(form.value.duracion_max_meses) : 6,
      telefono_contacto: form.value.telefono_contacto,
      email_contacto: form.value.email_contacto,
      wifi: form.value.wifi,
      terraza: form.value.terraza,
      garaje: form.value.garaje
    }

    const response = await fetch(`${API_URL}/api/anuncios/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(payload),
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
        data.titulo?.[0] ||
        'Server error. Could not create the listing.'
      )
    }

    success.value = 'Listing submitted successfully. It is now pending administrator approval.'

    setTimeout(() => {
      router.push(`/`)
    }, 2000)
    
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="max-w-3xl mx-auto px-4 py-12">
    
    <div class="mb-8">
      <button @click="router.back()" class="text-sm font-medium text-slate-500 hover:text-slate-900 mb-6 flex items-center gap-2 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
        Back to Listings
      </button>

      <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">Create New Listing</h1>
      <p class="text-sm text-slate-500 mt-2">Fill in the details below to list your property on ErasmusStay.</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-10">
      
      <section>
        <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 border-b border-slate-200 pb-2">Basic Information</h2>
        <div class="space-y-5">
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Title *</label>
            <input v-model="form.titulo" type="text" placeholder="e.g. Bright Studio in Sliema" required class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Description *</label>
            <textarea v-model="form.descripcion" rows="5" placeholder="Describe the property, neighborhood, rules..." required class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 resize-none"></textarea>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Location *</label>
              <input v-model="form.localizacion" type="text" placeholder="e.g. Sliema, Malta" required class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Property Type</label>
              <select v-model="form.tipo_vivienda" class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 bg-white">
                <option value="habitacion">Single Room</option>
                <option value="piso_completo">Full Flat</option>
                <option value="estudio">Private Studio</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 border-b border-slate-200 pb-2">Pricing & Stay Rules</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Monthly Price (€) *</label>
            <input v-model="form.precio_mes" type="number" min="0" placeholder="e.g. 500" required class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Min Stay (Months)</label>
            <input v-model="form.duracion_min_meses" type="number" min="1" placeholder="e.g. 3" class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Max Stay (Months)</label>
            <input v-model="form.duracion_max_meses" type="number" min="1" placeholder="e.g. 10" class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900" />
          </div>
        </div>
      </section>

      <section>
        <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 border-b border-slate-200 pb-2">Features & Amenities</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <label class="flex items-center gap-3 p-3 border border-slate-200 rounded cursor-pointer hover:bg-slate-50 transition">
            <input v-model="form.wifi" type="checkbox" class="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" />
            <span class="text-sm font-medium text-slate-700">Wifi</span>
          </label>
          <label class="flex items-center gap-3 p-3 border border-slate-200 rounded cursor-pointer hover:bg-slate-50 transition">
            <input v-model="form.terraza" type="checkbox" class="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" />
            <span class="text-sm font-medium text-slate-700">Terrace</span>
          </label>
          <label class="flex items-center gap-3 p-3 border border-slate-200 rounded cursor-pointer hover:bg-slate-50 transition">
            <input v-model="form.garaje" type="checkbox" class="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" />
            <span class="text-sm font-medium text-slate-700">Garage</span>
          </label>
        </div>
      </section>

      <section>
        <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 border-b border-slate-200 pb-2">Contact Details</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Contact Phone</label>
            <input v-model="form.telefono_contacto" type="text" placeholder="+356 XX XXXXXX" class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Contact Email</label>
            <input v-model="form.email_contacto" type="email" placeholder="host@example.com" class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900" />
          </div>
        </div>
      </section>

      <section>
        <h2 class="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 border-b border-slate-200 pb-2">Property Photos</h2>
        <div class="border border-slate-200 bg-slate-50 rounded-lg p-6 text-center">
          <svg class="w-8 h-8 text-slate-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          <p class="text-sm font-medium text-slate-600 mb-1">Image uploads are managed externally.</p>
          <p class="text-xs text-slate-500">The current system version handles images via URL parameters. Please contact the administrator to attach URLs to your listing.</p>
        </div>
      </section>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 rounded p-4 text-sm">{{ error }}</div>
      <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 rounded p-4 text-sm font-medium">{{ success }}</div>

      <div class="pt-6 border-t border-slate-200">
        <button type="submit" class="w-full bg-slate-900 text-white font-bold py-4 rounded hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition" :disabled="loading">
          {{ loading ? 'Uploading Listing...' : 'Publish Listing' }}
        </button>
      </div>

    </form>
  </main>
</template>