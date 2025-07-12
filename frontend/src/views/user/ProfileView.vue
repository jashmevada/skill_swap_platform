<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSkillsStore } from '@/stores/skills'
import { useSwapsStore } from '@/stores/swaps'
import { useToast } from 'primevue/usetoast'

const authStore = useAuthStore()
const skillsStore = useSkillsStore()
const swapsStore = useSwapsStore()
const toast = useToast()

const isEditing = ref(false)
const loading = ref(false)

const formData = ref({
  email: '',
  username: '',
  full_name: '',
  location: '',
  bio: '',
  availability: '',
  is_public: true
})

const userSkills = computed(() => 
  skillsStore.userSkills.filter(skill => skill.user_id === authStore.user?.id)
)

const userSwaps = computed(() => 
  swapsStore.swaps.filter(swap => 
    swap.requester_id === authStore.user?.id || swap.requested_id === authStore.user?.id
  )
)

const initializeForm = () => {
  if (authStore.user) {
    formData.value = {
      email: authStore.user.email,
      username: authStore.user.username,
      full_name: authStore.user.full_name || '',
      location: authStore.user.location || '',
      bio: authStore.user.bio || '',
      availability: authStore.user.availability || '',
      is_public: authStore.user.is_public
    }
  }
}

const handleEdit = () => {
  isEditing.value = true
  initializeForm()
}

const handleCancel = () => {
  isEditing.value = false
  initializeForm()
  authStore.clearError()
}

