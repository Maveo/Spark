<template>
    <div class="d-flex justify-content-center align-items-center" style="height: 100vh; margin: -3rem 0;">

        <div class="w-100 h-100 d-flex justify-content-center align-items-center" style="position: relative;">

            <div clas="d-flex justify-content-center" style="position: relative;">

                <div class="bg-shape bg-shape-anim-1" style="margin-left: -100px;">
                    <!--  -->
                </div>

                <div class="bg-shape bg-shape-anim-2" style="margin-left: 100px;">
                    <!--  -->
                </div>

                <div class="bg-shape bg-shape-anim-3" style="margin-top: 100px;">
                    <!--  -->
                </div>
    
                <div class="p-4 rounded d-flex flex-column justify-content-center shadow-lg" style="background-color: #444;">
                    <div class="d-flex justify-content-center">
                        <img src="../assets/spark-logo.png" alt="Spark Logo" class="align-self-center" style="background: transparent;">
                        <img src="../assets/spark-title.png" alt="Spark Logo" class="align-self-center" style="background: transparent;">
                    </div>
                    <button @click="login()" class="btn btn-dark btn-lg text-white mt-3 d-flex" style="background-color: #6c89e0;" :disabled="loading">
                        <div class="me-2" style="width: 24px; height: 30px;">
                            <i v-if="!loading" class="fab fa-fw fa-discord"></i>
                            <span v-if="loading" class="spinner-border spinner-border-sm mb-1 me-2" role="status" aria-hidden="true"></span>
                        </div>
                        {{ $filters.i18n('SIGN_IN_DISCORD') }}
                    </button>
                </div>

            </div>

        </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import store from '@/store'
import router from '@/router'
import api from '@/services/api'

// eslint-disable-next-line @typescript-eslint/no-var-requires
let Swal = require('sweetalert2/src/sweetalert2.js').default;
import { AxiosResponse } from 'axios';

export default defineComponent({
  name: 'Login',
  data() {
      return {
        loading: true,
      }
  },
  created() {
    if (Object.keys(this.$route.query).length > 0) {
        this.loading = true;
        console.log('got oauth2 result, creating session');

        const params = {...this.$route.query};

        window.history.replaceState({}, '', `${location.pathname}`);
    
        api.create_session(params).then((response: AxiosResponse) => {
            console.log(response.data);

            store.commit('login', response.data.session_token);
            if (store.state.persistant.wanted_redirect) {
                router.push(store.state.persistant.wanted_redirect);
                store.commit('set_redirect', '');
            } else {
                router.push('choose-server');
            }
            
        }).catch(() => {
            this.loading = false;

            Swal.fire({
                title: 'Error!',
                text: 'An unknown error occured',
                icon: 'error'
            });
        });
        return;
    }

    this.loading = false;


  },
  methods: {
    login() {
        console.log('Logging in...');
        this.loading = true;

        api.get_auth().then((response: AxiosResponse) => {
            console.log(response.data);
            console.log(response.headers);

            location.replace(response.data.auth_url);
        }).catch(() => {

            Swal.fire({
                title: 'Error!',
                text: 'An unknown error occured',
                icon: 'error'
            });
        });
    }
  }
});
</script>

<style scoped>

.bg-shape {
    /* mix-blend-mode: multiply; */
    /* mix-blend-mode: lighten; */
    z-index: -50;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 325px;
    height: 325px;
    border-radius: 50%;
    filter: blur(75px);
    opacity: 0.2;

    background-color: #F8AA15;
}
.bg-shape-anim-1 {
    animation: bg-shape-anim-1 9s infinite;
    width: 350px;
    height: 350px;
}
@keyframes bg-shape-anim-1 {
    0% {
        margin-left: -100px;
        margin-top: -20px;
    }
    40% {
        margin-left: -50px;
        margin-top: -40px;
    }
    70% {
        margin-left: -80px;
        margin-top: -30px;
    }
    100% {
        margin-left: -100px;
        margin-top: -20px;
    }
}
.bg-shape-anim-2 {
    animation: bg-shape-anim-2 10s infinite;
}
@keyframes bg-shape-anim-2 {
    0% {
        margin-left: 100px;
        margin-top: -30px;
    }
    50% {
        margin-left: 60px;
        margin-top: 10px;
    }
    75% {
        margin-left: 70px;
        margin-top: -10px;
    }
    100% {
        margin-left: 100px;
        margin-top: -30px;
    }
}
.bg-shape-anim-3 {
    animation: bg-shape-anim-3 12s infinite;
    width: 300px;
    height: 300px;
}
@keyframes bg-shape-anim-3 {
    0% {
        margin-left: -10px;
        margin-top: 80px;
    }
    20% {
        margin-left: 20px;
        margin-top: 50px;
    }
    50% {
        margin-left: 0px;
        margin-top: 40px;
    }
    100% {
        margin-left: -10px;
        margin-top: 80px;
    }
}

</style>