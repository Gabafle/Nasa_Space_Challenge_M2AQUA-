<script setup>
import { ref } from 'vue'
import { useAuth } from '../stores/auth'
import { useToast } from '../stores/toast'
import http from '../api/http'

const auth = useAuth()
const toast = useToast()

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileForm = ref({
  name: auth.user?.name || '',
  email: auth.user?.email || ''
})

const changing = ref(false)
const updating = ref(false)

const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    toast.error('Passwords do not match')
    return
  }
  
  if (passwordForm.value.newPassword.length < 8) {
    toast.error('Password must be at least 8 characters')
    return
  }
  
  changing.value = true
  try {
    await http.put('/api/auth/change-password', {
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    
    toast.success('Password changed successfully')
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error('Password change failed:', error)
  } finally {
    changing.value = false
  }
}

const updateProfile = async () => {
  toast.info('Profile update not implemented in backend yet')
}
</script>

<template>
  <div class="account-page">
    <h1>Account Settings</h1>
    
    <div class="settings-grid">
      <!-- Profile Information -->
      <div class="settings-section card">
        <h2>Profile Information</h2>
        
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">User ID</span>
            <span class="info-value">{{ auth.user?.id }}</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">Email</span>
            <span class="info-value">{{ auth.user?.email }}</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">Name</span>
            <span class="info-value">{{ auth.user?.name || 'Not set' }}</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">Role</span>
            <span class="info-value badge">{{ auth.user?.role }}</span>
          </div>
        </div>
        
        <div class="form-section">
          <h3>Update Profile</h3>
          
          <div class="form-group">
            <label>Display Name</label>
            <input v-model="profileForm.name" class="input" placeholder="John Doe" />
          </div>
          
          <button 
            class="btn primary" 
            @click="updateProfile"
            :disabled="updating"
          >
            Update Profile
          </button>
        </div>
      </div>
      
      <!-- Security Settings -->
      <div class="settings-section card">
        <h2>Security</h2>
        
        <div class="form-section">
          <h3>Change Password</h3>
          
          <div class="form-group">
            <label>Current Password</label>
            <input 
              v-model="passwordForm.oldPassword" 
              type="password" 
              class="input"
              placeholder="••••••••"
            />
          </div>
          
          <div class="form-group">
            <label>New Password</label>
            <input 
              v-model="passwordForm.newPassword" 
              type="password" 
              class="input"
              placeholder="At least 8 characters"
            />
          </div>
          
          <div class="form-group">
            <label>Confirm New Password</label>
            <input 
              v-model="passwordForm.confirmPassword" 
              type="password" 
              class="input"
              placeholder="••••••••"
            />
          </div>
          
          <button 
            class="btn primary" 
            @click="changePassword"
            :disabled="changing"
          >
            <span v-if="changing" class="loading-spinner"></span>
            {{ changing ? 'Changing...' : 'Change Password' }}
          </button>
        </div>
      </div>
      
      <!-- API Access -->
      <div class="settings-section card">
        <h2>API Access</h2>
        
        <div class="api-info">
          <p>Use your JWT tokens to access the API programmatically.</p>
          
          <div class="code-block">
            <div class="code-label">cURL Example</div>
            <pre>curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  {{ $route.meta.apiUrl || 'http://localhost:5000' }}/api/datasets</pre>
          </div>
          
          <div class="token-info">
            <div class="info-item">
              <span class="info-label">Access Token Expires</span>
              <span class="info-value">30 minutes</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">Refresh Token Expires</span>
              <span class="info-value">7 days</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Danger Zone -->
      <div class="settings-section card danger-zone">
        <h2>Danger Zone</h2>
        
        <div class="danger-content">
          <p>Permanently delete your account and all associated data.</p>
          <button class="btn danger" disabled>
            Delete Account (Not Implemented)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.account-page {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin: 0 0 32px 0;
}

.settings-grid {
  display: grid;
  gap: 24px;
}

.settings-section {
  padding: 24px;
}

.settings-section h2 {
  margin: 0 0 24px 0;
}

.settings-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
}

.form-section {
  padding-top: 24px;
  border-top: 1px solid var(--line);
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

.api-info p {
  color: var(--muted);
  margin: 0 0 16px 0;
}

.code-block {
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.code-label {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.code-block pre {
  margin: 0;
  font-family: monospace;
  font-size: 14px;
  color: var(--fg);
  overflow-x: auto;
}

.token-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.danger-zone {
  border: 1px solid var(--danger);
  background: rgba(255, 107, 107, 0.05);
}

.danger-zone h2 {
  color: var(--danger);
}

.danger-content p {
  color: var(--muted);
  margin: 0 0 16px 0;
}

.btn.danger {
  background: var(--danger);
}

.btn.danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>