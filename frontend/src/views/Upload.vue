<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../stores/toast'
import http from '../api/http'
import FileUpload from '../components/FileUpload.vue'

const router = useRouter()
const toast = useToast()

const selectedFiles = ref([])
const uploading = ref(false)
const isPublic = ref(false)

const handleFilesSelected = (files) => {
  selectedFiles.value = files
  console.log('Selected files:', files)
}

const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) {
    toast.error('Please select files first')
    return
  }

  uploading.value = true

  try {
    for (const file of selectedFiles.value) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('is_public', isPublic.value.toString())

      const response = await http.post('/api/datasets/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      console.log('Upload response:', response.data)
    }

    toast.success(`Uploaded ${selectedFiles.value.length} file(s)!`)
    selectedFiles.value = []
    router.push('/datasets')

  } catch (error) {
    console.error('Upload failed:', error)
    toast.error('Upload failed: ' + (error.response?.data?.error || 'Unknown error'))
  } finally {
    uploading.value = false
  }
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}
</script>

<template>
  <div class="upload-page">
    <div class="page-header">
      <h1>📁 Upload Dataset</h1>
      <p>Upload your exoplanet data files</p>
    </div>

    <!-- File Upload -->
    <div class="upload-section card">
      <h2>Select Files</h2>
      <p>Supports CSV, JSON, and JSONL files</p>
      
      <FileUpload @files="handleFilesSelected" />

      <!-- Selected Files -->
      <div v-if="selectedFiles.length > 0" class="selected-files">
        <h3>Selected Files ({{ selectedFiles.length }})</h3>
        <div class="file-list">
          <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
            <span>📄 {{ file.name }}</span>
            <span>{{ Math.round(file.size / 1024) }} KB</span>
            <button @click="removeFile(index)" class="btn danger small">✕</button>
          </div>
        </div>

        <!-- Options -->
        <div class="upload-options">
          <label class="checkbox-label">
            <input type="checkbox" v-model="isPublic" />
            Make dataset public
          </label>

          <button 
            @click="uploadFiles" 
            :disabled="uploading"
            class="btn primary large"
          >
            <span v-if="uploading">⏳ Uploading...</span>
            <span v-else>🚀 Upload {{ selectedFiles.length }} File(s)</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0 0 8px 0;
}

.page-header p {
  color: var(--muted);
  margin: 0;
}

.upload-section {
  padding: 32px;
}

.upload-section h2 {
  margin: 0 0 8px 0;
}

.upload-section p {
  color: var(--muted);
  margin: 0 0 24px 0;
}

.selected-files {
  margin-top: 32px;
  padding: 24px;
  background: var(--panel-2);
  border-radius: 12px;
}

.selected-files h3 {
  margin: 0 0 16px 0;
}

.file-list {
  margin-bottom: 24px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--panel);
  border-radius: 8px;
  margin-bottom: 8px;
}

.file-item span:first-child {
  flex: 1;
  font-weight: 500;
}

.file-item span:nth-child(2) {
  color: var(--muted);
  font-size: 12px;
}

.upload-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input {
  width: 16px;
  height: 16px;
  accent-color: var(--brand);
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn.primary {
  background: var(--brand);
  color: white;
}

.btn.primary:hover {
  background: #4a8cff;
  transform: translateY(-1px);
}

.btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn.danger {
  background: var(--danger);
  color: white;
}

.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

.btn.large {
  padding: 16px 32px;
  font-size: 16px;
}

@media (max-width: 768px) {
  .upload-options {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn.large {
    width: 100%;
  }
}
</style>
