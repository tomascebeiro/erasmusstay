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

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
    const response = await fetch(`${API_URL}/api-token-auth/`, {
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
  } catch (e) {
    error.value = 'Error de conexión'
  }
}

const register = async () => {
  error.value = ''
  success.value = ''
  try {
    const response = await fetch(`${API_URL}/api/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: regUsername.value,
        email: regEmail.value,
        password: regPassword.value,
        role: regRole.value,
      }),
    })

    if (!response.ok) {
      const data = await response.json()
      error.value = data.detail || JSON.stringify(data)
      return
    }

    success.value = '¡Registro exitoso! Ya puedes iniciar sesión.'
    registerMode.value = false
  } catch (e) {
    error.value = 'Error de conexión'
  }
}

const logout = () => {
  localStorage.removeItem('authToken')
  localStorage.removeItem('authUser')
  user.value = ''
}
</script>