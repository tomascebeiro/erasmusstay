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
            <option value="habitacion">Habitacion</option>
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

    <div v-else>
      <p class="conteo">{{ anuncios.length }} pisos disponibles en Malta</p>
      <div class="cuadricula">
        <div v-for="anuncio in anuncios" :key="anuncio.id" class="tarjeta">
          <div class="tarjeta-tipo">{{ tipoTexto(anuncio.tipo_vivienda) }}</div>
          <div class="tarjeta-cuerpo">
            <h3>{{ anuncio.titulo }}</h3>
            <p class="ubicacion">{{ anuncio.localizacion }}</p>
            <p class="descripcion">{{ anuncio.descripcion.substring(0, 90) }}...</p>
            <div class="extras">
              <span v-if="anuncio.wifi">Wifi</span>
              <span v-if="anuncio.terraza">Terraza</span>
              <span v-if="anuncio.garaje">Garaje</span>
            </div>
          </div>
          <div class="tarjeta-pie">
            <span class="precio">{{ anuncio.precio_mes }} euro/mes</span>
            <div class="acciones">
              <button class="btn-contactar">Contactar</button>
              <button
                v-if="puedeEliminar(anuncio)"
                @click="eliminarAnuncio(anuncio.id)"
                class="btn-borrar"
              >Eliminar</button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const apiUrl = import.meta.env.VITE_API_URL || ''
const anuncios = ref([])
const cargando = ref(true)
const error = ref('')
const mostrarFormulario = ref(false)
const errorCrear = ref('')

const nuevoAnuncio = ref({
  titulo: '', localizacion: '', descripcion: '',
  precio_mes: '', tipo_vivienda: 'habitacion',
  wifi: false, terraza: false, garaje: false,
  telefono_contacto: '', email_contacto: ''
})

const usuario = ref(JSON.parse(localStorage.getItem('usuarioObj') || 'null'))
const rol = computed(() => localStorage.getItem('rol') || '')
const token = computed(() => localStorage.getItem('token') || '')
const usuarioId = computed(() => localStorage.getItem('usuarioId') || '')

const puedeCrear = computed(() => ['propietario', 'administrador'].includes(rol.value))

function puedeEliminar(anuncio) {
  if (rol.value === 'administrador') return true
  if (rol.value === 'propietario' && String(anuncio.propietario) === String(usuarioId.value)) return true
  return false
}

function tipoTexto(tipo) {
  const tipos = { habitacion: 'Habitacion', piso_completo: 'Piso completo', estudio: 'Estudio' }
  return tipos[tipo] || tipo
}

async function cargarAnuncios() {
  cargando.value = true
  try {
    const r = await fetch(`${apiUrl}/api/anuncios/`)
    const datos = await r.json()
    anuncios.value = Array.isArray(datos) ? datos : (datos.results || [])
  } catch (e) {
    error.value = 'No se pudieron cargar los pisos'
  } finally {
    cargando.value = false
  }
}

async function crearAnuncio() {
  errorCrear.value = ''
  try {
    const r = await fetch(`${apiUrl}/api/anuncios/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token.value}`
      },
      body: JSON.stringify(nuevoAnuncio.value)
    })
    if (!r.ok) {
      const datos = await r.json()
      throw new Error(JSON.stringify(datos))
    }
    mostrarFormulario.value = false
    await cargarAnuncios()
  } catch (e) {
    errorCrear.value = e.message
  }
}

async function eliminarAnuncio(id) {
  if (!confirm('Seguro que quieres eliminar este piso?')) return
  try {
    await fetch(`${apiUrl}/api/anuncios/${id}/`, {
      method: 'DELETE',
      headers: { 'Authorization': `Token ${token.value}` }
    })
    await cargarAnuncios()
  } catch (e) {
    alert('No se pudo eliminar')
  }
}

onMounted(cargarAnuncios)
</script>

<style scoped>
.pagina {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.zona-publicar {
  margin-bottom: 2rem;
}

.btn-publicar {
  background: #e94560;
  color: white;
  border: none;
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-publicar:hover {
  opacity: 0.88;
}

.formulario-piso {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  margin-top: 1rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.formulario-piso h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #1a1a2e;
}

.campos {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-bottom: 1rem;
}

.campos input,
.campos textarea,
.campos select {
  padding: 0.5rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: inherit;
}

.campos textarea {
  min-height: 80px;
  resize: vertical;
}

.opciones-extra {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.conteo {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.2rem;
}

.cuadricula {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.4rem;
}

.tarjeta {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  display: flex;
  flex-direction: column;
  transition: transform 0.15s;
}

.tarjeta:hover {
  transform: translateY(-3px);
}

.tarjeta-tipo {
  background: #e94560;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tarjeta-cuerpo {
  padding: 1rem;
  flex: 1;
}

.tarjeta-cuerpo h3 {
  margin: 0 0 0.3rem;
  font-size: 1rem;
  color: #1a1a2e;
}

.ubicacion {
  color: #888;
  font-size: 0.82rem;
  margin: 0 0 0.6rem;
}

.descripcion {
  color: #444;
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0 0 0.8rem;
}

.extras {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.extras span {
  background: #f0f0f0;
  border-radius: 4px;
  padding: 0.2rem 0.5rem;
  font-size: 0.75rem;
  color: #555;
}

.tarjeta-pie {
  padding: 0.8rem 1rem;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.precio {
  font-weight: 700;
  color: #e94560;
  font-size: 1rem;
}

.acciones {
  display: flex;
  gap: 0.5rem;
}

.btn-contactar {
  background: #1a1a2e;
  color: white;
  border: none;
  padding: 0.35rem 0.8rem;
  border-radius: 5px;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-contactar:hover {
  opacity: 0.85;
}

.btn-borrar {
  background: transparent;
  color: #e94560;
  border: 1px solid #e94560;
  padding: 0.35rem 0.7rem;
  border-radius: 5px;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-borrar:hover {
  background: #e94560;
  color: white;
}

.estado {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.aviso-error {
  color: #e94560;
  font-size: 0.85rem;
}
</style>