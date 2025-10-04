<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const auth = useAuth()
const loading = ref(true)
const stats = ref({
  datasets: 0,
  analyses: 0,
  models: 0
})
const recentAnalyses = ref([])
const recentDatasets = ref([])

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

const loadDashboard = async () => {
  loading.value = true
  try {
    const [datasetsRes, analysesRes, modelsRes] = await Promise.all([
      http.get('/api/datasets?per_page=5'),
      http.get('/api/analyses?per_page=5'),
      http.get('/api/models?per_page=5')
    ])
    
    stats.value = {
      datasets: datasetsRes.data.pagination?.total || 0,
      analyses: analysesRes.data.pagination?.total || 0,
      models: modelsRes.data.models?.length || 0
    }
    
    recentDatasets.value = datasetsRes.data.datasets || []
    recentAnalyses.value = analysesRes.data.analyses || []
  } catch (error) {
    console.error('Dashboard load error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})

const getStatusBadge = (status) => {
  const badges = {
    done: 'success',
    running: 'warn',
    error: 'danger',
    pending: 'info'
  }
  return badges[status] || 'info'
}
</script>

<template>
  <div class="dashboard">
    <!-- Starfield Background -->
    <div class="starfield-bg"></div>
    
    <div class="welcome-section astro-fade-in">
      <h1>{{ greeting }}, {{ auth.user?.name || 'Researcher' }}!</h1>
      <p>Welcome to your exoplanet analysis dashboard — Powered by AstroMetric</p>
    </div>

    <LoadingSpinner v-if="loading" message="Loading dashboard..." />
    
    <template v-else>
      <!-- Stats Cards -->
      <div class="grid cols-3 stats-grid">
        <div class="stat-card astro-fade-in">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.datasets }}</div>
            <div class="stat-label">Datasets</div>
          </div>
          <div class="stat-glow"></div>
        </div>
        <div class="stat-card astro-fade-in">
          <div class="stat-icon">🔬</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.analyses }}</div>
            <div class="stat-label">Analyses</div>
          </div>
          <div class="stat-glow"></div>
        </div>
        <div class="stat-card astro-fade-in">
          <div class="stat-icon">🤖</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.models }}</div>
            <div class="stat-label">Models</div>
          </div>
          <div class="stat-glow"></div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions astro-fade-in">
        <h2>Quick Actions</h2>
        <div class="grid cols-4 actions-grid">
          <button class="action-card" @click="router.push('/upload')">
            <div class="action-icon">📁</div>
            <div class="action-label">Upload Dataset</div>
            <div class="action-glow"></div>
          </button>
          <button class="action-card" @click="router.push('/wizard')">
            <div class="action-icon">🔍</div>
            <div class="action-label">Analysis Grid</div>
            <div class="action-glow"></div>
          </button>
          <button class="action-card" @click="router.push('/analyses')">
            <div class="action-icon">📈</div>
            <div class="action-label">View Analyses</div>
            <div class="action-glow"></div>
          </button>
          <button class="action-card" @click="router.push('/leaderboard')">
            <div class="action-icon">🏆</div>
            <div class="action-label">Leaderboard</div>
            <div class="action-glow"></div>
          </button>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="grid cols-2 activity-grid">
        <div class="card recent-card">
          <h3>Recent Datasets</h3>
          <div v-if="recentDatasets.length === 0" class="empty-message">
            No datasets yet
          </div>
          <div v-else class="item-list">
            <div v-for="dataset in recentDatasets" :key="dataset.id" class="list-item">
              <div>
                <div class="item-title">{{ dataset.filename }}</div>
                <div class="item-meta">{{ dataset.rows }} rows • {{ dataset.cols }} columns</div>
              </div>
              <router-link :to="`/datasets`" class="btn ghost small">View</router-link>
            </div>
          </div>
        </div>
        
        <div class="card recent-card">
          <h3>Recent Analyses</h3>
          <div v-if="recentAnalyses.length === 0" class="empty-message">
            No analyses yet
          </div>
          <div v-else class="item-list">
            <div v-for="analysis in recentAnalyses" :key="analysis.id" class="list-item">
              <div>
                <div class="item-title">Analysis #{{ analysis.id }}</div>
                <div class="item-meta">
                  <span :class="`badge ${getStatusBadge(analysis.status)}`">
                    {{ analysis.status }}
                  </span>
                </div>
              </div>
              <router-link 
                v-if="analysis.status === 'done'" 
                :to="`/viz/${analysis.id}`" 
                class="btn ghost small"
              >
                View
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.welcome-section {
  margin-bottom: 40px;
  text-align: center;
}

.welcome-section h1 {
  margin: 0 0 12px 0;
  font-size: 3rem;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-section p {
  color: var(--astro-light);
  margin: 0;
  font-size: 1.2rem;
  font-family: Arial, sans-serif;
}

.stats-grid {
  margin-bottom: 40px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 32px 24px;
  background: var(--panel);
  border: 1px solid var(--accent);
  border-radius: var(--radius);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(29, 205, 159, 0.2);
}

.stat-card .stat-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(29, 205, 159, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover .stat-glow {
  opacity: 1;
}

.stat-icon {
  font-size: 40px;
  filter: drop-shadow(0 0 10px rgba(29, 205, 159, 0.5));
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--brand);
  font-family: "Arial Black", Arial, sans-serif;
}

.stat-label {
  color: var(--astro-light);
  font-size: 16px;
  font-family: Arial, sans-serif;
}

.quick-actions {
  margin: 40px 0;
}

.quick-actions h2 {
  margin: 0 0 24px 0;
  text-align: center;
}

.actions-grid {
  gap: 20px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px 24px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-card:hover {
  background: var(--panel-2);
  transform: translateY(-4px);
  border-color: var(--accent);
}

.action-card .action-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: var(--astro-gradient);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.action-card:hover .action-glow {
  opacity: 0.1;
}

.action-icon {
  font-size: 40px;
  filter: drop-shadow(0 0 8px rgba(72, 241, 175, 0.3));
}

.action-label {
  font-size: 16px;
  color: var(--astro-light);
  font-family: Arial, sans-serif;
  font-weight: 500;
}

.activity-grid {
  margin-top: 40px;
  gap: 24px;
}

.recent-card {
  padding: 24px;
}

.recent-card h3 {
  margin: 0 0 20px 0;
  font-size: 1.3rem;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--panel-2);
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.list-item:hover {
  border-color: var(--accent);
  background: rgba(29, 205, 159, 0.05);
}

.item-title {
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--fg);
  font-family: Arial, sans-serif;
}

.item-meta {
  font-size: 12px;
  color: var(--muted);
}

.empty-message {
  text-align: center;
  padding: 32px;
  color: var(--muted);
  font-family: Arial, sans-serif;
}

.btn.small {
  padding: 8px 16px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .welcome-section h1 {
    font-size: 2rem;
  }
  
  .stats-grid,
  .actions-grid,
  .activity-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 24px 20px;
  }
  
  .action-card {
    padding: 24px 20px;
  }
}
</style>
