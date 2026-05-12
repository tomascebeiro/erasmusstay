<template>
  <div class="pagina">

    <div v-if="puedeCrear" class="zona-publicar">
      <button @click="mostrarFormulario = !mostrarFormulario" class="btn-publicar">
        {{ mostrarFormulario ? 'Cancelar' : '+ Publicar piso' }}
      </button>

      <form v-if="mostrarFormulario" @submit.prevent="crearAnuncio" class="formulario-piso">
        <h3>Nuevo piso</h3>
        <div class="campos">
          <input v-model="nuevoAnuncio.titulo" placeholder="Titulo del piso" required />
          <input v-model="nuevoAnuncio.localizacion" placeholder="Zona o barrio" required />
          <textarea v-model="nuevoAnuncio.descripcion" placeholder="Describe el piso..." required></textarea>
          <input v-model="nuevoAnuncio.precio_mes" type="number" placeholder="Precio al mes (euros)" required />
          <select v-model="nuevoAnuncio.tipo_vivienda">
            <option value="habitacion">Habitación</option>
            <option value="piso_completo">Piso completo</option>
            <option value="estudio">Estudio</option>
          </select>
          <input v-model="nuevoAnuncio.telefono_contacto" placeholder="Telefono" />
          <input v-model="nuevoAnuncio.email_contacto" type="email" placeholder="Email" />
        </div>
        <div class="opciones-extra">
          <label><input type="checkbox" v-model="nuevoAnuncio.wifi" /> Wifi incluido</label>
          <label><input type="checkbox" v-model="nuevoAnuncio.terraza" /> Terraza</label>
          <label><input type="checkbox" v-model="nuevoAnuncio.garaje" /> Garaje</label>
        </div>
        <button type="submit" class="btn-publicar">Publicar</button>
        <p v-if="errorCrear" class="aviso-error">{{ errorCrear }}</p>
      </form>
    </div>

    <div v-if="cargando" class="estado">Cargando pisos...</div>
    <div v-else-if="error" class="estado aviso-error">{{ error }}</div>

    <div v-else class="lista-pisos">
      <div v-for="anuncio in anuncios" :key="anuncio.id" class="tarjeta">
        <div class="tarjeta-cabecera">
          <h2 class="tarjeta-titulo">{{ anuncio.titulo }}</h2>
          <span class="tarjeta-precio">{{ anuncio.precio_mes }}€/mes</span>
        </div>
        <p class="tarjeta-lugar">{{ anuncio.localizacion }}</p>
        <p class="tarjeta-desc">{{ anuncio.descripcion }}</p>
        <div class="tarjeta-extras">
          <span v-if="anuncio.wifi" class="extra">Wifi</span>
          <span v-if="anuncio.terraza" class="extra">Terraza</span>
          <span v-if="anuncio.garaje" class="extra">Garaje</span>
          <span class="extra tipo">{{ anuncio.tipo_vivienda }}</span>
        </div>
        <div class="tarjeta-contacto">
          <span v-if="anuncio.telefono_contacto">Tel: {{ anuncio.telefono_contacto }}</span>
          <span v-if="anuncio.email_contacto">Email: {{ anuncio.email_contacto }}</span>
        </div>
        <div class="tarjeta-acciones" v-if="puedeEliminar(anuncio)">
          <button @click="eliminarAnuncio(anuncio.id)" class="btn-borrar">Eliminar</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  usuario: Object
})

const URL_BACKEND = 'https://erasmusstay-production.up.railway.app'

const anuncios = ref([])
const cargando = ref(true)
const error = ref('')
const mostrarFormulario = ref(false)
const errorCrear = ref('')

const nuevoAnuncio = ref({
  titulo: '',
  localizacion: '',
  descripcion: '',
  precio_mes: '',
  tipo_vivienda: 'habitacion',
  telefono_contacto: '',
  email_contacto: '',
  wifi: false,
  terraza: false,
  garaje: false
})

const rol = computed(() => props.usuario?.rol || '')
const puedeCrear = computed(() => rol.value === 'propietario' || rol.value === 'administrador')

function puedeEliminar(anuncio) {
  if (!props.usuario) return false
  if (rol.value === 'administrador') return true
  if (rol.value === 'propietario' && anuncio.propietario_nombre === props.usuario.nombre) return true
  return false
}

