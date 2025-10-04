<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../stores/auth'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import EmptyState from '../components/EmptyState.vue'

const auth = useAuth()
const toast = useToast()

const models = ref([])
const loading = ref(false)
const showCreateModal = ref(false)
const pagination = ref(null)
const currentPage = ref(1)

const newModel = ref({
  name: '',
  version: '1.0',
  description: '',
  dataset_id: null
})

const loadModels = async () => {
  loading.value = true
  try {
    const { data } = await http.get('/api/models', {
      params: { page: currentPage.value, per_page: 12 }
    })
    models.value = data.models || []
    pagination.value = data.pagination
  } catch (error) {
    console.error('Failed to load models:', error)
  } finally {
    loading.value = false
  }
}

const createModel = async () => {
  if (!newModel.value.name || !newModel.value.dataset_id) {
    toast.error('Please provide model name and dataset')
    return
  }
  
  try {
    await http.post('/api/models/train', {
      name: newModel.value.name,
      version: newModel.value.version,
      description: newModel.value.description,
      dataset_id: newModel.value.dataset_id
    })
    
    toast.success('Model training started!')
    showCreateModal.value = false
    loadModels()
  } catch (error) {
    console.error('Failed to create model:', error)
  }
}

const tuneModel = async (modelId) => {
  try {
    await http.post(`/api/models/${modelId}/tune`, {
      params: { learning_rate: 0.001 }
    })
    toast.success('Model tuning started')
  } catch (error) {
    console.error('Failed to tune model:', error)
  }
}

onMounted(() => {
  loadModels()
})
</script>

<template>
  <div class="models-page">
    <div class="page-header">
      <div>
        <h1>Model Catalog</h1>
        <p>Browse and manage machine learning models</p>
      </div>
      <button 
        v-if="auth.isResearcher"
        class="btn primary" 
        @click="showCreateModal = true"
      >
        Train New Model
      </button>
    </div>
    
    <LoadingSpinner v-if="loading" message="Loading models..." />
    
    <EmptyState 
      v-else-if="models.length === 0"
      title="No models available"
      message="No trained models in the catalog yet"
    >
      <template #icon>🤖</template>
    </EmptyState>
    
    <div v-else class="models-grid">
      <div v-for="model in models" :key="model.id" class="model-card card">
        <div class="model-header">
          <div class="model-icon">🤖</div>
          <div class="model-published" v-if="model.is_published">
            <span class="badge success">Published</span>
          </div>
        </div>
        
        <div class="model-info">
          <h3>{{ model.name }}</h3>
          <div class="model-version">v{{ model.version }}</div>
          <p class="model-description">{{ model.description || 'No description available' }}</p>
        </div>
        
        <div v-if="model.metrics" class="model-metrics">
          <div class="metric">
            <span class="metric-label">Accuracy</span>
            <span class="metric-value">
              {{ model.metrics.accuracy ? `${(model.metrics.accuracy * 100).toFixed(1)}%` : 'N/A' }}
            </span>
          </div>
          <div class="metric">
            <span class="metric-label">Loss</span>
            <span class="metric-value">
              {{ model.metrics.loss ? model.metrics.loss.toFixed(4) : 'N/A' }}
            </span>
          </div>
        </div>
        
        <div class="model-actions">
          <button class="btn ghost small">Use Model</button>
          <button 
            v-if="auth.isResearcher"
            class="btn primary small"
            @click="tuneModel(model.id)"
          >
            Fine-tune
          </button>
        </div>
        
        <div class="model-footer">
          <span class="model-date">
            Created {{ new Date(model.created_at).toLocaleDateString() }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- Create Model Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal card">
        <h2>Train New Model</h2>
        
        <div class="form-group">
          <label>Model Name</label>
          <input v-model="newModel.name" class="input" placeholder="Exoplanet Classifier v1" />
        </div>
        
        <div class="form-group">
          <label>Version</label>
          <input v-model="newModel.version" class="input" placeholder="1.0" />
        </div>
        
        <div class="form-group">
          <label>Description</label>
          <textarea 
            v-model="newModel.description" 
            class="textarea" 
            rows="3"
            placeholder="Describe the model's purpose and capabilities..."
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>Training Dataset ID</label>
          <input 
            v-model.number="newModel.dataset_id" 
            type="number" 
            class="input" 
            placeholder="1"
          />
        </div>
        
        <div class="modal-actions">
          <button class="btn ghost" @click="showCreateModal = false">Cancel</button>
          <button class="btn primary" @click="createModel">Start Training</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.models-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.model-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.model-icon {
  font-size: 32px;
}

.model-info {
  margin-bottom: 16px;
}

.model-info h3 {
  margin: 0 0 4px 0;
}

.model-version {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 8px;
}

.model-description {
  font-size: 14px;
  color: var(--muted);
  margin: 0;
}

.model-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 12px;
  background: var(--panel-2);
  border-radius: 8px;
  margin-bottom: 16px;
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
}

.model-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.model-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--line);
  font-size: 12px;
  color: var(--muted);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  width: 90%;
  max-width: 500px;
  padding: 32px;
}

.modal h2 {
  margin: 0 0 24px 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--muted);
}

.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

.badge.success {
  background: rgba(62, 230, 176, 0.2);
  color: var(--accent);
}
</style>