<template>
  <nav class="navigation">
    <ul>
      <li><a href="#home">Inicio</a></li>
      <li><a href="#anuncios">Anuncios</a></li>
      <li><a href="#contacto">Contacto</a></li>
    </ul>
    <div class="login">
      <template v-if="user">
        <span>Hola, {{ user }}</span>
        <button type="button" @click="logout">Cerrar sesión</button>
      </template>
      <template v-else>
        <div class="auth-tabs">
          <button type="button" :class="{ active: !registerMode }" @click="registerMode = false">Login</button>
          <button type="button" :class="{ active: registerMode }" @click="registerMode = true">Registro</button>
        </div>

        <form v-if="!registerMode" @submit.prevent="login">
          <input v-model="username" type="text" placeholder="Usuario" required />
          <input v-model="password" type="password" placeholder="Contraseña" required />
          <button type="submit">Iniciar Sesión</button>
        </form>

        <form v-else @submit.prevent="register">
          <input v-model="regUsername" type="text" placeholder="Usuario" required />
          <input v-model="regEmail" type="email" placeholder="Email" required />
          <input v-model="regPassword" type="password" placeholder="Contraseña" required />
          <select v-model="regRole" required>
            <option value="estudiante">Estudiante</option>
            <option value="propietario">Propietario</option>
            <option value="administrador">Administrador</option>
          </select>
          <button type="submit">Registrarse</button>
        </form>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">{{ success }}</p>
      </template>
    </div>
  </nav>
</template>
<script setup>
import { ref, onMounted } from 'vue'

const username = ref('')
const password = ref('')
const regUsername = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regRole = ref('estudiante')
const registerMode = ref(false)
const error = ref('')
const success = ref('')
const user = ref('')

onMounted(() => {
  const savedUser = localStorage.getItem('authUser')
  if (savedUser) {
    user.value = savedUser
  }
})

const login = async () => {
  error.value = ''
  try {
    const response = await fetch('http://localhost:8000/api-token-auth/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    })

    if (!response.ok) {
      const data = await response.json()
      error.value = data.non_field_errors?.[0] || 'Usuario o contraseña incorrectos.'
      return
    }

    const data = await response.json()
    localStorage.setItem('authToken', data.token)
    localStorage.setItem('authUser', username.value)
    user.value = username.value
    username.value = ''
    password.value = ''
  } catch (err) {
    error.value = 'No se pudo conectar con el backend.'
  }
}

const register = async () => {
  error.value = ''
  success.value = ''

  try {
    const response = await fetch('http://localhost:8000/api/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: regUsername.value,
        email: regEmail.value,
        password: regPassword.value,
        rol: regRole.value,
      }),
    })

    if (!response.ok) {
      const data = await response.json()
      error.value = Object.values(data).flat().join(' ') || 'No se pudo crear el usuario.'
      return
    }

    const data = await response.json()
    localStorage.setItem('authToken', data.token)
    localStorage.setItem('authUser', regUsername.value)
    user.value = regUsername.value
    regUsername.value = ''
    regEmail.value = ''
    regPassword.value = ''
    regRole.value = 'estudiante'
    success.value = 'Usuario registrado correctamente.'
  } catch (err) {
    error.value = 'No se pudo conectar con el backend.'
  }
}

const logout = () => {
  localStorage.removeItem('authToken')
  localStorage.removeItem('authUser')
  user.value = ''
}
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

.login {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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

.auth-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.auth-tabs button {
  background: transparent;
  border: 1px solid #007bff;
  color: #007bff;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
}

.auth-tabs button.active {
  background-color: #007bff;
  color: white;
}

.error {
  color: #c53030;
  margin: 0;
  font-size: 0.9rem;
}

.success {
  color: #276749;
  margin: 0;
  font-size: 0.9rem;
}
</style>