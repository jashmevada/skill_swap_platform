<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUsersStore } from '@/stores/users'
import { useSkillsStore } from '@/stores/skills'
import { useSwapsStore } from '@/stores/swaps'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

const usersStore = useUsersStore()
const skillsStore = useSkillsStore()
const swapsStore = useSwapsStore()
const authStore = useAuthStore()
const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const activeTab = ref(0)

const tabs = [
  { label: 'Dashboard', icon: 'pi pi-chart-bar' },
  { label: 'Users', icon: 'pi pi-users' },
  { label: 'Skills', icon: 'pi pi-star' },
  { label: 'Swaps', icon: 'pi pi-sync' },
  { label: 'Messages', icon: 'pi pi-envelope' }
]

// Stats
const stats = computed(() => ({
  totalUsers: usersStore.users.length,
  totalSkills: skillsStore.skills.length,
  pendingSkills: skillsStore.skills.filter(s => !s.is_approved).length,
  totalSwaps: swapsStore.swaps.length,
  pendingSwaps: swapsStore.swaps.filter(s => s.status === 'pending').length
}))

const pendingSkills = computed(() => 
  skillsStore.skills.filter(skill => !skill.is_approved)
)

const recentUsers = computed(() => 
  [...usersStore.users]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 10)
)

const recentSwaps = computed(() => 
  [...swapsStore.swaps]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 10)
)

// Actions
const handleApproveSkill = async (skillId: number) => {
  try {
    await skillsStore.updateSkill(skillId, { is_approved: true })
    toast.add({
      severity: 'success',
      summary: 'Skill Approved',
      detail: 'The skill has been approved successfully',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to approve skill',
      life: 3000
    })
  }
}

const handleRejectSkill = (skillId: number) => {
  confirm.require({
    message: 'Are you sure you want to reject this skill?',
    header: 'Confirm Rejection',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await skillsStore.deleteSkill(skillId)
        toast.add({
          severity: 'info',
          summary: 'Skill Rejected',
          detail: 'The skill has been rejected and removed',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to reject skill',
          life: 3000
        })
      }
    }
  })
}

const handleToggleUserStatus = async (userId: number, currentStatus: boolean) => {
  try {
    await usersStore.updateUser(userId, { is_active: !currentStatus })
    toast.add({
      severity: 'success',
      summary: 'User Status Updated',
      detail: `User has been ${!currentStatus ? 'activated' : 'deactivated'}`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update user status',
      life: 3000
    })
  }
}

const getSwapStatusSeverity = (status: string) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'accepted': return 'success'
    case 'rejected': return 'danger'
    case 'completed': return 'info'
    default: return 'secondary'
  }
}

