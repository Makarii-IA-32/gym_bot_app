import { createApp } from 'vue'
import './style.css' // <--- Додай це
import App from './App.vue'
import router from './router' // Це ми зараз створимо

createApp(App).use(router).mount('#app')
