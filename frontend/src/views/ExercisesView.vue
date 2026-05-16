<script setup>
/**
 * @file Головний екран керування вправами (ExercisesView.vue).
 * Забезпечує відображення списку вправ, фільтрацію за м'язами та тегами,
 * додавання вправ до обраного, а також створення, редагування та видалення 
 * кастомних вправ користувача за допомогою модальних вікон.
 */

import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import WebApp from '@twa-dev/sdk'

/**
 * Список усіх груп м'язів для фільтрів та форми створення.
 * @type {import('vue').Ref<Array<{id: number, name: string}>>}
 */
const muscles = ref([])

/**
 * Список доступних тегів для фільтрації та вибору.
 * @type {import('vue').Ref<Array<{id: number, name: string, is_global: boolean}>>}
 */
const tags = ref([])

/**
 * Повний масив вправ, отриманий із сервера.
 * @type {import('vue').Ref<Array<Object>>}
 */
const exercises = ref([])

/**
 * Стан індикатора завантаження даних із сервера.
 * @type {import('vue').Ref<boolean>}
 */
const isLoading = ref(false)

/**
 * Внутрішній ідентифікатор користувача (за замовчуванням 1 для веб-розробки).
 * @type {import('vue').Ref<number>}
 */
const userId = ref(1)

/**
 * Поточний обраний об'єкт м'яза для фільтрації списку вправ.
 * @type {import('vue').Ref<Object|null>}
 */
const filterMuscle = ref(null) 

/**
 * Поточний обраний об'єкт тегу для фільтрації списку вправ.
 * @type {import('vue').Ref<Object|null>}
 */
const filterTag = ref(null)

/**
 * Стан відображення різних модальних вікон застосунку.
 * @type {import('vue').Ref<{muscle: boolean, tag: boolean, exercise: boolean, newTag: boolean}>}
 */
const modals = ref({
  muscle: false, tag: false, exercise: false, newTag: false
})

/**
 * Флаг, який визначає режим модального вікна вправи (true — редагування, false — створення).
 * @type {import('vue').Ref<boolean>}
 */
const isEditing = ref(false)

/**
 * Об'єкт стану форми для створення або редагування вправи.
 * @type {import('vue').Ref<{id: number|null, name: string, description: string, muscle_id: number|null, tag_ids: Array<number>, photo_path: string|null, is_mine: boolean, is_global: boolean}>}
 */
const formExercise = ref({
  id: null, name: '', description: '', muscle_id: null, 
  tag_ids: [], photo_path: null, is_mine: true, is_global: false
})

/**
 * Текстове поле для збереження назви нового тегу при створенні.
 * @type {import('vue').Ref<string>}
 */
const newTagName = ref('')

/**
 * Обчислювальний змінений масив вправ, відсортований за пріоритетом:
 * 1. Улюблені власні вправи (score = 4)
 * 2. Улюблені глобальні вправи (score = 3)
 * 3. Власні звичайні вправи (score = 2)
 * 4. Глобальні базові вправи (score = 1)
 * @type {import('vue').ComputedRef<Array<Object>>}
 */
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

/**
 * Первинно завантажує базову структуру даних: ініціалізує Telegram User,
 * завантажує м'язи, теги та викликає завантаження вправ.
 * @async
 * @function loadData
 * @returns {Promise<void>}
 */
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

/**
 * Завантажує список вправ із сервера з урахуванням обраних фільтрів м'язів та тегів.
 * @async
 * @function loadExercises
 * @returns {Promise<void>}
 */
const loadExercises = async () => {
  let url = `/api/exercises/?tg_id=${userId.value}`
  if (filterMuscle.value) url += `&muscle_id=${filterMuscle.value.id}`
  if (filterTag.value) url += `&tag_id=${filterTag.value.id}`
  const res = await axios.get(url)
  exercises.value = res.data
}

/**
 * Перемикає статус 'Обране' (лайк) для конкретної вправи на фронтенді та сервері.
 * @async
 * @function toggleFavorite
 * @param {Object} ex - Об'єкт вправи, для якої змінюється статус.
 * @returns {Promise<void>}
 */
const toggleFavorite = async (ex) => {
  ex.is_favorite = !ex.is_favorite
  try { await axios.post(`/api/exercises/toggle_favorite?tg_id=${userId.value}&exercise_id=${ex.id}`) } 
  catch (e) { ex.is_favorite = !ex.is_favorite }
}

/**
 * Ініціалізує пусту форму та відкриває модальне вікно для створення нової вправи.
 * @function openCreateModal
 */
const openCreateModal = () => {
  isEditing.value = false
  formExercise.value = { id: null, name: '', description: '', muscle_id: null, tag_ids: [], photo_path: null, is_mine: true, is_global: false }
  modals.value.exercise = true
}

/**
 * Заповнює форму даними обраної вправи та відкриває вікно для її перегляду або редагування.
 * @function openEditModal
 * @param {Object} ex - Об'єкт вправи, дані якої передаються у форму.
 */
const openEditModal = (ex) => {
  isEditing.value = true
  formExercise.value = {
    id: ex.id, name: ex.name, description: ex.description || '', 
    muscle_id: ex.main_muscle_id, tag_ids: ex.tags.map(t => t.id), 
    photo_path: ex.photo_path, is_mine: ex.is_mine, is_global: ex.is_global
  }
  modals.value.exercise = true
}

/**
 * Надсилає валідовані дані форми на сервер (POST для створення, PUT для оновлення).
 * @async
 * @function saveExercise
 * @returns {Promise<void>}
 */
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

/**
 * Надсилає DELETE-запит на сервер для повного видалення поточної кастомної вправи.
 * @async
 * @function deleteExercise
 * @returns {Promise<void>}
 */
const deleteExercise = async () => {
  if (!confirm("Видалити цю вправу?")) return
  try {
    await axios.delete(`/api/exercises/${formExercise.value.id}?tg_id=${userId.value}`)
    modals.value.exercise = false
    loadExercises()
  } catch (e) { alert("Неможливо видалити (глобальна вправа)") }
}

/**
 * Обробляє вибір медіафайлу користувачем, завантажує його через multipart/form-data
 * та зберігає отриманий від сервера шлях у форму вправи.
 * * @async
 * @function handleFileUpload
 * @param {Event} event - Подія вибору файлу з інпуту.
 * @returns {Promise<void>}
 */
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

/**
 * Створює новий кастомний тег для маркування вправ користувачем.
 * @async
 * @function createNewTag
 * @returns {Promise<void>}
 */
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

/**
 * Життєвий цикл компонента. Запускає первинне завантаження всіх масивів даних.
 */
onMounted(() => { loadData() })
</script>