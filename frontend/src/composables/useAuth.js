import { computed, ref } from 'vue'

// Estado global del usuario en el front-end.
const user = ref(null)
const isAuthenticated = ref(false)
const loadingAuth = ref(false)

// Base URL de la API, configurable desde variables de entorno.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useAuth() {
  // Computed para leer siempre el token más reciente de localStorage.
  const token = computed(() => localStorage.getItem('token'))

  /**
   * Restaura la sesión cuando se recarga la página.
   *
   * Si hay un token guardado, consulta /api/me/ para obtener los datos
   * del usuario actual y actualiza el estado global.
   */
  const restoreSession = async () => {
    const savedToken = localStorage.getItem('token')

    if (!savedToken) {
      // Si no hay token, no hay sesión activa.
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

      if (!response.ok) {
        // Si el token es inválido, borramos la sesión local.
        throw new Error('Sesión no válida')
      }

      const data = await response.json()

      user.value = data
      isAuthenticated.value = true
    } catch (error) {
      console.error('Error restaurando sesión:', error)

      // Si algo falla, limpiamos el token local y cerramos sesión.
      localStorage.removeItem('token')
      user.value = null
      isAuthenticated.value = false
    } finally {
      loadingAuth.value = false
    }
  }

  /**
   * Guarda el token y actualiza el estado de autenticación local.
   *
   * El usuario puede venir ya cargado desde la respuesta de login.
   */
  const login = (newToken, userData = null) => {
    localStorage.setItem('token', newToken)
    user.value = userData
    isAuthenticated.value = true
  }

  /**
   * Cierra sesión localmente y elimina el token de localStorage.
   */
  const logout = () => {
    localStorage.removeItem('token')
    user.value = null
    isAuthenticated.value = false
  }

  /**
   * Devuelve las cabeceras HTTP necesarias para las peticiones autenticadas.
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
   * Actualiza solo los datos del usuario en memoria sin tocar el token.
   * Útil tras editar el perfil o recibir nuevos datos del backend.
   */
  const updateLocalUser = (newUserData) => {
    user.value = {
      ...(user.value || {}),
      ...newUserData,
    }
  }

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