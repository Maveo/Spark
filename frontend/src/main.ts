import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import VueLazyLoad from 'vue3-lazyload'

import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css'
import '@fortawesome/fontawesome-free/css/all.min.css'
import '@/assets/product-sans-master/css/product-sans-all-latin.css'
import '@sweetalert2/theme-dark/dark.css'

createApp(App).use(store).use(router).use(VueLazyLoad).mount('#app')
