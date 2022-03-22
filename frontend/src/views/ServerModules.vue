<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Server Settings</h2>
            <span class="text-gray4">Edit default values or Sparks settings</span>
        </div>

        <div class="view-main-card">
            
            <div class="w-100">

                <div v-if="!loading">
                    <div v-for="(modul, key) in modules" :key="key" class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h5 class="mb-0">{{modul.title}}</h5>
                                <div class="text-gray4">{{modul.description}}</div>
                            </div>
                            <div v-if="modul.is_optional" class="d-flex align-items-center">
                                <template v-if="modul.loading">
                                    <span class="spinner-border" style="width: 1.5rem; height: 1.5rem; margin-left: 74px;" role="status" aria-hidden="true"></span>
                                </template>
                                <template v-else>
                                    <i v-if="modul.error" class="fas fa-exclamation-circle text-danger"></i>
                                    <div class="me-3">
                                        <button :disabled="state.selected_server.active_modules.includes(modul.name)" v-bind:class="{'btn-dark': !state.selected_server.active_modules.includes(modul.name)}" class="ms-2 btn btn-success btn-sm" style="height: 31px;" @click="set_module(modul, true)">
                                            <i class="fas fa-fw fa-check"></i>
                                        </button>
                                        <button :disabled="!state.selected_server.active_modules.includes(modul.name)" v-bind:class="{'btn-dark': state.selected_server.active_modules.includes(modul.name)}" class="ms-2 btn btn-danger btn-sm" style="height: 31px;" @click="set_module(modul, false)">
                                            <i class="fas fa-fw fa-times"></i>
                                        </button>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="loading" class="row">
                <div class="p-3 mb-2 text-center w-100">
                    <span class="spinner-border spinner-border-lg" role="status" aria-hidden="true"></span>
                </div>
            </div>

        </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import store from '@/store';
import api from '@/services/api';

// eslint-disable-next-line @typescript-eslint/no-var-requires
let Swal = require('sweetalert2/src/sweetalert2.js').default;
import { AxiosResponse } from "axios";

const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
});

export default defineComponent({
  name: "Server Modules",
  data() {
    return {
        state: store.state,
        loading: true,
        modules: {},
    }
  },
  created() {
      this.refresh_modules();
  },
  methods: {
    refresh_modules() {
        this.loading = true;
        this.modules = {};
        api.get_modules().then((response: AxiosResponse) => {
            console.log(response.data);
            this.modules = response.data.modules;
            this.loading = false;
        });
    },
    set_module(modul: any, activate: boolean) {
        modul.loading = true;
        api.set_module(modul.name, activate).then(async (response: AxiosResponse) => {
            modul.error = false;
            modul.loading = false;

            await store.dispatch('update_server');

            if (activate) {
                Toast.fire({
                    icon: 'success',
                    title: 'Modul activated successful'
                });
            } else {
                Toast.fire({
                    icon: 'success',
                    title: 'Modul deactivated successful'
                });
            }
            
        }).catch((error) => {
            modul.error = true;
            modul.loading = false;

            if (activate) {
                Toast.fire({
                    icon: 'error',
                    title: error.response.data.description
                });
            } else {
                Toast.fire({
                    icon: 'error',
                    title: error.response.data.description
                });
            }
        });
    }
  }
});
</script>
