import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import { applyEditorialDefaults } from './utils/chartDefaults.js'

applyEditorialDefaults()

createApp(App).mount('#app')
