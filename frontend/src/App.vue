<template>
  <div>
    <Navigation />
    <h1>ErasmusStay</h1>
    <p>Frontend funcionando con Vue en docker</p>
    <ListadoAnuncios />
  </div>
</template>

<script setup>
import Navigation from './components/Navigation.vue'
import ListadoAnuncios from './components/ListadoAnuncios.vue'
</script>

<style>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 2rem;
}
</style>