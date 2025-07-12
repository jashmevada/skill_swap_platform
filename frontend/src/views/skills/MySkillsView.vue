<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSkillsStore } from '@/stores/skills'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

const authStore = useAuthStore()
const skillsStore = useSkillsStore()
const toast = useToast()
const confirm = useConfirm()

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const selectedSkill = ref(null)
const loading = ref(false)

const skillForm = ref({
  name: '',
  category: '',
  description: ''
})

const categories = [
  'Programming',
  'Design',
  'Marketing',
  'Writing',
  'Music',
  'Languages',
  'Cooking',
  'Fitness',
  'Photography',
  'Business',
  'Other'
]

const userSkills = computed(() => 
  skillsStore.userSkills.filter(skill => skill.user_id === authStore.user?.id) || []
)

const approvedSkills = computed(() => 
  userSkills.value.filter(skill => skill.is_approved)
)

const pendingSkills = computed(() => 
  userSkills.value.filter(skill => !skill.is_approved)
)

const resetForm = () => {
  skillForm.value = {
    name: '',
    category: '',
    description: ''
  }
}

const handleAddSkill = () => {
  resetForm()
  showAddDialog.value = true
}

const handleEditSkill = (skill) => {
  selectedSkill.value = skill
  skillForm.value = {
    name: skill.name,
    category: skill.category || '',
    description: skill.description || ''
  }
  showEditDialog.value = true
}

const handleDeleteSkill = (skill) => {
  confirm.require({
    message: `Are you sure you want to delete "${skill.name}"?`,
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await skillsStore.deleteSkill(skill.id)
        toast.add({
          severity: 'success',
          summary: 'Skill Deleted',
          detail: 'The skill has been successfully deleted',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Delete Failed',
          detail: 'Failed to delete the skill',
          life: 3000
        })
      }
    }
  })
}

