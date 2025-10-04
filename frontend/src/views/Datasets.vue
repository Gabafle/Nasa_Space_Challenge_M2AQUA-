<script setup>
import { ref, onMounted, computed } from 'vue' // Add computed import
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import EmptyState from '../components/EmptyState.vue'
import filesize from 'filesize'

const router = useRouter()
const auth = useAuth()
const toast = useToast()

const loading = ref(true)
const datasets = ref([])
const pagination = ref(null)
const currentPage = ref(1)
const showPublic = ref(true)
const viewFilter = ref('all') // 'all', 'mine', 'public'

const loadDatasets = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: 12,
      show_public: showPublic.value
    }
    
    const { data } = await http.get('/api/datasets', { params })
    datasets.value = data.datasets || []
    pagination.value = data.pagination
  } catch (error) {
    console.error('Load datasets error:', error)
  } finally {
    loading.value = false
  }
}

const filteredDatasets = computed(() => {
  if (viewFilter.value === 'mine') {
    return datasets.value.filter(d => d.user_id === auth.user?.id)
  } else if (viewFilter.value === 'public') {
    return datasets.value.filter(d => d.is_public && d.user_id !== auth.user?.id)
  }
  return datasets.value
})

const downloadDataset = async (dataset) => {
  try {
    const response = await http.get(`/api/datasets/${dataset.id}/download`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', dataset.filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    toast.success('Download started')
  } catch (error) {
    console.error('Download error:', error)
  }
}

const deleteDataset = async (dataset) => {
  if (!confirm(`Delete dataset "${dataset.filename}"? This cannot be undone.`)) {
    return
  }
  
  try {
    await http.delete(`/api/datasets/${dataset.id}`)
    toast.success('Dataset deleted')
    loadDatasets()
  } catch (error) {
    console.error('Delete error:', error)
  }
}

const canModifyDataset = (dataset) => {
  return dataset.user_id === auth.user?.id
}

const getVisibilityIcon = (dataset) => {
  return dataset.is_public ? '🌍' : '🔒'
}

const getVisibilityText = (dataset) => {
  return dataset.is_public ? 'Public' : 'Private'
}

onMounted(() => {
  loadDatasets()
})
</script>

<template>
  <div class="datasets-page">
    <div class="page-header">
      <div>
        <h1>Datasets</h1>
        <p>Manage and explore exoplanet datasets</p>
      </div>
      <button class="btn primary" @click="router.push('/upload')">
        Upload New Dataset
      </button>
    </div>
    
    <!-- Filter Controls -->
    <div class="filters card">
      <div class="filter-group">
        <label>View</label>
        <div class="filter-buttons">
          <button 
            :class="['btn', viewFilter === 'all' ? 'primary' : 'ghost']"
            @click="viewFilter = 'all'"
          >
            All Datasets
          </button>
          <button 
            :class="['btn', viewFilter === 'mine' ? 'primary' : 'ghost']"
            @click="viewFilter = 'mine'"
          >
            My Datasets
          </button>
          <button 
            :class="['btn', viewFilter === 'public' ? 'primary' : 'ghost']"
            @click="viewFilter = 'public'"
          >
            Public Datasets
          </button>
        </div>
      </div>
      
      <div class="filter-group">
        <label class="checkbox-label">
          <input 
            type="checkbox" 
            v-model="showPublic"
            @change="loadDatasets"
            class="checkbox"
          />
          <span>Include public datasets</span>
        </label>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Loading datasets..." />
    
    <EmptyState 
      v-else-if="filteredDatasets.length === 0" 
      title="No datasets found" 
      :message="viewFilter === 'mine' ? 'You haven\'t uploaded any datasets yet' : 'No datasets match your current filter'"
    >
      <template #action>
        <button class="btn primary" @click="router.push('/upload')">
          Upload Dataset
        </button>
      </template>
    </EmptyState>
    
    <div v-else class="datasets-grid">
      <div 
        v-for="dataset in filteredDatasets" 
        :key="dataset.id" 
        class="dataset-card card"
      >
        <!-- Dataset Header -->
        <div class="dataset-header">
          <div class="dataset-title">
            <h3>{{ dataset.filename }}</h3>
            <div class="dataset-badges">
              <span :class="`badge ${dataset.is_public ? 'public' : 'private'}`">
                {{ getVisibilityIcon(dataset) }} {{ getVisibilityText(dataset) }}
              </span>
              <span v-if="dataset.owner_name" class="owner-badge">
                by {{ dataset.owner_name }}
              </span>
            </div>
          </div>
          
          <div class="dataset-actions">
            <button 
              class="btn ghost small" 
              @click="downloadDataset(dataset)"
              title="Download dataset"
            >
              ⬇️
            </button>
            <button 
              v-if="canModifyDataset(dataset)"
              class="btn danger small" 
              @click="deleteDataset(dataset)"
              title="Delete dataset"
            >
              🗑️
            </button>
          </div>
        </div>
        
        <!-- Dataset Stats -->
        <div class="dataset-stats">
          <div class="stat">
            <span class="stat-icon">📊</span>
            <div class="stat-info">
              <span class="stat-value">{{ dataset.rows?.toLocaleString() || 0 }}</span>
              <span class="stat-label">Rows</span>
            </div>
          </div>
          
          <div class="stat">
            <span class="stat-icon">📋</span>
            <div class="stat-info">
              <span class="stat-value">{{ dataset.cols || 0 }}</span>
              <span class="stat-label">Columns</span>
            </div>
          </div>
          
          <div class="stat">
            <span class="stat-icon">💾</span>
            <div class="stat-info">
              <span class="stat-value">{{ filesize(dataset.size_bytes || 0) }}</span>
              <span class="stat-label">Size</span>
            </div>
          </div>
        </div>
        
        <!-- Dataset Footer -->
        <div class="dataset-footer">
          <span class="dataset-date">
            Uploaded {{ new Date(dataset.created_at).toLocaleDateString() }}
          </span>
          <button 
            class="btn primary small" 
            @click="router.push(`/wizard?dataset=${dataset.id}`)"
          >
            Analyze
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination && pagination.pages > 1" class="pagination">
      <button 
        class="btn ghost" 
        :disabled="currentPage === 1" 
        @click="currentPage--; loadDatasets()"
      >
        Previous
      </button>
      
      <span class="page-info">
        Page {{ currentPage }} of {{ pagination.pages }}
      </span>
      
      <button 
        class="btn ghost" 
        :disabled="currentPage === pagination.pages" 
        @click="currentPage++; loadDatasets()"
      >
        Next
      </button>
    </div>
  </div>
</template>

<style scoped>
.datasets-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0 0 8px 0;
}

