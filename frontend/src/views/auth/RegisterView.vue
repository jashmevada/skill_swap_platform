<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const formData = ref({
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
  full_name: '',
  location: '',
  bio: ''
})

const errors = ref({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

const validateForm = () => {
  errors.value = {
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  }

  let isValid = true

  if (!formData.value.email) {
    errors.value.email = 'Email is required'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(formData.value.email)) {
    errors.value.email = 'Email is invalid'
    isValid = false
  }

  if (!formData.value.username) {
    errors.value.username = 'Username is required'
    isValid = false
  } else if (formData.value.username.length < 3) {
    errors.value.username = 'Username must be at least 3 characters'
    isValid = false
  }

  if (!formData.value.password) {
    errors.value.password = 'Password is required'
    isValid = false
  } else if (formData.value.password.length < 6) {
    errors.value.password = 'Password must be at least 6 characters'
    isValid = false
  }

  if (formData.value.password !== formData.value.confirmPassword) {
    errors.value.confirmPassword = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please fix the errors and try again',
      life: 3000
    })
    return
  }

  const userData = {
    email: formData.value.email,
    username: formData.value.username,
    password: formData.value.password,
    full_name: formData.value.full_name || undefined,
    location: formData.value.location || undefined,
    bio: formData.value.bio || undefined
  }

  const success = await authStore.register(userData)
  
  if (success) {
    toast.add({
      severity: 'success',
      summary: 'Registration Successful',
      detail: 'Welcome to SkillSwap!',
      life: 3000
    })
    router.push('/')
  } else {
    toast.add({
      severity: 'error',
      summary: 'Registration Failed',
      detail: authStore.error || 'An error occurred during registration',
      life: 5000
    })
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="flex justify-center items-center min-h-[60vh] py-8">
    <Card class="w-full max-w-2xl">
      <template #header>
        <div class="text-center py-6">
          <h1 class="text-2xl font-bold text-gray-900">Join SkillSwap</h1>
          <p class="text-gray-600 mt-2">Create your account and start learning</p>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Required Fields -->
            <div class="md:col-span-2">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Required Information</h3>
            </div>

            <FloatLabel>
              <InputText
                id="email"
                v-model="formData.email"
                class="w-full"
                :class="{ 'p-invalid': errors.email || authStore.error }"
                autocomplete="email"
                type="email"
              />
              <label for="email">Email Address *</label>
            </FloatLabel>
            <div v-if="errors.email" class="text-red-600 text-sm">{{ errors.email }}</div>

            <FloatLabel>
              <InputText
                id="username"
                v-model="formData.username"
                class="w-full"
                :class="{ 'p-invalid': errors.username || authStore.error }"
                autocomplete="username"
              />
              <label for="username">Username *</label>
            </FloatLabel>
            <div v-if="errors.username" class="text-red-600 text-sm">{{ errors.username }}</div>

            <FloatLabel>
              <Password
                id="password"
                v-model="formData.password"
                class="w-full"
                :class="{ 'p-invalid': errors.password || authStore.error }"
                autocomplete="new-password"
                toggleMask
              />
              <label for="password">Password *</label>
            </FloatLabel>
            <div v-if="errors.password" class="text-red-600 text-sm">{{ errors.password }}</div>

            <FloatLabel>
              <Password
                id="confirmPassword"
                v-model="formData.confirmPassword"
                class="w-full"
                :class="{ 'p-invalid': errors.confirmPassword }"
                autocomplete="new-password"
                :feedback="false"
              />
              <label for="confirmPassword">Confirm Password *</label>
            </FloatLabel>
            <div v-if="errors.confirmPassword" class="text-red-600 text-sm">{{ errors.confirmPassword }}</div>

            <!-- Optional Fields -->
            <div class="md:col-span-2 mt-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Optional Information</h3>
            </div>

            <FloatLabel>
              <InputText
                id="fullName"
                v-model="formData.full_name"
                class="w-full"
                autocomplete="name"
              />
              <label for="fullName">Full Name</label>
            </FloatLabel>

            <FloatLabel>
              <InputText
                id="location"
                v-model="formData.location"
                class="w-full"
                autocomplete="address-level2"
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
          </div>

          <div v-if="authStore.error" class="text-red-600 text-sm text-center">
            {{ authStore.error }}
          </div>

          <Button
            type="submit"
            :loading="authStore.loading"
            class="w-full"
            size="large"
          >
            <i class="pi pi-user-plus mr-2"></i>
            Create Account
          </Button>
        </form>
      </template>

      <template #footer>
        <div class="text-center space-y-4">
          <div class="text-sm text-gray-600">
            Already have an account?
          </div>
          <Button
            @click="goToLogin"
            variant="outlined"
            class="w-full"
          >
            <i class="pi pi-sign-in mr-2"></i>
            Sign In
          </Button>
        </div>
      </template>
    </Card>
  </div>
</template>
