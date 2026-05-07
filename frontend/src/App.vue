<template>
  <div id="aplicacion">
    <Navegacion />
    <main class="contenido-principal">
      <ListadoAnuncios />
    </main>
    <footer class="pie-pagina">
      <p>&copy; 2025 ErasmusStay &mdash; Encuentra tu piso en Malta</p>
    </footer>
  </div>
</template>

<script setup>
import Navegacion from './components/Navigation.vue'
import ListadoAnuncios from './components/ListadoAnuncios.vue'
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Arial, sans-serif;
  background: #f0f2f5;
  color: #222;
  min-height: 100vh;
}

#aplicacion {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.contenido-principal {
  flex: 1;
  padding-bottom: 2rem;
}

.pie-pagina {
  background: #1a1a2e;
  color: #aaa;
  text-align: center;
  padding: 1.2rem;
  font-size: 0.9rem;
}
</style>