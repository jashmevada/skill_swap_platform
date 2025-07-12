<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSwapsStore } from '@/stores/swaps'
import { useSkillsStore } from '@/stores/skills'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

const swapsStore = useSwapsStore()
const skillsStore = useSkillsStore()
const authStore = useAuthStore()
const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const activeTab = ref(0)

const tabs = [
  { label: 'Sent Requests', icon: 'pi pi-send' },
  { label: 'Received Requests', icon: 'pi pi-inbox' },
  { label: 'Completed', icon: 'pi pi-check-circle' }
]

const sentSwaps = computed(() => 
  swapsStore.swaps.filter(swap => swap.requester_id === authStore.user?.id)
)

const receivedSwaps = computed(() => 
  swapsStore.swaps.filter(swap => swap.requested_id === authStore.user?.id)
)

const completedSwaps = computed(() => 
  swapsStore.swaps.filter(swap => 
    (swap.requester_id === authStore.user?.id || swap.requested_id === authStore.user?.id) &&
    swap.status === 'completed'
  )
)

const pendingReceived = computed(() => 
  receivedSwaps.value.filter(swap => swap.status === 'pending')
)

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'accepted': return 'success'
    case 'rejected': return 'danger'
    case 'completed': return 'info'
    default: return 'secondary'
  }
}

const getSkillName = (skillId: number) => {
  const skill = skillsStore.skills.find(s => s.id === skillId)
  return skill?.name || 'Unknown Skill'
}

const handleAcceptSwap = async (swapId: number) => {
  try {
    await swapsStore.respondToSwapRequest(swapId, 'accepted')
    toast.add({
      severity: 'success',
      summary: 'Swap Accepted',
      detail: 'The swap request has been accepted',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to accept swap request',
      life: 3000
    })
  }
}

const handleRejectSwap = (swapId: number) => {
  confirm.require({
    message: 'Are you sure you want to reject this swap request?',
    header: 'Confirm Rejection',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await swapsStore.respondToSwapRequest(swapId, 'rejected')
        toast.add({
          severity: 'info',
          summary: 'Swap Rejected',
          detail: 'The swap request has been rejected',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to reject swap request',
          life: 3000
        })
      }
    }
  })
}

const handleMarkCompleted = async (swapId: number) => {
  try {
    await swapsStore.respondToSwapRequest(swapId, 'completed')
    toast.add({
      severity: 'success',
      summary: 'Swap Completed',
      detail: 'The swap has been marked as completed',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to mark swap as completed',
      life: 3000
    })
  }
}