const submitAddSkill = async () => {
  if (!skillForm.value.name.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Skill name is required',
      life: 3000
    })
    return
  }

  loading.value = true
  try {
    await skillsStore.createSkill({
      name: skillForm.value.name.trim(),
      category: skillForm.value.category || undefined,
      description: skillForm.value.description || undefined
    })

    toast.add({
      severity: 'success',
      summary: 'Skill Added',
      detail: 'Your skill has been submitted for approval',
      life: 3000
    })

    showAddDialog.value = false
    resetForm()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to add skill',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const submitEditSkill = async () => {
  if (!skillForm.value.name.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Skill name is required',
      life: 3000
    })
    return
  }

  loading.value = true
  try {
    await skillsStore.updateSkill(selectedSkill.value.id, {
      name: skillForm.value.name.trim(),
      category: skillForm.value.category || undefined,
      description: skillForm.value.description || undefined
    })

    toast.add({
      severity: 'success',
      summary: 'Skill Updated',
      detail: 'Your skill has been updated successfully',
      life: 3000
    })

    showEditDialog.value = false
    selectedSkill.value = null
    resetForm()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update skill',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (authStore.user) {
    await skillsStore.fetchUserSkills(authStore.user.id)
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">My Skills</h1>
        <p class="text-gray-600 mt-2">Manage the skills you offer to the community</p>
      </div>
      <Button
        @click="handleAddSkill"
        icon="pi pi-plus"
        label="Add Skill"
      />
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-primary">{{ userSkills.length }}</div>
            <div class="text-gray-600">Total Skills</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-green-600">{{ approvedSkills.length }}</div>
            <div class="text-gray-600">Approved Skills</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-2xl font-bold text-orange-600">{{ pendingSkills.length }}</div>
            <div class="text-gray-600">Pending Approval</div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Approved Skills -->
    <Card v-if="approvedSkills.length > 0">
      <template #header>
        <div class="flex items-center gap-2 p-6 pb-0">
          <i class="pi pi-check-circle text-green-600"></i>
          <h2 class="text-xl font-semibold text-gray-900">Approved Skills</h2>
        </div>
      </template>

      <template #content>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="skill in approvedSkills"
            :key="skill.id"
            class="border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div class="space-y-3">
              <div class="flex justify-between items-start">
                <h3 class="font-semibold text-gray-900">{{ skill.name }}</h3>
                <div class="flex gap-1">
                  <Button
                    @click="handleEditSkill(skill)"
                    icon="pi pi-pencil"
                    size="small"
                    outlined
                    severity="secondary"
                  />
                  <Button
                    @click="handleDeleteSkill(skill)"
                    icon="pi pi-trash"
                    size="small"
                    outlined
                    severity="danger"
                  />
                </div>
              </div>
              
              <div v-if="skill.category" class="flex items-center gap-2">
                <Tag :value="skill.category" severity="secondary" />
              </div>
              
              <p v-if="skill.description" class="text-gray-600 text-sm">
                {{ skill.description }}
              </p>
              
              <div class="flex items-center gap-2 text-xs text-gray-500">
                <i class="pi pi-calendar"></i>
                <span>Added {{ new Date(skill.created_at).toLocaleDateString() }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Pending Skills -->
    <Card v-if="pendingSkills.length > 0">
      <template #header>
        <div class="flex items-center gap-2 p-6 pb-0">
          <i class="pi pi-clock text-orange-600"></i>
          <h2 class="text-xl font-semibold text-gray-900">Pending Approval</h2>
        </div>
      </template>

      <template #content>
        <div class="space-y-3">
          <div
            v-for="skill in pendingSkills"
            :key="skill.id"
            class="border rounded-lg p-4 bg-orange-50 border-orange-200"
          >
            <div class="flex justify-between items-start">
              <div class="space-y-2">
                <h3 class="font-semibold text-gray-900">{{ skill.name }}</h3>
                <div v-if="skill.category" class="flex items-center gap-2">
                  <Tag :value="skill.category" severity="warning" />
                </div>
                <p v-if="skill.description" class="text-gray-600 text-sm">
                  {{ skill.description }}
                </p>
                <div class="flex items-center gap-2 text-xs text-gray-500">
                  <i class="pi pi-calendar"></i>
                  <span>Submitted {{ new Date(skill.created_at).toLocaleDateString() }}</span>
                </div>
              </div>
              
              <div class="flex gap-1">
                <Button
                  @click="handleEditSkill(skill)"
                  icon="pi pi-pencil"
                  size="small"
                  outlined
                  severity="secondary"
                />
                <Button
                  @click="handleDeleteSkill(skill)"
                  icon="pi pi-trash"
                  size="small"
                  outlined
                  severity="danger"
                />
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Empty State -->
    <Card v-if="userSkills.length === 0" class="text-center py-12">
      <template #content>
        <div class="space-y-4">
          <i class="pi pi-star text-4xl text-gray-400"></i>
          <h3 class="text-lg font-semibold text-gray-600">No skills added yet</h3>
          <p class="text-gray-500 max-w-md mx-auto">
            Start by adding skills you can offer to other community members.
            Your skills will be reviewed before appearing publicly.
          </p>
          <Button
            @click="handleAddSkill"
            icon="pi pi-plus"
            label="Add Your First Skill"
          />
        </div>
      </template>
    </Card>

    <!-- Add Skill Dialog -->
    <Dialog
      v-model:visible="showAddDialog"
      modal
      header="Add New Skill"
      :style="{ width: '500px' }"
    >
      <form @submit.prevent="submitAddSkill" class="space-y-4">
        <FloatLabel>
          <InputText
            id="skillName"
            v-model="skillForm.name"
            class="w-full"
            required
          />
          <label for="skillName">Skill Name *</label>
        </FloatLabel>

        <FloatLabel>
          <Dropdown
            id="skillCategory"
            v-model="skillForm.category"
            :options="categories"
            class="w-full"
            showClear
            placeholder="Select Category"
          />
          <label for="skillCategory">Category</label>
        </FloatLabel>

        <FloatLabel>
          <Textarea
            id="skillDescription"
            v-model="skillForm.description"
            class="w-full"
            :autoResize="true"
            rows="3"
          />
          <label for="skillDescription">Description</label>
        </FloatLabel>
      </form>

      <template #footer>
        <div class="flex gap-2">
          <Button
            @click="showAddDialog = false"
            label="Cancel"
            icon="pi pi-times"
            outlined
          />
          <Button
            @click="submitAddSkill"
            :loading="loading"
            label="Add Skill"
            icon="pi pi-plus"
          />
        </div>
      </template>
    </Dialog>

    <!-- Edit Skill Dialog -->
    <Dialog
      v-model:visible="showEditDialog"
      modal
      header="Edit Skill"
      :style="{ width: '500px' }"
    >
      <form @submit.prevent="submitEditSkill" class="space-y-4">
        <FloatLabel>
          <InputText
            id="editSkillName"
            v-model="skillForm.name"
            class="w-full"
            required
          />
          <label for="editSkillName">Skill Name *</label>
        </FloatLabel>

        <FloatLabel>
          <Dropdown
            id="editSkillCategory"
            v-model="skillForm.category"
            :options="categories"
            class="w-full"
            showClear
            placeholder="Select Category"
          />
          <label for="editSkillCategory">Category</label>
        </FloatLabel>

        <FloatLabel>
          <Textarea
            id="editSkillDescription"
            v-model="skillForm.description"
            class="w-full"
            :autoResize="true"
            rows="3"
          />
          <label for="editSkillDescription">Description</label>
        </FloatLabel>
      </form>

      <template #footer>
        <div class="flex gap-2">
          <Button
            @click="showEditDialog = false"
            label="Cancel"
            icon="pi pi-times"
            outlined
          />
          <Button
            @click="submitEditSkill"
            :loading="loading"
            label="Update Skill"
            icon="pi pi-check"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>
