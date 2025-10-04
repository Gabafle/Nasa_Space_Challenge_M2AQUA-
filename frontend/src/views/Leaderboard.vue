<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../stores/auth'
import { useToast } from '../stores/toast'
import http from '../api/http'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const auth = useAuth()
const toast = useToast()

const entries = ref([])
const loading = ref(false)
const selectedMetric = ref('accuracy')
const scope = ref('global')
const myBestRank = ref(null)

const metrics = [
  { value: 'accuracy', label: 'Accuracy' },
  { value: 'auroc', label: 'AUROC' },
  { value: 'f1', label: 'F1 Score' },
  { value: 'precision', label: 'Precision' },
  { value: 'recall', label: 'Recall' }
]

const loadLeaderboard = async () => {
  loading.value = true
  try {
    const { data } = await http.get('/api/leaderboard', {
      params: { 
        metric: selectedMetric.value,
        scope: scope.value,
        limit: 100
      }
    })
    entries.value = data.entries || []
    
    // Find user's best rank
    const userEntry = entries.value.find(e => e.user.id === auth.user?.id)
    myBestRank.value = userEntry?.rank || null
  } catch (error) {
    console.error('Failed to load leaderboard:', error)
  } finally {
    loading.value = false
  }
}

const submitToLeaderboard = async (runId) => {
  try {
    await http.post('/api/leaderboard/submit', { run_id: runId })
    toast.success('Submitted to leaderboard!')
    loadLeaderboard()
  } catch (error) {
    console.error('Failed to submit:', error)
  }
}

const getRankBadge = (rank) => {
  if (rank === 1) return '🥇'
  if (rank === 2) return '🥈'
  if (rank === 3) return '🥉'
  return `#${rank}`
}

const getRankClass = (rank) => {
  if (rank === 1) return 'gold'
  if (rank === 2) return 'silver'
  if (rank === 3) return 'bronze'
  return ''
}

onMounted(() => {
  loadLeaderboard()
})
</script>

<template>
  <div class="leaderboard-page">
    <div class="page-header">
      <div>
        <h1>🏆 Leaderboard</h1>
        <p>Top performing models and analyses</p>
      </div>
      <div v-if="myBestRank" class="my-rank">
        Your Best Rank: <span class="rank-value">{{ getRankBadge(myBestRank) }}</span>
      </div>
    </div>
    
    <div class="filters card">
      <div class="filter-group">
        <label>Metric</label>
        <select v-model="selectedMetric" @change="loadLeaderboard" class="select">
          <option v-for="metric in metrics" :key="metric.value" :value="metric.value">
            {{ metric.label }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Scope</label>
        <div class="scope-buttons">
          <button 
            :class="['btn', scope === 'global' ? 'primary' : 'ghost']"
            @click="scope = 'global'; loadLeaderboard()"
          >
            🌍 Global
          </button>
          <button 
            :class="['btn', scope === 'mine' ? 'primary' : 'ghost']"
            @click="scope = 'mine'; loadLeaderboard()"
          >
            👤 My Runs
          </button>
        </div>
      </div>
    </div>
    
    <LoadingSpinner v-if="loading" message="Loading leaderboard..." />
    
    <div v-else-if="entries.length === 0" class="empty-message">
      No entries yet. Be the first to submit!
    </div>
    
    <div v-else class="leaderboard-table card">
      <table>
        <thead>
          <tr>
            <th class="rank-col">Rank</th>
            <th>User</th>
            <th>Dataset</th>
            <th>Score</th>
            <th>Submitted</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="entry in entries" 
            :key="entry.run_id"
            :class="{ 'my-entry': entry.user.id === auth.user?.id }"
          >
            <td class="rank-col">
              <span :class="['rank', getRankClass(entry.rank)]">
                {{ getRankBadge(entry.rank) }}
              </span>
            </td>
            <td>
              <div class="user-info">
                <span class="user-name">{{ entry.user.name }}</span>
                <span class="user-role badge">{{ entry.user.role }}</span>
              </div>
            </td>
            <td>Dataset #{{ entry.dataset_id }}</td>
            <td class="score-col">
              <span class="score">
                {{ entry.value ? entry.value.toFixed(4) : 'N/A' }}
              </span>
            </td>
            <td class="date-col">
              {{ new Date(entry.finished_at).toLocaleDateString() }}
            </td>
            <td>
              <button class="btn ghost small" @click="$router.push(`/viz/${entry.run_id}`)">
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div class="leaderboard-info card">
      <h3>📊 How to Participate</h3>
      <ol>
        <li>Upload your exoplanet dataset</li>
        <li>Run analysis using our models or train your own</li>
        <li>Once analysis is complete, submit to leaderboard</li>
        <li>Track your progress and improve your models</li>
      </ol>
      <p class="info-note">
        Only researchers and admins can submit to the leaderboard. 
        Best score per user-dataset combination is shown.
      </p>
    </div>
  </div>
</template>

<style scoped>
.leaderboard-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.my-rank {
  padding: 12px 24px;
  background: linear-gradient(90deg, var(--brand), #7c5cff);
  border-radius: 10px;
  font-weight: 600;
}

.rank-value {
  font-size: 20px;
  margin-left: 8px;
}

.filters {
  display: flex;
  gap: 32px;
  padding: 20px;
  margin-bottom: 24px;
}

.filter-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--muted);
}

.scope-buttons {
  display: flex;
  gap: 8px;
}

.leaderboard-table {
  padding: 0;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--panel-2);
}

th {
  text-align: left;
  padding: 16px;
  font-weight: 600;
  font-size: 14px;
  color: var(--muted);
  text-transform: uppercase;
}

td {
  padding: 16px;
  border-top: 1px solid var(--line);
}

tbody tr {
  transition: background 0.2s;
}

tbody tr:hover {
  background: var(--panel-2);
}

tr.my-entry {
  background: rgba(90, 162, 255, 0.05);
}

.rank-col {
  width: 80px;
  text-align: center;
}

.rank {
  font-size: 20px;
  font-weight: 600;
}

.rank.gold {
  color: #ffd700;
}

.rank.silver {
  color: #c0c0c0;
}

.rank.bronze {
  color: #cd7f32;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-weight: 500;
}

.user-role {
  font-size: 10px;
}

.score-col {
  font-weight: 600;
  font-size: 18px;
  color: var(--accent);
}

.date-col {
  font-size: 14px;
  color: var(--muted);
}

.leaderboard-info {
  margin-top: 32px;
  padding: 24px;
}

.leaderboard-info h3 {
  margin: 0 0 16px 0;
}

.leaderboard-info ol {
  margin: 16px 0 16px 24px;
  line-height: 1.8;
}

.info-note {
  margin: 16px 0 0 0;
  padding: 12px;
  background: var(--panel-2);
  border-radius: 8px;
  font-size: 14px;
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