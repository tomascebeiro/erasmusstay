<script setup>
import { ref, onMounted } from 'vue'
import Navigation from './components/Navigation.vue'

const anuncios = ref([])
const cargando = ref(true)
const error = ref('')

const cargarAnuncios = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/anuncios/')
    if (!response.ok) {
      throw new Error('Error al cargar anuncios')
    }
    anuncios.value = await response.json()
  } catch (err) {
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

onMounted(() => {
  cargarAnuncios()
})
</script>

<template>
  <Navigation />
  <main>
    <h1>ErasmusStay</h1>
    <p>Listado de anuncios desde Django REST Framework</p>

    <p v-if="cargando">Cargando anuncios...</p>
    <p v-if="error">{{ error }}</p>

    <div v-if="anuncios.length">
      <article v-for="anuncio in anuncios" :key="anuncio.id" class="card">
        <h2>{{ anuncio.titulo }}</h2>
        <p>{{ anuncio.descripcion }}</p>
        <p><strong>Precio:</strong> {{ anuncio.precio_mes }} €/mes</p>
        <p><strong>Localización:</strong> {{ anuncio.localizacion }}</p>
        <p><strong>Tipo:</strong> {{ anuncio.tipo_vivienda }}</p>
      </article>
    </div>

    <p v-else-if="!cargando && !error">No hay anuncios todavía.</p>
  </main>
</template>

<style scoped>
main {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: Arial, sans-serif;
}

.card {
  border: 1px solid #ddd;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
}
</style>