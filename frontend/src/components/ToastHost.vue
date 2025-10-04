<script setup>
import { useToast } from '../stores/toast'

const toast = useToast()

// Expose globally for convenience
window.$toast = toast
</script>

<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="item in toast.items"
        :key="item.id"
        :class="['toast', item.type]"
        @click="toast.remove(item.id)"
      >
        <span class="toast-icon">
          {{ item.type === 'success' ? '✓' : item.type === 'error' ? '✕' : 'ℹ' }}
        </span>
        {{ item.message }}
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 100;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin-top: 8px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 10px;
  box-shadow: var(--shadow);
  pointer-events: all;
  cursor: pointer;
  max-width: 400px;
}

.toast.success {
  background: #15352b;
  border-color: #10b981;
}

.toast.error {
  background: #401e2a;
  border-color: var(--danger);
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  font-size: 12px;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>