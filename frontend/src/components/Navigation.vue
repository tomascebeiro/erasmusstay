<template>
  <header class="cabecera">
    <div class="cabecera-marca">
      <div class="cabecera-logo-texto">
        <span class="cabecera-titulo">ErasmusStay</span>
        <span class="cabecera-subtitulo">Pisos en Malta para estudiantes Erasmus</span>
      </div>
    </div>

    <nav class="cabecera-nav">
      <a href="#inicio">Inicio</a>
      <a href="#anuncios">Anuncios</a>
      <a href="#contacto">Contacto</a>
    </nav>

    <div class="cabecera-sesion">
      <template v-if="usuario">
        <div class="usuario-info">
          <span class="usuario-nombre">{{ usuario }}</span>
          <span class="etiqueta-rol" :class="'etiqueta-rol--' + rol">{{ etiquetaRol }}</span>
        </div>
        <button class="boton boton--salir" @click="cerrarSesion">Cerrar sesion</button>
      </template>

      <template v-else>
        <div class="pestanas-auth">
          <button :class="['pestana', { 'pestana--activa': !modoRegistro }]" @click="modoRegistro = false">Entrar</button>
          <button :class="['pestana', { 'pestana--activa': modoRegistro }]" @click="modoRegistro = true">Registrarse</button>
        </div>

        <form v-if="!modoRegistro" class="formulario-auth" @submit.prevent="iniciarSesion">
          <input v-model="nombreUsuario" type="text" placeholder="Usuario" required />
          <input v-model="contrasena" type="password" placeholder="Contrasena" required />
          <button type="submit" class="boton boton--primario">Entrar</button>
          <p v-if="error" class="mensaje-error">{{ error }}</p>
        </form>

        <form v-else class="formulario-auth" @submit.prevent="registrarse">
          <input v-model="regNombre" type="text" placeholder="Usuario" required />
          <input v-model="regEmail" type="email" placeholder="Correo" required />
          <input v-model="regContrasena" type="password" placeholder="Contrasena" required />
          <select v-model="regRol">
            <option value="estudiante">Estudiante</option>
            <option value="propietario">Propietario</option>
            <option value="administrador">Administrador</option>
          </select>
          <button type="submit" class="boton boton--primario">Crear cuenta</button>
          <p v-if="error" class="mensaje-error">{{ error }}</p>
          <p v-if="exito" class="mensaje-exito">{{ exito }}</p>
        </form>
      </template>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'

const apiUrl = 'https://erasmusstay-production.up.railway.app'

const usuario = ref(localStorage.getItem('usuario') || '')
const rol = ref(localStorage.getItem('rol') || '')
const token = ref(localStorage.getItem('token') || '')

const modoRegistro = ref(false)
const nombreUsuario = ref('')
const contrasena = ref('')
const regNombre = ref('')
const regEmail = ref('')
const regContrasena = ref('')
const regRol = ref('estudiante')
const error = ref('')
const exito = ref('')

const etiquetaRol = computed(() => {
  const etiquetas = { estudiante: 'Estudiante', propietario: 'Propietario', administrador: 'Administrador' }
  return etiquetas[rol.value] || rol.value
})

async function iniciarSesion() {
  error.value = ''
  try {
    const respuesta = await fetch(`${apiUrl}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: nombreUsuario.value, password: contrasena.value })
    })
    const datos = await respuesta.json()
    if (!respuesta.ok) throw new Error(datos.error || 'Error al iniciar sesion')
    localStorage.setItem('token', datos.token)
    localStorage.setItem('usuario', datos.username)
    localStorage.setItem('rol', datos.rol)
    localStorage.setItem('usuarioId', datos.id)
    usuario.value = datos.username
    rol.value = datos.rol
    token.value = datos.token
    nombreUsuario.value = ''
    contrasena.value = ''
  } catch (e) {
    error.value = e.message
  }
}

async function registrarse() {
  error.value = ''
  exito.value = ''
  try {
    const respuesta = await fetch(`${apiUrl}/api/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: regNombre.value,
        email: regEmail.value,
        password: regContrasena.value,
        rol: regRol.value
      })
    })
    const datos = await respuesta.json()
    if (!respuesta.ok) throw new Error(JSON.stringify(datos))
    exito.value = 'Cuenta creada. Ya puedes entrar.'
    modoRegistro.value = false
  } catch (e) {
    error.value = e.message
  }
}

function cerrarSesion() {
  localStorage.clear()
  usuario.value = ''
  rol.value = ''
  token.value = ''
}
</script>

<style scoped>
.cabecera {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 0.8rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}
.cabecera-marca { display: flex; align-items: center; gap: 0.8rem; }
.cabecera-logo-texto { display: flex; flex-direction: column; }
.cabecera-titulo { font-size: 1.2rem; font-weight: 700; color: #e94560; letter-spacing: 0.03em; }
.cabecera-subtitulo { font-size: 0.7rem; color: #aaa; }
.cabecera-nav { display: flex; gap: 1.2rem; flex: 1; }
.cabecera-nav a { color: #ccc; text-decoration: none; font-size: 0.88rem; transition: color 0.2s; }
.cabecera-nav a:hover { color: #e94560; }
.cabecera-sesion { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; }
.usuario-info { display: flex; align-items: center; gap: 0.5rem; }
.usuario-nombre { font-size: 0.9rem; font-weight: 500; }
.etiqueta-rol { font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; background: #444; }
.etiqueta-rol--administrador { background: #e94560; color: white; }
.etiqueta-rol--propietario { background: #f5a623; color: #1a1a2e; }
.etiqueta-rol--estudiante { background: #27ae60; color: white; }
.pestanas-auth { display: flex; gap: 0.4rem; }
.pestana { padding: 0.3rem 0.8rem; border: 1px solid #555; background: transparent; color: #aaa; border-radius: 4px; cursor: pointer; font-size: 0.82rem; transition: all 0.2s; }
.pestana--activa, .pestana:hover { background: #e94560; border-color: #e94560; color: white; }
.formulario-auth { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }
.formulario-auth input, .formulario-auth select { padding: 0.4rem 0.6rem; border-radius: 5px; border: none; font-size: 0.82rem; min-width: 110px; flex: 1; }
.boton { padding: 0.4rem 0.9rem; border: none; border-radius: 5px; cursor: pointer; font-size: 0.82rem; font-weight: 600; transition: opacity 0.2s; }
.boton:hover { opacity: 0.85; }
.boton--primario { background: #e94560; color: white; }
.boton--salir { background: #333; color: #ccc; }
.mensaje-error { color: #ff6b6b; font-size: 0.8rem; width: 100%; }
.mensaje-exito { color: #2ecc71; font-size: 0.8rem; width: 100%; }
</style>