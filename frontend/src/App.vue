<script setup>
import { onMounted } from 'vue'
import Navigation from './components/Navigation.vue'
import { useAuth } from './composables/useAuth'

const { restoreSession } = useAuth()

onMounted(() => {
  restoreSession()
})
</script>

<template>
  <div class="min-h-screen bg-white text-slate-900 flex flex-col font-sans">
    
    <Navigation />

    <main class="flex-1 w-full bg-[#f8fafc]">
      <router-view />
    </main>

    <footer class="bg-slate-50 border-t border-slate-200 text-slate-600 py-12">
      <div class="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div class="md:col-span-1">
          <span class="font-bold text-lg text-slate-900 flex items-center gap-2">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 12h3v8h14v-8h3L12 2zm0 2.83l5 5V18H7v-8.17l5-5z"/></svg>
            ERASMUSSTAY
          </span>
          <p class="text-sm mt-4 text-slate-500">
            Trusted accommodation platform for Erasmus students across Europe.
          </p>
        </div>

        <div>
          <h4 class="font-semibold text-slate-900 mb-4">Platform</h4>
          <ul class="space-y-2 text-sm">
            <li><router-link to="/anuncios" class="hover:text-blue-600">Search Rooms</router-link></li>
            <li><router-link to="/crear-anuncio" class="hover:text-blue-600">List Your Property</router-link></li>
            <li><a href="#" class="hover:text-blue-600">Safety & Trust</a></li>
            <li><router-link to="/contacto" class="hover:text-blue-600">Help Center</router-link></li>
          </ul>
        </div>

        <div>
          <h4 class="font-semibold text-slate-900 mb-4">Company</h4>
          <ul class="space-y-2 text-sm">
            <li><a href="#" class="hover:text-blue-600">About Us</a></li>
            <li><a href="#" class="hover:text-blue-600">Careers</a></li>
            <li><a href="#" class="hover:text-blue-600">Press</a></li>
            <li><router-link to="/contacto" class="hover:text-blue-600">Contact</router-link></li>
          </ul>
        </div>

        <div>
          <h4 class="font-semibold text-slate-900 mb-4">Legal</h4>
          <ul class="space-y-2 text-sm">
            <li><a href="#" class="hover:text-blue-600">Privacy Policy</a></li>
            <li><a href="#" class="hover:text-blue-600">Terms of Service</a></li>
            <li><a href="#" class="hover:text-blue-600">Cookie Policy</a></li>
          </ul>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-4 mt-12 pt-8 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between">
        <p class="text-xs text-slate-500">
          &copy; 2026 ErasmusStay Platform. All rights reserved.
        </p>
      </div>
    </footer>
  </div>
</template>