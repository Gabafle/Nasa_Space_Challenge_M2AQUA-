<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import EmptyState from '../components/EmptyState.vue'

const router = useRouter()
const toast = useToast()

const analyses = ref([])
const loading = ref(false)
const pagination = ref(null)
const currentPage = ref(1)
const statusFilter = ref('')

const loadAnalyses = async () => {
  loading.value = true
  try {
    const params = { 
      page: currentPage.value, 
      per_page: 10 
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const { data } = await http.get('/api/analyses', { params })
    analyses.value = data.analyses || []
    pagination.value = data.pagination
  } catch (error) {
    console.error('Failed to load analyses:', error)
  } finally {
    loading.value = false
  }
}

const getStatusColor = (status) => {
  const colors = {
    done: 'success',
    running: 'warn',
    error: 'danger',
    pending: 'info'
  }
  return colors[status] || 'info'
}

const formatDuration = (start, end) => {
  if (!start || !end) return 'N/A'
  const duration = new Date(end) - new Date(start)
  const seconds = Math.floor(duration / 1000)
  const minutes = Math.floor(seconds / 60)
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`
  return `${seconds}s`
}

onMounted(() => {
  loadAnalyses()
})
</script>

<template>
  <div class="analyses-page">
    <div class="page-header">
      <div>
        <h1>Analysis Runs</h1>
        <p>Track and manage your analysis runs</p>
      </div>
      <button class="btn primary" @click="router.push('/wizard')">
        New Analysis
      </button>
    </div>
    
    <div class="filters card">
      <select v-model="statusFilter" @change="loadAnalyses" class="select">
        <option value="">All Statuses</option>
        <option value="done">Completed</option>
        <option value="running">Running</option>
        <option value="pending">Pending</option>
        <option value="error">Failed</option>
      </select>
    </div>
    
    <LoadingSpinner v-if="loading" message="Loading analyses..." />
    
    <EmptyState 
      v-else-if="analyses.length === 0"
      title="No analyses yet"
      message="Start your first analysis to see results here"
    >
      <template #action>
        <button class="btn primary" @click="router.push('/wizard')">
          Start Analysis
        </button>
      </template>
    </EmptyState>
    
    <div v-else class="analyses-list">
      <div v-for="analysis in analyses" :key="analysis.id" class="analysis-card card">
        <div class="analysis-header">
          <div>
            <h3>Analysis #{{ analysis.id }}</h3>
            <div class="analysis-meta">
              <span :class="`badge ${getStatusColor(analysis.status)}`">
                {{ analysis.status }}
              </span>
              <span class="mode-badge">{{ analysis.mode?.toUpperCase() }}</span>
            </div>
          </div>
          <div class="analysis-actions">
            <router-link 
              v-if="analysis.status === 'done'"
              :to="`/viz/${analysis.id}`"
              class="btn primary small"
            >
              View Results
            </router-link>
            <div v-else-if="analysis.status === 'running'" class="running-indicator">
              <span class="loading-spinner"></span>
              Running...
            </div>
          </div>
        </div>
        
        <div class="analysis-details">
          <div class="detail-item">
            <span class="detail-label">Dataset ID:</span>
            <span class="detail-value">{{ analysis.dataset_id }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Started:</span>
            <span class="detail-value">
              {{ analysis.started_at ? new Date(analysis.started_at).toLocaleString() : 'N/A' }}
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Duration:</span>
            <span class="detail-value">
              {{ formatDuration(analysis.started_at, analysis.finished_at) }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="pagination && pagination.pages > 1" class="pagination">
      <button 
        class="btn ghost"
        :disabled="currentPage === 1"
        @click="currentPage--; loadAnalyses()"
      >
        Previous
      </button>
      <span>Page {{ currentPage }} of {{ pagination.pages }}</span>
      <button 
        class="btn ghost"
        :disabled="currentPage === pagination.pages"
        @click="currentPage++; loadAnalyses()"
      >
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
.analyses-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.filters {
  padding: 16px;
  margin-bottom: 24px;
}

.analyses-list {
  display: grid;
  gap: 16px;
}

.analysis-card {
  padding: 24px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.analysis-header h3 {
  margin: 0 0 8px 0;
}

.analysis-meta {
  display: flex;
  gap: 8px;
}

.mode-badge {
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--panel-2);
  font-size: 12px;
}

.analysis-actions {
  display: flex;
  gap: 8px;
}

.running-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--warn);
}

.analysis-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px;
  background: var(--panel-2);
  border-radius: 8px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: var(--muted);
}

.detail-value {
  font-size: 14px;
}

.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

.badge.success {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.badge.warn {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.badge.danger {
  background: rgba(255, 107, 107, 0.2);
  color: var(--danger);
}

.badge.info {
  background: rgba(90, 162, 255, 0.2);
  color: var(--brand);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}
</style>