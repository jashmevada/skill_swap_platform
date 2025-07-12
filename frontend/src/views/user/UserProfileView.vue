<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUsersStore } from '@/stores/users'
import { useSkillsStore } from '@/stores/skills'
import { useAuthStore } from '@/stores/auth'
import { useSwapsStore } from '@/stores/swaps'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const router = useRouter()
const usersStore = useUsersStore()
const skillsStore = useSkillsStore()
const authStore = useAuthStore()
const swapsStore = useSwapsStore()
const toast = useToast()

const loading = ref(true)
const showSwapDialog = ref(false)
const selectedSkill = ref(null)
const selectedOfferedSkill = ref('')
const swapMessage = ref('')

const userId = computed(() => parseInt(route.params.id as string))
const user = computed(() => usersStore.selectedUser)

const userSkills = computed(() => 
  skillsStore.userSkills.filter(skill => 
    skill.user_id === userId.value && skill.is_approved
  )
)

const mySkills = computed(() => 
  skillsStore.userSkills.filter(skill => 
    skill.user_id === authStore.user?.id && skill.is_approved
  )
)

const canRequestSwap = computed(() => 
  authStore.isAuthenticated && 
  authStore.user?.id !== userId.value &&
  mySkills.value.length > 0
)

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

  if (mySkills.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: 'No Skills Available',
      detail: 'You need to add skills to your profile before requesting swaps',
      life: 3000
    })
    router.push('/my-skills')
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

const loadUserProfile = async () => {
  loading.value = true
  try {
    await Promise.all([
      usersStore.fetchUser(userId.value),
      skillsStore.fetchUserSkills(userId.value)
    ])

    // Load current user's skills if authenticated
    if (authStore.isAuthenticated && authStore.user) {
      await skillsStore.fetchUserSkills(authStore.user.id)
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load user profile',
      life: 3000
    })
    router.push('/404')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserProfile()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <i class="pi pi-spinner pi-spin text-2xl text-primary"></i>
      <p class="text-gray-600 mt-2">Loading profile...</p>
    </div>

    <!-- Profile Content -->
    <div v-else-if="user" class="space-y-6">
      <!-- Profile Header -->
      <Card>
        <template #content>
          <div class="space-y-6">
            <div class="flex items-start gap-6">
              <Avatar
                :label="user.full_name?.charAt(0) || user.username?.charAt(0) || 'U'"
                size="xlarge"
                class="bg-primary text-white"
              />
              
              <div class="flex-1 space-y-3">
                <div>
                  <h1 class="text-2xl font-bold text-gray-900">
                    {{ user.full_name || user.username }}
                  </h1>
                  <p class="text-gray-600">@{{ user.username }}</p>
                </div>
                
                <div v-if="user.location" class="flex items-center text-gray-600">
                  <i class="pi pi-map-marker mr-2"></i>
                  <span>{{ user.location }}</span>
                </div>
                
                <div v-if="user.bio" class="text-gray-700">
                  <p>{{ user.bio }}</p>
                </div>
                
                <div v-if="user.availability" class="flex items-center text-gray-600">
                  <i class="pi pi-clock mr-2"></i>
                  <span>{{ user.availability }}</span>
                </div>
                
                <div class="flex items-center gap-4">
                  <Tag 
                    :value="user.is_public ? 'Public Profile' : 'Private Profile'"
                    :severity="user.is_public ? 'success' : 'warning'"
                  />
                  <span class="text-sm text-gray-500">
                    Member since {{ new Date(user.created_at).toLocaleDateString() }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="flex gap-3">
              <Button
                v-if="authStore.isAuthenticated && authStore.user?.id !== user.id"
                icon="pi pi-comment"
                label="Send Message"
                outlined
                disabled
              />
              <Button
                v-if="authStore.user?.id === user.id"
                @click="router.push('/profile')"
                icon="pi pi-pencil"
                label="Edit Profile"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- User Skills -->
      <Card>
        <template #header>
          <div class="flex justify-between items-center p-6 pb-0">
            <h2 class="text-xl font-semibold text-gray-900">Skills Offered</h2>
            <Badge :value="userSkills.length" />
          </div>
        </template>

        <template #content>
          <div v-if="userSkills.length === 0" class="text-center py-8">
            <i class="pi pi-star text-4xl text-gray-400"></i>
            <h3 class="text-lg font-semibold text-gray-600 mt-4">No skills listed</h3>
            <p class="text-gray-500">This user hasn't added any skills yet</p>
          </div>
          
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card 
              v-for="skill in userSkills"
              :key="skill.id"
              class="hover:shadow-md transition-shadow"
            >
              <template #content>
                <div class="space-y-3">
                  <div class="flex justify-between items-start">
                    <h3 class="font-semibold text-gray-900">{{ skill.name }}</h3>
                    <Tag 
                      v-if="skill.category"
                      :value="skill.category"
                      severity="secondary"
                    />
                  </div>
                  
                  <p v-if="skill.description" class="text-gray-600 text-sm line-clamp-3">
                    {{ skill.description }}
                  </p>
                  
                  <div class="flex items-center gap-2 text-xs text-gray-500">
                    <i class="pi pi-calendar"></i>
                    <span>Added {{ new Date(skill.created_at).toLocaleDateString() }}</span>
                  </div>

                  <div v-if="canRequestSwap" class="flex justify-end">
                    <Button
                      @click="handleRequestSwap(skill)"
                      icon="pi pi-sync"
                      label="Request Swap"
                      size="small"
                    />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </template>
      </Card>

      <!-- Profile Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card class="text-center">
          <template #content>
            <div class="space-y-2">
              <div class="text-2xl font-bold text-primary">{{ userSkills.length }}</div>
              <div class="text-gray-600">Skills Offered</div>
            </div>
          </template>
        </Card>
        
        <Card class="text-center">
          <template #content>
            <div class="space-y-2">
              <div class="text-2xl font-bold text-green-600">-</div>
              <div class="text-gray-600">Completed Swaps</div>
            </div>
          </template>
        </Card>
        
        <Card class="text-center">
          <template #content>
            <div class="space-y-2">
              <div class="text-2xl font-bold text-yellow-600">-</div>
              <div class="text-gray-600">Rating</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- User Not Found -->
    <Card v-else class="text-center py-12">
      <template #content>
        <div class="space-y-4">
          <i class="pi pi-user-times text-4xl text-gray-400"></i>
          <h3 class="text-lg font-semibold text-gray-600">User not found</h3>
          <p class="text-gray-500">The user you're looking for doesn't exist or is private</p>
          <Button
            @click="router.push('/')"
            icon="pi pi-home"
            label="Go Home"
          />
        </div>
      </template>
    </Card>

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
            :options="mySkills"
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
