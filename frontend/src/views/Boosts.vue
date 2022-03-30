<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Boosts</h2>
            <span class="text-gray4">Enter or create a Promo Code or manage your regular boosts</span>
        </div>

        <div class="view-main-card p-4">
            <div class="py-1 py-md-3 px-md-3 px-lg-4">
                <div class="row">

                    <div v-if="selected_server.active_modules.includes('promo')" class="col-xxl-4 mb-3">
                        <h4 class="mb-3">Promotion Code</h4>

                        <div style="position: relative;">

                            <div v-if="!profile.can_redeem_promo_code" class="spark-rounded d-flex justify-content-center align-items-center" style="z-index: 2; position: absolute; width: 100%; height: 100%; background-color: #20222aee; top: 0; bottom: 0; left: 0; right: 0;">
                                <div class="spark-rounded text-center bg-gray2 p-3" style="box-shadow: 0 .3rem 1rem rgba(0,0,0,.5) !important;">
                                    <i class="fas fa-fw fa-lock" style="font-size: 2rem;"></i>
                                </div>
                            </div>

                            <div class="bg-gray2 p-3 spark-rounded mb-3">

                                <div class="mb-3">
                                    <div class="font-weight-bold mb-2">
                                        Enter another members Promo Code to get:
                                    </div>

                                    <div>
                                        <i class="fas fa-fw fa-arrow-up" style="color: var(--green);"></i>
                                        Rankup to Level {{profile.promo_user_set_level}}
                                    </div>
                                </div>

                                <div class="d-flex">
                                    <form @submit.prevent="redeem_promo_code()" class="d-flex">
                                        <div class="me-2">   
                                            <div class="input-group">
                                                <input v-model.trim="redeem_code" type="text" class="form-control form-control-sm font-weight-bold" style="max-width: 150px;" placeholder="Promo Code" required>
                                            </div>
                                        </div>
                                        <div>
                                            <button type="submit" class="btn btn-success btn-sm font-weight-bold">
                                                Redeem
                                            </button>
                                        </div>
                                    </form>
                                </div>
                                <div v-if="redeem_code_error_msg" class="text-danger" style="font-size: 0.9rem;">
                                    {{redeem_code_error_msg}}
                                </div>

                            </div>

                        </div>

                        <div class="bg-gray2 p-3 spark-rounded">

                            <div class="mb-3">

                                <div class="font-weight-bold mb-2">
                                    Create your own Promo Code and send it to a new member and you get:
                                </div>

                                <div>
                                    <i class="fas fa-fw fa-plus"></i>
                                    <span style="color: var(--green); font-weight: bold;" class="ps-1">x{{profile.promo_boost_xp_multiplier}}</span>
                                    XP-Multiplier
                                </div>

                            </div>

                            <div class="d-flex">
                                <div>
                                    <button @click.prevent="get_promo_code()" class="btn btn-info btn-sm font-weight-bold">
                                        New Code
                                    </button>
                                </div>
                                <div class="ms-2">
                                    <span v-if="loading_promo_code" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                    <div v-if="!loading_promo_code && promo_code" class="input-group">
                                        <input :class="{'bg-grey2': true}" type="text" class="form-control form-control-sm font-weight-bold" :value="promo_code" disabled>
                                    </div>
                                </div>
                            </div>
                            <div class="text-gray4 font-weight-bold" style="font-size: 0.75rem;">Valid for {{profile.promo_code_expires_hours}} Hrs.</div>

                        </div>

                    </div>

                    <div class="col-xxl-8">
                        <div v-if="selected_server.active_modules.includes('promo')" class="d-none d-xxl-block vertical-divider"></div>
                        <h4 class="mb-3">Boosts</h4>

                        <div class="row">
                            <div v-if="selected_server.active_modules.includes('boost')" class="col-lg-5 mb-3">

                                <div class="bg-gray2 p-3 spark-rounded">
                                
                                    <div class="mb-3">

                                        <div class="font-weight-bold">
                                            Boost another member:
                                        </div>

                                        <div>
                                            Give a
                                            <span style="color: var(--green); font-weight: bold;">x{{profile.boost_xp_multiplier}}</span>
                                            XP-Multiplier
                                        </div>

                                    </div>

                                    <form class="row" @submit.prevent="boost_user()">
                                        <div class="col mb-2">   
                                            <div class="input-group">
                                                <input v-model.trim="boost_username" @input="boost_username_change" :class="{'is-invalid': !!boost_error_msg}" type="text" class="form-control form-control-sm font-weight-bold" style="width: 150px;" placeholder="Username" :disabled="profile.boosting" required>
                                            </div>
                                        </div>
                                        <div class="col">
                                            <button type="submit" class="btn btn-success btn-sm w-100 font-weight-bold" :disabled="profile.boosting">
                                                Boost
                                            </button>
                                        </div>
                                    </form>
                                    <div v-if="boost_error_msg" class="text-danger" style="font-size: 0.9rem;">
                                        {{boost_error_msg}}
                                    </div>
                                    <div v-if="profile.boosting" class="text-gray4 font-weight-bold" style="font-size: 0.9rem;">
                                        Boost again in {{profile.boosting_remaining_days}} Days and {{profile.boosting_remaining_hours}} Hours
                                    </div>

                                    <div v-if="profile.boosting" class="mt-4">
                                        <div class="font-weight-bold mb-2">
                                            Currently boosting:
                                        </div>
                                        <div class="bg-gray1 spark-rounded p-2">
                                            {{profile.boosting_name}}
                                        </div>
                                    </div>

                                </div>

                            </div>
                            <div class="col-lg-7">

                                <div v-if="selected_server.active_modules.includes('boost')" class="mb-4">

                                    <div class="text-field-dark d-flex flex-row mb-3 mt-1">
                                        Normal Boosts
                                        <div class="col d-flex justify-content-end" style="color: var(--green);">
                                            x{{profile.boost_xp_multiplier}}&nbsp;<span class="d-none d-md-flex d-lg-none d-xl-flex">XP-Boost</span>
                                        </div>
                                    </div>
                                    <div v-for="boost in profile.boosts_raw_data" :key="boost.name" class="ms-3 mb-2">
                                        <div class="d-flex flex-row">
                                            <h5 class="col-8">{{boost.name}}</h5>
                                            <p class="col text-gray4 d-flex justify-content-end me-3">{{boost.remaining_days}} Days and {{boost.remaining_hours}} Hours</p>
                                        </div>
                                    </div>
                                </div>

                                <div v-if="selected_server.active_modules.includes('promo')">
                                    <div class="text-field-dark d-flex flex-row mb-3 mt-1">
                                        Promo Boosts
                                        <div class="col d-flex justify-content-end" style="color: var(--green);">
                                            x{{profile.promo_boost_xp_multiplier}}&nbsp;<span class="d-none d-md-flex d-lg-none d-xl-flex">XP-Boost</span>
                                        </div>
                                    </div>
                                    <div v-for="boost in profile.promo_boosts_raw_data" :key="boost.name" class="ms-3 mb-2">
                                        <div class="d-flex flex-row">
                                            <h5 class="col-8">{{boost.name}}</h5>
                                            <p class="col text-gray4 d-flex justify-content-end me-3">{{boost.remaining_days}} Days and {{boost.remaining_hours}} Hours</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                    </div>


                </div>
            </div>

        </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import store from '@/store';
