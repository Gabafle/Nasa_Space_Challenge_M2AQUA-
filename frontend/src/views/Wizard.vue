<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const toast = useToast()

const currentStep = ref(1)
const datasets = ref([])
const loadingDatasets = ref(false)
const submitting = ref(false)

const wizardData = ref({
  datasetId: null,
  analysisMode: 'eda',
  parameters: {
    normalize: true,
    imputation: 'mean',
    pca_components: 6,
    cluster_method: 'kmeans',
    cluster_k_max: 8
  }
})

const steps = [
  { id: 1, name: 'Select Dataset', icon: '📊' },
  { id: 2, name: 'Choose Analysis', icon: '🔬' },
  { id: 3, name: 'Configure Parameters', icon: '⚙️' },
  { id: 4, name: 'Review & Run', icon: '🚀' }
]

const canProceed = computed(() => {
  if (currentStep.value === 1) return wizardData.value.datasetId
  if (currentStep.value === 2) return wizardData.value.analysisMode
  if (currentStep.value === 3) return true
  return false
})

const loadDatasets = async () => {
  loadingDatasets.value = true
  try {
    const { data } = await http.get('/api/datasets?per_page=100')
    datasets.value = data.datasets || []
  } catch (error) {
    console.error('Failed to load datasets:', error)
  } finally {
    loadingDatasets.value = false
  }
}

