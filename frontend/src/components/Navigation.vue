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

const emit = defineEmits(['login', 'logout'])

const BACKEND = ''

const usuario = ref('')
const rol = ref('')
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
  if (rol.value === 'administrador') return 'Administrador'
  if (rol.value === 'propietario') return 'Propietario'
  return 'Estudiante'
})

async function iniciarSesion() {
  error.value = ''
  try {
    const res = await fetch(`${BACKEND}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: nombreUsuario.value, password: contrasena.value })
    })
    const text = await res.text()
    let datos
    try {
      datos = JSON.parse(text)
    } catch {
      throw new Error(`Respuesta del servidor no es JSON: ${text}`)
    }
    if (!res.ok) throw new Error(datos.error || 'Error al entrar')
    localStorage.setItem('token', datos.token)
    usuario.value = datos.username
    rol.value = datos.rol
    emit('login', { nombre: datos.username, rol: datos.rol })
  } catch (e) {
    error.value = e.message
  }
}

async function registrarse() {
  error.value = ''
  exito.value = ''
  try {
    const res = await fetch(`${BACKEND}/api/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: regNombre.value,
        email: regEmail.value,
        password: regContrasena.value,
        rol: regRol.value
      })
    })
    const datos = await res.json()
    if (!res.ok) throw new Error(JSON.stringify(datos))
    exito.value = 'Cuenta creada. Ya puedes entrar.'
    modoRegistro.value = false
  } catch (e) {
    error.value = e.message
  }
}

function cerrarSesion() {
  localStorage.removeItem('token')
  usuario.value = ''
  rol.value = ''
  emit('logout')
}
</script>

<style scoped>
.cabecera {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
  position: sticky;
  top: 0;
  z-index: 100;
  background: #0f3460;
  padding: 0.6rem 1.5rem;
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
.usuario-nombre { font-size: 0.9rem; font-weight: 500; color: white; }
.etiqueta-rol { font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 20px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; }
.etiqueta-rol--administrador { background: #e94560; color: white; }
.etiqueta-rol--propietario { background: #f5a623; color: #1a1a2e; }
.etiqueta-rol--estudiante { background: #27ae60; color: white; }

.pestanas-auth { display: flex; gap: 0.4rem; }
.pestana { padding: 0.15rem 0.5rem; border: 1px solid #555; background: transparent; color: #aaa; border-radius: 4px; cursor: pointer; font-size: 0.82rem; }
.pestana--activa { background: #e94560; border-color: #e94560; color: white; }

.formulario-auth { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }
.formulario-auth input, .formulario-auth select { padding: 0.4rem 0.6rem; border-radius: 5px; border: none; font-size: 0.82rem; min-width: 110px; background: #16213e; color: #eee; }
.boton { padding: 0.4rem 0.9rem; border-radius: 5px; border: none; cursor: pointer; font-size: 0.82rem; }
.boton--primario { background: #e94560; color: white; font-weight: 600; }
.boton--salir { background: #333; color: #ccc; }
.boton:hover { opacity: 0.85; }

.mensaje-error { color: #ff6b6b; font-size: 0.8rem; width: 100%; }
.mensaje-exito { color: #2ecc71; font-size: 0.8rem; width: 100%; }
</style>