const loadAdminData = async () => {
  loading.value = true
  try {
    await Promise.all([
      usersStore.fetchUsers(),
      skillsStore.fetchSkills({ page: 1, size: 1000 }),
      swapsStore.fetchSwaps()
    ])
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load admin data',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Check if user is admin
  if (!authStore.user?.is_admin) {
    toast.add({
      severity: 'error',
      summary: 'Access Denied',
      detail: 'You do not have admin privileges',
      life: 3000
    })
    return
  }
  
  loadAdminData()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p class="text-gray-600 mt-2">Manage users, skills, and platform activity</p>
      </div>
      <div class="flex items-center gap-2">
        <i class="pi pi-shield text-primary"></i>
        <span class="text-sm font-medium text-primary">Administrator</span>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-blue-600">{{ stats.totalUsers }}</div>
            <div class="text-gray-600 text-sm">Total Users</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-green-600">{{ stats.totalSkills }}</div>
            <div class="text-gray-600 text-sm">Total Skills</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-orange-600">{{ stats.pendingSkills }}</div>
            <div class="text-gray-600 text-sm">Pending Skills</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-purple-600">{{ stats.totalSwaps }}</div>
            <div class="text-gray-600 text-sm">Total Swaps</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-red-600">{{ stats.pendingSwaps }}</div>
            <div class="text-gray-600 text-sm">Pending Swaps</div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Admin Tabs -->
    <Card>
      <template #content>
        <div class="space-y-6">
          <!-- Tab Navigation -->
          <div class="flex border-b">
            <button
              v-for="(tab, index) in tabs"
              :key="index"
              @click="activeTab = index"
              :class="[
                'px-4 py-2 font-medium text-sm border-b-2 transition-colors',
                activeTab === index
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              <i :class="tab.icon" class="mr-2"></i>
              {{ tab.label }}
            </button>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="text-center py-8">
            <i class="pi pi-spinner pi-spin text-2xl text-primary"></i>
            <p class="text-gray-600 mt-2">Loading admin data...</p>
          </div>

          <!-- Dashboard Tab -->
          <div v-else-if="activeTab === 0" class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Recent Users -->
              <Card>
                <template #header>
                  <h3 class="text-lg font-semibold text-gray-900 p-6 pb-0">Recent Users</h3>
                </template>
                <template #content>
                  <div class="space-y-3">
                    <div
                      v-for="user in recentUsers"
                      :key="user.id"
                      class="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div class="flex items-center gap-3">
                        <Avatar
                          :label="user.full_name?.charAt(0) || user.username?.charAt(0) || 'U'"
                          size="small"
                        />
                        <div>
                          <div class="font-medium">{{ user.full_name || user.username }}</div>
                          <div class="text-sm text-gray-500">@{{ user.username }}</div>
                        </div>
                      </div>
                      <Tag 
                        :value="user.is_active ? 'Active' : 'Inactive'"
                        :severity="user.is_active ? 'success' : 'danger'"
                      />
                    </div>
                  </div>
                </template>
              </Card>

              <!-- Pending Skills -->
              <Card>
                <template #header>
                  <div class="flex justify-between items-center p-6 pb-0">
                    <h3 class="text-lg font-semibold text-gray-900">Pending Skills</h3>
                    <Badge :value="pendingSkills.length" severity="warning" />
                  </div>
                </template>
                <template #content>
                  <div v-if="pendingSkills.length === 0" class="text-center py-4">
                    <p class="text-gray-500">No pending skills</p>
                  </div>
                  <div v-else class="space-y-3">
                    <div
                      v-for="skill in pendingSkills.slice(0, 5)"
                      :key="skill.id"
                      class="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div>
                        <div class="font-medium">{{ skill.name }}</div>
                        <div v-if="skill.category" class="text-sm text-gray-500">{{ skill.category }}</div>
                      </div>
                      <div class="flex gap-1">
                        <Button
                          @click="handleApproveSkill(skill.id)"
                          icon="pi pi-check"
                          size="small"
                          severity="success"
                        />
                        <Button
                          @click="handleRejectSkill(skill.id)"
                          icon="pi pi-times"
                          size="small"
                          severity="danger"
                          outlined
                        />
                      </div>
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </div>

          <!-- Users Tab -->
          <div v-else-if="activeTab === 1" class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-semibold text-gray-900">User Management</h3>
              <div class="text-sm text-gray-600">{{ usersStore.users.length }} total users</div>
            </div>
            
            <div class="grid grid-cols-1 gap-4">
              <Card
                v-for="user in usersStore.users"
                :key="user.id"
                class="border-l-4 border-l-blue-500"
              >
                <template #content>
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                      <Avatar
                        :label="user.full_name?.charAt(0) || user.username?.charAt(0) || 'U'"
                        size="large"
                      />
                      <div>
                        <h4 class="font-semibold text-gray-900">{{ user.full_name || user.username }}</h4>
                        <p class="text-gray-600">{{ user.email }}</p>
                        <div class="flex items-center gap-2 mt-1">
                          <span class="text-sm text-gray-500">@{{ user.username }}</span>
                          <Tag 
                            :value="user.is_active ? 'Active' : 'Inactive'"
                            :severity="user.is_active ? 'success' : 'danger'"
                          />
                          <Tag 
                            v-if="user.is_admin"
                            value="Admin"
                            severity="info"
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div class="flex gap-2">
                      <Button
                        icon="pi pi-eye"
                        size="small"
                        outlined
                      />
                      <Button
                        @click="handleToggleUserStatus(user.id, user.is_active)"
                        :icon="user.is_active ? 'pi pi-ban' : 'pi pi-check'"
                        :label="user.is_active ? 'Deactivate' : 'Activate'"
                        :severity="user.is_active ? 'danger' : 'success'"
                        size="small"
                        outlined
                      />
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </div>

          <!-- Skills Tab -->
          <div v-else-if="activeTab === 2" class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-semibold text-gray-900">Skill Management</h3>
              <div class="text-sm text-gray-600">{{ stats.pendingSkills }} pending approval</div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card
                v-for="skill in skillsStore.skills"
                :key="skill.id"
                :class="[
                  'border-l-4',
                  skill.is_approved ? 'border-l-green-500' : 'border-l-orange-500'
                ]"
              >
                <template #content>
                  <div class="space-y-3">
                    <div class="flex justify-between items-start">
                      <div>
                        <h4 class="font-semibold text-gray-900">{{ skill.name }}</h4>
                        <p v-if="skill.category" class="text-sm text-gray-600">{{ skill.category }}</p>
                      </div>
                      <Tag 
                        :value="skill.is_approved ? 'Approved' : 'Pending'"
                        :severity="skill.is_approved ? 'success' : 'warning'"
                      />
                    </div>
                    
                    <p v-if="skill.description" class="text-gray-700 text-sm">{{ skill.description }}</p>
                    
                    <div class="text-xs text-gray-500">
                      Created {{ new Date(skill.created_at).toLocaleDateString() }}
                    </div>
                    
                    <div v-if="!skill.is_approved" class="flex gap-2">
                      <Button
                        @click="handleApproveSkill(skill.id)"
                        icon="pi pi-check"
                        label="Approve"
                        size="small"
                        severity="success"
                      />
                      <Button
                        @click="handleRejectSkill(skill.id)"
                        icon="pi pi-times"
                        label="Reject"
                        size="small"
                        severity="danger"
                        outlined
                      />
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </div>

          <!-- Swaps Tab -->
          <div v-else-if="activeTab === 3" class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-semibold text-gray-900">Swap Management</h3>
              <div class="text-sm text-gray-600">{{ stats.totalSwaps }} total swaps</div>
            </div>
            
            <div class="space-y-4">
              <Card
                v-for="swap in swapsStore.swaps"
                :key="swap.id"
                class="border-l-4 border-l-purple-500"
              >
                <template #content>
                  <div class="space-y-3">
                    <div class="flex justify-between items-start">
                      <div>
                        <h4 class="font-semibold text-gray-900">Swap Request #{{ swap.id }}</h4>
                        <div class="text-sm text-gray-600">
                          {{ new Date(swap.created_at).toLocaleDateString() }}
                        </div>
                      </div>
                      <Tag 
                        :value="swap.status"
                        :severity="getSwapStatusSeverity(swap.status)"
                      />
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span class="font-medium">Offered Skill ID:</span> {{ swap.skill_offered_id }}
                      </div>
                      <div>
                        <span class="font-medium">Requested Skill ID:</span> {{ swap.skill_wanted_id }}
                      </div>
                    </div>
                    
                    <div v-if="swap.message" class="text-sm">
                      <span class="font-medium">Message:</span> {{ swap.message }}
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </div>

          <!-- Messages Tab -->
          <div v-else-if="activeTab === 4" class="space-y-4">
            <div class="text-center py-12">
              <i class="pi pi-envelope text-4xl text-gray-400"></i>
              <h3 class="text-lg font-semibold text-gray-600 mt-4">Messages Feature</h3>
              <p class="text-gray-500">Admin messaging system coming soon</p>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>
