<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../stores/toast'
import http from '../api/http'

const router = useRouter()
const toast = useToast()

const email = ref('')
const password = ref('')
const name = ref('')
const role = ref('user')
const loading = ref(false)

const submit = async () => {
  if (!email.value || !password.value || !name.value) {
    toast.error('Please fill all required fields')
    return
  }
  
  if (password.value.length < 8) {
    toast.error('Password must be at least 8 characters')
    return
  }
  
  loading.value = true
  try {
    await http.post('/api/auth/signup', {
      email: email.value,
      password: password.value,
      name: name.value,
      role: role.value
    })
    toast.success('Account created! Please login.')
    router.push('/login')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1>Create Account</h1>
      <p>Join the exoplanet research community</p>
      
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Name</label>
          <input
            v-model="name"
            type="text"
            class="input"
            placeholder="John Doe"
            required
          />
        </div>
        
        <div class="form-group">
          <label>Email</label>
          <input
            v-model="email"
            type="email"
            class="input"
            placeholder="you@example.com"
            required
          />
        </div>
        
        <div class="form-group">
          <label>Password</label>
          <input
            v-model="password"
            type="password"
            class="input"
            placeholder="At least 8 characters"
            minlength="8"
            required
          />
        </div>
        
        <div class="form-group">
          <label>Role</label>
          <select v-model="role" class="select">
            <option value="user">User</option>
            <option value="researcher">Researcher</option>
          </select>
        </div>
        
        <button type="submit" class="btn primary full-width" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? 'Creating account...' : 'Sign Up' }}
        </button>
      </form>
      
      <div class="auth-footer">
        <p>Already have an account? <router-link to="/login">Login</router-link></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 32px;
  box-shadow: var(--shadow);
}

h1 {
  margin: 0 0 8px 0;
}

p {
  color: var(--muted);
  margin: 0 0 24px 0;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--muted);
}

.full-width {
  width: 100%;
}

.auth-footer {
  margin-top: 24px;
  text-align: center;
}

.auth-footer p {
  margin: 0;
}

.auth-footer a {
  color: var(--brand);
}
</style>