const nextStep = () => {
  if (canProceed.value && currentStep.value < 4) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const submitAnalysis = async () => {
  submitting.value = true
  try {
    const payload = {
      dataset_id: wizardData.value.datasetId,
      mode: wizardData.value.analysisMode,
      params: wizardData.value.parameters
    }
    
    const { data } = await http.post('/api/analyses', payload)
    toast.success('Analysis started successfully!')
    
    // Redirect to analysis view
    setTimeout(() => {
      router.push(`/analyses`)
    }, 1000)
  } catch (error) {
    console.error('Analysis submission failed:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadDatasets()
})
</script>

<template>
  <div class="wizard-container">
    <h1>Analysis Grid</h1>
    <p>Let's guide you through setting up your exoplanet analysis</p>
    
    <!-- Progress Steps -->
    <div class="wizard-steps">
      <div 
        v-for="step in steps" 
        :key="step.id"
        :class="['step', { 
          active: currentStep === step.id, 
          completed: currentStep > step.id 
        }]"
      >
        <div class="step-circle">
          <span v-if="currentStep > step.id">✓</span>
          <span v-else>{{ step.icon }}</span>
        </div>
        <div class="step-label">{{ step.name }}</div>
      </div>
      <div class="step-line"></div>
    </div>
    
    <!-- Step Content -->
    <div class="wizard-content card">
      <!-- Step 1: Select Dataset -->
      <div v-if="currentStep === 1" class="step-content">
        <h2>Select Your Dataset</h2>
        <p>Choose the dataset you want to analyze</p>
        
        <LoadingSpinner v-if="loadingDatasets" message="Loading datasets..." />
        
        <div v-else-if="datasets.length === 0" class="empty-message">
          No datasets available. Please upload a dataset first.
        </div>
        
        <div v-else class="dataset-grid">
          <div 
            v-for="dataset in datasets" 
            :key="dataset.id"
            :class="['dataset-option', { selected: wizardData.datasetId === dataset.id }]"
            @click="wizardData.datasetId = dataset.id"
          >
            <div class="dataset-icon">📁</div>
            <div class="dataset-info">
              <div class="dataset-name">{{ dataset.filename }}</div>
              <div class="dataset-meta">
                {{ dataset.rows }} rows • {{ dataset.cols }} columns
              </div>
            </div>
            <div v-if="wizardData.datasetId === dataset.id" class="check-mark">✓</div>
          </div>
        </div>
      </div>
      
      <!-- Step 2: Choose Analysis Type -->
      <div v-else-if="currentStep === 2" class="step-content">
        <h2>Choose Analysis Type</h2>
        <p>Select the type of analysis you want to perform</p>
        
        <div class="analysis-options">
          <div 
            :class="['analysis-option', { selected: wizardData.analysisMode === 'eda' }]"
            @click="wizardData.analysisMode = 'eda'"
          >
            <div class="option-icon">📊</div>
            <h3>Exploratory Data Analysis</h3>
            <p>Comprehensive statistical analysis, distributions, and correlations</p>
          </div>
          
          <div 
            :class="['analysis-option', { selected: wizardData.analysisMode === 'predict' }]"
            @click="wizardData.analysisMode = 'predict'"
          >
            <div class="option-icon">🎯</div>
            <h3>Prediction</h3>
            <p>Use trained models to predict exoplanet characteristics</p>
          </div>
          
          <div 
            :class="['analysis-option', { selected: wizardData.analysisMode === 'train' }]"
            @click="wizardData.analysisMode = 'train'"
          >
            <div class="option-icon">🤖</div>
            <h3>Model Training</h3>
            <p>Train new models on your dataset</p>
          </div>
        </div>
      </div>
      
      <!-- Step 3: Configure Parameters -->
      <div v-else-if="currentStep === 3" class="step-content">
        <h2>Configure Parameters</h2>
        <p>Adjust analysis parameters to your needs</p>
        
        <div class="parameters-form">
          <div class="form-group">
            <label>Data Normalization</label>
            <select v-model="wizardData.parameters.normalize" class="select">
              <option :value="true">Yes - Standardize features</option>
              <option :value="false">No - Keep original scale</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Missing Value Imputation</label>
            <select v-model="wizardData.parameters.imputation" class="select">
              <option value="mean">Mean</option>
              <option value="median">Median</option>
              <option value="mode">Mode</option>
              <option value="drop">Drop rows with missing values</option>
            </select>
          </div>
          
          <div v-if="wizardData.analysisMode === 'eda'" class="form-group">
            <label>PCA Components (2-12)</label>
            <input 
              v-model.number="wizardData.parameters.pca_components" 
              type="number" 
              min="2" 
              max="12"
              class="input"
            />
          </div>
          
          <div v-if="wizardData.analysisMode === 'eda'" class="form-group">
            <label>Clustering Method</label>
            <select v-model="wizardData.parameters.cluster_method" class="select">
              <option value="kmeans">K-Means</option>
              <option value="dbscan">DBSCAN</option>
              <option value="hierarchical">Hierarchical</option>
            </select>
          </div>
          
          <div v-if="wizardData.parameters.cluster_method === 'kmeans'" class="form-group">
            <label>Maximum Clusters (K)</label>
            <input 
              v-model.number="wizardData.parameters.cluster_k_max" 
              type="number" 
              min="2" 
              max="15"
              class="input"
            />
          </div>
        </div>
      </div>
      
      <!-- Step 4: Review & Run -->
      <div v-else-if="currentStep === 4" class="step-content">
        <h2>Review Your Configuration</h2>
        <p>Please review your settings before starting the analysis</p>
        
        <div class="review-section">
          <div class="review-item">
            <span class="review-label">Dataset:</span>
            <span class="review-value">
              {{ datasets.find(d => d.id === wizardData.datasetId)?.filename }}
            </span>
          </div>
          
          <div class="review-item">
            <span class="review-label">Analysis Type:</span>
            <span class="review-value">{{ wizardData.analysisMode.toUpperCase() }}</span>
          </div>
          
          <div class="review-item">
            <span class="review-label">Normalization:</span>
            <span class="review-value">{{ wizardData.parameters.normalize ? 'Yes' : 'No' }}</span>
          </div>
          
          <div class="review-item">
            <span class="review-label">Imputation:</span>
            <span class="review-value">{{ wizardData.parameters.imputation }}</span>
          </div>
          
          <div v-if="wizardData.analysisMode === 'eda'">
            <div class="review-item">
              <span class="review-label">PCA Components:</span>
              <span class="review-value">{{ wizardData.parameters.pca_components }}</span>
            </div>
            
            <div class="review-item">
              <span class="review-label">Clustering:</span>
              <span class="review-value">
                {{ wizardData.parameters.cluster_method }} 
                (K={{ wizardData.parameters.cluster_k_max }})
              </span>
            </div>
          </div>
        </div>
        
        <div class="launch-section">
          <button 
            class="btn success large" 
            @click="submitAnalysis"
            :disabled="submitting"
          >
            <span v-if="submitting" class="loading-spinner"></span>
            {{ submitting ? 'Starting Analysis...' : '🚀 Launch Analysis' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Navigation Buttons -->
    <div class="wizard-nav">
      <button 
        v-if="currentStep > 1" 
        class="btn ghost" 
        @click="prevStep"
      >
        ← Previous
      </button>
      <div class="spacer"></div>
      <button 
        v-if="currentStep < 4" 
        class="btn primary" 
        @click="nextStep"
        :disabled="!canProceed"
      >
        Next →
      </button>
    </div>
  </div>
</template>

<style scoped>
.wizard-container {
  max-width: 900px;
  margin: 0 auto;
}

.wizard-steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 32px 0;
  position: relative;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 2;
}

.step-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--panel);
  border: 2px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: all 0.3s;
}

