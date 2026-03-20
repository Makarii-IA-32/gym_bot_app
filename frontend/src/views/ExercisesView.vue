<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import WebApp from '@twa-dev/sdk'

const muscles = ref([])
const tags = ref([])
const exercises = ref([])
const isLoading = ref(false)
const userId = ref(1)

const filterMuscle = ref(null) 
const filterTag = ref(null)

const modals = ref({
  muscle: false, tag: false, exercise: false, newTag: false
})

const isEditing = ref(false)
const formExercise = ref({
  id: null, name: '', description: '', muscle_id: null, 
  tag_ids: [], photo_path: null, is_mine: true, is_global: false
})
const newTagName = ref('')

// --- СОРТУВАННЯ (з використанням is_mine) ---
const sortedExercises = computed(() => {
  return [...exercises.value].sort((a, b) => {
    let scoreA = 0, scoreB = 0
    
    if (a.is_favorite && a.is_mine) scoreA = 4
    else if (a.is_favorite) scoreA = 3
    else if (a.is_mine) scoreA = 2
    else scoreA = 1
    
    if (b.is_favorite && b.is_mine) scoreB = 4
    else if (b.is_favorite) scoreB = 3
    else if (b.is_mine) scoreB = 2
    else scoreB = 1
    
    return scoreB - scoreA
  })
})

const loadData = async () => {
  isLoading.value = true
  try {
    const tgUser = WebApp.initDataUnsafe?.user
    userId.value = tgUser ? tgUser.id : 1; 

    const [musclesRes, tagsRes] = await Promise.all([
      axios.get('/api/exercises/muscles'),
      axios.get(`/api/exercises/tags?tg_id=${userId.value}`)
    ])
    muscles.value = musclesRes.data
    tags.value = tagsRes.data

    await loadExercises()
  } catch (e) { console.error(e) } 
  finally { isLoading.value = false }
}

const loadExercises = async () => {
  let url = `/api/exercises/?tg_id=${userId.value}`
  if (filterMuscle.value) url += `&muscle_id=${filterMuscle.value.id}`
  if (filterTag.value) url += `&tag_id=${filterTag.value.id}`
  const res = await axios.get(url)
  exercises.value = res.data
}

const toggleFavorite = async (ex) => {
  ex.is_favorite = !ex.is_favorite
  try { await axios.post(`/api/exercises/toggle_favorite?tg_id=${userId.value}&exercise_id=${ex.id}`) } 
  catch (e) { ex.is_favorite = !ex.is_favorite }
}

const openCreateModal = () => {
  isEditing.value = false
  formExercise.value = { id: null, name: '', description: '', muscle_id: null, tag_ids: [], photo_path: null, is_mine: true, is_global: false }
  modals.value.exercise = true
}

const openEditModal = (ex) => {
  isEditing.value = true
  formExercise.value = {
    id: ex.id, name: ex.name, description: ex.description || '', 
    muscle_id: ex.main_muscle_id, tag_ids: ex.tags.map(t => t.id), 
    photo_path: ex.photo_path, is_mine: ex.is_mine, is_global: ex.is_global
  }
  modals.value.exercise = true
}

const saveExercise = async () => {
  if (!formExercise.value.name || !formExercise.value.muscle_id) {
    alert("Назва та м'яз обов'язкові!")
    return
  }
  const url = isEditing.value ? `/api/exercises/${formExercise.value.id}` : '/api/exercises/create'
  const method = isEditing.value ? 'put' : 'post'
  try {
    await axios[method](url, {
      name: formExercise.value.name, description: formExercise.value.description,
      main_muscle_id: formExercise.value.muscle_id, tag_ids: formExercise.value.tag_ids,
      user_id: userId.value, photo_path: formExercise.value.photo_path 
    })
    modals.value.exercise = false
    loadExercises()
  } catch (e) { alert("Помилка збереження") }
}

