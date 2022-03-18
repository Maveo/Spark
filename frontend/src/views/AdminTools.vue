<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Admin Tools</h2>
            <span class="text-gray4">Admins have fun!</span>
        </div>

        <div class="view-main-card">
            <div class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="mr-3">
                        <h5 class="mb-0">Nickname:</h5>
                    </div>
                    <form class="my-2 d-flex align-items-center flex-grow-1" @submit.prevent="set_nickname(nickname)">
                        <div class="mr-3 flex-grow-1 d-flex justify-content-end">
                            <input type="text" class="form-control form-control-sm" style="max-width: 200px;" placeholder="Nickname" v-model="nickname" required>
                        </div>
                        <button type="button" class="btn btn-dark btn-sm" style="height: 31px;" @click="set_nickname(null)">
                            <i class="fas fa-fw fa-undo-alt"></i>
                        </button>
                        <button class="btn btn-info btn-sm ml-2 text-nowrap" type="submit">
                            Send
                        </button>
                    </form>
                </div>
            </div>

            <div class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="mr-3">
                        <h5 class="mb-0">Audio:</h5>
                    </div>
                    <form class="my-2 d-flex align-items-center flex-grow-1" @submit.prevent="send_voice_audio()">
                        <select class="mr-2 form-control form-control-sm" v-model="selected_voice_channel" style="max-width: 180px;" required>
                            <option value="0" hidden>Loading channels...</option>
                            <option v-for="option in voice_channel_options" :key="option.id" :value="option.id">
                                {{ option.name}}
                            </option>
                        </select>
                        <div class="mr-3 flex-grow-1">
                            <div class="custom-file">
                                <input type="file" onchange="this.nextElementSibling.innerText=this.files[0].name;" class="custom-file-input" id="audioFile" ref="audioFile" required>
                                <label class="custom-file-label" for="audioFile">Choose file...</label>
                            </div>
                        </div>
                        <button class="btn btn-info btn-sm text-nowrap" type="submit">
                            Stream
                        </button>
                    </form>
                </div>
            </div>

            <div class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="mr-3">
                        <h5 class="mb-0">Invites:</h5>
                    </div>
                    <div class="my-2 d-flex align-items-center">
                        <button class="mr-2 btn btn-info btn-sm text-nowrap" @click="create_invite()">
                            Create Invite Link
                        </button>
                        <button class="btn btn-info btn-sm text-nowrap" @click="get_invites()">
                            Get Invite Links
                        </button>
                    </div>
                </div>
            </div>

            <div class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="mr-3">
                        <h5 class="mb-0">Send:</h5>
                    </div>
                    <form class="my-2 d-flex align-items-center flex-grow-1" @submit.prevent="send_msg_channel()">
                        <select class="mr-2 form-control form-control-sm" v-model="selected_send_channel" style="max-width: 180px;" required>
                            <option value="0" hidden>Loading channels...</option>
                            <option v-for="option in text_channel_options" :key="option.id" :value="option.id">
                                {{ option.name}}
                            </option>
                        </select>
                        <div class="mr-3 flex-grow-1">
                            <input type="text" class="form-control form-control-sm" placeholder="Message" v-model="send_message" required>
                        </div>
                        <button class="btn btn-info btn-sm text-nowrap" type="submit">
                            Send
                        </button>
                    </form>
                </div>
            </div>

            <div class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="mr-3">
                        <h5 class="mb-0">Watch:</h5>
                    </div>
                    <div class="my-2 d-flex align-items-center justify-content-end flex-grow-1">
                        <select @change="refresh_watch_channel(true)" class="mr-2 form-control form-control-sm" v-model="selected_watch_channel" style="max-width: 180px;" required>
                            <option value="0" hidden>Loading channels...</option>
                            <option v-for="option in text_channel_options" :key="option.id" :value="option.id">
                                {{ option.name}}
                            </option>
                        </select>
                        <a @click="refresh_watch_channel()" class="btn btn-nofocus text-white" data-toggle="collapse" data-target="#collapseWatch">
                            <i class="fas fa-fw fa-chevron-down"></i>
                            Click to watch
                        </a>
                    </div>
                </div>
                <div class="collapse" id="collapseWatch">
                    <div class="px-3 py-4">
                        <textarea disabled v-model="watch_content" class="w-100 bg-dark text-white p-3" style="border: none;" rows="10" spellcheck="false" ref="watchTextarea"></textarea>
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" id="autoRefresh" @change="set_auto_refresh()" v-model="watch_auto_refresh">
                            <label class="form-check-label" for="autoRefresh">Auto Refresh</label>
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

// eslint-disable-next-line @typescript-eslint/no-var-requires
let Swal = require('sweetalert2/src/sweetalert2.js').default;
import { AxiosResponse } from "axios";
import { Subject } from 'rxjs';

const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
});

const Toast2 = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timerProgressBar: true,
});