async function cargarAnuncios() {
  try {
    const r = await fetch(`${URL_BACKEND}/api/anuncios/`)
    if (!r.ok) throw new Error('Error al cargar')
    const datos = await r.json()
    anuncios.value = datos.results || []
  } catch (e) {
    error.value = 'No se pudieron cargar los pisos'
  } finally {
    cargando.value = false
  }
}

async function crearAnuncio() {
  errorCrear.value = ''
  try {
    const token = localStorage.getItem('token')
    const r = await fetch(`${URL_BACKEND}/api/anuncios/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      },
      body: JSON.stringify(nuevoAnuncio.value)
    })
    if (!r.ok) {
      const datos = await r.json()
      throw new Error(JSON.stringify(datos))
    }
    const creado = await r.json()
    anuncios.value.unshift(creado)
    mostrarFormulario.value = false
    nuevoAnuncio.value = {
      titulo: '', localizacion: '', descripcion: '', precio_mes: '',
      tipo_vivienda: 'habitacion', telefono_contacto: '', email_contacto: '',
      wifi: false, terraza: false, garaje: false
    }
  } catch (e) {
    errorCrear.value = 'Error al publicar: ' + e.message
  }
}

async function eliminarAnuncio(id) {
  try {
    const token = localStorage.getItem('token')
    await fetch(`${URL_BACKEND}/api/anuncios/${id}/`, {
      method: 'DELETE',
      headers: { 'Authorization': `Token ${token}` }
    })
    anuncios.value = anuncios.value.filter(a => a.id !== id)
  } catch (e) {
    alert('Error al eliminar')
  }
}

onMounted(cargarAnuncios)
</script>

<style scoped>
.pagina { padding: 1rem 2rem; max-width: 900px; margin: 0 auto; }

.zona-publicar { margin-bottom: 1.5rem; }
.btn-publicar { background: #e94560; color: white; border: none; padding: 0.5rem 1.2rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }
.btn-publicar:hover { opacity: 0.88; }

.formulario-piso { background: #1a1a2e; border: 1px solid #333; border-radius: 8px; padding: 1.5rem; margin-top: 1rem; }
.formulario-piso h3 { color: #e94560; margin-bottom: 1rem; }
.campos { display: flex; flex-direction: column; gap: 0.7rem; }
.campos input, .campos textarea, .campos select { background: #16213e; border: 1px solid #444; color: #eee; padding: 0.5rem 0.7rem; border-radius: 5px; font-size: 0.88rem; }
.campos textarea { min-height: 80px; resize: vertical; }
.opciones-extra { display: flex; gap: 1rem; margin-top: 0.5rem; color: #aaa; font-size: 0.85rem; }

.estado { text-align: center; padding: 2rem; color: #aaa; }
.aviso-error { color: #e94560; font-size: 0.85rem; margin-top: 0.5rem; }

.lista-pisos { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.2rem; }

.tarjeta { background: #16213e; border: 1px solid #1a1a2e; border-radius: 10px; padding: 1.2rem; transition: box-shadow 0.2s; }
.tarjeta:hover { box-shadow: 0 4px 16px rgba(233,69,96,0.15); }

.tarjeta-cabecera { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.3rem; }
.tarjeta-titulo { font-size: 1rem; font-weight: 600; color: white; margin: 0; }
.tarjeta-precio { color: #e94560; font-weight: 700; font-size: 0.95rem; white-space: nowrap; }

.tarjeta-lugar { color: #aaa; font-size: 0.82rem; margin: 0.2rem 0; }
.tarjeta-desc { color: #ccc; font-size: 0.85rem; margin: 0.5rem 0; }

.tarjeta-extras { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.5rem 0; }
.extra { background: #0f3460; color: #aaa; font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 10px; }
.extra.tipo { background: #e94560; color: white; }

.tarjeta-contacto { font-size: 0.8rem; color: #888; margin-top: 0.4rem; display: flex; flex-direction: column; gap: 0.2rem; }

.tarjeta-acciones { margin-top: 0.8rem; }
.btn-borrar { background: #333; color: #e94560; border: 1px solid #e94560; padding: 0.3rem 0.8rem; border-radius: 5px; cursor: pointer; font-size: 0.82rem; }
.btn-borrar:hover { background: #e94560; color: white; }
</style>