.step.active .step-circle {
  background: var(--brand);
  border-color: var(--brand);
  transform: scale(1.1);
}

.step.completed .step-circle {
  background: var(--accent);
  border-color: var(--accent);
}

.step-label {
  font-size: 12px;
  color: var(--muted);
  text-align: center;
}

.step.active .step-label {
  color: var(--brand);
  font-weight: 600;
}

.step-line {
  position: absolute;
  top: 25px;
  left: 60px;
  right: 60px;
  height: 2px;
  background: var(--line);
  z-index: 1;
}

.wizard-content {
  padding: 32px;
  min-height: 400px;
}

.step-content h2 {
  margin: 0 0 8px 0;
}

.step-content > p {
  color: var(--muted);
  margin: 0 0 32px 0;
}

.dataset-grid {
  display: grid;
  gap: 16px;
}

.dataset-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--panel-2);
  border: 2px solid var(--line);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.dataset-option:hover {
  border-color: var(--brand);
}

.dataset-option.selected {
  border-color: var(--accent);
  background: rgba(62, 230, 176, 0.05);
}

.dataset-icon {
  font-size: 32px;
}

.dataset-info {
  flex: 1;
}

.dataset-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.dataset-meta {
  font-size: 12px;
  color: var(--muted);
}

.check-mark {
  font-size: 24px;
  color: var(--accent);
}

.analysis-options {
  display: grid;
  gap: 16px;
}

.analysis-option {
  padding: 24px;
  background: var(--panel-2);
  border: 2px solid var(--line);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.analysis-option:hover {
  border-color: var(--brand);
  transform: translateY(-2px);
}

.analysis-option.selected {
  border-color: var(--accent);
  background: rgba(62, 230, 176, 0.05);
}

.option-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.analysis-option h3 {
  margin: 0 0 8px 0;
}

.analysis-option p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.parameters-form {
  display: grid;
  gap: 24px;
  max-width: 500px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--muted);
}

.review-section {
  background: var(--panel-2);
  padding: 24px;
  border-radius: 10px;
  margin-bottom: 32px;
}

.review-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.review-item:last-child {
  border-bottom: none;
}

.review-label {
  color: var(--muted);
  font-size: 14px;
}

.review-value {
  font-weight: 500;
}

.launch-section {
  text-align: center;
}

.btn.large {
  font-size: 18px;
  padding: 14px 32px;
}

.wizard-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
}

.spacer {
  flex: 1;
}

.empty-message {
  text-align: center;
  padding: 48px;
  color: var(--muted);
}
</style>