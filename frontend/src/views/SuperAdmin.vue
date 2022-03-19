<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Super Admin</h2>
            <span class="text-gray4">You are Super!</span>
        </div>

        <div class="view-main-card">
            <div class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="me-3">
                        <h5 class="mb-0">Status:</h5>
                    </div>
                    <form class="my-2 d-flex align-items-center flex-grow-1" @submit.prevent="set_presence(activity_name, activity_type, status_type)">
                        
                        <div class="me-3 flex-grow-1 d-flex justify-content-end">
                            <select class="me-2 form-control form-control-sm" v-model="activity_type" style="max-width: 180px;">
                                <option :value="0" >Playing</option>
                                <option :value="1">Streaming</option>
                                <option :value="2">Listening</option>
                                <option :value="3">Watching</option>
                                <option :value="5">Competing</option>
                            </select>
                            <select class="me-2 form-control form-control-sm" v-model="status_type" style="max-width: 180px;">
                                <option :value="'online'" >Online</option>
                                <option :value="'offline'">Offline</option>
                                <option :value="'idle'">Idle</option>
                                <option :value="'dnd'">Do not disturb</option>
                                <option :value="'invisible'">Invisible</option>
                            </select>
                            <input type="text" class="form-control form-control-sm" style="max-width: 200px;" placeholder="Status" v-model="activity_name">
                        </div>
                        <button type="button" class="btn btn-dark btn-sm" style="height: 31px;" @click="set_presence()">
                            <i class="fas fa-fw fa-undo-alt"></i>
                        </button>
                        <button class="btn btn-info btn-sm ms-2 text-nowrap" type="submit">
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import api from '@/services/api';

// eslint-disable-next-line @typescript-eslint/no-var-requires
let Swal = require('sweetalert2/src/sweetalert2.js').default;

const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
});

export default defineComponent({
  name: "Super Admin",
  data() {
    return {
        activity_name: '',
        activity_type: 0,
        status_type: 'online'
    }
  },
  methods: {
      set_presence(activity_name: string | null = null, activity_type: number | null = null, status_type: string | null = null) {
        const Toast2 = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timerProgressBar: true,
        });

        Toast2.fire({
            title: 'Loading...',
            iconHtml: '<span class="spinner-border"></span>',
        });

        api.set_presence(activity_name, activity_type, status_type).then(() => {
            Toast.fire({
                icon: 'success',
                text: 'Successfull',
            });
        }).catch((error) => {
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
    }
  }
});
</script>
