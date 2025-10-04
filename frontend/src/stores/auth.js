import { defineStore } from 'pinia'

export const useAuth = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    userRole: (state) => state.user?.role || 'guest',
    isResearcher: (state) => state.user?.role === 'researcher' || state.user?.role === 'admin',
    isAdmin: (state) => state.user?.role === 'admin'
  },
  
  actions: {
    setSession({ user, access_token, refresh_token }) {
      this.user = user
      this.accessToken = access_token
      this.refreshToken = refresh_token
      localStorage.setItem('session', JSON.stringify({ user, access_token, refresh_token }))
    },
    
    setAccessToken(token) {
      this.accessToken = token
      const session = JSON.parse(localStorage.getItem('session') || '{}')
      session.access_token = token
      localStorage.setItem('session', JSON.stringify(session))
    },
    
    load() {
      const session = JSON.parse(localStorage.getItem('session') || 'null')
      if (session) {
        this.user = session.user
        this.accessToken = session.access_token
        this.refreshToken = session.refresh_token
      }
    },
    
    logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('session')
    }
  }
})