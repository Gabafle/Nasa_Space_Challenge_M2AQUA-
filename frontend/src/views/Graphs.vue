<script setup>
import { ref, onMounted, provide, computed } from 'vue'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { 
  LineChart, 
  BarChart, 
  ScatterChart, 
  PieChart, 
  HeatmapChart,
  RadarChart
} from 'echarts/charts'
import { 
  TitleComponent, 
  TooltipComponent, 
  GridComponent, 
  LegendComponent, 
  ToolboxComponent, 
  DataZoomComponent,
  VisualMapComponent
} from 'echarts/components'

// Register ECharts components
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  ScatterChart,
  PieChart,
  HeatmapChart,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
  VisualMapComponent
])

// Provide dark theme
provide('THEME', 'dark')

const toast = useToast()
const loading = ref(true)
const graphData = ref(null)
const selectedView = ref('overview')

// Color palettes for different chart types
const colors = {
  primary: ['#5aa2ff', '#3ee6b0', '#ffb454', '#ff6b6b', '#7c5cff'],
  gradient: ['#5aa2ff', '#4a8cff', '#3a7aff', '#2a68ff', '#1a56ff'],
  space: ['#5aa2ff', '#3ee6b0', '#00d9ff', '#7c5cff', '#ff6b6b'],
  performance: ['#10b981', '#3ee6b0', '#22d3ee', '#5aa2ff', '#7c5cff']
}

const loadGraphData = async () => {
  loading.value = true
  try {
    const { data } = await http.get('/api/graphs/template')
    graphData.value = data
  } catch (error) {
    console.error('Failed to load graph data:', error)
    toast.error('Failed to load graph data')
  } finally {
    loading.value = false
  }
}

// Computed chart options
const confusionMatrixOption = computed(() => {
  if (!graphData.value?.confusion_matrix) return {}
  
  const matrix = graphData.value.confusion_matrix.matrix
  const labels = graphData.value.confusion_matrix.labels
  
  // Convert matrix to heatmap format
  const data = []
  matrix.forEach((row, i) => {
    row.forEach((value, j) => {
      data.push([j, i, value])
    })
  })
  
  return {
    animation: true,
    animationDuration: 1500,
    animationEasing: 'cubicOut',
    title: {
      text: '🔥 Confusion Matrix Heatmap',
      left: 'center',
      textStyle: {
        color: '#eaf0ff',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      position: 'top',
      formatter: (params) => {
        const [x, y, value] = params.data
        return `True: ${labels[y]}<br/>Predicted: ${labels[x]}<br/>Count: ${value}`
      },
      backgroundColor: '#111735',
      borderColor: '#5aa2ff',
      textStyle: { color: '#eaf0ff' }
    },
    grid: {
      height: '50%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: labels,
      splitArea: {
        show: true
      },
      axisLabel: {
        color: '#aab7d3'
      }
    },
    yAxis: {
      type: 'category',
      data: labels,
      splitArea: {
        show: true
      },
      axisLabel: {
        color: '#aab7d3'
      }
    },
    visualMap: {
      min: 0,
      max: Math.max(...matrix.flat()),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%',
      inRange: {
        color: ['#0a1128', '#1a2147', '#2a3266', '#3a4385', '#5aa2ff']
      },
      textStyle: {
        color: '#aab7d3'
      }
    },
    series: [{
      name: 'Confusion Matrix',
      type: 'heatmap',
      data: data,
      label: {
        show: true,
        color: '#fff',
        fontSize: 14,
        fontWeight: 'bold'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(90, 162, 255, 0.5)'
        }
      }
    }]
  }
})

