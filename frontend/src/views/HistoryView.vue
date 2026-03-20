<script setup>
import { ref } from 'vue'

// Стан: яка вкладка активна (list або calendar)
const activeTab = ref('list') 
</script>

<template>
  <div class="page-container">
    <div class="tabs-header">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'list' }"
        @click="activeTab = 'list'"
      >
        Історія
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'calendar' }"
        @click="activeTab = 'calendar'"
      >
        Календар
      </button>
    </div>

    <div class="tab-content">
      <div v-if="activeTab === 'list'">
        <div class="history-item">09.02 - День Грудних (Виконано)</div>
        <div class="history-item">07.02 - Спина (Виконано)</div>
      </div>

      <div v-if="activeTab === 'calendar'">
        <div class="calendar-placeholder">📅 Тут буде календар</div>
      </div>
    </div>

    <div class="floating-actions">
      <button class="main-action start">▶ Почати</button>
      <button class="main-action plan">📅 Запланувати</button>
    </div>
  </div>
</template>

<style scoped>
.tabs-header {
  display: flex;
  background: var(--tg-theme-secondary-bg-color, #eef);
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 15px;
}
.tab-btn {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px;
  border-radius: 6px;
  font-weight: 500;
  color: var(--tg-theme-text-color);
}
.tab-btn.active {
  background: var(--tg-theme-bg-color, #fff);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.history-item {
  background: var(--tg-theme-bg-color);
  border: 1px solid var(--tg-theme-hint-color);
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 8px;
}

.floating-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.main-action {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  font-size: 14px;
}
.main-action.start {
  background: var(--tg-theme-button-color, #3390ec);
  color: #fff;
}
.main-action.plan {
  background: var(--tg-theme-secondary-bg-color, #eef);
  color: var(--tg-theme-text-color);
}
</style>