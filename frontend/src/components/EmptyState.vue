<template>
  <div class="empty-state">
    <div class="icon">
      <slot name="icon">🔭</slot>
    </div>
    <h3>{{ title || 'No data yet' }}</h3>
    <p>{{ message || 'Get started by uploading your first dataset.' }}</p>
    <slot name="action"></slot>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  message: String
})
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 48px 24px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
}

.icon {
  font-size: 48px;
  margin-bottom: 16px;
}

h3 {
  margin: 0 0 8px 0;
  color: var(--fg);
}

p {
  margin: 0 0 16px 0;
  color: var(--muted);
}
</style>