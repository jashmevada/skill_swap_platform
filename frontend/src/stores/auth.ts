import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi, type User } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const currentUser = computed(() => user.value)

  // Actions
  const login = async (username: string, password: string) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await authApi.login(username, password)
      token.value = response.access_token
      localStorage.setItem('auth_token', response.access_token)
      
      // Fetch user data
      await fetchCurrentUser()
      
      return true
    } catch (err: any) {
      error.value = err.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const register = async (userData: {
    email: string
    username: string
    password: string
    full_name?: string
    location?: string
    bio?: string
  }) => {
    try {
      loading.value = true
      error.value = null
      
      const newUser = await authApi.register(userData)
      
      // Auto-login after registration
      await login(userData.username, userData.password)
      
      return true
    } catch (err: any) {
      error.value = err.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
    }
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return

    try {
      user.value = await userApi.getCurrentUser(token.value)
    } catch (err: any) {
      if (err.status === 401) {
        // Token is invalid, logout
        await logout()
      }
      throw err
    }
  }

  const updateProfile = async (userData: Partial<User>) => {
    if (!token.value) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      const updatedUser = await userApi.updateCurrentUser(token.value, userData)
      user.value = updatedUser
      
      return true
    } catch (err: any) {
      error.value = err.data?.detail || 'Update failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  // Initialize auth state
  const initializeAuth = async () => {
    if (token.value) {
      try {
        await fetchCurrentUser()
      } catch {
        // If fetching user fails, clear the token
        await logout()
      }
    }
  }

  return {
    // State
    token: computed(() => token.value),
    user: currentUser,
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    
    // Getters
    isAuthenticated,
    
    // Actions
    login,
    register,
    logout,
    fetchCurrentUser,
    updateProfile,
    clearError,
    initializeAuth,
  }
})
