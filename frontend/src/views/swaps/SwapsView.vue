<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSwapsStore } from '@/stores/swaps'
import { useSkillsStore } from '@/stores/skills'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const swapsStore = useSwapsStore()
const skillsStore = useSkillsStore()
const authStore = useAuthStore()
const toast = useToast()

const loading = ref(false)
const statusFilter = ref('')
const searchQuery = ref('')

const statusOptions = [
  { label: 'All Status', value: '' },
  { label: 'Pending', value: 'pending' },
  { label: 'Accepted', value: 'accepted' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'Completed', value: 'completed' }
]

const filteredSwaps = computed(() => {
  let swaps = [...swapsStore.swaps]

  // Filter by status
  if (statusFilter.value) {
    swaps = swaps.filter(swap => swap.status === statusFilter.value)
  }

  // Filter by search query (could include skill names, usernames, etc.)
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    swaps = swaps.filter(swap => 
      // This would need to be expanded based on the actual data structure
      swap.message?.toLowerCase().includes(query) ||
      swap.status.toLowerCase().includes(query)
    )
  }

  return swaps
})

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

const loadSwaps = async () => {
  loading.value = true
  try {
    await swapsStore.fetchSwaps()
    // Also load skills to display skill names
    await skillsStore.fetchSkills({ page: 1, size: 1000 })
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

const clearFilters = () => {
  statusFilter.value = ''
  searchQuery.value = ''
}

onMounted(() => {
  loadSwaps()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Skill Swap Requests</h1>
        <p class="text-gray-600 mt-2">Browse and manage skill exchange requests</p>
      </div>
      <Button
        v-if="authStore.isAuthenticated"
        @click="router.push('/my-swaps')"
        icon="pi pi-user"
        label="My Swaps"
        outlined
      />
    </div>

    <!-- Filters -->
    <Card>
      <template #content>
        <div class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="md:col-span-2">
              <div class="p-input-icon-left w-full">
                <i class="pi pi-search"></i>
                <InputText
                  v-model="searchQuery"
                  placeholder="Search swaps..."
                  class="w-full"
                />
              </div>
            </div>
            
            <Dropdown
              v-model="statusFilter"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Filter by status"
              class="w-full"
            />
          </div>
          
          <div class="flex justify-between items-center">
            <div class="text-sm text-gray-600">
              {{ filteredSwaps.length }} swap requests found
            </div>
            <Button
              @click="clearFilters"
              icon="pi pi-filter-slash"
              label="Clear Filters"
              size="small"
              outlined
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Swaps List -->
    <div v-if="loading" class="text-center py-8">
      <i class="pi pi-spinner pi-spin text-2xl text-primary"></i>
      <p class="text-gray-600 mt-2">Loading swap requests...</p>
    </div>
    
    <div v-else-if="filteredSwaps.length === 0" class="text-center py-12">
      <Card>
        <template #content>
          <div class="space-y-4">
            <i class="pi pi-sync text-4xl text-gray-400"></i>
            <h3 class="text-lg font-semibold text-gray-600">No swap requests found</h3>
            <p class="text-gray-500">
              {{ statusFilter || searchQuery ? 'Try adjusting your search criteria' : 'Be the first to create a swap request!' }}
            </p>
            <Button
              v-if="authStore.isAuthenticated"
              @click="router.push('/skills')"
              icon="pi pi-plus"
              label="Browse Skills"
            />
          </div>
        </template>
      </Card>
    </div>
    
    <div v-else class="space-y-4">
      <Card 
        v-for="swap in filteredSwaps"
        :key="swap.id"
        class="hover:shadow-md transition-shadow"
      >
        <template #content>
          <div class="space-y-4">
            <!-- Swap Header -->
            <div class="flex justify-between items-start">
              <div class="space-y-2">
                <div class="flex items-center gap-2">
                  <h3 class="text-lg font-semibold text-gray-900">Skill Exchange Request</h3>
                  <Tag 
                    :value="swap.status"
                    :severity="getStatusSeverity(swap.status)"
                  />
                </div>
                <div class="text-sm text-gray-500">
                  {{ new Date(swap.created_at).toLocaleString() }}
                </div>
              </div>
            </div>

            <!-- Skills Exchange Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-2">
                <h4 class="font-medium text-gray-700">Skill Offered:</h4>
                <div class="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <span class="font-medium text-blue-900">
                    {{ getSkillName(swap.skill_offered_id) }}
                  </span>
                </div>
              </div>

              <div class="space-y-2">
                <h4 class="font-medium text-gray-700">Skill Wanted:</h4>
                <div class="p-3 bg-green-50 rounded-lg border border-green-200">
                  <span class="font-medium text-green-900">
                    {{ getSkillName(swap.skill_wanted_id) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Message -->
            <div v-if="swap.message" class="space-y-2">
              <h4 class="font-medium text-gray-700">Message:</h4>
              <div class="p-3 bg-gray-50 rounded-lg border">
                <p class="text-gray-700">{{ swap.message }}</p>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-between items-center pt-4 border-t">
              <div class="text-sm text-gray-500">
                <span>Request ID: #{{ swap.id }}</span>
              </div>
              
              <div class="flex gap-2">
                <Button
                  icon="pi pi-eye"
                  label="View Details"
                  size="small"
                  outlined
                />
                <Button
                  v-if="authStore.isAuthenticated && swap.requested_id === authStore.user?.id && swap.status === 'pending'"
                  icon="pi pi-check"
                  label="Accept"
                  size="small"
                  severity="success"
                />
                <Button
                  v-if="authStore.isAuthenticated && swap.requested_id === authStore.user?.id && swap.status === 'pending'"
                  icon="pi pi-times"
                  label="Reject"
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

    <!-- Load More -->
    <div v-if="filteredSwaps.length > 0" class="text-center">
      <Button
        icon="pi pi-refresh"
        label="Load More"
        outlined
        @click="loadSwaps"
      />
    </div>
  </div>
</template>
