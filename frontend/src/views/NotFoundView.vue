<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="flex justify-center items-center min-h-[60vh]">
    <Card class="w-full max-w-md text-center">
      <template #content>
        <div class="space-y-6 py-8">
          <div class="space-y-4">
            <i class="pi pi-exclamation-triangle text-6xl text-gray-400"></i>
            <h1 class="text-4xl font-bold text-gray-900">404</h1>
            <h2 class="text-xl font-semibold text-gray-700">Page Not Found</h2>
            <p class="text-gray-600">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </div>
          
          <div class="flex gap-3 justify-center">
            <Button
              @click="goHome"
              icon="pi pi-home"
              label="Go Home"
            />
            <Button
              @click="goBack"
              icon="pi pi-arrow-left"
              label="Go Back"
              outlined
            />
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>
