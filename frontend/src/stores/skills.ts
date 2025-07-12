import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { skillApi, userApi, type Skill } from '@/services/api'
import { useAuthStore } from './auth'

export const useSkillsStore = defineStore('skills', () => {
  // State
  const skills = ref<Skill[]>([])
  const categories = ref<string[]>([])
  const userSkillsOffered = ref<Skill[]>([])
  const userSkillsWanted = ref<Skill[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  const fetchSkills = async (params?: {
    category?: string
    search?: string
    limit?: number
    offset?: number
  }) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      skills.value = await skillApi.getSkills(authStore.token, params)
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to fetch skills'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createSkill = async (skillData: {
    name: string
    category?: string
    description?: string
  }) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      loading.value = true
      error.value = null
      
      const newSkill = await skillApi.createSkill(authStore.token, skillData)
      skills.value.push(newSkill)
      
      return newSkill
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to create skill'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCategories = async () => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      categories.value = await skillApi.getSkillCategories(authStore.token)
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to fetch categories'
      throw err
    }
  }

  const fetchUserSkills = async (userId?: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    const targetUserId = userId || authStore.user?.id
    if (!targetUserId) throw new Error('No user ID available')

    try {
      loading.value = true
      error.value = null
      
      const [offered, wanted] = await Promise.all([
        userApi.getUserSkillsOffered(authStore.token, targetUserId),
        userApi.getUserSkillsWanted(authStore.token, targetUserId),
      ])
      
      if (!userId || userId === authStore.user?.id) {
        userSkillsOffered.value = offered
        userSkillsWanted.value = wanted
      }
      
      return { offered, wanted }
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to fetch user skills'
      throw err
    } finally {
      loading.value = false
    }
  }

  const addSkillOffered = async (skillId: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      await userApi.addSkillOffered(authStore.token, skillId)
      
      // Find and add the skill to offered skills
      const skill = skills.value.find(s => s.id === skillId)
      if (skill && !userSkillsOffered.value.find(s => s.id === skillId)) {
        userSkillsOffered.value.push(skill)
      }
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to add skill'
      throw err
    }
  }

  const removeSkillOffered = async (skillId: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      await userApi.removeSkillOffered(authStore.token, skillId)
      
      // Remove the skill from offered skills
      userSkillsOffered.value = userSkillsOffered.value.filter(s => s.id !== skillId)
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to remove skill'
      throw err
    }
  }

  const addSkillWanted = async (skillId: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      await userApi.addSkillWanted(authStore.token, skillId)
      
      // Find and add the skill to wanted skills
      const skill = skills.value.find(s => s.id === skillId)
      if (skill && !userSkillsWanted.value.find(s => s.id === skillId)) {
        userSkillsWanted.value.push(skill)
      }
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to add skill'
      throw err
    }
  }

  const removeSkillWanted = async (skillId: number) => {
    const authStore = useAuthStore()
    if (!authStore.token) throw new Error('Not authenticated')

    try {
      await userApi.removeSkillWanted(authStore.token, skillId)
      
      // Remove the skill from wanted skills
      userSkillsWanted.value = userSkillsWanted.value.filter(s => s.id !== skillId)
    } catch (err: any) {
      error.value = err.data?.detail || 'Failed to remove skill'
      throw err
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    skills: computed(() => skills.value),
    categories: computed(() => categories.value),
    userSkillsOffered: computed(() => userSkillsOffered.value),
    userSkillsWanted: computed(() => userSkillsWanted.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    
    // Actions
    fetchSkills,
    createSkill,
    fetchCategories,
    fetchUserSkills,
    addSkillOffered,
    removeSkillOffered,
    addSkillWanted,
    removeSkillWanted,
    clearError,
  }
})