const deleteExercise = async () => {
  if (!confirm("Видалити цю вправу?")) return
  try {
    await axios.delete(`/api/exercises/${formExercise.value.id}?tg_id=${userId.value}`)
    modals.value.exercise = false
    loadExercises()
  } catch (e) { alert("Неможливо видалити (глобальна вправа)") }
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await axios.post('/api/exercises/upload_image', formData, { headers: { 'Content-Type': 'multipart/form-data' }})
    formExercise.value.photo_path = res.data.path
  } catch (e) { alert("Помилка завантаження фото") }
}

const createNewTag = async () => {
  if (!newTagName.value.trim()) return
  try {
    const res = await axios.post(`/api/exercises/tags/create?tg_id=${userId.value}`, { name: newTagName.value })
    const newTagId = res.data.id
    const tagsRes = await axios.get(`/api/exercises/tags?tg_id=${userId.value}`)
    tags.value = tagsRes.data
    if (modals.value.exercise) formExercise.value.tag_ids.push(newTagId)
    modals.value.newTag = false
    newTagName.value = ''
  } catch (e) { alert("Помилка створення тегу") }
}

onMounted(() => { loadData() })
</script>

<template>
  <div class="page-container ex-view">
    <div class="filters-header">
      <button class="filter-box" @click="modals.muscle = true">
        <span class="label">М'яз:</span>
        <span class="value">{{ filterMuscle ? filterMuscle.name : 'Всі' }}</span><span class="arrow">▼</span>
      </button>
      <button class="filter-box" @click="modals.tag = true">
        <span class="label">Тег:</span>
        <span class="value">{{ filterTag ? filterTag.name : 'Всі' }}</span><span class="arrow">▼</span>
      </button>
    </div>

    <div class="exercises-list">
      <div 
        v-for="ex in sortedExercises" :key="ex.id" 
        class="ex-card" :class="{ favorite: ex.is_favorite, mine: ex.is_mine }" @click="openEditModal(ex)"
      >
        <div class="ex-left">
          <div class="ex-thumb" v-if="ex.photo_path"><img :src="ex.photo_path" /></div>
          <div class="ex-thumb placeholder" v-else>🏋️</div>
          <div class="ex-info">
            <h3>{{ ex.name }}</h3>
             <div class="card-tags">
               <span v-if="ex.is_mine" class="mini-tag mine">👤 Моє</span>
               <span v-for="t in ex.tags" :key="t.id" class="mini-tag">#{{ t.name }}</span>
            </div>
          </div>
        </div>
        <button class="like-btn" @click.stop="toggleFavorite(ex)">{{ ex.is_favorite ? '★' : '☆' }}</button>
      </div>
    </div>
    <button class="fab" @click="openCreateModal">+</button>

    <div v-if="modals.muscle" class="modal-overlay" @click.self="modals.muscle = false">
      <div class="modal-sheet">
        <div class="sheet-header">
           <h3>Група м'язів</h3><button class="close-txt" @click="filterMuscle = null; modals.muscle = false; loadExercises()">Скинути</button>
        </div>
        <div class="grid-muscles">
          <div v-for="m in muscles" :key="m.id" class="grid-item" :class="{ active: filterMuscle?.id === m.id }" @click="filterMuscle = m; modals.muscle = false; loadExercises()">
             <div class="emoji">💪</div><span>{{ m.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="modals.tag" class="modal-overlay" @click.self="modals.tag = false">
      <div class="modal-sheet">
        <div class="sheet-header">
           <h3>Фільтр тегів</h3><button class="close-txt" @click="filterTag = null; modals.tag = false; loadExercises()">Скинути</button>
        </div>
        <div class="list-tags">
           <div v-for="t in tags" :key="t.id" class="list-item" :class="{ active: filterTag?.id === t.id }" @click="filterTag = t; modals.tag = false; loadExercises()"># {{ t.name }}</div>
           <div class="list-item create" @click="modals.tag = false; modals.newTag = true">➕ Створити тег</div>
        </div>
      </div>
    </div>

    <div v-if="modals.exercise" class="modal-overlay center z-1500" @click.self="modals.exercise = false">
      <div class="modal-card">
        <div class="card-header">
           <h3>{{ isEditing ? 'Редагування' : 'Нова вправа' }}</h3><button class="close-icon" @click="modals.exercise = false">✕</button>
        </div>
        <div class="card-body">
          <div class="photo-area">
             <img v-if="formExercise.photo_path" :src="formExercise.photo_path" class="preview-img" />
             <div v-else class="photo-placeholder">Без фото</div>
             <label v-if="formExercise.is_mine" class="btn outline small">
               📷 Змінити <input type="file" @change="handleFileUpload" accept="image/*" hidden />
             </label>
          </div>
          <label class="input-label">Назва</label>
          <input v-model="formExercise.name" class="input-field" :disabled="!formExercise.is_mine" />
          <div class="label-row"><label class="input-label">Опис</label><span class="char-count">{{ formExercise.description.length }}/300</span></div>
          <textarea v-model="formExercise.description" class="input-field textarea" maxlength="300" :disabled="!formExercise.is_mine"></textarea>
          <label class="input-label">М'яз</label>
          <select v-model="formExercise.muscle_id" class="input-field" :disabled="!formExercise.is_mine">
             <option v-for="m in muscles" :key="m.id" :value="m.id">{{ m.name }}</option>
          </select>
          <label class="input-label">Теги</label>
          <div class="tags-cloud">
             <span v-for="t in tags" :key="t.id" class="tag-chip" :class="{ selected: formExercise.tag_ids.includes(t.id) }" @click="formExercise.tag_ids.includes(t.id) ? formExercise.tag_ids = formExercise.tag_ids.filter(id => id !== t.id) : formExercise.tag_ids.push(t.id)">{{ t.name }}</span>
             <button class="tag-chip add" @click="modals.newTag = true">+ Тег</button>
          </div>
          <div v-if="!formExercise.is_mine" class="hint-text">💡 Це глобальна вправа. Змінювати можна тільки теги.</div>
        </div>
        <div class="card-footer">
           <button v-if="isEditing && formExercise.is_mine" class="btn danger" @click="deleteExercise">Видалити</button>
           <div style="flex: 1"></div>
           <button class="btn secondary" @click="modals.exercise = false">Скасувати</button>
           <button class="btn primary" @click="saveExercise">Зберегти</button>
        </div>
      </div>
    </div>

    <div v-if="modals.newTag" class="modal-overlay center z-2000" @click.self="modals.newTag = false">
       <div class="modal-card mini">
          <h3>Назва тегу</h3>
          <input v-model="newTagName" class="input-field" placeholder="Напр. Вдома" autofocus />
          <div class="card-footer right">
             <button @click="modals.newTag = false" class="btn secondary">Назад</button>
             <button @click="createNewTag" class="btn primary">OK</button>
          </div>
       </div>
    </div>
  </div>
</template>

<style scoped>
.ex-view { padding-bottom: 90px; }
.filters-header { display: flex; gap: 10px; padding: 10px 0; position: sticky; top: 0; background: var(--tg-theme-bg-color, #f0f2f5); z-index: 5; }
.filter-box { flex: 1; display: flex; align-items: center; justify-content: space-between; background: var(--tg-theme-secondary-bg-color, #ffffff); border: 1px solid var(--tg-theme-hint-color, #ccc); padding: 10px 12px; border-radius: 12px; color: var(--tg-theme-text-color, #000); box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.filter-box .label { font-size: 11px; color: var(--tg-theme-hint-color, #888); margin-right: 5px; }
.filter-box .value { font-weight: 600; font-size: 13px; flex: 1; text-align: left; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;}
.exercises-list { padding-top: 10px; }
.ex-card { display: flex; justify-content: space-between; align-items: center; background: var(--tg-theme-bg-color, #ffffff); border: 1px solid var(--tg-theme-hint-color, #e0e0e0); padding: 12px; border-radius: 14px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.ex-card.favorite { border-color: #ffb74d; background: linear-gradient(to right, rgba(255,183,77,0.05), transparent); }
.ex-card.mine { border-left: 4px solid var(--tg-theme-button-color, #3390ec); }
.ex-left { display: flex; align-items: center; gap: 12px; overflow: hidden;}
.ex-thumb { width: 45px; height: 45px; border-radius: 10px; flex-shrink: 0; overflow: hidden; background: var(--tg-theme-secondary-bg-color, #eee); display: flex; align-items: center; justify-content: center; font-size: 20px; }
.ex-thumb img { width: 100%; height: 100%; object-fit: cover; }
.ex-info h3 { margin: 0; font-size: 15px; font-weight: 600; color: var(--tg-theme-text-color, #000); }
.card-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; }
.mini-tag { font-size: 10px; background: var(--tg-theme-secondary-bg-color, #f5f5f5); padding: 3px 6px; border-radius: 6px; color: var(--tg-theme-hint-color, #666); }
.mini-tag.mine { background: rgba(51, 144, 236, 0.1); color: var(--tg-theme-button-color, #3390ec); font-weight: 600;}
.like-btn { flex-shrink: 0; background: none; border: none; font-size: 24px; color: #ff9800; padding: 5px; }
.empty-state { text-align: center; margin-top: 40px; color: var(--tg-theme-hint-color, #888); font-size: 14px;}
.fab { position: fixed; bottom: 80px; right: 20px; width: 56px; height: 56px; border-radius: 50%; background: var(--tg-theme-button-color, #3390ec); color: #fff; font-size: 32px; border: none; box-shadow: 0 4px 12px rgba(51,144,236,0.4); display: flex; align-items: center; justify-content: center; z-index: 90; }

/* ВИПРАВЛЕНІ МОДАЛКИ */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); z-index: 1000; display: flex; flex-direction: column;}
.modal-overlay.center { justify-content: center; align-items: center; padding: 20px; box-sizing: border-box; }
.z-1500 { z-index: 1500 !important; }
.z-2000 { z-index: 2000 !important; }

/* BOTTOM SHEET */
.modal-sheet { margin-top: auto; width: 100%; max-height: 80vh; background: var(--tg-theme-bg-color, #ffffff); border-radius: 20px 20px 0 0; padding: 20px; box-shadow: 0 -5px 15px rgba(0,0,0,0.1); overflow-y: auto;}
.sheet-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--tg-theme-hint-color, #eee); padding-bottom: 15px; margin-bottom: 15px;}
.sheet-header h3 { margin: 0; font-size: 16px; color: var(--tg-theme-text-color, #000);}
.close-txt { background: none; border: none; color: var(--tg-theme-button-color, #3390ec); font-weight: 600; font-size: 14px;}

.grid-muscles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.grid-item { background: var(--tg-theme-secondary-bg-color, #f5f5f5); border: 1px solid transparent; padding: 15px 5px; border-radius: 12px; text-align: center; font-size: 12px; font-weight: 500; color: var(--tg-theme-text-color, #000); display: flex; flex-direction: column; align-items: center;}
.grid-item.active { background: rgba(51, 144, 236, 0.1); border-color: var(--tg-theme-button-color, #3390ec); color: var(--tg-theme-button-color, #3390ec); }
.grid-item .emoji { font-size: 24px; margin-bottom: 6px; }

.list-tags { margin-top: 10px; }
.list-item { padding: 15px 10px; border-bottom: 1px solid var(--tg-theme-hint-color, #eee); font-size: 15px; color: var(--tg-theme-text-color, #000);}
.list-item.active { font-weight: bold; color: var(--tg-theme-button-color, #3390ec); }
.list-item.create { color: var(--tg-theme-button-color, #3390ec); font-weight: bold; border-bottom: none;}

.modal-card { background: var(--tg-theme-bg-color, #ffffff); width: 100%; max-width: 400px; max-height: 90vh; border-radius: 16px; display: flex; flex-direction: column; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden;}
.modal-card.mini { height: auto; padding: 20px;}
.modal-card.mini h3 { margin: 0 0 15px 0; color: var(--tg-theme-text-color, #000);}

.card-header { padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--tg-theme-hint-color, #eee); background: var(--tg-theme-bg-color, #fff);}
.card-header h3 { margin: 0; font-size: 18px; color: var(--tg-theme-text-color, #000);}
.close-icon { background: var(--tg-theme-secondary-bg-color, #eee); border: none; width: 30px; height: 30px; border-radius: 15px; font-size: 14px; display: flex; align-items: center; justify-content: center; color: var(--tg-theme-text-color, #000);}

.card-body { padding: 20px; overflow-y: auto; flex: 1; background: var(--tg-theme-bg-color, #fff);}
.card-footer { padding: 15px 20px; display: flex; gap: 10px; border-top: 1px solid var(--tg-theme-hint-color, #eee); background: var(--tg-theme-bg-color, #fff);}
.card-footer.right { padding: 0; border: none; justify-content: flex-end; margin-top: 15px;}

.input-label { display: block; font-size: 12px; color: var(--tg-theme-hint-color, #888); margin-bottom: 6px; font-weight: 500;}
.label-row { display: flex; justify-content: space-between; align-items: flex-end;}
.char-count { font-size: 11px; color: var(--tg-theme-hint-color, #aaa); margin-bottom: 6px;}

.input-field { width: 100%; padding: 12px; background: var(--tg-theme-secondary-bg-color, #f9f9f9); border: 1px solid var(--tg-theme-hint-color, #ccc); border-radius: 10px; margin-bottom: 15px; color: var(--tg-theme-text-color, #000); font-size: 15px; box-sizing: border-box;}
.input-field:disabled { opacity: 0.6; background: #eee; }
.textarea { resize: none; height: 100px; font-family: inherit;}

.btn { padding: 10px 16px; border-radius: 10px; border: none; font-weight: 600; font-size: 14px; text-align: center;}
.btn.primary { background: var(--tg-theme-button-color, #3390ec); color: #fff; }
.btn.secondary { background: var(--tg-theme-secondary-bg-color, #eee); color: var(--tg-theme-text-color, #000); }
.btn.danger { background: rgba(255, 59, 48, 0.1); color: #ff3b30; }
.btn.outline { background: transparent; border: 1px solid var(--tg-theme-button-color, #3390ec); color: var(--tg-theme-button-color, #3390ec);}
.btn.small { padding: 6px 12px; font-size: 12px; border-radius: 8px;}

.tags-cloud { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;}
.tag-chip { padding: 8px 14px; border: 1px solid var(--tg-theme-hint-color, #ccc); border-radius: 20px; font-size: 13px; color: var(--tg-theme-text-color, #000); background: var(--tg-theme-bg-color, #fff); transition: 0.2s;}
.tag-chip.selected { background: var(--tg-theme-button-color, #3390ec); color: #fff; border-color: transparent; }
.tag-chip.add { border-style: dashed; background: transparent; padding: 8px 16px; color: var(--tg-theme-button-color, #3390ec); border-color: var(--tg-theme-button-color, #3390ec);}
.hint-text { font-size: 12px; color: var(--tg-theme-hint-color, #888); background: var(--tg-theme-secondary-bg-color, #f5f5f5); padding: 10px; border-radius: 8px; line-height: 1.4;}

.photo-area { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
.preview-img { width: 70px; height: 70px; border-radius: 12px; object-fit: cover; border: 1px solid var(--tg-theme-hint-color, #eee);}
.photo-placeholder { width: 70px; height: 70px; background: var(--tg-theme-secondary-bg-color, #f5f5f5); border: 1px dashed var(--tg-theme-hint-color, #ccc); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 11px; color: var(--tg-theme-hint-color, #888); text-align: center;}
</style>