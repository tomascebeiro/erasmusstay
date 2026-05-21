<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuth } from '../composables/useAuth'

const API_URL = import.meta.env.VITE_API_URL || 'http://erasmusstay-production.up.railway.app'
const { getAuthHeaders } = useAuth()

// Estados Globales
const currentTab = ref('listings') // 'listings' o 'users'
const loading = ref(true)
const error = ref('')

// Estados de Alojamientos
const anuncios = ref([])
const filtroEstado = ref('all')

// Estados de Usuarios
const usuarios = ref([])

// Computed para filtrar anuncios
const anunciosFiltrados = computed(() => {
  if (filtroEstado.value === 'pending') return anuncios.value.filter(a => !a.aprobado)
  if (filtroEstado.value === 'approved') return anuncios.value.filter(a => a.aprobado)
  return anuncios.value
})

// Peticiones
const fetchData = async () => {
  loading.value = true
  error.value = ''
  try {
    // 1. Cargar anuncios
    const resAnuncios = await fetch(`${API_URL}/api/anuncios/`, {
      headers: { ...getAuthHeaders() }
    })
    if (!resAnuncios.ok) throw new Error('Failed to load listings.')
    const dataAnuncios = await resAnuncios.json()
    anuncios.value = dataAnuncios.results || dataAnuncios

    // 2. Cargar usuarios
    const resUsuarios = await fetch(`${API_URL}/api/admin/usuarios/`, {
      headers: { ...getAuthHeaders() }
    })
    if (!resUsuarios.ok) throw new Error('Failed to load users.')
    usuarios.value = await resUsuarios.json()

  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Acciones de Moderación: Alojamientos
const toggleAprobacion = async (anuncio) => {
  const nuevoEstado = !anuncio.aprobado
  try {
    const response = await fetch(`${API_URL}/api/anuncios/${anuncio.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({ aprobado: nuevoEstado })
    })
    if (!response.ok) throw new Error('Could not update listing status.')
    anuncio.aprobado = nuevoEstado
  } catch (err) {
    alert(err.message)
  }
}

const eliminarAnuncio = async (id) => {
  if (!confirm('Are you sure you want to permanently delete this listing?')) return
  try {
    const response = await fetch(`${API_URL}/api/anuncios/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    if (!response.ok) throw new Error('Failed to delete listing.')
    anuncios.value = anuncios.value.filter(a => a.id !== id)
  } catch (err) {
    alert(err.message)
  }
}

// Acciones de Moderación: Usuarios
const toggleBloqueoUsuario = async (usuario) => {
  const nuevoEstado = !usuario.activo // Si está activo, lo volvemos inactivo (bloqueado)
  const accionText = nuevoEstado ? 'unblock' : 'block'
  
  if (!confirm(`Are you sure you want to ${accionText} the user ${usuario.username}?`)) return

  try {
    const response = await fetch(`${API_URL}/api/admin/usuarios/${usuario.id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({ activo: nuevoEstado })
    })
    if (!response.ok) throw new Error('Could not update user status.')
    usuario.activo = nuevoEstado
  } catch (err) {
    alert(err.message)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <main class="max-w-7xl mx-auto px-4 py-12">
    
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">Admin Dashboard</h1>
      <p class="text-sm text-slate-500 mt-2 mb-6">Manage system listings, user access, and platform integrity.</p>
      
      <div class="flex gap-4 border-b border-slate-200">
        <button 
          @click="currentTab = 'listings'"
          :class="['pb-3 px-2 text-sm font-bold transition-colors border-b-2', currentTab === 'listings' ? 'border-slate-900 text-slate-900' : 'border-transparent text-slate-500 hover:text-slate-700']"
        >
          Manage Listings
        </button>
        <button 
          @click="currentTab = 'users'"
          :class="['pb-3 px-2 text-sm font-bold transition-colors border-b-2', currentTab === 'users' ? 'border-slate-900 text-slate-900' : 'border-transparent text-slate-500 hover:text-slate-700']"
        >
          Manage Users
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-slate-500 py-12 text-center text-sm animate-pulse">
      Loading system data...
    </div>
    
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-600 p-4 rounded text-sm mb-6">
      {{ error }}
    </div>

    <div v-else>
      
      <div v-if="currentTab === 'listings'">
        <div class="flex bg-slate-100 border border-slate-200 rounded p-1 w-fit mb-6">
          <button @click="filtroEstado = 'all'" :class="['px-4 py-1.5 text-xs font-bold rounded transition-colors', filtroEstado === 'all' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700']">All</button>
          <button @click="filtroEstado = 'pending'" :class="['px-4 py-1.5 text-xs font-bold rounded transition-colors', filtroEstado === 'pending' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700']">Pending</button>
          <button @click="filtroEstado = 'approved'" :class="['px-4 py-1.5 text-xs font-bold rounded transition-colors', filtroEstado === 'approved' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700']">Approved</button>
        </div>

        <div class="bg-white border border-slate-200 rounded shadow-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-xs font-bold">
                <tr>
                  <th class="px-6 py-4">Property Details</th>
                  <th class="px-6 py-4">Host Details</th>
                  <th class="px-6 py-4">Status</th>
                  <th class="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="anuncio in anunciosFiltrados" :key="anuncio.id" class="hover:bg-slate-50 transition">
                  <td class="px-6 py-4">
                    <p class="font-bold text-slate-900 line-clamp-1">{{ anuncio.titulo }}</p>
                    <p class="text-xs text-slate-500 mt-0.5 capitalize">{{ anuncio.localizacion }} • {{ (anuncio.tipo_vivienda || '').replace('_', ' ') }}</p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <p class="font-medium text-slate-700">{{ anuncio.propietario_nombre || 'Unknown' }}</p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span v-if="anuncio.aprobado" class="inline-flex px-2 py-1 rounded text-[10px] font-bold bg-green-100 text-green-700 uppercase tracking-wide">Approved</span>
                    <span v-else class="inline-flex px-2 py-1 rounded text-[10px] font-bold bg-yellow-100 text-yellow-700 uppercase tracking-wide">Pending</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right space-x-4">
                    <router-link :to="`/anuncio/${anuncio.id}`" class="text-blue-600 hover:text-blue-800 font-bold text-xs transition-colors">View</router-link>
                    <button @click="toggleAprobacion(anuncio)" :class="anuncio.aprobado ? 'text-yellow-600 hover:text-yellow-800' : 'text-green-600 hover:text-green-800'" class="font-bold text-xs transition-colors">
                      {{ anuncio.aprobado ? 'Revoke' : 'Approve' }}
                    </button>
                    <button @click="eliminarAnuncio(anuncio.id)" class="text-red-600 hover:text-red-800 font-bold text-xs transition-colors">Delete</button>
                  </td>
                </tr>
                <tr v-if="anunciosFiltrados.length === 0">
                  <td colspan="4" class="px-6 py-10 text-center text-slate-500 italic">No listings match the current filter.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="currentTab === 'users'">
        <div class="bg-white border border-slate-200 rounded shadow-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-xs font-bold">
                <tr>
                  <th class="px-6 py-4">User Identity</th>
                  <th class="px-6 py-4">Role Profile</th>
                  <th class="px-6 py-4">Account Status</th>
                  <th class="px-6 py-4 text-right">Moderation</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="usuario in usuarios" :key="usuario.id" class="hover:bg-slate-50 transition">
                  <td class="px-6 py-4">
                    <p class="font-bold text-slate-900">{{ usuario.username }}</p>
                    <p class="text-xs text-slate-500 mt-0.5">{{ usuario.email }}</p>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap capitalize font-medium text-slate-700">
                    {{ usuario.rol }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span v-if="usuario.activo" class="inline-flex px-2 py-1 rounded text-[10px] font-bold bg-green-100 text-green-700 uppercase tracking-wide">Active</span>
                    <span v-else class="inline-flex px-2 py-1 rounded text-[10px] font-bold bg-red-100 text-red-700 uppercase tracking-wide">Blocked</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right">
                    <button 
                      @click="toggleBloqueoUsuario(usuario)" 
                      :class="usuario.activo ? 'text-red-600 hover:bg-red-50' : 'text-green-600 hover:bg-green-50'" 
                      class="font-bold text-xs px-3 py-1.5 rounded transition border border-transparent"
                    >
                      {{ usuario.activo ? 'Block User' : 'Unblock User' }}
                    </button>
                  </td>
                </tr>
                <tr v-if="usuarios.length === 0">
                  <td colspan="4" class="px-6 py-10 text-center text-slate-500 italic">No users found in the system.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </main>
</template>