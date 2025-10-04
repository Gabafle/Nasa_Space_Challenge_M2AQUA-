<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuth()

const isActive = (path) => route.path === path

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="navbar">
    <div class="container">
      <div class="nav-content">
        <div class="nav-left">
          <router-link to="/" class="brand">
            <span class="title">AstroMetric</span>
          </router-link>
          <nav v-if="auth.isAuthenticated" class="nav-links">
            <router-link to="/dashboard" :class="{ active: isActive('/dashboard') }">Dashboard</router-link>
            <router-link to="/datasets" :class="{ active: isActive('/datasets') }">Datasets</router-link>
            <router-link to="/upload" :class="{ active: isActive('/upload') }">Upload</router-link>
            <router-link to="/wizard" :class="{ active: isActive('/wizard') }">Wizard</router-link>
            <router-link to="/analyses" :class="{ active: isActive('/analyses') }">Analyses</router-link>
            <router-link to="/models" :class="{ active: isActive('/models') }">Models</router-link>
            <router-link to="/graphs" :class="{ active: isActive('/graphs') }">Graphs</router-link>
            <router-link to="/leaderboard" :class="{ active: isActive('/leaderboard') }">Leaderboard</router-link>
            <router-link v-if="auth.isResearcher" to="/labels" :class="{ active: isActive('/labels') }">Labels</router-link>
          </nav>
        </div>
        <div class="nav-right">
          <template v-if="auth.isAuthenticated">
            <span class="badge">{{ auth.userRole }}</span>
            <span class="user-name">{{ auth.user?.name || auth.user?.email }}</span>
            <button class="btn ghost" @click="logout">Logout</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn">Login</router-link>
            <router-link to="/signup" class="btn primary">Sign Up</router-link>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(34, 34, 34, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--accent);
  box-shadow: 0 2px 20px rgba(29, 205, 159, 0.1);
}

.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--fg);
  font-weight: 600;
  font-size: 20px;
  font-family: "Arial Black", Arial, sans-serif;
}

.brand .title {
  color: var(--brand);
  text-shadow: 0 0 10px rgba(72, 241, 175, 0.3);
}

.logo {
  font-size: 28px;
  filter: drop-shadow(0 0 8px rgba(29, 205, 159, 0.5));
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-links a {
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--astro-light);
  transition: all 0.3s ease;
  font-family: Arial, sans-serif;
}

.nav-links a:hover {
  color: var(--brand);
  background: rgba(29, 205, 159, 0.1);
  transform: translateY(-1px);
}

.nav-links a.active {
  color: var(--brand);
  background: rgba(72, 241, 175, 0.15);
  box-shadow: 0 0 15px rgba(29, 205, 159, 0.2);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  color: var(--astro-light);
  font-size: 14px;
  font-family: Arial, sans-serif;
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  
  .nav-content {
    height: 60px;
  }
  
  .brand {
    font-size: 18px;
  }
}
</style>