const rocCurveOption = computed(() => {
  if (!graphData.value?.roc_curve) return {}
  
  const { fpr, tpr, auc } = graphData.value.roc_curve
  
  return {
    animation: true,
    animationDuration: 2000,
    animationEasing: 'elasticOut',
    title: {
      text: `📈 ROC Curve (AUC = ${auc.toFixed(3)})`,
      left: 'center',
      textStyle: {
        color: '#eaf0ff',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#111735',
      borderColor: '#3ee6b0',
      textStyle: { color: '#eaf0ff' }
    },
    legend: {
      data: ['ROC Curve', 'Random Classifier'],
      textStyle: { color: '#aab7d3' },
      top: '8%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'False Positive Rate',
      nameTextStyle: { color: '#aab7d3' },
      axisLabel: { color: '#aab7d3' },
      splitLine: { lineStyle: { color: '#202a53', opacity: 0.3 } }
    },
    yAxis: {
      type: 'value',
      name: 'True Positive Rate',
      nameTextStyle: { color: '#aab7d3' },
      axisLabel: { color: '#aab7d3' },
      splitLine: { lineStyle: { color: '#202a53', opacity: 0.3 } }
    },
    series: [
      {
        name: 'ROC Curve',
        type: 'line',
        data: fpr.map((x, i) => [x, tpr[i]]),
        smooth: true,
        lineStyle: {
          color: '#3ee6b0',
          width: 3,
          shadowColor: 'rgba(62, 230, 176, 0.5)',
          shadowBlur: 10
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(62, 230, 176, 0.3)' },
              { offset: 1, color: 'rgba(62, 230, 176, 0.05)' }
            ]
          }
        },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: '#3ee6b0',
          borderColor: '#fff',
          borderWidth: 2
        }
      },
      {
        name: 'Random Classifier',
        type: 'line',
        data: [[0, 0], [1, 1]],
        lineStyle: {
          color: '#ff6b6b',
          width: 2,
          type: 'dashed'
        },
        symbol: 'none'
      }
    ]
  }
})

const learningCurveOption = computed(() => {
  if (!graphData.value?.learning_curve) return {}
  
  const { train_sizes, train_scores_mean, train_scores_std, test_scores_mean, test_scores_std } = graphData.value.learning_curve
  
  return {
    animation: true,
    animationDuration: 2000,
    animationEasing: 'bounceOut',
    title: {
      text: '📚 Learning Curves',
      left: 'center',
      textStyle: {
        color: '#eaf0ff',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#111735',
      borderColor: '#5aa2ff',
      textStyle: { color: '#eaf0ff' }
    },
    legend: {
      data: ['Training Score', 'Validation Score'],
      textStyle: { color: '#aab7d3' },
      top: '8%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: train_sizes,
      name: 'Training Set Size',
      nameTextStyle: { color: '#aab7d3' },
      axisLabel: { color: '#aab7d3' }
    },
    yAxis: {
      type: 'value',
      name: 'Accuracy Score',
      nameTextStyle: { color: '#aab7d3' },
      axisLabel: { color: '#aab7d3' },
      splitLine: { lineStyle: { color: '#202a53', opacity: 0.3 } }
    },
    series: [
      {
        name: 'Training Score',
        type: 'line',
        data: train_scores_mean,
        smooth: true,
        lineStyle: {
          color: '#5aa2ff',
          width: 3
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(90, 162, 255, 0.3)' },
              { offset: 1, color: 'rgba(90, 162, 255, 0.05)' }
            ]
          }
        },
        symbol: 'circle',
        symbolSize: 8
      },
      {
        name: 'Validation Score',
        type: 'line',
        data: test_scores_mean,
        smooth: true,
        lineStyle: {
          color: '#3ee6b0',
          width: 3
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(62, 230, 176, 0.3)' },
              { offset: 1, color: 'rgba(62, 230, 176, 0.05)' }
            ]
          }
        },
        symbol: 'diamond',
        symbolSize: 8
      }
    ]
  }
})

