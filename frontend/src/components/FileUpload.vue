<script setup>
import { ref } from 'vue'

const emit = defineEmits(['files', 'error'])
const fileInput = ref(null)

const handleFileChange = (event) => {
  console.log('File input changed!', event.target.files)
  const files = Array.from(event.target.files || [])
  if (files.length > 0) {
    emit('files', files)
  }
}

const clickInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}
</script>

<template>
  <div class="file-upload">
    <!-- Hidden file input -->
    <input 
      ref="fileInput" 
      type="file" 
      accept=".csv,.json,.jsonl" 
      multiple 
      @change="handleFileChange" 
      style="display: none;" 
    />
    
    <div class="upload-area" @click="clickInput">
      <div class="upload-icon">📁</div>
      <h3>Choose Files</h3>
      <p>Drag and drop your files here, or click to browse</p>
      <div class="upload-button">
        <span class="btn primary">
          🚀 Select Files
        </span>
      </div>
    </div>
    
    <div class="upload-info">
      <p>Supports CSV, JSON, and JSONL files</p>
    </div>
  </div>
</template>

<style scoped>
.file-upload {
  text-align: center;
  width: 100%;
}

.upload-area {
  padding: 60px 40px;
  background: var(--panel);
  border: 2px dashed var(--accent);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.upload-area:hover {
  border-color: var(--brand);
  background: rgba(29, 205, 159, 0.05);
  transform: translateY(-2px);
}

.upload-area::before {
  content: '';
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

.upload-area:hover::before {
  opacity: 0.1;
}

.upload-icon {
  font-size: 64px;
  margin-bottom: 16px;
  filter: drop-shadow(0 0 15px rgba(29, 205, 159, 0.4));
}

.upload-area h3 {
  margin: 0 0 8px 0;
  font-size: 1.5rem;
  color: var(--brand);
  font-family: "Arial Black", Arial, sans-serif;
}

.upload-area p {
  color: var(--astro-light);
  margin: 0 0 24px 0;
  font-family: Arial, sans-serif;
}

.upload-button {
  margin-top: 20px;
}

.upload-button .btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 16px;
  pointer-events: none;
}

.upload-info {
  margin-top: 16px;
}

.upload-info p {
  font-size: 14px;
  color: var(--muted);
  margin: 0;
  font-family: Arial, sans-serif;
}

@media (max-width: 768px) {
  .upload-area {
    padding: 40px 20px;
  }
  
  .upload-icon {
    font-size: 48px;
  }
  
  .upload-area h3 {
    font-size: 1.3rem;
  }
}
</style>
