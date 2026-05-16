<script setup>
/**
 * @file Компонент нижньої панелі навігації (BottomNav.vue).
 * @component BottomNav
 * @description Забезпечує фіксовано меню перемикання між основними розділами застосунку.
 */

import { useRouter, useRoute } from 'vue-router'

/**
 * Об'єкт маршрутизатора для виконання програмних переходів між сторінками.
 * @type {import('vue-router').Router}
 */
const router = useRouter()

/**
 * Об'єкт поточного стану активного маршруту для відстеження URL.
 * @type {import('vue-router').RouteLocationNormalizedLoaded}
 */
const route = useRoute()

/**
 * Перевіряє, чи є вказаний URL-шлях активним у даний момент.
 * Використовується для динамічного призначення CSS-класу `.active`.
 * * @function isActive
 * @param {string} path - Шлях маршруту для перевірки (наприклад, '/exercises').
 * @returns {boolean} True, якщо переданий шлях збігається з поточним шляхом у браузері.
 */
const isActive = (path) => route.path === path
</script>

<template>
  <nav class="bottom-nav">
    <button 
      class="nav-item" 
      :class="{ active: isActive('/programs') }"
      @click="router.push('/programs')"
    >
      <span class="icon">📋</span>
      <span class="label">Програми</span>
    </button>

    <button 
      class="nav-item" 
      :class="{ active: isActive('/exercises') }"
      @click="router.push('/exercises')"
    >
      <span class="icon">💪</span>
      <span class="label">Вправи</span>
    </button>

    <button 
      class="nav-item" 
      :class="{ active: isActive('/history') }"
      @click="router.push('/history')"
    >
      <span class="icon">📅</span>
      <span class="label">Історія</span>
    </button>

    <button 
      class="nav-item" 
      :class="{ active: isActive('/profile') }"
      @click="router.push('/profile')"
    >
      <span class="icon">👤</span>
      <span class="label">Профіль</span>
    </button>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background: var(--tg-theme-secondary-bg-color, #fff);
  border-top: 1px solid var(--tg-theme-hint-color, #ccc);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom); /* Для iPhone X+ */
}

.nav-item {
  background: none;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--tg-theme-hint-color, #888);
  font-size: 10px;
}

.nav-item .icon {
  font-size: 20px;
}

.nav-item.active {
  color: var(--tg-theme-button-color, #3390ec);
}
</style>