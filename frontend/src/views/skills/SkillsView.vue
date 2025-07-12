<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSkillsStore } from '@/stores/skills'
import { useAuthStore } from '@/stores/auth'
import { useSwapsStore } from '@/stores/swaps'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const skillsStore = useSkillsStore()
const authStore = useAuthStore()
const swapsStore = useSwapsStore()
const toast = useToast()

const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('name')
const loading = ref(false)
const showSwapDialog = ref(false)
const selectedSkill = ref(null)
const selectedOfferedSkill = ref('')
const swapMessage = ref('')

const pagination = ref({
  page: 1,
  size: 12,
  total: 0
})

const categories = computed(() => {
  const cats = [...new Set(skillsStore.skills.map(skill => skill.category).filter(Boolean))]
  return cats.map(cat => ({ label: cat, value: cat }))
})

const sortOptions = [
  { label: 'Name (A-Z)', value: 'name' },
  { label: 'Name (Z-A)', value: 'name_desc' },
  { label: 'Newest First', value: 'created_at_desc' },
  { label: 'Oldest First', value: 'created_at' }
]

const filteredAndSortedSkills = computed(() => {
  let skills = [...skillsStore.skills]

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    skills = skills.filter(skill => 
      skill.name.toLowerCase().includes(query) ||
      (skill.description && skill.description.toLowerCase().includes(query)) ||
      (skill.category && skill.category.toLowerCase().includes(query))
    )
  }

  // Filter by category
  if (selectedCategory.value) {
    skills = skills.filter(skill => skill.category === selectedCategory.value)
  }

  // Sort skills
  skills.sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'name_desc':
        return b.name.localeCompare(a.name)
      case 'created_at_desc':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'created_at':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      default:
        return 0
    }
  })

  return skills
})

const userSkills = computed(() => 
  skillsStore.userSkills.filter(skill => skill.user_id === authStore.user?.id)
)

const loadSkills = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size,
      search: searchQuery.value || undefined,
      category: selectedCategory.value || undefined,
      sort_by: sortBy.value
    }
    
    await skillsStore.fetchSkills(params)
    pagination.value.total = skillsStore.skills.length // This would come from API response
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load skills',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  sortBy.value = 'name'
  pagination.value.page = 1
}

const handleRequestSwap = (skill) => {
  if (!authStore.isAuthenticated) {
    toast.add({
      severity: 'warn',
      summary: 'Login Required',
      detail: 'Please log in to request skill swaps',
      life: 3000
    })
    router.push('/login')
    return
  }

  selectedSkill.value = skill
  showSwapDialog.value = true
}

const submitSwapRequest = async () => {
  if (!selectedOfferedSkill.value) {
    toast.add({
      severity: 'warn',
      summary: 'Skill Required',
      detail: 'Please select a skill to offer',
      life: 3000
    })
    return
  }

  try {
    const swapData = {
      skill_offered_id: parseInt(selectedOfferedSkill.value),
      skill_wanted_id: selectedSkill.value.id,
      message: swapMessage.value
    }

    await swapsStore.createSwapRequest(swapData)
    
    toast.add({
      severity: 'success',
      summary: 'Swap Request Sent',
      detail: 'Your swap request has been sent successfully',
      life: 3000
    })
    
    showSwapDialog.value = false
    selectedOfferedSkill.value = ''
    swapMessage.value = ''
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Request Failed',
      detail: 'Failed to send swap request',
      life: 3000
    })
  }
}

// Watch for changes and reload
watch([searchQuery, selectedCategory, sortBy], () => {
  pagination.value.page = 1
  loadSkills()
}, { debounce: 300 })

