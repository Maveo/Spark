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

const app = createApp(App);
app.use(store).use(router).use(VueLazyLoad).mount('#app');

function format(s: string, args: Array<string>) {
    return [...args].reduce((p,c) => p.replace(/{}/,c), s);
}

app.config.globalProperties.$filters = {
    i18n(key: string, args = []) {
        if (key in store.state.i18n) return format(store.state.i18n[key], args);
        return key;
    }
}

app.provide('filters', app.config.globalProperties.$filters)
