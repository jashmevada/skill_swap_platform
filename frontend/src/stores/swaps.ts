import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { swapApi, type SwapRequest } from '@/services/api'
import { useAuthStore } from './auth'

export const useSwapsStore = defineStore('swaps', () => {
  // State
  const swapRequests = ref<SwapRequest[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const sentRequests = computed(() => {
    const authStore = useAuthStore()
    return swapRequests.value.filter(request => request.requester_id === authStore.user?.id)
  })

  const receivedRequests = computed(() => {
    const authStore = useAuthStore()
    return swapRequests.value.filter(request => request.requested_id === authStore.user?.id)
  })

  const pendingRequests = computed(() => {
    return swapRequests.value.filter(request => request.status === 'pending')
  })

  const acceptedRequests = computed(() => {
    return swapRequests.value.filter(request => request.status === 'accepted')
  })

  const completedRequests = computed(() => {
    return swapRequests.value.filter(request => request.status === 'completed')
  })

  // Actions
  const fetchSwapRequests = async (params?: {
    status_filter?: string
    type_filter?: string
  }) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      swapRequests.value = await swapApi.getSwapRequests(authStore.token, params)
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to fetch swap requests'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createSwapRequest = async (requestData: {
    requested_id: number
    skill_offered_id: number
    skill_wanted_id: number
    message?: string
  }) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      const newRequest = await swapApi.createSwapRequest(authStore.token, requestData)
      swapRequests.value.push(newRequest)
      
      return newRequest
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to create swap request'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateSwapRequest = async (requestId: number, updateData: {
    status: string
    message?: string
  }) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      const updatedRequest = await swapApi.updateSwapRequest(authStore.token, requestId, updateData)
      
      // Update the request in the store
      const index = swapRequests.value.findIndex(request => request.id === requestId)
      if (index !== -1) {
        swapRequests.value[index] = updatedRequest
      }
      
      return updatedRequest
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to update swap request'
      throw err
    } finally {
      loading.value = false
    }
  }

  const acceptSwapRequest = async (requestId: number) => {
    return updateSwapRequest(requestId, { status: 'accepted' })
  }

  const rejectSwapRequest = async (requestId: number) => {
    return updateSwapRequest(requestId, { status: 'rejected' })
  }

  const cancelSwapRequest = async (requestId: number) => {
    return updateSwapRequest(requestId, { status: 'cancelled' })
  }

  const completeSwapRequest = async (requestId: number) => {
    return updateSwapRequest(requestId, { status: 'completed' })
  }

  const deleteSwapRequest = async (requestId: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      await swapApi.deleteSwapRequest(authStore.token, requestId)
      
      // Remove the request from the store
      swapRequests.value = swapRequests.value.filter(request => request.id !== requestId)
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to delete swap request'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    swapRequests: computed(() => swapRequests.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    
    // Getters
    sentRequests,
    receivedRequests,
    pendingRequests,
    acceptedRequests,
    completedRequests,
    
    // Actions
    fetchSwapRequests,
    createSwapRequest,
    updateSwapRequest,
    acceptSwapRequest,
    rejectSwapRequest,
    cancelSwapRequest,
    completeSwapRequest,
    deleteSwapRequest,
    clearError,
  }
})
