<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import WebApp from '@twa-dev/sdk'
import BottomNav from './components/BottomNav.vue'

const isAuth = ref(false) // Чи пройшли ми авторизацію
const status = ref('Завантаження...')
const backendUrl = '/api'

onMounted(async () => {
  WebApp.ready()
  WebApp.expand() // Розгорнути на весь екран одразу

  const tgUser = WebApp.initDataUnsafe?.user

  if (tgUser) {
    try {
      // Тиха реєстрація/вхід
      await axios.post(`${backendUrl}/users/`, {
        tg_id: tgUser.id,
        username: tgUser.username || "unknown",
        full_name: `${tgUser.first_name} ${tgUser.last_name || ''}`.trim()
      })
      isAuth.value = true
    } catch (error) {
      status.value = 'Помилка сервера. Спробуйте пізніше.'
      console.error(error)
    }
  } else {
    // Режим розробки в браузері
    isAuth.value = true 
  }
})
</script>

<template>
  <div v-if="!isAuth" class="loading-screen">
    <h3>🏋️ Gym Bot</h3>
    <p>{{ status }}</p>
  </div>

  <div v-else class="app-layout">
    <router-view></router-view>
    
    <BottomNav />
  </div>
</template>

<style>
.loading-screen {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: var(--tg-theme-bg-color);
}
</style>