const featureImportanceOption = computed(() => {
  if (!graphData.value?.feature_importance) return {}
  
  const features = graphData.value.feature_importance.top_features
  
  return {
    animation: true,
    animationDuration: 1500,
    animationDelayUpdate: (idx) => idx * 100,
    title: {
      text: '⭐ Feature Importance Ranking',
      left: 'center',
      textStyle: {
        color: '#eaf0ff',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: '#111735',
      borderColor: '#ffb454',
      textStyle: { color: '#eaf0ff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'Importance Score',
      nameTextStyle: { color: '#aab7d3' },
      axisLabel: { color: '#aab7d3' },
      splitLine: { lineStyle: { color: '#202a53', opacity: 0.3 } }
    },
    yAxis: {
      type: 'category',
      data: features.map(f => f.name).reverse(),
      axisLabel: { color: '#aab7d3' }
    },
    series: [{
      name: 'Feature Importance',
      type: 'bar',
      data: features.map(f => f.importance).reverse(),
      itemStyle: {
        color: (params) => {
          const colors = ['#ff6b6b', '#ffb454', '#3ee6b0', '#5aa2ff', '#7c5cff']
          return colors[params.dataIndex % colors.length]
        },
        borderRadius: [0, 8, 8, 0],
        shadowColor: 'rgba(0, 0, 0, 0.3)',
        shadowBlur: 5
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowColor: 'rgba(90, 162, 255, 0.8)'
        }
      },
      label: {
        show: true,
        position: 'right',
        color: '#eaf0ff',
        formatter: '{c}'
      }
    }]
  }
})

const crossValidationOption = computed(() => {
  if (!graphData.value?.cross_validation_results) return {}
  
  const folds = graphData.value.cross_validation_results.folds
  const metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
  
  return {
    animation: true,
    animationDuration: 2000,
    animationEasing: 'cubicInOut',
    title: {
      text: '🔄 Cross-Validation Performance',
      left: 'center',
      textStyle: {
        color: '#eaf0ff',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#111735',
      borderColor: '#7c5cff',
      textStyle: { color: '#eaf0ff' }
    },
    legend: {
      data: metrics.map(m => m.toUpperCase()),
      textStyle: { color: '#aab7d3' },
      top: '8%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: folds.map((_, i) => `Fold ${i + 1}`),
      axisLabel: { color: '#aab7d3' }
    },
    yAxis: {
      type: 'value',
      name: 'Score',
      nameTextStyle: { color: '#aab7d3' },
      axisLabel: { color: '#aab7d3' },
      splitLine: { lineStyle: { color: '#202a53', opacity: 0.3 } }
    },
    series: metrics.map((metric, index) => ({
      name: metric.toUpperCase(),
      type: 'line',
      data: folds.map(fold => fold.metrics[metric]),
      smooth: true,
      lineStyle: {
        color: colors.primary[index],
        width: 3
      },
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: {
        color: colors.primary[index],
        borderColor: '#fff',
        borderWidth: 2
      }
    }))
  }
})

const performanceMetricsOption = computed(() => {
  if (!graphData.value?.test_metrics) return {}
  
  const metrics = graphData.value.test_metrics
  const data = Object.entries(metrics).map(([key, value]) => ({
    name: key.toUpperCase(),
    value: value
  }))
  
  return {
    animation: true,
    animationDuration: 2000,
    animationEasing: 'elasticOut',
    title: {
      text: '🎯 Model Performance Metrics',
      left: 'center',
      textStyle: {
        color: '#eaf0ff',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: '#111735',
      borderColor: '#3ee6b0',
      textStyle: { color: '#eaf0ff' }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#aab7d3' }
    },
    series: [{
      name: 'Performance',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      data: data,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#0b1020',
        borderWidth: 2
      },
      color: colors.performance,
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowOffsetX: 0,
          shadowColor: 'rgba(62, 230, 176, 0.8)'
        }
      },
      label: {
        formatter: '{b}\n{d}%',
        color: '#eaf0ff'
      }
    }]
  }
})

onMounted(() => {
  loadGraphData()
})
</script>