.page-header p {
  margin: 0;
  color: var(--muted);
}

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  margin-bottom: 24px;
  gap: 24px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: var(--muted);
}

.filter-buttons {
  display: flex;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--brand);
}

.datasets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.dataset-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s;
}

.dataset-card:hover {
  transform: translateY(-2px);
}

.dataset-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.dataset-title {
  flex: 1;
}

.dataset-title h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  word-break: break-word;
}

.dataset-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.badge.public {
  background: rgba(62, 230, 176, 0.2);
  color: var(--accent);
}

.badge.private {
  background: rgba(90, 162, 255, 0.2);
  color: var(--brand);
}

.owner-badge {
  padding: 2px 8px;
  border-radius: 12px;
  background: var(--panel-2);
  color: var(--muted);
  font-size: 11px;
}

.dataset-actions {
  display: flex;
  gap: 6px;
  margin-left: 12px;
}

.dataset-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px;
  background: var(--panel-2);
  border-radius: 8px;
  margin-bottom: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-icon {
  font-size: 16px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
}

.stat-label {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

.dataset-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--line);
}

.dataset-date {
  font-size: 12px;
  color: var(--muted);
}

.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
}

.page-info {
  color: var(--muted);
  font-size: 14px;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-buttons {
    flex-wrap: wrap;
  }
  
  .datasets-grid {
    grid-template-columns: 1fr;
  }
}
</style>
