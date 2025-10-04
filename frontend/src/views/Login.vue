<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../stores/auth'
import { useToast } from '../stores/toast'
import http from '../api/http'

const router = useRouter()
const route = useRoute()
const auth = useAuth()
const toast = useToast()

const email = ref('')
const password = ref('')
const loading = ref(false)

const submit = async () => {
  if (!email.value || !password.value) {
    toast.error('Please enter email and password')
    return
  }
  
  loading.value = true
  try {
    const { data } = await http.post('/api/auth/login', {
      email: email.value,
      password: password.value
    })
    
    auth.setSession(data)
    toast.success('Welcome back!')
    router.push(route.query.r || '/dashboard')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="starfield-bg"></div>
    <div class="auth-card astro-fade-in">
      <div class="auth-header">
        <div class="logo-container">
          <span class="auth-logo">🚀</span>
        </div>
        <h1>Welcome Back</h1>
        <p>Login to access your exoplanet analysis platform</p>
      </div>
      
      <form @submit.prevent="submit">
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
            placeholder="••••••••" 
            required 
          />
        </div>
        
        <button type="submit" class="btn primary full-width" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
      
      <div class="auth-footer">
        <p>Don't have an account? <router-link to="/signup">Sign up</router-link></p>
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
  position: relative;
}

.auth-card {
  width: 100%;
  max-width: 450px;
  background: var(--panel);
  border: 2px solid var(--accent);
  border-radius: var(--radius);
  padding: 40px;
  box-shadow: 0 20px 60px rgba(29, 205, 159, 0.15);
  position: relative;
  z-index: 1;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-container {
  margin-bottom: 16px;
}

.auth-logo {
  font-size: 48px;
  filter: drop-shadow(0 0 15px rgba(29, 205, 159, 0.6));
}

.auth-card h1 {
  margin: 0 0 12px 0;
  font-size: 2rem;
}

.auth-card p {
  color: var(--astro-light);
  margin: 0 0 32px 0;
  font-family: Arial, sans-serif;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--astro-light);
  font-family: Arial, sans-serif;
  font-weight: 500;
}

.full-width {
  width: 100%;
  padding: 14px 24px;
  font-size: 16px;
}

.auth-footer {
  margin-top: 32px;
  text-align: center;
}

.auth-footer p {
  margin: 0;
  font-family: Arial, sans-serif;
}

.auth-footer a {
  color: var(--brand);
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  text-shadow: 0 0 8px rgba(72, 241, 175, 0.5);
}
</style>
