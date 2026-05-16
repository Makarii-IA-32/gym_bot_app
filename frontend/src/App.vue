<script setup>
/**
 * @file Кореневий компонент застосунку (App.vue).
 * Відповідає за первинне налаштування Telegram Mini App, розгортання вікна,
 * автоматичну авторизацію (або реєстрацію) користувача на бекенді при старті 
 * та відображення глобального макету (Layout) із нижньою навігацією.
 */

import { ref, onMounted } from 'vue'
import axios from 'axios'
import WebApp from '@twa-dev/sdk'
import BottomNav from './components/BottomNav.vue'

/**
 * Стан авторизації користувача.
 * @type {import('vue').Ref<boolean>}
 * @default false
 */
const isAuth = ref(false)

/**
 * Текстовий статус завантаження або помилки для відображення на Splash-screen.
 * @type {import('vue').Ref<string>}
 * @default 'Завантаження...'
 */
const status = ref('Завантаження...')

/**
 * Базовий префікс URL для запитів до API бекенду.
 * @type {string}
 */
const backendUrl = '/api'

/**
 * Хук життєвого циклу компонента. Виконує ініціалізацію Telegram SDK,
 * розгортає застосунок на повний екран та здійснює реєстрацію/вхід користувача.
 * * @async
 * @function onMounted
 * @returns {Promise<void>}
 */
onMounted(async () => {
  // Сповіщаємо Telegram, що додаток готовий до відображення
  WebApp.ready()
  // Розгортаємо Mini App на всю доступну висоту екрана смартфона
  WebApp.expand() 

  // Отримуємо дані користувача з безпечного контексту ініціалізації Telegram
  const tgUser = WebApp.initDataUnsafe?.user

  if (tgUser) {
    try {
      // Виконуємо  реєстрацію або авторизацію на бекенді
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
    // Режим розробки: якщо застосунок відкрито у звичайному браузері поза Telegram
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