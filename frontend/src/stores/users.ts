import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi, type User } from '@/services/api'
import { useAuthStore } from './auth'

export const useUsersStore = defineStore('users', () => {
  // State
  const users = ref<User[]>([])
  const selectedUser = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  const searchUsers = async (params?: {
    skill?: string
    location?: string
    category?: string
    limit?: number
    offset?: number
  }) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      users.value = await userApi.searchUsers(authStore.token, params)
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to search users'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getUserById = async (userId: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      const user = await userApi.getUserById(authStore.token, userId)
      selectedUser.value = user
      
      return user
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to fetch user'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearSelectedUser = () => {
    selectedUser.value = null
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    users: computed(() => users.value),
    selectedUser: computed(() => selectedUser.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    
    // Actions
    searchUsers,
    getUserById,
    clearSelectedUser,
    clearError,
  }
})
