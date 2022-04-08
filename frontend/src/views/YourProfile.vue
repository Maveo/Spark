<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>{{ $filters.i18n('YOUR_PROFILE_TITLE') }}</h2>
            <span class="text-gray4">{{ $filters.i18n('YOUR_PROFILE_SUBTITLE') }}</span>
        </div>
        <div class="view-main-card py-4 px-3">
            <div class="p-sm-2">
                <div class="row mb-4">
                    <div class="col-12 col-xl-6">

                        <div class="d-flex">
                            <div class="d-none d-xl-block">
                                <img class="rounded-circle" :src="profile.member.avatar_url" style="max-width: 150px;">
                            </div>
                            <div class="ps-3 d-flex flex-column justify-content-between">
                                <div>
                                    <h2 class="mb-0">{{profile.member.nick}}</h2>
                                    <div class="text-gray4">{{profile.member.name}}</div>
                                    <h5>{{profile.member.top_role}}</h5>
                                </div>
                                <div v-if="selected_server.active_modules.includes('levelsystem')">
                                    <span class="text-gray3">Level:</span>
                                    <span style="font-size: 1.5em; padding-left: 0.25em;">{{profile.level}}</span>
                                </div>
                            </div>

                            <div class="d-block d-xl-none ms-auto">
                                <img class="rounded-circle" :src="profile.member.avatar_url" style="max-width: 150px;">
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-xl-6">
                        <div class="d-none d-xl-block vertical-divider"></div>
                        <table class="ms-3 ms-xl-0">
                            <tbody>
                                <tr>
                                    <td><h6 class="mb-0">{{ $filters.i18n('USER_ID') }}:</h6></td>
                                    <td class="text-muted ps-3">{{profile.member.id}}</td>
                                </tr>
                                <tr>
                                    <td><h6 class="mb-0">{{ $filters.i18n('DISCORD_TAG') }}:</h6></td>
                                    <td class="text-muted ps-3">#{{profile.member.tag}}</td>
                                </tr>
                                <tr>
                                    <td><h6 class="mb-0">{{ $filters.i18n('JOINED_AT') }}:</h6></td>
                                    <td class="text-muted ps-3">{{profile.joined_at}}</td>
                                </tr>
                                <tr>
                                    <td><h6 class="mb-0">{{ $filters.i18n('HYPESQUAD') }}:</h6></td>
                                    <td class="text-muted ps-3">{{profile.hype_squad}}</td>
                                </tr>
                                <tr>
                                    <td><h6 class="mb-0">{{ $filters.i18n('BOOSTING_SINCE') }}:</h6></td>
                                    <td class="text-muted ps-3">{{profile.boosting_since}}</td>
                                </tr>
                            </tbody>
                        </table>

                    </div>
                </div>

                <div v-if="selected_server.active_modules.includes('levelsystem')">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h6 class="text-gray4">{{ $filters.i18n('GAINED_XP_ORIGIN') }}</h6>
                        </div>
                        <div>
                            <h6 class="text-gray4">{{ $filters.i18n('TOTAL_XP_GAINED') }} <span class="text-white">{{profile.total_xp.toFixed(0)}}</span></h6>
                        </div>
                    </div>
                    <div class="progress" style="border-radius: 3rem; background-color: unset !important;">
                        <div class="progress-bar bg-gray2-important" role="progressbar" :style="{'width': '' + unknown_xp_percent + '%'}"></div>
                        <div class="progress-bar bg-purple" role="progressbar" :style="{'width': '' + text_msg_xp_percent + '%'}"></div>
                        <div class="progress-bar bg-blue" role="progressbar" :style="{'width': '' + voice_xp_percent + '%'}"></div>
                        <div class="progress-bar bg-cyan" role="progressbar" :style="{'width': '' + boost_xp_percent + '%'}"></div>
                    </div>

                    <div class="mx-4 row pt-2">
                        <div v-if="unknown_xp_percent > 0" class="col d-flex align-items-center">
                            <div class="xp-dot me-2 bg-gray2-important">
                            </div>
                            <span class="text-gray4 text-nowrap">{{ $filters.i18n('UNKNOWN_XP_SOURCE') }}</span>
                        </div>
                        <div v-if="text_msg_xp_percent > 0" class="col d-flex align-items-center">
                            <div class="xp-dot me-2 bg-purple">
                            </div>
                            <span class="text-gray4 text-nowrap">{{ $filters.i18n('TEXT_MESSAGES_XP_SOURCE') }}</span>
                        </div>
                        <div v-if="voice_xp_percent > 0" class="col d-flex align-items-center">
                            <div class="xp-dot me-2 bg-blue">
                            </div>
                            <span class="text-gray4 text-nowrap">{{ $filters.i18n('VOICE_ACTIVITY_XP_SOURCE') }}</span>
                        </div>
                        <div v-if="boost_xp_percent > 0" class="col d-flex align-items-center">
                            <div class="xp-dot me-2 bg-cyan">
                            </div>
                            <span class="text-gray4 text-nowrap">{{ $filters.i18n('XP_BOOST') }}</span>
                        </div>
                    </div>

                    <hr>

                    <div class="row" v-if="selected_server.active_modules.includes('boost') && selected_server.active_modules.includes('promo')">

                        <div class="col-12 col-xl-6">

                            <div class="text-field-dark d-flex flex-row mb-3 mt-1">
                                {{ $filters.i18n('BOOSTS_PROMO') }}
                                <div class="col d-flex justify-content-end" style="color: var(--green);">x{{profile.promo_boost_xp_multiplier}} {{ $filters.i18n('XP_BOOST') }}
                                </div>
                            </div>
                            <div v-for="boost in profile.promo_boosts_raw_data" :key="boost.name" class="ms-3 mb-2">
                                <div class="d-flex flex-row">
                                    <h5 class="col-8">{{boost.name}}</h5>
                                    <p class="col text-gray4 d-flex justify-content-end me-3">{{ $filters.i18n('DAYS_AND_HOURS', [boost.remaining_days, boost.remaining_hours]) }}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-xl-6">
                            <div class="d-none d-xl-block vertical-divider"></div>
                            <div class="text-field-dark d-flex flex-row mb-3 mt-1">
                                {{ $filters.i18n('BOOSTS_NORMAL') }}
                                <div class="col d-flex justify-content-end" style="color: var(--green);">
                                    x{{profile.boost_xp_multiplier}} {{ $filters.i18n('XP_BOOST') }}
                                </div>
                            </div>
                            <div v-for="boost in profile.boosts_raw_data" :key="boost.name" class="ms-3 mb-2">
                                <div class="d-flex flex-row">
                                    <h5 class="col-8">{{boost.name}}</h5>
                                    <p class="col text-gray4 d-flex justify-content-end me-3">{{ $filters.i18n('DAYS_AND_HOURS', [boost.remaining_days, boost.remaining_hours]) }}</p>
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
import { defineComponent } from "vue";
import store from '@/store'

export default defineComponent({
  name: "Your Profile",
  data() {
      return {
          selected_server: store.state.selected_server,
          profile: store.state.profile,
      };
  },
  computed: {
    unknown_xp_percent() {
        if (store.state.profile.total_xp == 0) return 100;
        return (store.state.profile.total_xp -
            (store.state.profile.text_msg_xp + store.state.profile.voice_xp + store.state.profile.boost_xp)) * 100
            / store.state.profile.total_xp;
    },
    text_msg_xp_percent() {
        if (store.state.profile.total_xp == 0) return 0;
        return store.state.profile.text_msg_xp * 100 / store.state.profile.total_xp;
    },
    voice_xp_percent() {
        if (store.state.profile.total_xp == 0) return 0;
        return store.state.profile.voice_xp * 100 / store.state.profile.total_xp;
    },
    boost_xp_percent() {
        if (store.state.profile.total_xp == 0) return 0;
        return store.state.profile.boost_xp * 100 / store.state.profile.total_xp;
    }
  },
});
</script>
