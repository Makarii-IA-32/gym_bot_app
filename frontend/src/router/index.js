/**
 * @file Конфігурація маршрутизації (Vue Router) для клієнтської частини Gym Bot.
 * Визначає зв'язки між URL-шляхами застосунку та компонентами сторінок (Views).
 * @module router/index
 */

import { createRouter, createWebHistory } from 'vue-router'

// Імпортуємо сторінки застосунку
import ProgramsView from '../views/ProgramsView.vue'
import ExercisesView from '../views/ExercisesView.vue'
import HistoryView from '../views/HistoryView.vue'
import ProfileView from '../views/ProfileView.vue'

/**
 * Об'єкт роутера, що керує навігацією та історією переходів користувача.
 * * Маршрути у застосунку:
 * - `/` : Автоматичне перенаправлення на головну сторінку історії тренувань.
 * - `/programs` : Екран перегляду та створення шаблонів програм тренувань.
 * - `/exercises` : Інтерактивний каталог базових та кастомних вправ.
 * - `/history` : Журнал виконаних тренувань та календар планування.
 * - `/profile` : Сторінка профілю користувача з налаштуваннями.
 * * @type {import('vue-router').Router}
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { 
      path: '/', 
      redirect: '/history' 
    },
    { 
      path: '/programs', 
      component: ProgramsView 
    },
    { 
      path: '/exercises', 
      component: ExercisesView 
    },
    { 
      path: '/history', 
      component: HistoryView 
    },
    { 
      path: '/profile', 
      component: ProfileView 
    },
  ]
})

export default router