const handleSave = async () => {
  loading.value = true
  
  const success = await authStore.updateProfile(formData.value)
  
  if (success) {
    isEditing.value = false
    toast.add({
      severity: 'success',
      summary: 'Profile Updated',
      detail: 'Your profile has been successfully updated',
      life: 3000
    })
  } else {
    toast.add({
      severity: 'error',
      summary: 'Update Failed',
      detail: authStore.error || 'Failed to update profile',
      life: 5000
    })
  }
  
  loading.value = false
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

onMounted(async () => {
  initializeForm()
  
  // Load user's skills and swaps
  if (authStore.user) {
    await Promise.all([
      skillsStore.fetchUserSkills(authStore.user.id),
      swapsStore.fetchUserSwaps(authStore.user.id)
    ])
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Profile Header -->
    <Card>
      <template #header>
        <div class="flex justify-between items-center p-6 pb-0">
          <h1 class="text-2xl font-bold text-gray-900">My Profile</h1>
          <Button
            v-if="!isEditing"
            @click="handleEdit"
            icon="pi pi-pencil"
            label="Edit Profile"
            outlined
          />
        </div>
      </template>

      <template #content>
        <div v-if="!isEditing" class="space-y-6">
          <!-- Profile Display -->
          <div class="flex items-start gap-6">
            <Avatar
              :label="authStore.user?.full_name?.charAt(0) || authStore.user?.username?.charAt(0) || 'U'"
              size="xlarge"
              class="bg-primary text-white"
            />
            
            <div class="flex-1 space-y-3">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">
                  {{ authStore.user?.full_name || authStore.user?.username }}
                </h2>
                <p class="text-gray-600">@{{ authStore.user?.username }}</p>
              </div>
              
              <div v-if="authStore.user?.location" class="flex items-center text-gray-600">
                <i class="pi pi-map-marker mr-2"></i>
                <span>{{ authStore.user.location }}</span>
              </div>
              
              <div v-if="authStore.user?.bio" class="text-gray-700">
                <p>{{ authStore.user.bio }}</p>
              </div>
              
              <div class="flex items-center gap-4">
                <Tag 
                  :value="authStore.user?.is_public ? 'Public Profile' : 'Private Profile'"
                  :severity="authStore.user?.is_public ? 'success' : 'warning'"
                />
                <span class="text-sm text-gray-500">
                  Member since {{ new Date(authStore.user?.created_at || '').toLocaleDateString() }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Edit Form -->
        <div v-else class="space-y-6">
          <form @submit.prevent="handleSave" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FloatLabel>
                <InputText
                  id="email"
                  v-model="formData.email"
                  class="w-full"
                  type="email"
                  disabled
                />
                <label for="email">Email Address</label>
              </FloatLabel>

              <FloatLabel>
                <InputText
                  id="username"
                  v-model="formData.username"
                  class="w-full"
                  disabled
                />
                <label for="username">Username</label>
              </FloatLabel>

              <FloatLabel>
                <InputText
                  id="fullName"
                  v-model="formData.full_name"
                  class="w-full"
                />
                <label for="fullName">Full Name</label>
              </FloatLabel>

              <FloatLabel>
                <InputText
                  id="location"
                  v-model="formData.location"
                  class="w-full"
                />
                <label for="location">Location</label>
              </FloatLabel>

              <div class="md:col-span-2">
                <FloatLabel>
                  <Textarea
                    id="bio"
                    v-model="formData.bio"
                    class="w-full"
                    :autoResize="true"
                    rows="3"
                  />
                  <label for="bio">Bio</label>
                </FloatLabel>
              </div>

              <div class="md:col-span-2">
                <FloatLabel>
                  <InputText
                    id="availability"
                    v-model="formData.availability"
                    class="w-full"
                  />
                  <label for="availability">Availability</label>
                </FloatLabel>
              </div>

              <div class="md:col-span-2">
                <div class="flex items-center gap-3">
                  <ToggleButton
                    v-model="formData.is_public"
                    onLabel="Public Profile"
                    offLabel="Private Profile"
                    onIcon="pi pi-eye"
                    offIcon="pi pi-eye-slash"
                  />
                  <span class="text-sm text-gray-600">
                    {{ formData.is_public ? 'Others can see your profile' : 'Your profile is private' }}
                  </span>
                </div>
              </div>
            </div>

            <div v-if="authStore.error" class="text-red-600 text-sm">
              {{ authStore.error }}
            </div>

            <div class="flex gap-3">
              <Button
                type="submit"
                :loading="loading"
                icon="pi pi-check"
                label="Save Changes"
              />
              <Button
                @click="handleCancel"
                icon="pi pi-times"
                label="Cancel"
                outlined
              />
            </div>
          </form>
        </div>
      </template>
    </Card>

    <!-- User Stats -->
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
            <div class="text-2xl font-bold text-primary">{{ userSwaps.length }}</div>
            <div class="text-gray-600">Total Swaps</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-primary">
              {{ userSwaps.filter(s => s.status === 'completed').length }}
            </div>
            <div class="text-gray-600">Completed Swaps</div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- My Skills -->
      <Card>
        <template #header>
          <div class="flex justify-between items-center p-6 pb-0">
            <h3 class="text-lg font-semibold text-gray-900">My Skills</h3>
            <Button
              icon="pi pi-plus"
              label="Add Skill"
              size="small"
              outlined
            />
          </div>
        </template>

        <template #content>
          <div v-if="userSkills.length === 0" class="text-center text-gray-500 py-8">
            No skills added yet
          </div>
          
          <div v-else class="space-y-3">
            <div
              v-for="skill in userSkills.slice(0, 5)"
              :key="skill.id"
              class="flex justify-between items-center p-3 border rounded-lg"
            >
              <div>
                <h4 class="font-medium text-gray-900">{{ skill.name }}</h4>
                <p v-if="skill.category" class="text-sm text-gray-600">{{ skill.category }}</p>
              </div>
              <Tag 
                :value="skill.is_approved ? 'Approved' : 'Pending'"
                :severity="skill.is_approved ? 'success' : 'warning'"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- Recent Swaps -->
      <Card>
        <template #header>
          <div class="flex justify-between items-center p-6 pb-0">
            <h3 class="text-lg font-semibold text-gray-900">Recent Swaps</h3>
            <Button
              icon="pi pi-external-link"
              label="View All"
              size="small"
              outlined
            />
          </div>
        </template>

        <template #content>
          <div v-if="userSwaps.length === 0" class="text-center text-gray-500 py-8">
            No swaps yet
          </div>
          
          <div v-else class="space-y-3">
            <div
              v-for="swap in userSwaps.slice(0, 5)"
              :key="swap.id"
              class="flex justify-between items-center p-3 border rounded-lg"
            >
              <div class="flex-1">
                <div class="text-sm text-gray-600">
                  {{ swap.requester_id === authStore.user?.id ? 'Requesting' : 'Requested by' }}
                </div>
                <div class="text-sm font-medium">Skill Exchange</div>
              </div>
              <Tag 
                :value="swap.status"
                :severity="getSwapStatusSeverity(swap.status)"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>
