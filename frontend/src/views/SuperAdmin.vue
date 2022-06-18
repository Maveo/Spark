<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>{{ $filters.i18n('SUPER_ADMIN_TITLE') }}</h2>
            <span class="text-gray4">{{ $filters.i18n('SUPER_ADMIN_SUBTITLE') }}</span>
        </div>

        <div class="view-main-card">
            <div class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="me-3">
                        <h5 class="mb-0 text-nowrap">Status:</h5>
                    </div>
                    <form class="my-2 d-flex align-items-center flex-grow-1" @submit.prevent="set_presence(activity_name, activity_type, status_type)">
                        
                        <div class="me-3 flex-grow-1 d-flex justify-content-end">
                            <select class="me-2 form-select form-select-sm" v-model="activity_type" style="max-width: 180px;">
                                <option :value="0" >Playing</option>
                                <option :value="1">Streaming</option>
                                <option :value="2">Listening</option>
                                <option :value="3">Watching</option>
                                <option :value="5">Competing</option>
                            </select>
                            <select class="me-2 form-select form-select-sm" v-model="status_type" style="max-width: 180px;">
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

            <div v-if="selected_server.id" class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="me-3">
                        <h5 class="mb-0 text-nowrap">Change emoji:</h5>
                    </div>
                    <div class="my-2 d-flex align-items-center flex-grow-1">
                        <a @click="get_emojis()" class="btn btn-toggle btn-nofocus text-nowrap text-white collapsed me-2" data-bs-toggle="collapse" data-bs-target="#collapseEmojis" aria-expanded="false">
                            <i class="fas fa-fw toggle-icon"></i>
                            Show emojis
                        </a>
                        <input type="text" class="me-2 form-control form-control-sm" style="max-width: 100px;" placeholder="Emoji" v-model="emoji_change">
                        <div class="flex-grow-1">
                            <div class="input-group input-group-sm custom-file-button">
                                <input type="file" class="form-control form-control-sm" id="emojiFile" ref="emojiFile" :disabled="!emoji_change" @change="upload_emoji($event.target)" required>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="collapse" id="collapseEmojis">
                    <div class="px-3 py-4 d-flex flex-row flex-wrap">
                        <div v-for="emoji in emojis" :key="emoji.emoji">
                            <div class="row justify-content-center">
                                {{emoji.emoji}}
                            </div>
                            <div class="row justify-content-center">
                                <img style="width: auto; height: 50px;" :src="'data:image/png;base64, ' + emoji.base64">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import api from '@/services/api';
import store from '@/store';
import { Subject } from "rxjs";
import { AxiosResponse } from "axios";

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
        selected_server: store.state.selected_server,
        activity_name: '',
        activity_type: 0,
        status_type: 'online',
        emoji_change: '',
        emojis: []
    }
  },
  methods: {
    set_presence(activity_name: string | null = null,
                 activity_type: number | null = null,
                 status_type: string | null = null) {
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

        api.set_presence(activity_name, +activity_type, status_type).then(() => {
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
    },
    get_emojis(force = false) {
        if (!force && this.emojis.length > 0) {
            return;
        }
        api.get_emojis().then((response: AxiosResponse) => {
            this.emojis = response.data.emojis;
        }).catch((error) => {
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
    },
    upload_emoji(input: HTMLInputElement) {
        if (!input.files || input.files.length == 0 || input.files[0]['type'].split('/')[0] !== 'image' || input.files[0].size > 250000000 || !FileReader) {
            Toast.fire({
                icon: 'error',
                title: 'Something went wrong'
            });
            return;
        }
        const fileReader = new FileReader();
        fileReader.onload = (e) => {
            if (!e.target || !e.target.result) {
                Toast.fire({
                    icon: 'error',
                    title: 'Something went wrong'
                });
                return;
            }
            Swal.fire({
                title: `Emoji for ${this.emoji_change}`,
                text: `Do you want to upload this as the emoji for ${this.emoji_change}?`,
                imageUrl: fileReader.result,
                imageHeight: 200,
                showCancelButton: true,
                confirmButtonColor: "#198754",
                cancelButtonColor: "#dc3545",
                confirmButtonText: "Yes!",
                cancelButtonText: "No, abort mission!",
            }).then((reset: any) => {
                if (reset.isConfirmed) {

                    const loadingSubject = new Subject<number>();

                    const Toast2 = Swal.mixin({
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 100,
                        timerProgressBar: true,
                        didOpen: () => {
                            Swal.stopTimer();
                            const progressbar = Swal.getTimerProgressBar() as HTMLElement;
                            progressbar.style.width = '0';
                            
                            loadingSubject.subscribe({
                                next: (progress) => {
                                    progressbar.style.width = '' + (progress * 100) + '%';
                                    progressbar.style.transition = 'width 1s linear';
                                },
                            });
                        },
                    });

                    Toast2.fire({
                        title: 'Loading...',
                        iconHtml: '<span class="spinner-border"></span>',
                    });

                    api.change_emoji_image(this.emoji_change, (input as any).files[0], loadingSubject).then(() => {
                        this.get_emojis(true);
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
                input.value = '';
                this.emoji_change = '';
            });
        }
        fileReader.readAsDataURL(input.files[0]);
    }
  }
});
</script>
