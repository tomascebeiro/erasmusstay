/**
 * Composable global de autenticación de ErasmusStay.
 *
 * Este archivo centraliza el estado de sesión del frontend Vue.
 *
 * En Vue, un composable es una función reutilizable que agrupa lógica común.
 * En este caso, `useAuth` permite que cualquier componente o vista pueda saber:
 *
 * - si el usuario está autenticado;
 * - qué usuario está conectado;
 * - si se está restaurando la sesión;
 * - cuál es el token actual;
 * - cómo iniciar sesión;
 * - cómo cerrar sesión;
 * - cómo construir cabeceras autenticadas para llamar a la API.
 *
 * El backend utiliza autenticación por token de Django REST Framework.
 * Por eso, cuando el usuario inicia sesión correctamente, el token se guarda en
 * localStorage y se envía después en cada petición privada usando la cabecera:
 *
 * Authorization: Token <token>
 *
 * Variables principales:
 *
 * - user:
 *   datos del usuario autenticado.
 *
 * - isAuthenticated:
 *   indica si existe una sesión válida.
 *
 * - loadingAuth:
 *   indica si se está comprobando/restaurando la sesión.
 *
 * - token:
 *   token actual leído desde localStorage.
 */

import { computed, ref } from 'vue'


// Estado global del usuario autenticado.
// Está fuera de useAuth para que sea compartido entre todos los componentes
// que importen este composable.
const user = ref(null)


// Indica si el usuario tiene sesión activa.
const isAuthenticated = ref(false)


// Indica si se está comprobando el token guardado.
// Es útil para evitar mostrar contenido privado antes de saber si la sesión es válida.
const loadingAuth = ref(false)


// URL base de la API.
// En producción se lee desde VITE_API_URL.
// En desarrollo, si no existe variable de entorno, usa localhost:8000.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'


export function useAuth() {
  /**
   * Token actual de autenticación.
   *
   * Se define como computed para que pueda usarse de forma reactiva desde Vue.
   * El valor se lee desde localStorage, donde se guarda tras hacer login.
   */
  const token = computed(() => localStorage.getItem('token'))

  /**
   * Restaura la sesión del usuario al cargar la aplicación.
   *
   * Flujo:
   * 1. Comprueba si existe un token guardado en localStorage.
   * 2. Si no existe, limpia el estado de sesión.
   * 3. Si existe, llama al endpoint /api/me/ para validar el token.
   * 4. Si el backend responde correctamente, guarda los datos del usuario.
   * 5. Si el token no es válido, lo elimina y cierra la sesión local.
   *
   * Esta función suele ejecutarse al arrancar la app, por ejemplo desde App.vue
   * o desde una guardia de rutas.
   */
  const restoreSession = async () => {
    const savedToken = localStorage.getItem('token')

    // Si no hay token guardado, no hay sesión que restaurar.
    if (!savedToken) {
      user.value = null
      isAuthenticated.value = false
      return
    }

    loadingAuth.value = true

    try {
      const response = await fetch(`${API_URL}/api/me/`, {
        headers: {
          Authorization: `Token ${savedToken}`,
        },
      })

      // Si el backend rechaza el token, se considera sesión inválida.
      if (!response.ok) {
        throw new Error('Sesión no válida')
      }

      const data = await response.json()

      // Guarda los datos actualizados del usuario.
      user.value = data
      isAuthenticated.value = true
    } catch (error) {
      console.error('Error restaurando sesión:', error)

      // Si hay error, se elimina el token para no seguir usando una sesión rota.
      localStorage.removeItem('token')
      user.value = null
      isAuthenticated.value = false
    } finally {
      loadingAuth.value = false
    }
  }

  /**
   * Guarda una sesión después de iniciar sesión correctamente.
   *
   * Parámetros:
   * - newToken: token devuelto por el backend.
   * - userData: datos básicos del usuario devueltos por el backend.
   *
   * El token se guarda en localStorage para que la sesión pueda mantenerse al
   * recargar la página.
   */
  const login = (newToken, userData = null) => {
    localStorage.setItem('token', newToken)
    user.value = userData
    isAuthenticated.value = true
  }

  /**
   * Cierra la sesión local del usuario.
   *
   * Elimina el token de localStorage y limpia el estado reactivo.
   * No llama al backend porque la autenticación por token puede invalidarse
   * simplemente dejando de enviar el token desde el frontend.
   */
  const logout = () => {
    localStorage.removeItem('token')
    user.value = null
    isAuthenticated.value = false
  }

  /**
   * Devuelve las cabeceras de autenticación para peticiones privadas.
   *
   * Si no hay token, devuelve un objeto vacío.
   * Si hay token, devuelve:
   *
   * {
   *   Authorization: 'Token ...'
   * }
   *
   * Se usa en vistas como perfil, creación de anuncios, administración,
   * solicitudes de contacto, etc.
   */
  const getAuthHeaders = () => {
    const savedToken = localStorage.getItem('token')

    if (!savedToken) {
      return {}
    }

    return {
      Authorization: `Token ${savedToken}`,
    }
  }

  /**
   * Actualiza los datos locales del usuario sin recargar la aplicación.
   *
   * Se usa, por ejemplo, después de editar el perfil. En lugar de volver a
   * iniciar sesión, se fusionan los nuevos datos con los que ya había.
   */
  const updateLocalUser = (newUserData) => {
    user.value = {
      ...(user.value || {}),
      ...newUserData,
    }
  }

  /**
   * API pública del composable.
   *
   * Todo lo que se devuelve aquí puede ser usado por componentes y vistas Vue.
   */
  return {
    user,
    isAuthenticated,
    loadingAuth,
    token,
    restoreSession,
    login,
    logout,
    getAuthHeaders,
    updateLocalUser,
  }
}