<template>
  <div class="graphs-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Analytics</h1>
        <p>Comprehensive model performance visualization and insights</p>
        <div v-if="graphData?.metadata" class="model-info">
          <div class="info-badge">
            🤖 {{ graphData.metadata.model_name }}
          </div>
          <div class="info-badge">
            📊 {{ graphData.metadata.num_features }} Features
          </div>
          <div class="info-badge">
            🎯 {{ graphData.metadata.num_classes }} Classes
          </div>
        </div>
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Loading advanced analytics..." />

    <div v-else-if="!graphData" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>No Data Available</h3>
      <p>Unable to load graph template data. Please try again later.</p>
    </div>

    <div v-else class="dashboard-content">
      <!-- Navigation Tabs -->
      <div class="view-selector">
        <button 
          :class="['view-btn', { active: selectedView === 'overview' }]"
          @click="selectedView = 'overview'"
        >
          📈 Overview
        </button>
        <button 
          :class="['view-btn', { active: selectedView === 'performance' }]"
          @click="selectedView = 'performance'"
        >
          🎯 Performance
        </button>
        <button 
          :class="['view-btn', { active: selectedView === 'analysis' }]"
          @click="selectedView = 'analysis'"
        >
          🔍 Analysis
        </button>
      </div>

      <!-- Overview Section -->
      <div v-if="selectedView === 'overview'" class="charts-grid overview-grid">
        <div class="chart-card large">
          <v-chart 
            :option="learningCurveOption" 
            class="chart"
            autoresize 
          />
        </div>
        
        <div class="chart-card">
          <v-chart 
            :option="performanceMetricsOption" 
            class="chart"
            autoresize 
          />
        </div>

        <div class="metrics-summary card">
          <h3>📊 Training Summary</h3>
          <div v-if="graphData.training_info" class="summary-grid">
            <div class="metric-item">
              <span class="metric-label">⏱️ Training Time</span>
              <span class="metric-value">{{ graphData.training_info.fit_time_sec.toFixed(2) }}s</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">⚡ Prediction Time</span>
              <span class="metric-value">{{ (graphData.training_info.predict_time_sec * 1000).toFixed(1) }}ms</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">🔄 CV Folds</span>
              <span class="metric-value">{{ graphData.training_info.cross_validation_folds }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">🎯 CV Score</span>
              <span class="metric-value">{{ (graphData.training_info.cross_val_score_mean * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Section -->
      <div v-if="selectedView === 'performance'" class="charts-grid performance-grid">
        <div class="chart-card large">
          <v-chart 
            :option="confusionMatrixOption" 
            class="chart"
            autoresize 
          />
        </div>
        
        <div class="chart-card large">
          <v-chart 
            :option="rocCurveOption" 
            class="chart"
            autoresize 
          />
        </div>

        <div class="chart-card">
          <v-chart 
            :option="crossValidationOption" 
            class="chart"
            autoresize 
          />
        </div>

        <div class="performance-stats card">
          <h3>🏆 Best Scores</h3>
          <div v-if="graphData.test_metrics" class="stats-grid">
            <div class="stat-card accuracy">
              <div class="stat-icon">🎯</div>
              <div class="stat-info">
                <div class="stat-value">{{ (graphData.test_metrics.accuracy * 100).toFixed(1) }}%</div>
                <div class="stat-label">Accuracy</div>
              </div>
            </div>
            <div class="stat-card precision">
              <div class="stat-icon">🔍</div>
              <div class="stat-info">
                <div class="stat-value">{{ (graphData.test_metrics.precision * 100).toFixed(1) }}%</div>
                <div class="stat-label">Precision</div>
              </div>
            </div>
            <div class="stat-card recall">
              <div class="stat-icon">📊</div>
              <div class="stat-info">
                <div class="stat-value">{{ (graphData.test_metrics.recall * 100).toFixed(1) }}%</div>
                <div class="stat-label">Recall</div>
              </div>
            </div>
            <div class="stat-card f1">
              <div class="stat-icon">⚖️</div>
              <div class="stat-info">
                <div class="stat-value">{{ (graphData.test_metrics.f1 * 100).toFixed(1) }}%</div>
                <div class="stat-label">F1-Score</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Analysis Section -->
      <div v-if="selectedView === 'analysis'" class="charts-grid analysis-grid">
        <div class="chart-card wide">
          <v-chart 
            :option="featureImportanceOption" 
            class="chart"
            autoresize 
          />
        </div>

        <div class="feature-details card">
          <h3>🔍 Feature Analysis</h3>
          <div v-if="graphData.feature_importance" class="feature-list">
            <div 
              v-for="(feature, index) in graphData.feature_importance.top_features.slice(0, 5)" 
              :key="feature.name"
              class="feature-item"
              :style="{ '--delay': index * 0.1 + 's' }"
            >
              <div class="feature-rank">{{ index + 1 }}</div>
              <div class="feature-info">
                <div class="feature-name">{{ feature.name }}</div>
                <div class="feature-bar">
                  <div 
                    class="feature-progress" 
                    :style="{ width: (feature.importance * 100) + '%' }"
                  ></div>
                </div>
              </div>
              <div class="feature-score">{{ (feature.importance * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </div>

        <div class="class-distribution card">
          <h3>🏷️ Class Distribution</h3>
          <div v-if="graphData.metadata" class="class-grid">
            <div 
              v-for="(className, index) in graphData.metadata.target_names" 
              :key="className"
              class="class-item"
            >
              <div class="class-color" :style="{ backgroundColor: colors.primary[index] }"></div>
              <span class="class-name">{{ className }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.graphs-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.header-content h1 {
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #5aa2ff, #3ee6b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 2.5rem;
  font-weight: 700;
}

.header-content p {
  color: var(--muted);
  font-size: 1.1rem;
  margin: 0 0 20px 0;
}

.model-info {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.info-badge {
  padding: 8px 16px;
  background: rgba(90, 162, 255, 0.1);
  border: 1px solid rgba(90, 162, 255, 0.3);
  border-radius: 20px;
  color: var(--brand);
  font-size: 14px;
  font-weight: 500;
}

.view-selector {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
  padding: 8px;
  background: var(--panel-2);
  border-radius: 12px;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

.view-btn {
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--muted);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn:hover {
  color: var(--fg);
  background: rgba(90, 162, 255, 0.1);
}

.view-btn.active {
  background: var(--brand);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(90, 162, 255, 0.3);
}

.charts-grid {
  display: grid;
  gap: 24px;
}

.overview-grid {
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
}

.performance-grid {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
}

.analysis-grid {
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
}

.chart-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: slideUp 0.6s ease-out;
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(90, 162, 255, 0.15);
}

.chart-card.large {
  grid-column: span 2;
}

.chart-card.wide {
  grid-column: span 2;
}

.chart {
  height: 400px;
  width: 100%;
}

.card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.6s ease-out;
}

.metrics-summary h3,
.performance-stats h3,
.feature-details h3,
.class-distribution h3 {
  margin: 0 0 20px 0;
  color: var(--fg);
  font-size: 1.2rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: var(--panel-2);
  border-radius: 8px;
}

.metric-label {
  font-size: 12px;
  color: var(--muted);
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: scale(1.05);
}

.stat-card.accuracy { background: rgba(62, 230, 176, 0.1); }
.stat-card.precision { background: rgba(90, 162, 255, 0.1); }
.stat-card.recall { background: rgba(255, 180, 84, 0.1); }
.stat-card.f1 { background: rgba(124, 92, 255, 0.1); }

.stat-icon {
  font-size: 24px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--fg);
}

.stat-label {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--panel-2);
  border-radius: 8px;
  animation: slideInRight 0.5s ease-out;
  animation-delay: var(--delay);
  animation-fill-mode: both;
}

.feature-rank {
  width: 32px;
  height: 32px;
  background: var(--brand);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.feature-info {
  flex: 1;
}

.feature-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.feature-bar {
  height: 4px;
  background: var(--line);
  border-radius: 2px;
  overflow: hidden;
}

.feature-progress {
  height: 100%;
  background: linear-gradient(90deg, var(--brand), var(--accent));
  transition: width 1s ease-out 0.5s;
}

.feature-score {
  font-weight: 600;
  color: var(--accent);
}

.class-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
}

.class-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.class-name {
  font-weight: 500;
}

.error-state {
  text-align: center;
  padding: 80px 20px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.error-state h3 {
  margin: 0 0 12px 0;
  color: var(--fg);
}

.error-state p {
  color: var(--muted);
  margin: 0;
}

/* Animations */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Responsive Design */
@media (max-width: 1200px) {
  .overview-grid,
  .performance-grid,
  .analysis-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card.large,
  .chart-card.wide {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .graphs-page {
    padding: 16px;
  }
  
  .header-content h1 {
    font-size: 2rem;
  }
  
  .view-selector {
    flex-direction: column;
    width: 100%;
  }
  
  .summary-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .chart {
    height: 300px;
  }
}
</style>
