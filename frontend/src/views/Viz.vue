<script setup>
import { ref, onMounted, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, ScatterChart, HeatmapChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent
} from 'echarts/components'

// Register ECharts components
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  ScatterChart,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent
])

// Provide theme
provide('THEME', 'dark')

const route = useRoute()
const toast = useToast()

const loading = ref(true)
const analysis = ref(null)
const vizData = ref(null)
const artifacts = ref([])
const selectedTab = ref('charts')

const loadVisualization = async () => {
  loading.value = true
  try {
    const runId = route.params.runId
    
    const [analysisRes, vizRes, artifactsRes] = await Promise.all([
      http.get(`/api/analyses/${runId}`),
      http.get(`/api/analyses/${runId}/viz`),
      http.get(`/api/analyses/${runId}/artifacts`)
    ])
    
    analysis.value = analysisRes.data
    vizData.value = vizRes.data
    artifacts.value = artifactsRes.data.artifacts || []
  } catch (error) {
    console.error('Failed to load visualization:', error)
    toast.error('Failed to load analysis results')
  } finally {
    loading.value = false
  }
}

const downloadArtifact = async (filename) => {
  try {
    const response = await http.get(
      `/api/analyses/${route.params.runId}/artifact/${filename}`,
      { responseType: 'blob' }
    )
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    toast.success('Download started')
  } catch (error) {
    console.error('Download failed:', error)
  }
}

const getChartOption = (chart) => {
  const baseOption = {
    backgroundColor: 'transparent',
    title: {
      text: chart.title,
      textStyle: { color: '#eaf0ff' }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#111735',
      borderColor: '#202a53',
      textStyle: { color: '#eaf0ff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chart.data?.bins || [],
      axisLine: { lineStyle: { color: '#202a53' } },
      axisLabel: { color: '#aab7d3' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#202a53' } },
      axisLabel: { color: '#aab7d3' },
      splitLine: { lineStyle: { color: '#202a53', opacity: 0.3 } }
    }
  }
  
  if (chart.type === 'histogram') {
    return {
      ...baseOption,
      series: [{
        name: 'Count',
        type: 'bar',
        data: chart.data?.counts || [],
        itemStyle: {
          color: '#5aa2ff'
        }
      }]
    }
  } else if (chart.type === 'scatter') {
    return {
      ...baseOption,
      xAxis: { type: 'value' },
      series: [{
        name: 'Data',
        type: 'scatter',
        symbolSize: 8,
        data: chart.data?.points || [],
        itemStyle: {
          color: '#3ee6b0'
        }
      }]
    }
  }
  
  return baseOption
}

onMounted(() => {
  loadVisualization()
})
</script>

<template>
  <div class="viz-page">
    <div class="page-header">
      <div>
        <h1>Analysis Results #{{ route.params.runId }}</h1>
        <p v-if="analysis">
          Status: <span :class="`badge ${analysis.status === 'done' ? 'success' : 'info'}`">
            {{ analysis.status }}
          </span>
        </p>
      </div>
    </div>
    
    <LoadingSpinner v-if="loading" message="Loading visualizations..." />
    
    <template v-else>
      <!-- Tab Navigation -->
      <div class="tabs">
        <button 
          :class="['tab', { active: selectedTab === 'charts' }]"
          @click="selectedTab = 'charts'"
        >
          📊 Charts
        </button>
        <button 
          :class="['tab', { active: selectedTab === 'metrics' }]"
          @click="selectedTab = 'metrics'"
        >
          📈 Metrics
        </button>
        <button 
          :class="['tab', { active: selectedTab === 'artifacts' }]"
          @click="selectedTab = 'artifacts'"
        >
          📁 Artifacts
        </button>
      </div>
      
      <!-- Charts Tab -->
      <div v-if="selectedTab === 'charts'" class="charts-grid">
        <div v-if="!vizData?.charts || vizData.charts.length === 0" class="empty-message">
          No charts available for this analysis
        </div>
        <div 
          v-for="(chart, index) in vizData?.charts || []" 
          :key="index"
          class="chart-container card"
        >
          <v-chart 
            :option="getChartOption(chart)" 
            style="height: 400px;"
            autoresize
          />
        </div>
      </div>
      
      <!-- Metrics Tab -->
      <div v-if="selectedTab === 'metrics'" class="metrics-section card">
        <h2>Analysis Metrics</h2>
        <div v-if="!analysis?.metrics || Object.keys(analysis.metrics).length === 0">
          No metrics available
        </div>
        <pre v-else class="metrics-display">{{ JSON.stringify(analysis.metrics, null, 2) }}</pre>
      </div>
      
      <!-- Artifacts Tab -->
      <div v-if="selectedTab === 'artifacts'" class="artifacts-section">
        <div v-if="artifacts.length === 0" class="empty-message">
          No artifacts generated for this analysis
        </div>
        <div v-else class="artifacts-grid">
          <div 
            v-for="artifact in artifacts" 
            :key="artifact.filename"
            class="artifact-card card"
          >
            <div class="artifact-icon">
              {{ artifact.type === 'image' ? '🖼️' : '📄' }}
            </div>
            <div class="artifact-info">
              <div class="artifact-name">{{ artifact.filename }}</div>
              <div class="artifact-size">{{ artifact.size_bytes }} bytes</div>
            </div>
            <button class="btn primary small" @click="downloadArtifact(artifact.filename)">
              Download
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.viz-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--line);
}

.tab {
  padding: 12px 24px;
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.tab:hover {
  color: var(--fg);
}

.tab.active {
  color: var(--brand);
  border-bottom-color: var(--brand);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
  gap: 24px;
}

.chart-container {
  padding: 24px;
}

.metrics-section {
  padding: 24px;
}

.metrics-display {
  background: var(--panel-2);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: monospace;
  font-size: 14px;
  color: var(--fg);
}

.artifacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.artifact-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.artifact-icon {
  font-size: 32px;
}

.artifact-info {
  flex: 1;
}

.artifact-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.artifact-size {
  font-size: 12px;
  color: var(--muted);
}

.empty-message {
  text-align: center;
  padding: 48px;
  color: var(--muted);
}

.btn.small {
  padding: 6px 12px;
  font-size: 12px;
}
</style>