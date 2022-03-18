<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Server Settings</h2>
            <span class="text-gray4">Edit default values or Sparks settings</span>
        </div>

        <div class="view-main-card">
            
            <div class="w-100">
                
                <div class="row mb-4">
                    <div class="col-6">
                        <div class="d-flex">
                            <div class="flex-grow-1">
                                <input type="text" class="form-control" v-model="search" placeholder="Search">
                            </div>
                            <button class="btn text-white mr-2" style="pointer-events: none;">
                                <i class="fas fa-fw fa-search"></i>
                            </button>
                            <button :disabled="loading" class="btn btn-info mr-2" @click="import_settings()">
                                Import Settings
                            </button>
                            <button :disabled="loading" class="btn btn-info mr-2" @click="export_settings()">
                                Export Settings
                            </button>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="d-flex w-100 justify-content-center">
                            <div>
                                <button v-bind:class="{'btn-secondary': selected_filter == -1}" class="btn dark-hover text-white mr-2" @click="select_all_filter()">
                                    All
                                </button>
                                <button v-for="(categorie, index) in categories" :key="index" v-bind:class="{'btn-secondary': selected_filter == index}" class="btn dark-hover text-white mr-2" @click="select_filter(index, categorie)">
                                    {{categorie}}
                                </button>
                                <button v-bind:class="{'btn-secondary': selected_filter == -2}" class="btn dark-hover text-white mr-2" @click="select_misc_filter()">
                                    Misc.
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="!loading">
                    <div v-for="(setting, key, index) in searched_settings()" :key="key" class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                        <template v-if="setting.type == 'list'">
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="mr-3">
                                    <h5 class="mb-0">{{key}}</h5>
                                    <div class="text-gray4">{{setting.description}}</div>
                                </div>
                                <div class="d-flex align-items-center">
                                    <div class="mr-3">
                                        <a href="#" class="btn btn-nofocus text-white text-nowrap" data-toggle="collapse" :data-target="'#collapseSetting' + index">
                                            <i class="fas fa-fw fa-chevron-down"></i>
                                            Click to edit list
                                        </a>
                                    </div>
                                    <template v-if="setting.loading">
                                        <span class="spinner-border" style="width: 1.5rem; height: 1.5rem; margin-left: 74px;" role="status" aria-hidden="true"></span>
                                    </template>
                                    <template v-else>
                                        <i v-if="setting.error" class="fas fa-exclamation-circle text-danger"></i>
                                        <button class="ml-2 btn btn-dark btn-sm" style="height: 31px;" @click="reset_setting(key)">
                                        <i class="fas fa-fw fa-undo-alt"></i>
                                        </button>
                                        <button class="ml-2 btn btn-success btn-sm" style="height: 31px;" @click="save_setting(key, setting.value)">
                                            Save
                                        </button>
                                    </template>
                                </div>
                            </div>
                            <div class="collapse" :id="'collapseSetting' + index">
                                <div class="mt-2 px-3 py-4 d-flex justify-content-center">
                                    <div style="width: 100%;">
                                        <div v-for="(value, index) in setting.value" :key="index">
                                            <div class="d-flex justify-content-center mb-2">
                                                <input :disabled="setting.loading" type="text" class="form-control form-control-sm" v-model="setting.value[index]">
                                                <button :disabled="setting.loading" class="btn btn-sm btn-danger ml-2" @click="setting.value.splice(index, 1)">
                                                    <i class="fas fa-fw fa-trash"></i>
                                                </button>
                                            </div>
                                        </div>
                                        <button :disabled="setting.loading" class="w-100 btn btn-dark btn-sm" @click="setting.value.push('')">
                                            <i class="fas fa-fw fa-plus"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else-if="setting.type == 'text'">
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="mr-3">
                                    <h5 class="mb-0">{{key}}</h5>
                                    <div class="text-gray4">{{setting.description}}</div>
                                </div>
                                <div class="d-flex align-items-center">
                                    <div class="mr-3">
                                        <a @click="refresh_preview(setting, false)" class="btn btn-nofocus text-white" data-toggle="collapse" :data-target="'#collapseSetting' + index">
                                            <i class="fas fa-fw fa-chevron-down"></i>
                                            Click to edit text
                                        </a>
                                    </div>
                                    <template v-if="setting.loading">
                                        <span class="spinner-border" style="width: 1.5rem; height: 1.5rem; margin-left: 74px;" role="status" aria-hidden="true"></span>
                                    </template>
                                    <template v-else>
                                        <i v-if="setting.error" class="fas fa-exclamation-circle text-danger"></i>
                                        <button class="ml-2 btn btn-dark btn-sm" style="height: 31px;" @click="reset_setting(key)">
                                        <i class="fas fa-fw fa-undo-alt"></i>
                                        </button>
                                        <button class="ml-2 btn btn-success btn-sm" style="height: 31px;" @click="save_setting(key, setting.value)">
                                            Save
                                        </button>
                                    </template>
                                </div>
                            </div>
                            <div class="collapse" :id="'collapseSetting' + index">
                                <div class="mt-2 px-3 py-4">
                                    <textarea :disabled="setting.loading" v-bind:class="{'is-invalid': setting.error}" class="w-100 bg-dark text-white p-3" style="border: none;" rows="10" spellcheck="false" v-model="setting.value"></textarea>
                                    <div v-if="setting.preview_call" class="d-flex justify-content-center">
                                        <button v-if="!setting.preview_loading" class="btn btn-info" @click="refresh_preview(setting)">
                                            Preview
                                        </button>
                                        <span v-else class="spinner-border"></span>
                                    </div>
                                    <div v-if="setting.preview_result" class="d-flex justify-content-center mt-2">
                                        <img class="mw-100" :src="setting.preview_result">
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else-if="setting.type == 'bool'">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h5 class="mb-0">{{key}}</h5>
                                    <div class="text-gray4">{{setting.description}}</div>
                                </div>
                                <div class="d-flex align-items-center">
                                    <div class="mr-3">
                                        <button :disabled="setting.loading" v-bind:class="{'btn-dark': !setting.value}" class="ml-2 btn btn-success btn-sm" style="height: 31px;" @click="setting.value = true">
                                            <i class="fas fa-fw fa-check"></i>
                                        </button>
                                        <button :disabled="setting.loading" v-bind:class="{'btn-dark': setting.value}" class="ml-2 btn btn-danger btn-sm" style="height: 31px;" @click="setting.value = false">
                                            <i class="fas fa-fw fa-times"></i>
                                        </button>
                                    </div>
                                    <template v-if="setting.loading">
                                        <span class="spinner-border" style="width: 1.5rem; height: 1.5rem; margin-left: 74px;" role="status" aria-hidden="true"></span>
                                    </template>
                                    <template v-else>
                                        <i v-if="setting.error" class="fas fa-exclamation-circle text-danger"></i>
                                        <button class="ml-2 btn btn-dark btn-sm" style="height: 31px;" @click="reset_setting(key)">
                                        <i class="fas fa-fw fa-undo-alt"></i>
                                        </button>
                                        <button class="ml-2 btn btn-success btn-sm" style="height: 31px;" @click="save_setting(key, setting.value)">
                                            Save
                                        </button>
                                    </template>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="mr-3">
                                    <h5 class="mb-0">{{key}}</h5>
                                    <div class="text-gray4">{{setting.description}}</div>
                                </div>
                                <div class="d-flex align-items-center">
                                    <div class="mr-3">
                                        <input :disabled="setting.loading" v-bind:class="{'is-invalid': setting.error}" :type="(setting.type == 'int' || setting.type == 'float' ? 'number' : 'text')" class="form-control form-control-sm" placeholder="" v-model="setting.value" style="width: 300px;">
                                    </div>
                                    <template v-if="setting.loading">
                                        <span class="spinner-border" style="width: 1.5rem; height: 1.5rem; margin-left: 74px;" role="status" aria-hidden="true"></span>
                                    </template>
                                    <template v-else>
                                        <i v-if="setting.error" class="fas fa-exclamation-circle text-danger"></i>
                                        <button class="ml-2 btn btn-dark btn-sm" style="height: 31px;" @click="reset_setting(key)">
                                        <i class="fas fa-fw fa-undo-alt"></i>
                                        </button>
                                        <button class="ml-2 btn btn-success btn-sm" style="height: 31px;" @click="save_setting(key, setting.value)">
                                            Save
                                        </button>
                                    </template>
                                </div>
                            </div>
                        </template>
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
import { Subject } from 'rxjs';
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
  name: "Server Settings",
  data() {
    return {
        loading: true,
        categories: [],
        settings: {},
        shown_settings: {},
        selected_filter: -1,
        search: '',
    }
  },
  created() {
      this.refresh_settings();
  },
  methods: {
    refresh_settings() {
        this.settings = {};
        this.shown_settings = {};
        api.get_settings().then((response: AxiosResponse) => {
            console.log(response.data);
            this.categories = response.data.categories;
            this.settings = response.data.settings;
            this.select_all_filter();
            this.loading = false;
        });
    },
    count_loading_settings(): number {
        return Object.values<any>(this.settings).reduce((l, r) => l + (r.loading ? 1 : 0), 0);
    },
    reset_setting(key: string) {
        Swal.fire({
            title: "Are you sure?",
            text: `Do you really, really want to reset the ${key} setting?`,
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            confirmButtonText: "Yes, yeet it!",
            cancelButtonText: "No, cancel!",
        }).then((reset: any) => {
            if (reset.isConfirmed) {
                console.log('resetting', key);
                (this.settings as any)[key].loading = true;
                api.reset_setting(key).then((response: AxiosResponse) => {
                    (this.settings as any)[key].value = response.data.value;
                    (this.settings as any)[key].error = false;
                    (this.settings as any)[key].loading = false;

                    this.refresh_preview((this.settings as any)[key]);

                    store.commit('update_profile');

                    Toast.fire({
                        icon: 'success',
                        title: 'Reset successfull'
                    });
                });
            }
        });
    },
    save_setting(key: string, value: any, show_toast = true, refresh_preview = true, subject: Subject<boolean> | null = null, update_profile = true) {
        (this.settings as any)[key].loading = true;
        api.set_setting(key, value).then((response: AxiosResponse) => {
            (this.settings as any)[key].value = response.data.value;
            (this.settings as any)[key].error = false;
            (this.settings as any)[key].loading = false;

            if (refresh_preview) {
                this.refresh_preview((this.settings as any)[key]);
            } else {
                delete (this.settings as any)[key].preview_result;
            }

            if (subject !== null) {
                subject.next(true);
            }

            if (update_profile) {
                store.commit('update_profile');
            }

            if (show_toast) {
                Toast.fire({
                    icon: 'success',
                    title: 'Saved successfull'
                });
            }
        }).catch((e) => {
            console.log(e);
            (this.settings as any)[key].error = true;
            (this.settings as any)[key].loading = false;

            if (subject !== null) {
                subject.next(false);
            }
            if (show_toast) {
                Toast.fire({
                    icon: 'error',
                    title: 'Value invalid'
                });
            }
        });
    },
    select_all_filter() {
        this.selected_filter = -1;
        this.shown_settings = this.settings;
    },
    select_misc_filter() {
        this.selected_filter = -2;
        this.shown_settings = Object.fromEntries(Object.entries(this.settings).filter(
                ([key, value]) => (value as any).categories.length == 0)
        );
    },
    select_filter(index: number, categorie: string) {
        this.selected_filter = index;
        this.shown_settings = Object.fromEntries(Object.entries(this.settings).filter(
                ([key, value]) => (value as any).categories.includes(categorie))
        );
    },
    searched_settings() {
        const lower = this.search.toLowerCase();
        return Object.fromEntries(Object.entries(this.shown_settings).filter(
                ([key, value]) => 
                    key.toLowerCase().includes(lower) ||
                    (value as any).description.toLowerCase().includes(lower) || 
                    String((value as any).value).toLowerCase().includes(lower)
                )
        );
    },
    download(content: string, fileName: string) {
        const a = document.createElement('a');
        const file = new Blob([content], {type: 'text/plain'});
        a.href = URL.createObjectURL(file);
        a.download = fileName;
        a.click();
    },
    export_settings() {
        const filename = `spark_settings_${store.state.selected_server.id}.json`;
        this.download(
            JSON.stringify(Object.fromEntries(Object.entries(this.settings).map(
                ([key, value]) => [key, (value as any).value]
            ))),
            filename
        );
        Toast.fire({
            icon: 'success',
            title: `Saved to file`
        });
    },
    import_settings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.style.display = 'none';
        document.body.appendChild(input);
        input.onchange = () => {
            if (!input.files || input.files.length == 0 || input.files[0].size > 250000000) {
                Toast.fire({
                    icon: 'error',
                    title: 'Something went wrong'
                });
                return;
            }
            this.loading = true;

            const loadingSubject = new Subject<boolean>();

            let updateCount = 0;

            const Toast2 = Swal.mixin({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 100,
                timerProgressBar: true,
                didOpen: () => {
                    Swal.stopTimer();
                    const progressbar = Swal.getTimerProgressBar() as HTMLElement;
                    const title = Swal.getTitle() as HTMLElement;
                    progressbar.style.width = '0';

                    let errorCount = 0;
                    
                    loadingSubject.subscribe({
                        next: (correct) => {
                            if (!correct) errorCount++;
                            const leftLoading = this.count_loading_settings();
                            if (leftLoading == 0) {
                                if (errorCount > 0) {
                                    Toast.fire({
                                        icon: 'error',
                                        title: `${errorCount} errors occured while importing`
                                    });
                                } else {
                                    Toast.fire({
                                        icon: 'success',
                                        title: 'Settings imported'
                                    });
                                }
                            } else {
                                title.innerText = `Importing (${updateCount - leftLoading} / ${updateCount}) ...`;
                                progressbar.style.width = '' + (100-(leftLoading*100/updateCount)) + '%';
                                progressbar.style.transition = 'width 1s linear';
                            }
                        },
                    });
                },
            });

            Toast2.fire({
                title: 'Importing...',
                iconHtml: '<span class="spinner-border"></span>',
            });

            const file = input.files[0];
            const fileReader = new FileReader();
            fileReader.onload = (e) => {
                if (!e.target || !e.target.result) {
                    Toast.fire({
                        icon: 'error',
                        title: 'Something went wrong'
                    });
                    return;
                }
                const content = e.target.result as string;
                try {
                    Object.entries(JSON.parse(content)).forEach(
                        ([key, value]) => {
                            if (key in this.settings) {
                                (this.settings as any)[key].value = value;
                                this.save_setting(key, value, false, false, loadingSubject, false);
                                updateCount++;
                            } else {
                                console.log('unknown key', key);
                            }                            
                        }
                    );
                } catch {
                    Toast.fire({
                        icon: 'error',
                        title: 'Something went wrong'
                    });
                }
                this.loading = false;                
            };
            fileReader.readAsText(file);
        };
        input.click();
    },
    refresh_preview(setting: any, refresh = true) {
        if (!('preview_call' in setting) ||  typeof setting.preview_call != 'string') {
            console.log('unknown', setting.preview_call);
            return;
        }
        if (refresh == false && 'preview_result' in setting) {
            return;
        }
        if (setting.last_value == setting.value) {
            return;
        }
        setting.last_value = setting.value;
        setting.preview_loading = true;
        api.preview_call(setting.preview_call, setting.value, 'blob').then((response: AxiosResponse) => {

            const reader = new FileReader();
            reader.onloadend = () => {
                setting.preview_result = reader.result;
                setting.error = false;
                setting.preview_loading = false;
            }
            reader.readAsDataURL(response.data);

        }).catch((e) => {
            console.log(e);
            setting.error = true;
            setting.preview_loading = false;
        });
    }
  }
});
</script>
