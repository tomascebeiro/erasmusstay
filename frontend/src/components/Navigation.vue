<template>
  <nav class="navigation">
    <ul>
      <li><a href="#home">Inicio</a></li>
      <li><a href="#anuncios">Anuncios</a></li>
      <li><a href="#contacto">Contacto</a></li>
    </ul>
    <div class="login">
      <form>
        <input  type="text" placeholder="Usuario" required>
        <input  type="password" placeholder="Contraseña" required>
        <button type="submit">Iniciar Sesión</button>
      </form>
    </div>
  </nav>
</template>
<script setup>
</script>

<style scoped>
.navigation {
  background-color: #f8f9fa;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navigation ul {
  list-style: none;
  display: flex;
  gap: 1rem;
  margin: 0;
  padding: 0;
}

.navigation a {
  text-decoration: none;
  color: #007bff;
}

.navigation a:hover {
  text-decoration: underline;
}

.login form {
  display: flex;
  gap: 0.5rem;
}

.login input {
  padding: 0.5rem;
}

.login button {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

.login button:hover {
  background-color: #0056b3;
}
</style>