const loadUserSwaps = async () => {
  if (!authStore.user) return
  
  loading.value = true
  try {
    await Promise.all([
      swapsStore.fetchUserSwaps(authStore.user.id),
      skillsStore.fetchSkills({ page: 1, size: 1000 })
    ])
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load swap requests',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserSwaps()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900">My Swap Requests</h1>
      <p class="text-gray-600 mt-2">Manage your skill exchange requests</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-blue-600">{{ sentSwaps.length }}</div>
            <div class="text-gray-600">Sent Requests</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-green-600">{{ receivedSwaps.length }}</div>
            <div class="text-gray-600">Received Requests</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-orange-600">{{ pendingReceived.length }}</div>
            <div class="text-gray-600">Pending Action</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-purple-600">{{ completedSwaps.length }}</div>
            <div class="text-gray-600">Completed</div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Tabs -->
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

          <!-- Tab Content -->
          <div v-if="loading" class="text-center py-8">
            <i class="pi pi-spinner pi-spin text-2xl text-primary"></i>
            <p class="text-gray-600 mt-2">Loading swap requests...</p>
          </div>

          <!-- Sent Requests Tab -->
          <div v-else-if="activeTab === 0" class="space-y-4">
            <div v-if="sentSwaps.length === 0" class="text-center py-8">
              <i class="pi pi-send text-4xl text-gray-400"></i>
              <h3 class="text-lg font-semibold text-gray-600 mt-4">No sent requests</h3>
              <p class="text-gray-500">You haven't sent any swap requests yet</p>
            </div>
            
            <Card 
              v-for="swap in sentSwaps"
              :key="swap.id"
              class="border-l-4 border-l-blue-500"
            >
              <template #content>
                <div class="space-y-4">
                  <div class="flex justify-between items-start">
                    <div class="space-y-2">
                      <div class="flex items-center gap-2">
                        <h3 class="font-semibold text-gray-900">Request #{{ swap.id }}</h3>
                        <Tag 
                          :value="swap.status"
                          :severity="getStatusSeverity(swap.status)"
                        />
                      </div>
                      <div class="text-sm text-gray-500">
                        Sent on {{ new Date(swap.created_at).toLocaleDateString() }}
                      </div>
                    </div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                      <h4 class="font-medium text-gray-700">You Offered:</h4>
                      <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <span class="font-medium text-blue-900">
                          {{ getSkillName(swap.skill_offered_id) }}
                        </span>
                      </div>
                    </div>

                    <div class="space-y-2">
                      <h4 class="font-medium text-gray-700">You Requested:</h4>
                      <div class="p-3 bg-green-50 rounded-lg border border-green-200">
                        <span class="font-medium text-green-900">
                          {{ getSkillName(swap.skill_wanted_id) }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div v-if="swap.message" class="space-y-2">
                    <h4 class="font-medium text-gray-700">Your Message:</h4>
                    <div class="p-3 bg-gray-50 rounded-lg border">
                      <p class="text-gray-700">{{ swap.message }}</p>
                    </div>
                  </div>

                  <div v-if="swap.status === 'accepted'" class="flex justify-end">
                    <Button
                      @click="handleMarkCompleted(swap.id)"
                      icon="pi pi-check"
                      label="Mark as Completed"
                      size="small"
                      severity="success"
                    />
                  </div>
                </div>
              </template>
            </Card>
          </div>

          <!-- Received Requests Tab -->
          <div v-else-if="activeTab === 1" class="space-y-4">
            <div v-if="receivedSwaps.length === 0" class="text-center py-8">
              <i class="pi pi-inbox text-4xl text-gray-400"></i>
              <h3 class="text-lg font-semibold text-gray-600 mt-4">No received requests</h3>
              <p class="text-gray-500">You haven't received any swap requests yet</p>
            </div>
            
            <Card 
              v-for="swap in receivedSwaps"
              :key="swap.id"
              class="border-l-4 border-l-green-500"
            >
              <template #content>
                <div class="space-y-4">
                  <div class="flex justify-between items-start">
                    <div class="space-y-2">
                      <div class="flex items-center gap-2">
                        <h3 class="font-semibold text-gray-900">Request #{{ swap.id }}</h3>
                        <Tag 
                          :value="swap.status"
                          :severity="getStatusSeverity(swap.status)"
                        />
                      </div>
                      <div class="text-sm text-gray-500">
                        Received on {{ new Date(swap.created_at).toLocaleDateString() }}
                      </div>
                    </div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                      <h4 class="font-medium text-gray-700">They Offered:</h4>
                      <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <span class="font-medium text-blue-900">
                          {{ getSkillName(swap.skill_offered_id) }}
                        </span>
                      </div>
                    </div>

                    <div class="space-y-2">
                      <h4 class="font-medium text-gray-700">They Want:</h4>
                      <div class="p-3 bg-green-50 rounded-lg border border-green-200">
                        <span class="font-medium text-green-900">
                          {{ getSkillName(swap.skill_wanted_id) }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div v-if="swap.message" class="space-y-2">
                    <h4 class="font-medium text-gray-700">Their Message:</h4>
                    <div class="p-3 bg-gray-50 rounded-lg border">
                      <p class="text-gray-700">{{ swap.message }}</p>
                    </div>
                  </div>

                  <div v-if="swap.status === 'pending'" class="flex gap-2 justify-end">
                    <Button
                      @click="handleAcceptSwap(swap.id)"
                      icon="pi pi-check"
                      label="Accept"
                      size="small"
                      severity="success"
                    />
                    <Button
                      @click="handleRejectSwap(swap.id)"
                      icon="pi pi-times"
                      label="Reject"
                      size="small"
                      severity="danger"
                      outlined
                    />
                  </div>

                  <div v-else-if="swap.status === 'accepted'" class="flex justify-end">
                    <Button
                      @click="handleMarkCompleted(swap.id)"
                      icon="pi pi-check"
                      label="Mark as Completed"
                      size="small"
                      severity="success"
                    />
                  </div>
                </div>
              </template>
            </Card>
          </div>

          <!-- Completed Swaps Tab -->
          <div v-else-if="activeTab === 2" class="space-y-4">
            <div v-if="completedSwaps.length === 0" class="text-center py-8">
              <i class="pi pi-check-circle text-4xl text-gray-400"></i>
              <h3 class="text-lg font-semibold text-gray-600 mt-4">No completed swaps</h3>
              <p class="text-gray-500">You haven't completed any skill swaps yet</p>
            </div>
            
            <Card 
              v-for="swap in completedSwaps"
              :key="swap.id"
              class="border-l-4 border-l-purple-500"
            >
              <template #content>
                <div class="space-y-4">
                  <div class="flex justify-between items-start">
                    <div class="space-y-2">
                      <div class="flex items-center gap-2">
                        <h3 class="font-semibold text-gray-900">Completed Swap #{{ swap.id }}</h3>
                        <Tag value="completed" severity="info" />
                      </div>
                      <div class="text-sm text-gray-500">
                        Completed on {{ new Date(swap.updated_at).toLocaleDateString() }}
                      </div>
                    </div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                      <h4 class="font-medium text-gray-700">
                        {{ swap.requester_id === authStore.user?.id ? 'You Offered:' : 'They Offered:' }}
                      </h4>
                      <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <span class="font-medium text-blue-900">
                          {{ getSkillName(swap.skill_offered_id) }}
                        </span>
                      </div>
                    </div>

                    <div class="space-y-2">
                      <h4 class="font-medium text-gray-700">
                        {{ swap.requester_id === authStore.user?.id ? 'You Received:' : 'They Received:' }}
                      </h4>
                      <div class="p-3 bg-green-50 rounded-lg border border-green-200">
                        <span class="font-medium text-green-900">
                          {{ getSkillName(swap.skill_wanted_id) }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="flex justify-end">
                    <Button
                      icon="pi pi-star"
                      label="Leave Review"
                      size="small"
                      outlined
                    />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>
