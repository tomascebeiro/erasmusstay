<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const menuOpen = ref(false)

const { user, isAuthenticated, logout } = useAuth()

const closeMenu = () => {
  menuOpen.value = false
}

const handleLogout = () => {
  logout()
  closeMenu()
  router.push('/')
}

// Flexible role logic supporting native admin username or role text
const isAdmin = computed(() => {
  return isAuthenticated.value && (user.value?.rol === 'administrador' || user.value?.username === 'admin')
})

const canPublish = computed(() => {
  if (!isAuthenticated.value) return false
  return ['propietario', 'administrador'].includes(user.value?.rol) || user.value?.username === 'admin'
})

// Visual mapping to keep the UI strictly in English
const displayRole = computed(() => {
  if (!user.value?.rol) return 'User'
  const role = user.value.rol.toLowerCase().trim()
  if (role === 'administrador') return 'Admin'
  if (role === 'propietario') return 'Owner'
  if (role === 'estudiante') return 'Student'
  return 'User'
})
</script>

<template>
  <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
    <nav class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      
      <router-link to="/" class="flex items-center gap-2" @click="closeMenu">
        <span class="font-bold text-xl text-slate-900 tracking-tight">Erasmus<span class="text-slate-600">Stay</span></span>
      </router-link>

      <div class="hidden md:flex items-center gap-6">
        <router-link to="/" class="text-sm font-medium text-slate-600 hover:text-slate-900" active-class="text-slate-900 font-semibold">Home</router-link>
        <router-link to="/anuncios" class="text-sm font-medium text-slate-600 hover:text-slate-900" active-class="text-slate-900 font-semibold">Accommodations</router-link>
        <router-link to="/contacto" class="text-sm font-medium text-slate-600 hover:text-slate-900" active-class="text-slate-900 font-semibold">Contact</router-link>
        
        <router-link v-if="isAdmin" to="/admin-panel" class="text-sm font-medium text-blue-600 hover:text-blue-700" active-class="text-blue-700 font-semibold">Admin Panel</router-link>
      </div>

      <div class="hidden md:flex items-center gap-3">
        <template v-if="isAuthenticated">
          <router-link to="/profile" class="text-sm font-medium text-slate-600 hover:text-slate-900 mr-2" active-class="text-slate-900 font-semibold">
            My Profile
          </router-link>

          <router-link v-if="canPublish" to="/crear-anuncio" class="text-sm font-medium bg-slate-900 text-white px-4 py-2 rounded hover:bg-slate-800 transition">
            Publish Listing
          </router-link>
          
          <div class="flex items-center gap-3 pl-4 border-l border-slate-200">
            <div class="text-right">
              <p class="text-sm font-bold text-slate-900 leading-none">{{ user?.username }}</p>
              <p class="text-xs text-slate-400 mt-1">{{ displayRole }}</p>
            </div>
            <button @click="handleLogout" class="text-sm text-slate-500 hover:text-red-600 font-medium transition-colors">Logout</button>
          </div>
        </template>

        <template v-else>
          <router-link to="/login" class="text-sm font-medium bg-slate-100 text-slate-900 px-5 py-2 rounded hover:bg-slate-200 transition">
            Login
          </router-link>
          <router-link to="/register" class="text-sm font-medium bg-slate-900 text-white px-5 py-2 rounded hover:bg-slate-800 transition">
            Register
          </router-link>
        </template>
      </div>

      <button class="md:hidden text-slate-900 p-1" @click="menuOpen = !menuOpen">
        <svg v-if="!menuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </nav>

    <div v-if="menuOpen" class="md:hidden bg-white border-t border-slate-200 p-4 space-y-3 shadow-sm">
      <router-link to="/" class="block text-slate-600 font-medium" @click="closeMenu">Home</router-link>
      <router-link to="/anuncios" class="block text-slate-600 font-medium" @click="closeMenu">Accommodations</router-link>
      <router-link to="/contacto" class="block text-slate-600 font-medium" @click="closeMenu">Contact</router-link>
      <router-link v-if="isAdmin" class="block text-blue-600 font-medium" to="/admin-panel" @click="closeMenu">Admin Panel</router-link>
      <router-link v-if="isAuthenticated" class="block text-slate-600 font-medium" to="/profile" @click="closeMenu">My Profile</router-link>
      
      <div class="pt-4 border-t border-slate-100 flex flex-col gap-2" v-if="!isAuthenticated">
        <router-link to="/login" class="text-center bg-slate-100 text-slate-900 py-2 rounded font-medium" @click="closeMenu">Login</router-link>
        <router-link to="/register" class="text-center bg-slate-900 text-white py-2 rounded font-medium" @click="closeMenu">Register</router-link>
      </div>
      <div class="pt-4 border-t border-slate-100 flex flex-col gap-2" v-else>
        <router-link v-if="canPublish" to="/crear-anuncio" class="text-center bg-slate-900 text-white py-2 rounded font-medium" @click="closeMenu">Publish Listing</router-link>
        <button @click="handleLogout" class="text-center bg-red-50 text-red-600 py-2 rounded font-medium">Logout</button>
      </div>
    </div>
  </header>
</template>