import api from '@/services/api';
import { AxiosResponse } from 'axios';

export default defineComponent({
  name: 'Boosts',
  data() {
      return {
        selected_server: store.state.selected_server,
        profile: store.state.profile,
        boost_username: '',
        boost_error_msg: '',
        redeem_code: '',
        redeem_code_error_msg: '',
        promo_code: '',
        loading_promo_code: false
      }
  },
  methods: {
    get_promo_code() {
        this.loading_promo_code = true;
        api.get_promo_code().then((response: AxiosResponse) => {
            console.log(response.data);
            this.promo_code = response.data.promo_code;
            this.loading_promo_code = false;
        }).catch((e) => {
            console.log(e);
        });
    },
    boost_user() {
        api.boost_user(this.boost_username).then(async (response: AxiosResponse) => {
            console.log(response.data);
            await store.dispatch("update_server");
        }).catch((e) => {
            if (e.response && e.response.status == 400) {
                console.log(e.response.data);
                this.boost_error_msg = e.response.data.description;
            }
        });
    },
    redeem_promo_code() {
        api.redeem_promo_code(this.redeem_code).then(async (response: AxiosResponse) => {
            console.log(response.data);
            await store.dispatch("update_server");
        }).catch((e) => {
            if (e.response && e.response.status == 400) {
                console.log(e.response.data);
                this.redeem_code_error_msg = e.response.data.description;
            }
        });
    },
    boost_username_change() {
        this.boost_error_msg = '';
    },
  }
});
</script>
