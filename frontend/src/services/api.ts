import axios, { AxiosResponse, ResponseType } from 'axios';
import { Subject } from 'rxjs';
import store from '@/store';

function get_auth(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/get-auth');
}

function create_session(params: unknown): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/create-session', params);
}

function get_profile(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/profile', {
        params: {
            'guild_id': store.state.selected_server.id
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_guild(id: string): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/guild', {
        params: {
            'guild_id': id
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_guilds(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/guilds', {
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_settings(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/settings', {
        params: {
            'guild_id': store.state.selected_server.id
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_modules(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/modules', {
        params: {
            'guild_id': store.state.selected_server.id
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function set_module(modul: string, activate: boolean): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/set-module', {
        'module': modul,
        'activate': activate
    },
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_promo_code(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/promo', {
        params: {
            'guild_id': store.state.selected_server.id
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function boost_user(username: string): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/boost', {
        'username': username
    },
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function redeem_promo_code(promo_code: string): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/redeem', {
        'promo_code': promo_code
    },
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_ranking(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/ranking', {
        params: {
            'guild_id': store.state.selected_server.id
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function reset_setting(key: string): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/reset-setting', {
        'key': key
    },
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function set_setting(key: string, value: any): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/set-setting', {
        'key': key,
        'value': value,
    },
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function preview_call(preview_target: string, preview: any, responseType: ResponseType | undefined = undefined): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + `/${preview_target}`, {
        'preview': preview,
    },
    {
        responseType: responseType,
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function create_invite_link(options: any): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + `/invite-link`,
    options,
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_invite_links(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + `/invite-links`,
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_text_channels(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + `/text-channels`,
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_voice_channels(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + `/voice-channels`,
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function send_msg_channel(channel_id: string, message: string): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/send-message', {
        'channel_id': channel_id,
        'message': message,
    },
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_messages(channel_id: string, limit: number): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/messages', 
    {
        params: {
            'guild_id': store.state.selected_server.id,
            'channel_id': channel_id,
            'limit': limit,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function set_nickname(nickname: string | null): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/nickname', {
        'nickname': nickname,
    },
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function set_presence(activity_name: string | null, activity_type: number | null, status_type: string | null): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/presence', {
        'activity_name': activity_name,
        'activity_type': activity_type,
        'status_type': status_type,
    },
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function send_voice_audio(voice_channel: string, audio_file: string | Blob, progressSubject: Subject<number> = new Subject()): Promise<AxiosResponse> {
    const formData = new FormData();
    formData.append('audio_file', audio_file);
    formData.append('voice_channel', voice_channel);


    return axios.post(process.env.VUE_APP_API_BASE_URL + '/audio', formData, {
        onUploadProgress: progressEvent => progressSubject.next(progressEvent.loaded / progressEvent.total),
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': store.state.persistant.token,
        }
    });
}

function change_emoji_image(emoji: string, emoji_file: string | Blob, progressSubject: Subject<number> = new Subject()): Promise<AxiosResponse> {
    const formData = new FormData();
    formData.append('emoji', emoji);
    formData.append('emoji_file', emoji_file);

    return axios.post(process.env.VUE_APP_API_BASE_URL + '/change-emoji', formData, {
        onUploadProgress: progressEvent => progressSubject.next(progressEvent.loaded / progressEvent.total),
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': store.state.persistant.token,
        }
    });
}

function get_emojis(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/emojis', {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token,
        }
    });
}

const api = {
    get_auth,
    create_session,
    get_profile,
    get_guild,
    get_guilds,
    get_settings,
    get_modules,
    set_module,
    get_promo_code,
    boost_user,
    redeem_promo_code,
    get_ranking,
    reset_setting,
    set_setting,
    preview_call,
    create_invite_link,
    get_invite_links,
    get_text_channels,
    get_voice_channels,
    send_msg_channel,
    get_messages,
    set_nickname,
    set_presence,
    send_voice_audio,
    get_emojis,
    change_emoji_image
};

export default api;