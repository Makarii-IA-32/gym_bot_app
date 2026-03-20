<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// Дані
const muscles = ref([])
const exercises = ref([])
const activeMuscleId = ref(null) // Який м'яз зараз вибрано
const isLoading = ref(false)

// Функція завантаження м'язів
const fetchMuscles = async () => {
  try {
    const res = await axios.get('/api/exercises/muscles')
    muscles.value = res.data
    
    // Одразу вибираємо перший м'яз і вантажимо вправи для нього
    if (muscles.value.length > 0) {
      selectMuscle(muscles.value[0].id)
    }
  } catch (e) {
    console.error("Помилка завантаження м'язів:", e)
  }
}

// Функція вибору м'яза (фільтрація)
const selectMuscle = async (id) => {
  activeMuscleId.value = id
  isLoading.value = true
  exercises.value = [] // Очищуємо список перед завантаженням

  try {
    // Запит на бекенд з параметром ?muscle_id=...
    const res = await axios.get(`/api/exercises/?muscle_id=${id}`)
    exercises.value = res.data
  } catch (e) {
    console.error("Помилка вправ:", e)
  } finally {
    isLoading.value = false
  }
}

// Запускаємо при старті
onMounted(() => {
  fetchMuscles()
})
</script>

<template>
  <div class="catalog-container">
    <h2>📚 Каталог вправ</h2>

    <div class="muscles-scroll">
      <button 
        v-for="muscle in muscles" 
        :key="muscle.id"
        class="chip"
        :class="{ active: activeMuscleId === muscle.id }"
        @click="selectMuscle(muscle.id)"
      >
        {{ muscle.name }}
      </button>
    </div>

    <div class="exercises-list">
      <div v-if="isLoading" class="loading">Завантаження...</div>
      
      <div v-else-if="exercises.length === 0" class="empty">
        Вправ поки немає
      </div>

      <div 
        v-else 
        v-for="ex in exercises" 
        :key="ex.id" 
        class="exercise-card"
      >
        <div class="card-header">
          <h3>{{ ex.name }}</h3>
          <span v-if="ex.is_global" class="badge">Базова</span>
        </div>
        <p class="desc">{{ ex.description }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Стилі під Телеграм */
.catalog-container {
  padding-bottom: 20px;
}

h2 {
  font-size: 20px;
  margin-bottom: 15px;
}

/* Скрол м'язів */
.muscles-scroll {
  display: flex;
  overflow-x: auto;
  gap: 8px;
  padding-bottom: 10px;
  margin-bottom: 10px;
  /* Ховаємо скролбар для краси */
  scrollbar-width: none; 
}
.muscles-scroll::-webkit-scrollbar {
  display: none;
}

/* Кнопки-чіпи */
.chip {
  background: var(--tg-theme-secondary-bg-color, #eef);
  color: var(--tg-theme-text-color, #000);
  border: 1px solid transparent;
  padding: 8px 16px;
  border-radius: 20px;
  white-space: nowrap;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.chip.active {
  background: var(--tg-theme-button-color, #3390ec);
  color: var(--tg-theme-button-text-color, #fff);
}

/* Картки вправ */
.exercise-card {
  background: var(--tg-theme-bg-color, #fff);
  border: 1px solid var(--tg-theme-hint-color, #ccc);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h3 {
  margin: 0;
  font-size: 16px;
}

.desc {
  color: var(--tg-theme-hint-color, #888);
  font-size: 13px;
  margin-top: 5px;
}

.badge {
  background: #e0f7fa;
  color: #006064;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.loading, .empty {
  text-align: center;
  color: var(--tg-theme-hint-color, #888);
  margin-top: 20px;
}
</style>