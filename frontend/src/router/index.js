import { createRouter, createWebHistory } from 'vue-router'

// Імпортуємо сторінки (ми їх зараз створимо)
import ProgramsView from '../views/ProgramsView.vue'
import ExercisesView from '../views/ExercisesView.vue'
import HistoryView from '../views/HistoryView.vue'
import ProfileView from '../views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/history' }, // За замовчуванням відкриваємо Історію
    { path: '/programs', component: ProgramsView },
    { path: '/exercises', component: ExercisesView },
    { path: '/history', component: HistoryView },
    { path: '/profile', component: ProfileView },
  ]
})

export default router