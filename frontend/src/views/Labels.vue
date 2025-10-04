<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../stores/auth'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const auth = useAuth()
const toast = useToast()

const datasets = ref([])
const selectedDataset = ref(null)
const labels = ref([])
const loading = ref(false)
const saving = ref(false)
const currentPage = ref(1)

const newLabels = ref([])
const batchSize = 10

const loadDatasets = async () => {
  try {
    const { data } = await http.get('/api/datasets')
    datasets.value = data.datasets || []
    if (datasets.value.length > 0 && !selectedDataset.value) {
      selectedDataset.value = datasets.value[0].id
    }
  } catch (error) {
    console.error('Failed to load datasets:', error)
  }
}

const loadLabels = async () => {
  if (!selectedDataset.value) return
  
  loading.value = true
  try {
    const { data } = await http.get('/api/labels', {
      params: { 
        dataset_id: selectedDataset.value,
        page: currentPage.value,
        per_page: batchSize
      }
    })
    labels.value = data.labels || []
    
    // Initialize new labels array
    newLabels.value = Array(batchSize).fill(null).map((_, index) => ({
      row_id: (currentPage.value - 1) * batchSize + index,
      label: '',
      confidence: 1.0,
      notes: ''
    }))
  } catch (error) {
    console.error('Failed to load labels:', error)
  } finally {
    loading.value = false
  }
}

const saveLabels = async () => {
  const validLabels = newLabels.value.filter(l => l.label)
  if (validLabels.length === 0) {
    toast.error('No labels to save')
    return
  }
  
  saving.value = true
  try {
    await http.post('/api/labels/batch', {
      dataset_id: selectedDataset.value,
      items: validLabels
    })
    
    toast.success(`${validLabels.length} labels saved`)
    newLabels.value.forEach(l => {
      l.label = ''
      l.confidence = 1.0
      l.notes = ''
    })
    loadLabels()
  } catch (error) {
    console.error('Failed to save labels:', error)
  } finally {
    saving.value = false
  }
}

const exportLabels = async () => {
  if (!selectedDataset.value) return
  
  try {
    const response = await http.get('/api/labels/export', {
      params: { dataset_id: selectedDataset.value, format: 'csv' },
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `labeled_dataset_${selectedDataset.value}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    toast.success('Export started')
  } catch (error) {
    console.error('Export failed:', error)
  }
}

onMounted(() => {
  if (!auth.isResearcher) {
    toast.error('Researcher access required')
    return
  }
  loadDatasets()
})
</script>

<template>
  <div class="labels-page">
    <div class="page-header">
      <div>
        <h1>Data Labeling</h1>
        <p>Label datasets for supervised learning</p>
      </div>
      <button 
        v-if="selectedDataset"
        class="btn success" 
        @click="exportLabels"
      >
        Export Labeled Data
      </button>
    </div>
    
    <div class="controls card">
      <div class="control-row">
        <div class="form-group">
          <label>Dataset</label>
          <select 
            v-model="selectedDataset" 
            @change="loadLabels"
            class="select"
          >
            <option :value="null">Select a dataset...</option>
            <option v-for="dataset in datasets" :key="dataset.id" :value="dataset.id">
              {{ dataset.filename }} ({{ dataset.rows }} rows)
            </option>
          </select>
        </div>
        
        <div class="pagination-controls">
          <button 
            class="btn ghost"
            :disabled="currentPage === 1"
            @click="currentPage--; loadLabels()"
          >
            Previous Batch
          </button>
          <span>Batch {{ currentPage }}</span>
          <button 
            class="btn ghost"
            @click="currentPage++; loadLabels()"
          >
            Next Batch
          </button>
        </div>
      </div>
    </div>
    
    <LoadingSpinner v-if="loading" message="Loading labels..." />
    
    <div v-else-if="selectedDataset" class="labeling-interface">
      <div class="existing-labels card" v-if="labels.length > 0">
        <h3>Existing Labels</h3>
        <div class="labels-list">
          <div v-for="label in labels" :key="label.id" class="label-item">
            <span class="label-row">Row {{ label.row_id }}:</span>
            <span class="label-value">{{ label.label }}</span>
            <span class="label-confidence">{{ (label.confidence * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>
      
      <div class="new-labels card">
        <h3>Add Labels (Rows {{ (currentPage - 1) * batchSize }} - {{ currentPage * batchSize }})</h3>
        
        <div class="label-grid">
          <div v-for="(item, index) in newLabels" :key="index" class="label-entry">
            <div class="label-header">
              Row {{ item.row_id }}
            </div>
            
            <div class="label-fields">
              <div class="field-group">
                <label>Label</label>
                <input 
                  v-model="item.label" 
                  class="input small"
                  placeholder="e.g., confirmed, candidate, false_positive"
                />
              </div>
              
              <div class="field-group">
                <label>Confidence</label>
                <input 
                  v-model.number="item.confidence" 
                  type="number" 
                  min="0" 
                  max="1" 
                  step="0.1"
                  class="input small"
                />
              </div>
              
              <div class="field-group">
                <label>Notes</label>
                <input 
                  v-model="item.notes" 
                  class="input small"
                  placeholder="Optional notes"
                />
              </div>
            </div>
          </div>
        </div>
        
        <div class="label-actions">
          <button 
            class="btn primary" 
            @click="saveLabels"
            :disabled="saving"
          >
            <span v-if="saving" class="loading-spinner"></span>
            {{ saving ? 'Saving...' : 'Save Labels' }}
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-message">
      Please select a dataset to start labeling
    </div>
  </div>
</template>

<style scoped>
.labels-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.controls {
  padding: 16px;
  margin-bottom: 24px;
}

.control-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.labeling-interface {
  display: grid;
  gap: 24px;
}

.existing-labels h3,
.new-labels h3 {
  margin: 0 0 16px 0;
}

.labels-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.label-item {
  display: flex;
  gap: 12px;
  padding: 8px;
  background: var(--panel-2);
  border-radius: 6px;
  font-size: 14px;
}

.label-row {
  color: var(--muted);
}

.label-value {
  flex: 1;
  font-weight: 500;
}

.label-confidence {
  color: var(--accent);
}

.label-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.label-entry {
  padding: 16px;
  background: var(--panel-2);
  border-radius: 8px;
}

.label-header {
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
}

.label-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-group label {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

.input.small {
  padding: 6px 10px;
  font-size: 14px;
}

.label-actions {
  display: flex;
  justify-content: flex-end;
}

.empty-message {
  text-align: center;
  padding: 48px;
  color: var(--muted);
}

.form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--muted);
}
</style>