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

function get_ranking(offset: number | undefined, amount: number | undefined, style_wanted: boolean): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/ranking', {
        params: {
            'offset': offset,
            'amount': amount,
            'style_wanted': style_wanted ? true : undefined,
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

function get_rarities(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/rarities', {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token,
        }
    });
}

function edit_rarity(rarity: any): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/edit-rarity', {
        'rarity': rarity,
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

function remove_rarity(rarity_id: number): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/remove-rarity', {
        'rarity_id': rarity_id,
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

function set_rarity_order(rarity_order: any): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/set-rarity-order', {
        'rarity_order': rarity_order,
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


function get_item_action_options(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/item-action-options', {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token,
        }
    });
}

function get_item_types(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/item-types', {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token,
        }
    });
}

function remove_item_type(item_type_id: number): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/remove-item-type', {
        'item_type_id': item_type_id,
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

function edit_item_type(item_type: any): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/edit-item-type', {
        'item_type': item_type,
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

function get_wheelspin(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/get-wheelspin',
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function can_wheelspin(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/can-wheelspin',
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function get_wheelspin_admin(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/get-wheelspin-admin',
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function set_wheelspin(wheelspin: any): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/set-wheelspin', {
        'wheelspin': wheelspin,
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

function spin_wheel(): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/spin-wheel', {},
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function set_store(item_store: any): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/set-store', {
        store: item_store
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


function get_store(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/get-store',
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
        }
    });
}

function buy_offer(offer_id: number, amount: number): Promise<AxiosResponse> {
    return axios.post(process.env.VUE_APP_API_BASE_URL + '/buy-offer',
    {
        offer_id: offer_id,
        amount: amount,
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

function get_inventory(): Promise<AxiosResponse> {
    return axios.get(process.env.VUE_APP_API_BASE_URL + '/inventory',
    {
        params: {
            'guild_id': store.state.selected_server.id,
        },
        headers: {
            'Authorization': store.state.persistant.token
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
    change_emoji_image,
    get_rarities,
    edit_rarity,
    remove_rarity,
    set_rarity_order,
    get_item_action_options,
    get_item_types,
    remove_item_type,
    edit_item_type,
    can_wheelspin,
    get_wheelspin,
    get_wheelspin_admin,
    set_wheelspin,
    spin_wheel,
    set_store,
    get_store,
    buy_offer,
    get_inventory
};

export default api;