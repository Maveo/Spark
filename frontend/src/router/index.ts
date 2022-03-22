import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import store from '@/store'
import YourProfile from '../views/YourProfile.vue'
import Boosts from '../views/Boosts.vue'
import ProfileCard from '../views/ProfileCard.vue'
import ServerSettings from '../views/ServerSettings.vue'
import AdminTools from '../views/AdminTools.vue'
import SuperAdmin from '../views/SuperAdmin.vue'
import ServerModules from '../views/ServerModules.vue'
import Ranking from '../views/Ranking.vue'
import ChooseServer from '../views/ChooseServer.vue'
import PageNotFound from '../views/PageNotFound.vue'
import Login from '../views/Login.vue'


const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: 'Home',
        redirect: () => {
            return '/login';
        }
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        beforeEnter: () => {
            if (store.state.persistant.token) {
                return '/choose-server'
            }
        }
    },
    {
        path: '/your-profile/:id',
        name: 'Your Profile',
        component: YourProfile,
        meta: { requiresLogin: true, requiresServer: true }
    },
    {
        path: '/boosts/:id',
        name: 'Boosts',
        component: Boosts,
        meta: { requiresLogin: true, requiresServer: true }
    },
    {
        path: '/profile-card/:id',
        name: 'ProfileCard',
        component: ProfileCard,
        meta: { requiresLogin: true, requiresServer: true }
    },
    {
        path: '/server-settings/:id',
        name: 'ServerSettings',
        component: ServerSettings,
        meta: { requiresLogin: true, requiresServer: true }
    },
    {
        path: '/admin-tools/:id',
        name: 'AdminTools',
        component: AdminTools,
        meta: { requiresLogin: true, requiresServer: true }
    },
    {
        path: '/server-modules/:id',
        name: 'ServerModules',
        component: ServerModules,
        meta: { requiresLogin: true, requiresServer: true }
    },
    {
        path: '/ranking/:id',
        name: 'Ranking',
        component: Ranking,
        meta: { requiresLogin: true, requiresServer: true }
    },
    {
        path: '/super-admin/:id?',
        name: 'SuperAdmin',
        component: SuperAdmin,
        meta: { requiresLogin: true, serverOptional: true }
    },
    {
        path: '/choose-server',
        name: 'Choose Server',
        component: ChooseServer,
        meta: { requiresLogin: true }
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'PageNotFound',
        component: PageNotFound,
        meta: { requiresLogin: true }
    },
    // {
    //   path: '/about',
    //   name: 'About',
    //   // route level code-splitting
    //   // this generates a separate chunk (about.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
    // }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

router.beforeResolve(async (to, from, next) => {
    if (to.matched.some(record => record.meta.requiresLogin) && !store.state.persistant.token) {
        store.commit('set_redirect', to.fullPath);
        next('/login');
    } else if ((to.matched.some(record => record.meta.requiresServer) || to.matched.some(record => record.meta.serverOptional)) && !store.state.selected_server.id) {
        if (to.params.id) {
            await store.dispatch('choose_server', to.params.id);
            next();
        } else if (to.matched.some(record => record.meta.requiresServer)) {
            next('/choose-server');
        } else {
            next();
        }
    } else {
        next();
    }
})

export default router
