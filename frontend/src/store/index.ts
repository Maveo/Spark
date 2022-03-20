import { createStore } from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import router from '@/router';
import api from '@/services/api';
import { AxiosError, AxiosResponse } from 'axios';
import { ProfileModel } from '@/models/profile.model';
import { ServerModel } from '@/models/server.model';


function update_profile(state: any) {
    api.get_profile().then((response: AxiosResponse) => {
        state.profile.assign(response.data);
        state.global_loading = false;

    }).catch((e: AxiosError) => {
        if (e.response) {
            console.log(e.response);
        }
        state.global_loading = false;
        state.persistant.token = '';
        router.push('/login');
    });
}

function update_server(state: any, id: string) {
    api.get_guild(id).then((response: AxiosResponse) => {

        state.selected_server.assign(response.data);
        update_profile(state);
    }).catch((e: AxiosError) => {
        if (e.response) {
            console.log(e.response);
        }
        state.global_loading = false;
        state.persistant.token = '';
        router.push('/login');
    });
}


export default createStore({
    state: {
        persistant: {
            token: '',
            wanted_redirect: '',
        },
        global_loading: false,
        selected_server: new ServerModel(),
        profile: new ProfileModel()
    },
    mutations: {
        set_redirect(state, redirect: string) {
            state.persistant.wanted_redirect = redirect;
        },
        login(state, token: string) {
            state.persistant.token = token;
        },
        logout(state) {
            state.persistant.token = '';
            state.global_loading = false;
        },
        update_profile(state) {
            update_profile(state);
        },
        update_server(state) {
            update_server(state, state.selected_server.id);
        },
        choose_server(state, id: string) {
            state.global_loading = true;
            update_server(state, id);
        },
    },
    plugins: [createPersistedState({
        paths: ['persistant']
      })]
})
