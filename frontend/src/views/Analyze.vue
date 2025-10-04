<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const toast = useToast()

const datasets = ref([])
const models = ref([])
const loading = ref(false)
const submitting = ref(false)

const form = ref({
  datasetId: null,
  modelId: null,
  mode: 'eda',
  params: {
    n_components: 6,
    cluster_k_max: 8,
    normalize: true,
    imputation: 'mean'
  }
})

const loadResources = async () => {
  loading.value = true
  try {
    const [datasetsRes, modelsRes] = await Promise.all([
      http.get('/api/datasets?per_page=100'),
      http.get('/api/models')
    ])
    datasets.value = datasetsRes.data.datasets || []
    models.value = modelsRes.data.models || []
  } catch (error) {
    console.error('Failed to load resources:', error)
  } finally {
    loading.value = false
  }
}

const submitAnalysis = async () => {
  if (!form.value.datasetId) {
    toast.error('Please select a dataset')
    return
  }
  
  submitting.value = true
  try {
    const payload = {
      dataset_id: form.value.datasetId,
      mode: form.value.mode,
      params: form.value.params
    }
    
    if (form.value.mode === 'predict' && form.value.modelId) {
      payload.model_id = form.value.modelId
    }
    
    const { data } = await http.post('/api/analyses', payload)
    toast.success('Analysis started successfully!')
    router.push('/analyses')
  } catch (error) {
    console.error('Analysis submission failed:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadResources()
})
</script>

<template>
  <div class="analyze-page">
    <h1>Manual Analysis Configuration</h1>
    <p>Configure and run custom analysis on your datasets</p>
    
    <LoadingSpinner v-if="loading" message="Loading resources..." />
    
    <div v-else class="analyze-form card">
      <div class="form-section">
        <h3>Dataset Selection</h3>
        <select v-model="form.datasetId" class="select">
          <option :value="null">Select a dataset...</option>
          <option v-for="dataset in datasets" :key="dataset.id" :value="dataset.id">
            {{ dataset.filename }} ({{ dataset.rows }} rows)
          </option>
        </select>
      </div>
      
      <div class="form-section">
        <h3>Analysis Mode</h3>
        <div class="radio-group">
          <label class="radio-option">
            <input type="radio" v-model="form.mode" value="eda" />
            <span>Exploratory Data Analysis</span>
          </label>
          <label class="radio-option">
            <input type="radio" v-model="form.mode" value="predict" />
            <span>Prediction</span>
          </label>
          <label class="radio-option">
            <input type="radio" v-model="form.mode" value="train" />
            <span>Model Training</span>
          </label>
        </div>
      </div>
      
      <div v-if="form.mode === 'predict'" class="form-section">
        <h3>Model Selection</h3>
        <select v-model="form.modelId" class="select">
          <option :value="null">Select a model...</option>
          <option v-for="model in models" :key="model.id" :value="model.id">
            {{ model.name }} v{{ model.version }}
          </option>
        </select>
      </div>
      
      <div class="form-section">
        <h3>Parameters</h3>
        <div class="params-grid">
          <div class="form-group">
            <label>Normalization</label>
            <select v-model="form.params.normalize" class="select">
              <option :value="true">Yes</option>
              <option :value="false">No</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Imputation</label>
            <select v-model="form.params.imputation" class="select">
              <option value="mean">Mean</option>
              <option value="median">Median</option>
              <option value="mode">Mode</option>
              <option value="drop">Drop</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>PCA Components</label>
            <input 
              v-model.number="form.params.n_components" 
              type="number" 
              min="2" 
              max="20"
              class="input"
            />
          </div>
          
          <div class="form-group">
            <label>Max Clusters</label>
            <input 
              v-model.number="form.params.cluster_k_max" 
              type="number" 
              min="2" 
              max="15"
              class="input"
            />
          </div>
        </div>
      </div>
      
      <div class="form-actions">
        <button class="btn ghost" @click="router.push('/wizard')">
          Use Wizard Instead
        </button>
        <button 
          class="btn primary" 
          @click="submitAnalysis"
          :disabled="submitting || !form.datasetId"
        >
          <span v-if="submitting" class="loading-spinner"></span>
          {{ submitting ? 'Starting...' : 'Start Analysis' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analyze-page {
  max-width: 800px;
  margin: 0 auto;
}

.analyze-form {
  padding: 32px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section h3 {
  margin: 0 0 16px 0;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--muted);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
}
</style>