onMounted(async () => {
  await loadSkills()
  
  // Load user skills if authenticated
  if (authStore.isAuthenticated && authStore.user) {
    await skillsStore.fetchUserSkills(authStore.user.id)
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Browse Skills</h1>
        <p class="text-gray-600 mt-2">Discover skills offered by our community</p>
      </div>
      <Button
        v-if="authStore.isAuthenticated"
        @click="router.push('/my-skills')"
        icon="pi pi-user"
        label="My Skills"
        outlined
      />
    </div>

    <!-- Filters -->
    <Card>
      <template #content>
        <div class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="md:col-span-2">
              <div class="p-input-icon-left w-full">
                <i class="pi pi-search"></i>
                <InputText
                  v-model="searchQuery"
                  placeholder="Search skills..."
                  class="w-full"
                />
              </div>
            </div>
            
            <Dropdown
              v-model="selectedCategory"
              :options="categories"
              optionLabel="label"
              optionValue="value"
              placeholder="All Categories"
              showClear
              class="w-full"
            />
            
            <Dropdown
              v-model="sortBy"
              :options="sortOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Sort by"
              class="w-full"
            />
          </div>
          
          <div class="flex justify-between items-center">
            <div class="text-sm text-gray-600">
              {{ filteredAndSortedSkills.length }} skills found
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

    <!-- Skills Grid -->
    <div v-if="loading" class="text-center py-8">
      <i class="pi pi-spinner pi-spin text-2xl text-primary"></i>
      <p class="text-gray-600 mt-2">Loading skills...</p>
    </div>
    
    <div v-else-if="filteredAndSortedSkills.length === 0" class="text-center py-12">
      <i class="pi pi-search text-4xl text-gray-400 mb-4"></i>
      <h3 class="text-lg font-semibold text-gray-600 mb-2">No skills found</h3>
      <p class="text-gray-500">Try adjusting your search criteria</p>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card 
        v-for="skill in filteredAndSortedSkills"
        :key="skill.id"
        class="hover:shadow-lg transition-shadow h-full"
      >
        <template #content>
          <div class="space-y-4 h-full flex flex-col">
            <div class="flex-1">
              <div class="flex justify-between items-start mb-3">
                <h3 class="text-lg font-semibold text-gray-900">{{ skill.name }}</h3>
                <Tag 
                  v-if="skill.category"
                  :value="skill.category"
                  severity="secondary"
                />
              </div>
              
              <p v-if="skill.description" class="text-gray-600 text-sm line-clamp-3 mb-4">
                {{ skill.description }}
              </p>
              
              <div class="flex items-center gap-2 text-sm text-gray-500">
                <i class="pi pi-calendar"></i>
                <span>{{ new Date(skill.created_at).toLocaleDateString() }}</span>
              </div>
            </div>
            
            <div class="flex gap-2 mt-auto">
              <Button
                @click="handleRequestSwap(skill)"
                :disabled="!authStore.isAuthenticated"
                icon="pi pi-sync"
                label="Request Swap"
                size="small"
                class="flex-1"
              />
              <Button
                icon="pi pi-info-circle"
                size="small"
                outlined
                @click="router.push(`/users/${skill.user_id}`)"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Swap Request Dialog -->
    <Dialog
      v-model:visible="showSwapDialog"
      modal
      header="Request Skill Swap"
      :style="{ width: '500px' }"
    >
      <div v-if="selectedSkill" class="space-y-4">
        <div class="border rounded-lg p-4 bg-gray-50">
          <h4 class="font-semibold text-gray-900 mb-2">Skill You Want:</h4>
          <div class="flex items-center gap-2">
            <span class="font-medium">{{ selectedSkill.name }}</span>
            <Tag v-if="selectedSkill.category" :value="selectedSkill.category" severity="secondary" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Skill You Offer:
          </label>
          <Dropdown
            v-model="selectedOfferedSkill"
            :options="userSkills"
            optionLabel="name"
            optionValue="id"
            placeholder="Select a skill to offer"
            class="w-full"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Message (Optional):
          </label>
          <Textarea
            v-model="swapMessage"
            placeholder="Add a message to your swap request..."
            :autoResize="true"
            rows="3"
            class="w-full"
          />
        </div>
      </div>

      <template #footer>
        <div class="flex gap-2">
          <Button
            @click="showSwapDialog = false"
            label="Cancel"
            icon="pi pi-times"
            outlined
          />
          <Button
            @click="submitSwapRequest"
            label="Send Request"
            icon="pi pi-send"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
