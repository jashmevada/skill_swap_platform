<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSkillsStore } from '@/stores/skills'
import { useSwapsStore } from '@/stores/swaps'

const router = useRouter()
const authStore = useAuthStore()
const skillsStore = useSkillsStore()
const swapsStore = useSwapsStore()

const loading = ref(true)
const featuredSkills = ref([])
const recentSwaps = ref([])

const stats = computed(() => ({
  totalSkills: skillsStore.skills.length,
  totalSwaps: swapsStore.swaps.length,
  activeUsers: 150 // This would come from an API in real implementation
}))

const features = [
  {
    icon: 'pi pi-search',
    title: 'Find Skills',
    description: 'Browse through hundreds of skills offered by our community members.'
  },
  {
    icon: 'pi pi-share-alt',
    title: 'Share Knowledge',
    description: 'Offer your expertise and help others learn new skills.'
  },
  {
    icon: 'pi pi-sync',
    title: 'Skill Exchange',
    description: 'Trade skills with others in mutually beneficial exchanges.'
  },
  {
    icon: 'pi pi-users',
    title: 'Community',
    description: 'Join a growing community of learners and skill sharers.'
  }
]

const handleGetStarted = () => {
  if (authStore.isAuthenticated) {
    router.push('/skills')
  } else {
    router.push('/register')
  }
}

const handleExploreSkills = () => {
  router.push('/skills')
}

onMounted(async () => {
  try {
    // Load some initial data for the homepage
    await Promise.all([
      skillsStore.fetchSkills({ page: 1, size: 6 }),
      swapsStore.fetchSwaps({ page: 1, size: 4 })
    ])
    
    featuredSkills.value = skillsStore.skills.slice(0, 6)
    recentSwaps.value = swapsStore.swaps.slice(0, 4)
  } catch (error) {
    console.error('Failed to load homepage data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-12">
    <!-- Hero Section -->
    <div class="text-center space-y-6">
      <div class="space-y-4">
        <h1 class="text-5xl font-bold text-gray-900 leading-tight">
          Share Skills, <span class="text-primary">Learn Together</span>
        </h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">
          Connect with others to exchange skills, learn new abilities, and build meaningful relationships 
          through knowledge sharing.
        </p>
      </div>
      
      <div class="flex justify-center gap-4 flex-wrap">
        <Button 
          @click="handleGetStarted"
          size="large"
          class="px-8 py-3"
        >
          <i class="pi pi-arrow-right mr-2"></i>
          {{ authStore.isAuthenticated ? 'Browse Skills' : 'Get Started' }}
        </Button>
        
        <Button 
          @click="handleExploreSkills"
          variant="outlined"
          size="large"
          class="px-8 py-3"
        >
          <i class="pi pi-search mr-2"></i>
          Explore Skills
        </Button>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-3xl font-bold text-primary">{{ stats.totalSkills }}+</div>
            <div class="text-gray-600">Skills Available</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-3xl font-bold text-primary">{{ stats.totalSwaps }}+</div>
            <div class="text-gray-600">Successful Swaps</div>
          </div>
        </template>
      </Card>
      
      <Card class="text-center">
        <template #content>
          <div class="space-y-2">
            <div class="text-3xl font-bold text-primary">{{ stats.activeUsers }}+</div>
            <div class="text-gray-600">Active Members</div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Features Section -->
    <div class="space-y-8">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">How It Works</h2>
        <p class="text-gray-600 max-w-2xl mx-auto">
          Our platform makes it easy to share your skills and learn from others in your community.
        </p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card v-for="feature in features" :key="feature.title" class="text-center h-full">
          <template #content>
            <div class="space-y-4">
              <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                <i :class="feature.icon" class="text-2xl text-primary"></i>
              </div>
              <h3 class="text-xl font-semibold text-gray-900">{{ feature.title }}</h3>
              <p class="text-gray-600">{{ feature.description }}</p>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Featured Skills Section -->
    <div v-if="!loading && featuredSkills.length > 0" class="space-y-6">
      <div class="flex justify-between items-center">
        <h2 class="text-3xl font-bold text-gray-900">Featured Skills</h2>
        <Button 
          @click="handleExploreSkills"
          variant="outlined"
          size="small"
        >
          View All
        </Button>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card v-for="skill in featuredSkills" :key="skill.id" class="hover:shadow-lg transition-shadow">
          <template #content>
            <div class="space-y-3">
              <div class="flex justify-between items-start">
                <h3 class="text-lg font-semibold text-gray-900">{{ skill.name }}</h3>
                <Tag v-if="skill.category" :value="skill.category" severity="secondary" />
              </div>
              <p v-if="skill.description" class="text-gray-600 text-sm line-clamp-2">
                {{ skill.description }}
              </p>
              <div class="flex justify-end">
                <Button 
                  @click="router.push('/skills')"
                  size="small"
                  outlined
                >
                  Learn More
                </Button>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Call to Action -->
    <Card class="bg-primary text-white">
      <template #content>
        <div class="text-center space-y-6 py-8">
          <h2 class="text-3xl font-bold">Ready to Start Learning?</h2>
          <p class="text-lg opacity-90 max-w-2xl mx-auto">
            Join our community today and start exchanging skills with people around the world.
          </p>
          <Button 
            @click="handleGetStarted"
            severity="secondary"
            size="large"
            class="px-8 py-3"
          >
            <i class="pi pi-user-plus mr-2"></i>
            {{ authStore.isAuthenticated ? 'Browse Skills' : 'Join Now' }}
          </Button>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
