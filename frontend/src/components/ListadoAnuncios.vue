<template>
  <div class="container">
    <h2>Anuncios Disponibles</h2>
    <div v-if="cargando">Cargando...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else class="grid">
      <div v-for="anuncio in anuncios" :key="anuncio.id" class="card">
        <h3>{{ anuncio.titulo }}</h3>
        <p><strong>{{ anuncio.localizacion }}</strong></p>
        <p>{{ anuncio.descripcion.substring(0, 80) }}...</p>
        <div class="tags">
          <span v-if="anuncio.wifi">📶 Wifi</span>
          <span v-if="anuncio.terraza">🏡 Terraza</span>
          <span v-if="anuncio.garaje">🚗 Garaje</span>
        </div>
        <div v-if="anuncio.valoraciones?.length" class="rating">
          ⭐ {{ (anuncio.valoraciones.reduce((a,b)=>a+b.puntuacion,0)/anuncio.valoraciones.length).toFixed(1) }}
        </div>
        <div class="footer">
          <span class="price">{{ anuncio.precio_mes }}€/mes</span>
          <button>Contactar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const anuncios = ref([])
const cargando = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const res = await fetch(`${API_URL}/api/anuncios/`)
    anuncios.value = (await res.json()).results || []
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

h2 { margin-bottom: 2rem; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  background: white;
}

.card h3 { margin: 0 0 0.5rem; color: #007bff; }
.card p { margin: 0.5rem 0; color: #666; font-size: 0.95rem; }

.tags {
  display: flex;
  gap: 0.5rem;
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.tags span {
  background: #f0f0f0;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
}

.rating { color: #f39c12; margin: 0.5rem 0; }

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.price { font-weight: bold; color: #28a745; font-size: 1.1rem; }

button {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

button:hover { background: #0056b3; }
</style>