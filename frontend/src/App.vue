<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'

const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const menuItems = computed(() => {
  const items = [
    {
      label: 'Home',
      icon: 'pi pi-home',
      command: () => router.push('/')
    }
  ]

  if (authStore.isAuthenticated) {
    items.push(
      {
        label: 'Skills',
        icon: 'pi pi-star',
        items: [
          {
            label: 'Browse Skills',
            icon: 'pi pi-search',
            command: () => router.push('/skills')
          },
          {
            label: 'My Skills',
            icon: 'pi pi-user',
            command: () => router.push('/my-skills')
          }
        ]
      },
      {
        label: 'Swaps',
        icon: 'pi pi-sync',
        items: [
          {
            label: 'Browse Requests',
            icon: 'pi pi-list',
            command: () => router.push('/swaps')
          },
          {
            label: 'My Requests',
            icon: 'pi pi-user',
            command: () => router.push('/my-swaps')
          }
        ]
      },
      {
        label: 'Profile',
        icon: 'pi pi-user',
        command: () => router.push('/profile')
      }
    )

    if (authStore.currentUser?.is_admin) {
      items.push({
        label: 'Admin',
        icon: 'pi pi-cog',
        command: () => router.push('/admin')
      })
    }
  }

  return items
})

const userMenuItems = computed(() => {
  if (!authStore.isAuthenticated) {
    return [
      {
        label: 'Login',
        icon: 'pi pi-sign-in',
        command: () => router.push('/login')
      },
      {
        label: 'Register',
        icon: 'pi pi-user-plus',
        command: () => router.push('/register')
      }
    ]
  }

  return [
    {
      label: `Welcome, ${authStore.currentUser?.full_name || authStore.currentUser?.username}`,
      icon: 'pi pi-user',
      items: [
        {
          label: 'Profile',
          icon: 'pi pi-user',
          command: () => router.push('/profile')
        },
        {
          label: 'Logout',
          icon: 'pi pi-sign-out',
          command: () => handleLogout()
        }
      ]
    }
  ]
})

const handleLogout = async () => {
  await authStore.logout()
  toast.add({
    severity: 'success',
    summary: 'Logged out',
    detail: 'You have been successfully logged out',
    life: 3000
  })
  router.push('/')
}

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    await authStore.fetchCurrentUser()
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <Menubar :model="menuItems" class="border-none shadow-md">
      <template #start>
        <div class="flex items-center gap-2">
          <i class="pi pi-sync text-2xl text-primary"></i>
          <span class="text-xl font-bold text-primary">SkillSwap</span>
        </div>
      </template>
      <template #end>
        <div class="flex items-center gap-2">
          <Menubar :model="userMenuItems" class="border-none bg-transparent">
            <template #start>
              <div v-if="authStore.isAuthenticated" class="flex items-center gap-2">
                <Avatar 
                  :label="authStore.currentUser?.full_name?.charAt(0) || authStore.currentUser?.username?.charAt(0) || 'U'"
                  class="bg-primary text-white"
                  size="normal"
                />
              </div>
            </template>
          </Menubar>
        </div>
      </template>
    </Menubar>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
      <RouterView />
    </main>

    <!-- Toast Messages -->
    <Toast />
    
    <!-- Confirmation Dialog -->
    <ConfirmDialog />
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
}
</style>
</style>
