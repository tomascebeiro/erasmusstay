<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'https://erasmusstay-production.up.railway.app'

const route = useRoute()
const router = useRouter()
const { user, isAuthenticated, getAuthHeaders } = useAuth()

const anuncio = ref(null)
const loading = ref(false)
const error = ref('')

const ratingForm = ref({
  puntuacion: 5,
  comentario: ''
})
const loadingRating = ref(false)
const ratingError = ref('')

const fetchAnuncio = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_URL}/api/anuncios/${route.params.id}/`)

    if (!response.ok) {
      throw new Error('No se pudo recuperar la información detallada del alojamiento.')
    }

    anuncio.value = await response.json()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Lógica de reseñas (Solo estudiantes)
const canReview = computed(() => {
  if (!isAuthenticated.value) return false
  const rolUsuario = (user.value?.rol || '').toLowerCase().trim();
  return rolUsuario === 'estudiante' || (rolUsuario === '' && user.value?.username !== 'admin');
})

const submitRating = async () => {
  if (!ratingForm.value.comentario.trim()) {
    ratingError.value = 'Por favor, escribe un comentario para enviar tu reseña.'
    return
  }

  loadingRating.value = true
  ratingError.value = ''

  try {
    const payload = {
      anuncio: anuncio.value.id,
      usuario: user.value.id,
      puntuacion: Number(ratingForm.value.puntuacion),
      comentario: ratingForm.value.comentario
    }

    const response = await fetch(`${API_URL}/api/valoraciones/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error('Error al guardar la valoración.')

    ratingForm.value.comentario = ''
    ratingForm.value.puntuacion = 5
    await fetchAnuncio()

  } catch (err) {
    ratingError.value = err.message
  } finally {
    loadingRating.value = false
  }
}

onMounted(() => {
  fetchAnuncio()
})
</script>

