import { ofetch } from 'ofetch'

const API_BASE = 'http://127.0.0.1:8000/api'

// Create API instance
export const api = ofetch.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  location?: string
  bio?: string
  availability?: string
  is_public: boolean
  profile_photo?: string
  is_active: boolean
  is_admin: boolean
  created_at: string
}

export interface Skill {
  id: number
  name: string
  category?: string
  description?: string
  is_approved: boolean
  created_at: string
}

export interface SwapRequest {
  id: number
  requester_id: number
  requested_id: number
  skill_offered_id: number
  skill_wanted_id: number
  message?: string
  status: string
  created_at: string
  updated_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

// API Functions
export const authApi = {
  async login(username: string, password: string): Promise<LoginResponse> {
    return api('/auth/login', {
      method: 'POST',
      body: { username, password },
    })
  },

  async register(userData: {
    email: string
    username: string
    password: string
    full_name?: string
    location?: string
    bio?: string
  }): Promise<User> {
    return api('/auth/register', {
      method: 'POST',
      body: userData,
    })
  },

  async logout(): Promise<{ message: string }> {
    return api('/auth/logout', {
      method: 'POST',
    })
  },
}

export const userApi = {
  async getCurrentUser(token: string): Promise<User> {
    return api('/users/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async updateCurrentUser(token: string, userData: Partial<User>): Promise<User> {
    return api('/users/me', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: userData,
    })
  },

  async searchUsers(token: string, params?: {
    skill?: string
    location?: string
    category?: string
    limit?: number
    offset?: number
  }): Promise<User[]> {
    const searchParams = new URLSearchParams()
    if (params?.skill) searchParams.append('skill', params.skill)
    if (params?.location) searchParams.append('location', params.location)
    if (params?.category) searchParams.append('category', params.category)
    if (params?.limit) searchParams.append('limit', params.limit.toString())
    if (params?.offset) searchParams.append('offset', params.offset.toString())

    return api(`/users/search?${searchParams.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async getUserById(token: string, userId: number): Promise<User> {
    return api(`/users/${userId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async getUserSkillsOffered(token: string, userId: number): Promise<Skill[]> {
    return api(`/users/${userId}/skills/offered`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async getUserSkillsWanted(token: string, userId: number): Promise<Skill[]> {
    return api(`/users/${userId}/skills/wanted`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async addSkillOffered(token: string, skillId: number): Promise<{ message: string }> {
    return api(`/users/me/skills/offered/${skillId}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async removeSkillOffered(token: string, skillId: number): Promise<{ message: string }> {
    return api(`/users/me/skills/offered/${skillId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async addSkillWanted(token: string, skillId: number): Promise<{ message: string }> {
    return api(`/users/me/skills/wanted/${skillId}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async removeSkillWanted(token: string, skillId: number): Promise<{ message: string }> {
    return api(`/users/me/skills/wanted/${skillId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },
}

export const skillApi = {
  async getSkills(token: string, params?: {
    category?: string
    search?: string
    limit?: number
    offset?: number
  }): Promise<Skill[]> {
    const searchParams = new URLSearchParams()
    if (params?.category) searchParams.append('category', params.category)
    if (params?.search) searchParams.append('search', params.search)
    if (params?.limit) searchParams.append('limit', params.limit.toString())
    if (params?.offset) searchParams.append('offset', params.offset.toString())

    return api(`/skills/?${searchParams.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async createSkill(token: string, skillData: {
    name: string
    category?: string
    description?: string
  }): Promise<Skill> {
    return api('/skills/', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: skillData,
    })
  },

  async getSkillCategories(token: string): Promise<string[]> {
    return api('/skills/categories', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },
}

export const swapApi = {
  async getSwapRequests(token: string, params?: {
    status_filter?: string
    type_filter?: string
  }): Promise<SwapRequest[]> {
    const searchParams = new URLSearchParams()
    if (params?.status_filter) searchParams.append('status_filter', params.status_filter)
    if (params?.type_filter) searchParams.append('type_filter', params.type_filter)

    return api(`/swaps/?${searchParams.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async createSwapRequest(token: string, requestData: {
    requested_id: number
    skill_offered_id: number
    skill_wanted_id: number
    message?: string
  }): Promise<SwapRequest> {
    return api('/swaps/', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: requestData,
    })
  },

  async updateSwapRequest(token: string, requestId: number, updateData: {
    status: string
    message?: string
  }): Promise<SwapRequest> {
    return api(`/swaps/${requestId}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: updateData,
    })
  },

  async deleteSwapRequest(token: string, requestId: number): Promise<{ message: string }> {
    return api(`/swaps/${requestId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },
}
