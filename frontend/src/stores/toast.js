import { defineStore } from 'pinia'

export const useToast = defineStore('toast', {
  state: () => ({
    items: []
  }),
  
  actions: {
    add(message, type = 'info', duration = 3500) {
      const id = Math.random().toString(36).slice(2)
      this.items.push({ id, message, type })
      setTimeout(() => this.remove(id), duration)
    },
    
    remove(id) {
      this.items = this.items.filter(t => t.id !== id)
    },
    
    success(message) {
      this.add(message, 'success')
    },
    
    error(message) {
      this.add(message, 'error')
    },
    
    info(message) {
      this.add(message, 'info')
    }
  }
})