<template>
  <main class="max-w-7xl mx-auto px-4 py-8 md:py-12">
    <button
      @click="router.back()"
      class="text-sm font-medium text-slate-500 hover:text-slate-900 mb-6 flex items-center gap-2 transition"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
      Back to results
    </button>

    <div v-if="loading" class="py-20 flex justify-center">
      <div class="w-10 h-10 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-600 rounded p-4 text-sm">
      {{ error }}
    </div>

    <div v-else-if="anuncio" class="grid grid-cols-1 lg:grid-cols-3 gap-10">
      
      <div class="lg:col-span-2 space-y-10">
        
        <div class="flex flex-col gap-2">
          <div class="h-64 md:h-[400px] bg-[#e5e7eb] rounded flex items-center justify-center text-slate-400 font-medium border border-slate-200">
            Main Property Image Placeholder
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="h-32 md:h-48 bg-[#e5e7eb] rounded flex items-center justify-center text-slate-400 text-sm font-medium border border-slate-200">Photo 2</div>
            <div class="h-32 md:h-48 bg-[#e5e7eb] rounded flex items-center justify-center text-slate-400 text-sm font-medium border border-slate-200">Photo 3</div>
          </div>
        </div>

        <div class="border-b border-slate-200 pb-6">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider bg-slate-100 px-2.5 py-1 rounded">
              {{ (anuncio.tipo_vivienda || '').replace('_', ' ') }}
            </span>
            <div class="flex items-center gap-1 text-sm font-bold text-slate-800">
              <span class="text-yellow-500">★</span> 
              {{ anuncio.valoraciones?.length ? (anuncio.valoraciones.reduce((acc, val) => acc + val.puntuacion, 0) / anuncio.valoraciones.length).toFixed(1) : 'New' }}
            </div>
          </div>
          <h1 class="text-3xl font-bold text-slate-900 mb-2">{{ anuncio.titulo }}</h1>
          <p class="text-sm text-slate-500 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            {{ anuncio.localizacion }}
          </p>
        </div>

        <div>
          <h2 class="text-lg font-bold text-slate-900 mb-4">Description</h2>
          <p class="text-slate-600 text-sm leading-relaxed whitespace-pre-line">
            {{ anuncio.descripcion }}
          </p>
        </div>

        <div>
          <h2 class="text-lg font-bold text-slate-900 mb-4">Features</h2>
          <div class="flex gap-8">
            <div v-if="anuncio.wifi" class="flex flex-col items-center gap-2 text-slate-700">
              <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.906 14.142 0M1.394 9.393c5.857-5.857 15.355-5.858 21.213 0"></path></svg>
              </div>
              <span class="text-xs font-medium">Wifi</span>
            </div>
            
            <div v-if="anuncio.terraza" class="flex flex-col items-center gap-2 text-slate-700">
              <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
              </div>
              <span class="text-xs font-medium">Terrace</span>
            </div>

            <div v-if="anuncio.garaje" class="flex flex-col items-center gap-2 text-slate-700">
              <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path></svg>
              </div>
              <span class="text-xs font-medium">Garage</span>
            </div>

            <p v-if="!anuncio.wifi && !anuncio.terraza && !anuncio.garaje" class="text-sm text-slate-500 italic">
              No additional features specified.
            </p>
          </div>
        </div>

        <div>
          <h2 class="text-lg font-bold text-slate-900 mb-4">Location</h2>
          <div class="h-48 bg-[#e5e7eb] rounded border border-slate-200 flex flex-col items-center justify-center text-slate-400">
            <svg class="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
            <span class="text-sm font-medium">Map View Placeholder</span>
          </div>
        </div>

        <div class="pt-8 border-t border-slate-200">
          <h2 class="text-xl font-bold text-slate-900 mb-6">Reviews</h2>

          <div v-if="canReview" class="mb-8 bg-slate-50 border border-slate-200 rounded p-6">
            <h3 class="text-sm font-bold text-slate-900 mb-4">Leave a review</h3>
            <form @submit.prevent="submitRating" class="space-y-4">
              <div class="w-full sm:w-48">
                <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Rating</label>
                <select v-model="ratingForm.puntuacion" class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900">
                  <option value="5">5 ★ Excellent</option>
                  <option value="4">4 ★ Very Good</option>
                  <option value="3">3 ★ Average</option>
                  <option value="2">2 ★ Poor</option>
                  <option value="1">1 ★ Terrible</option>
                </select>
              </div>
              
              <div>
                <label class="block text-xs font-semibold text-slate-500 uppercase mb-2">Comment</label>
                <textarea 
                  v-model="ratingForm.comentario" 
                  rows="3" 
                  class="w-full border border-slate-300 rounded px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-slate-900 resize-none"
                  placeholder="Share your experience..."
                ></textarea>
              </div>
              <div v-if="ratingError" class="text-red-500 text-xs">{{ ratingError }}</div>
              <button type="submit" :disabled="loadingRating" class="bg-slate-900 text-white text-sm font-medium px-5 py-2 rounded hover:bg-slate-800 disabled:opacity-50">
                {{ loadingRating ? 'Submitting...' : 'Submit Review' }}
              </button>
            </form>
          </div>

          <div v-else-if="!isAuthenticated" class="mb-8 p-4 bg-slate-50 border border-slate-200 rounded text-slate-500 text-sm text-center">
            You must be logged in as a student to leave a review.
          </div>
          <div v-else-if="user?.username === 'admin' || user?.rol === 'propietario'" class="mb-8 p-4 bg-slate-50 border border-slate-200 rounded text-slate-500 text-sm text-center">
            Only student accounts can review properties.
          </div>

          <div v-if="anuncio.valoraciones?.length" class="space-y-4">
            <div v-for="valoracion in anuncio.valoraciones" :key="valoracion.id" class="bg-white border border-slate-200 rounded p-5">
              <div class="flex justify-between items-center mb-3">
                <span class="text-sm font-bold text-slate-900">
                  {{ valoracion.usuario_nombre || 'Anonymous Student' }}
                </span>
                <span class="text-xs font-bold text-slate-800 flex items-center gap-1 bg-slate-100 px-2 py-1 rounded">
                  <span class="text-yellow-500">★</span> {{ valoracion.puntuacion }} / 5
                </span>
              </div>
              <p class="text-sm text-slate-600 leading-relaxed">{{ valoracion.comentario }}</p>
            </div>
          </div>
          <div v-else class="text-slate-500 text-sm italic py-4">
            No reviews yet. Be the first to share your experience!
          </div>
        </div>
      </div>

      <div class="lg:col-span-1">
        <div class="sticky top-24 space-y-6">
          
          <div class="border border-slate-200 rounded p-6 bg-white shadow-sm">
            <div class="flex items-end justify-between mb-4 border-b border-slate-100 pb-4">
              <span class="text-3xl font-extrabold text-slate-900">{{ anuncio.precio_mes }}€</span>
              <span class="text-slate-500 text-sm font-medium mb-1">/ month</span>
            </div>
            
            <div class="space-y-3 text-sm">
              <div class="flex justify-between text-slate-600">
                <span>Minimum stay</span> 
                <span class="font-bold text-slate-900">{{ anuncio.duracion_min_meses }} months</span>
              </div>
              <div class="flex justify-between text-slate-600">
                <span>Maximum stay</span> 
                <span class="font-bold text-slate-900">{{ anuncio.duracion_max_meses }} months</span>
              </div>
            </div>
          </div>

          <div class="border border-slate-200 rounded p-6 bg-white shadow-sm text-center">
            <div class="w-20 h-20 bg-slate-200 rounded-full mx-auto mb-3 flex items-center justify-center text-slate-400">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
            </div>
            <h3 class="font-bold text-slate-900">{{ anuncio.propietario_nombre || 'Property Manager' }}</h3>
            <p class="text-xs text-slate-500 mb-6">Verified Host</p>

            <div v-if="isAuthenticated">
              <div class="w-full bg-slate-50 border border-slate-200 text-slate-900 font-bold py-3 rounded mb-3 flex justify-center items-center gap-2">
                <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
                {{ anuncio.telefono_contacto || 'No phone provided' }}
              </div>
              
              <a 
                :href="`mailto:${anuncio.email_contacto}`" 
                class="block w-full bg-slate-900 text-white font-medium py-3 rounded hover:bg-slate-800 transition"
              >
                Send Message
              </a>
            </div>
            
            <div v-else>
              <p class="text-xs text-slate-500 mb-3 leading-relaxed">
                Log in to view the owner's phone number and send them a message directly.
              </p>
              <router-link 
                to="/login" 
                class="block w-full bg-slate-900 text-white font-medium py-3 rounded hover:bg-slate-800 transition shadow-sm"
              >
                Login to contact
              </router-link>
            </div>

          </div>
        </div>
      </div>
    </div>
  </main>
</template>