<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const formData = ref({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  if (!formData.value.username || !formData.value.password) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Please fill in all required fields',
      life: 3000
    })
    return
  }

  const success = await authStore.login(formData.value.username, formData.value.password)
  
  if (success) {
    toast.add({
      severity: 'success',
      summary: 'Login Successful',
      detail: 'Welcome back!',
      life: 3000
    })
    router.push('/')
  } else {
    toast.add({
      severity: 'error',
      summary: 'Login Failed',
      detail: authStore.error || 'Invalid credentials',
      life: 5000
    })
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="flex justify-center items-center min-h-[60vh]">
    <Card class="w-full max-w-md">
      <template #header>
        <div class="text-center py-6">
          <h1 class="text-2xl font-bold text-gray-900">Welcome Back</h1>
          <p class="text-gray-600 mt-2">Sign in to your account</p>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div class="space-y-4">
            <FloatLabel>
              <InputText
                id="username"
                v-model="formData.username"
                class="w-full"
                :class="{ 'p-invalid': authStore.error }"
                autocomplete="username"
              />
              <label for="username">Username or Email</label>
            </FloatLabel>

            <FloatLabel>
              <Password
                id="password"
                v-model="formData.password"
                class="w-full"
                :class="{ 'p-invalid': authStore.error }"
                :feedback="false"
                autocomplete="current-password"
              />
              <label for="password">Password</label>
            </FloatLabel>
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
            <i class="pi pi-sign-in mr-2"></i>
            Sign In
          </Button>
        </form>
      </template>

      <template #footer>
        <div class="text-center space-y-4">
          <div class="text-sm text-gray-600">
            Don't have an account?
          </div>
          <Button
            @click="goToRegister"
            variant="outlined"
            class="w-full"
          >
            <i class="pi pi-user-plus mr-2"></i>
            Create Account
          </Button>
        </div>
      </template>
    </Card>
  </div>
</template>