export default defineComponent({
  name: "Admin Tools",
  data() {
    return {
        selected_send_channel: '0',
        selected_watch_channel: '0',
        text_channel_options: [],
        selected_voice_channel: '0',
        voice_channel_options: [],
        send_message: '',
        watch_content: '',
        watch_auto_refresh: false,
        auto_refresh_intervall: undefined as number | undefined,
        nickname: '',
    }
  },
  created() {
      api.get_text_channels().then((response: AxiosResponse) => {
          this.text_channel_options = response.data.text_channels;
          this.selected_send_channel = (this.text_channel_options[0] as any).id;
          this.selected_watch_channel = this.selected_send_channel;
      }).catch((error) => {
          console.log(error);
      });

      api.get_voice_channels().then((response: AxiosResponse) => {
          this.voice_channel_options = response.data.voice_channels;
          this.selected_voice_channel = (this.voice_channel_options[0] as any).id;
      }).catch((error) => {
          console.log(error);
      });
  },
  unmounted() {
      if (this.auto_refresh_intervall) {
          clearInterval(this.auto_refresh_intervall);
      }
  },
  methods: {
    create_invite() {
        Swal.fire({
            title: 'Create Invite Link',
            html: `<h4>Options:</h4>
            <ul class="text-left">
                <li><p><strong>search_channel</strong>(str) &ndash; Search for a Textchannel for which this invite will be created.</p></li>
                <li><p><strong>max_age</strong>(int) &ndash; How long the invite should last in seconds. If it&rsquo;s 0 then the invite doesn&rsquo;t expire. Defaults to 0.</p></li>
                <li><p><strong>max_uses</strong>(int) &ndash; How many uses the invite could be used for. If it&rsquo;s 0 then there are unlimited uses. Defaults to 0.</p></li>
                <li><p><strong>temporary</strong>(bool) &ndash; Denotes that the invite grants temporary membership (i.e. they get kicked after they disconnect). Defaults to False.</p></li>
                <li><p><strong>unique</strong>(bool) &ndash; Indicates if a unique invite URL should be created. Defaults to True. If this is set to False then it will return a previously created invite.</p></li>
                <li><p><strong>reason</strong>(str) &ndash; The reason for creating this invite. Shows up on the audit log.</p></li>
            </ul>
            <h4>Example:</h4>
            {"search_cannel": "test", "max_age": 0, "max_uses": 0, "temporary": false, "unique": false, "reason": "Flo suckt"}`,
            input: 'text',
            inputAttributes: {
                autocapitalize: 'off'
            },
            showCancelButton: true,
            confirmButtonText: 'Create',
            showLoaderOnConfirm: true,
            preConfirm: (data: string) => {
                let data_obj = {};
                try {
                    if (data != '') data_obj = JSON.parse(data);
                } catch (error) {
                    Swal.showValidationMessage(
                        `Options invalid: ${error}`
                    );
                    return;
                }
                return api.create_invite_link(data_obj).then(response => {
                    return response;
                }).catch(error => {
                    Swal.showValidationMessage(
                        error.response.data.description
                    );
                });
            },
        }).then((result: any) => {
            if (result.isConfirmed) {
                Swal.fire({
                    title: 'Invite Link',
                    html: `<input type="text" onclick="event.target.select();event.target.setSelectionRange(0,99999);navigator.clipboard.writeText(event.target.value);" class="form-control" value="${result.value.data.invite_link.url}">`,
                });
            }
        });
        
    },
    get_invites() {
        api.get_invite_links().then((response: AxiosResponse) => {
            Swal.fire({
                title: 'Invite Links',
                grow: 'row',
                html: `<pre class="text-left bg-white">${JSON.stringify(response.data.invite_links, undefined, 2)}</pre>`,
            });
        }).catch((error) => {
            Swal.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
    },
    send_msg_channel() {
        Toast2.fire({
            title: 'Loading...',
            iconHtml: '<span class="spinner-border"></span>',
        });

        api.send_msg_channel(this.selected_send_channel, this.send_message).then(() => {
            this.send_message = '';
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
    set_auto_refresh() {
        if (this.watch_auto_refresh) {
            if (!this.auto_refresh_intervall) {
                this.auto_refresh_intervall = setInterval(() => this.refresh_watch_channel(true), 2000);
            }
        } else {
            clearInterval(this.auto_refresh_intervall);
            this.auto_refresh_intervall = undefined;
        }
    },
    refresh_watch_channel(refresh = false) {
        if (!refresh) {
            if (this.watch_content != '') {
                this.watch_auto_refresh = false;
                this.set_auto_refresh();
                return;
            }
            this.watch_auto_refresh = true;
            this.set_auto_refresh();
        }
        api.get_messages(this.selected_watch_channel, 100).then((response: AxiosResponse) => {
            this.watch_content = response.data.messages.reverse().map((e: any) => `${e.author.nick}: ${e.content}`).join('\n');
            const ref = this.$refs.watchTextarea as HTMLElement;
            this.$nextTick(() => {
                ref.scrollTop = ref.scrollHeight + 120;
            });
        }).catch((error) => {
            this.watch_auto_refresh = false;
            this.set_auto_refresh();
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
    },
    set_nickname(nickname: string | null) {
        Toast2.fire({
            title: 'Loading...',
            iconHtml: '<span class="spinner-border"></span>',
        });

        api.set_nickname(nickname).then(() => {
            this.nickname = '';
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
    send_voice_audio() {

        const loadingSubject = new Subject<number>();

        const Toast3 = Swal.mixin({
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
                        console.log(progress);
                        progressbar.style.width = '' + (progress * 100) + '%';
                        progressbar.style.transition = 'width 1s linear';
                    },
                });
            },
        });

        Toast3.fire({
            title: 'Loading...',
            iconHtml: '<span class="spinner-border"></span>',
        });

        api.send_voice_audio(this.selected_voice_channel, (this.$refs.audioFile as any).files[0], loadingSubject).then(() => {
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
