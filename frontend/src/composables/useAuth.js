import { ref, computed } from 'vue'

const user = ref(null)
const isAuthenticated = ref(false)
const loadingAuth = ref(false)

const API_URL = import.meta.env.VITE_API_URL || 'https://erasmusstay-production.up.railway.app'

export function useAuth() {
  const token = computed(() => localStorage.getItem('token'))

  const restoreSession = async () => {
    const savedToken = localStorage.getItem('token')

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

      if (!response.ok) {
        throw new Error('Sesión no válida')
      }

      const data = await response.json()

      user.value = data
      isAuthenticated.value = true
    } catch (error) {
      console.error('Error restaurando sesión:', error)

      localStorage.removeItem('token')
      user.value = null
      isAuthenticated.value = false
    } finally {
      loadingAuth.value = false
    }
  }

  const login = (newToken, userData = null) => {
    localStorage.setItem('token', newToken)
    user.value = userData
    isAuthenticated.value = true
  }

  const logout = () => {
    localStorage.removeItem('token')
    user.value = null
    isAuthenticated.value = false
  }

  const getAuthHeaders = () => {
    const savedToken = localStorage.getItem('token')

    if (!savedToken) {
      return {}
    }

    return {
      Authorization: `Token ${savedToken}`,
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
  }
}