<script setup>
import Navbar from './components/Navbar.vue'
import ToastHost from './components/ToastHost.vue'
import { onMounted, ref } from 'vue'

const starsCanvas = ref(null)

onMounted(() => {
  const canvas = starsCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  let stars = []
  const nbStars = 80
  
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    
    stars = Array.from({ length: nbStars }).map(() => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 2 + 0.5,
      speed: Math.random() * 0.2 + 0.1,
      opacity: Math.random() * 0.8 + 0.2
    }))
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    for (const star of stars) {
      ctx.globalAlpha = star.opacity
      ctx.fillStyle = Math.random() > 0.7 ? '#1DCD9F' : '#48f1af'
      ctx.beginPath()
      ctx.arc(star.x, star.y, star.size, 0, 2 * Math.PI)
      ctx.fill()
      
      star.y += star.speed
      if (star.y > canvas.height) {
        star.y = 0
        star.x = Math.random() * canvas.width
      }
    }
    
    requestAnimationFrame(animate)
  }
  
  resize()
  animate()
  window.addEventListener('resize', resize)
})
</script>

<template>
  <div id="app">
    <canvas ref="starsCanvas" class="background-canvas"></canvas>
    <Navbar />
    <main class="container" role="main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <ToastHost />
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.background-canvas {
  position: fixed;
  top: 0;
  left: 0;
  z-index: -1;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

main {
  flex: 1;
  padding-top: 24px;
  padding-bottom: 48px;
  position: relative;
  z-index: 1;
}
</style>
