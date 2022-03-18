<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Your Profile</h2>
            <span class="text-gray4">View general information of your Server Account</span>
        </div>
        <div class="view-main-card p-4">
            
            <div class="row mb-4">
                <div class="col-12 col-xl-6">
                    
                    <div class="d-flex">
                        <div class="d-none d-xl-block">
                            <img class="rounded-circle" :src="profile.member.avatar_url" style="max-width: 150px;">
                        </div>
                        <div class="pl-3 d-flex flex-column justify-content-between">
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

                        <div class="d-block d-xl-none ml-auto">
                            <img class="rounded-circle" :src="profile.member.avatar_url" style="max-width: 150px;">
                        </div>
                    </div>
                </div>
                <div class="col-12 col-xl-6">
                    <div class="d-none d-xl-block vertical-divider"></div>
                    <table class="ml-3 ml-xl-0">
                        <tbody>
                            <tr>
                                <td><h6 class="mb-0">User-ID:</h6></td>
                                <td class="text-muted pl-3">{{profile.member.id}}</td>
                            </tr>
                            <tr>
                                <td><h6 class="mb-0">Discord Tag:</h6></td>
                                <td class="text-muted pl-3">#{{profile.member.tag}}</td>
                            </tr>
                            <tr>
                                <td><h6 class="mb-0">Joined At:</h6></td>
                                <td class="text-muted pl-3">{{profile.joined_at}}</td>
                            </tr>
                            <tr>
                                <td><h6 class="mb-0">Hypesquad:</h6></td>
                                <td class="text-muted pl-3">{{profile.hype_squad}}</td>
                            </tr>
                            <tr>
                                <td><h6 class="mb-0">Boosting since:</h6></td>
                                <td class="text-muted pl-3">{{profile.boosting_since}}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                </div>
            </div>

            <div v-if="selected_server.active_modules.includes('levelsystem')">
                <div class="d-flex justify-content-between">
                    <div>
                        <h6 class="text-gray4">Gained XP Origin</h6>
                    </div>
                    <div>
                        <h6 class="text-gray4">Total XP Gained: <span class="text-white">{{profile.total_xp}}</span></h6>
                    </div>
                </div>
                <div class="progress" style="border-radius: 3rem; background-color: unset !important;">
                    <div class="progress-bar bg-gray2-important" role="progressbar" :style="{'width': '' + unknown_xp_percent + '%'}"></div>
                    <div class="progress-bar bg-purple" role="progressbar" :style="{'width': '' + text_msg_xp_percent + '%'}"></div>
                    <div class="progress-bar bg-blue" role="progressbar" :style="{'width': '' + voice_xp_percent + '%'}"></div>
                    <div class="progress-bar bg-cyan" role="progressbar" :style="{'width': '' + boost_xp_percent + '%'}"></div>
                </div>

                <div class="mx-4 d-flex justify-content-between pt-2">
                    <div v-if="unknown_xp_percent > 0" class="d-flex align-items-center">
                        <div class="xp-dot mr-2 bg-gray2-important">
                        </div>
                        <span class="text-gray4 text-nowrap">Unknown</span>
                    </div>
                    <div v-if="text_msg_xp_percent > 0" class="d-flex align-items-center">
                        <div class="xp-dot mr-2 bg-purple">
                        </div>
                        <span class="text-gray4 text-nowrap">Text-Messages</span>
                    </div>
                    <div v-if="voice_xp_percent > 0" class="d-flex align-items-center">
                        <div class="xp-dot mr-2 bg-blue">
                        </div>
                        <span class="text-gray4 text-nowrap">Voice-Activity</span>
                    </div>
                    <div v-if="boost_xp_percent > 0" class="d-flex align-items-center">
                        <div class="xp-dot mr-2 bg-cyan">
                        </div>
                        <span class="text-gray4 text-nowrap">XP-Boost</span>
                    </div>
                </div>

                <hr>

                <div class="row" v-if="selected_server.active_modules.includes('boost') && selected_server.active_modules.includes('promo')">

                    <div class="col-12 col-xl-6">
                        
                        <div class="text-field-dark d-flex flex-row mb-3 mt-1">
                            Promo Boosts
                            <div class="col d-flex justify-content-end" style="color: var(--green);">x{{profile.promo_boost_xp_multiplier}} XP-Boost
                            </div>
                        </div>
                        <div v-for="boost in profile.promo_boosts_raw_data" :key="boost.name" class="ms-3 mb-2">
                            <div class="d-flex flex-row">
                                <h5 class="col-8">{{boost.name}}</h5>
                                <p class="col text-gray4 d-flex justify-content-end me-3">{{boost.remaining_days}} Days and {{boost.remaining_hours}} Hours</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-xl-6">
                        <div class="d-none d-xl-block vertical-divider"></div>
                        <div class="text-field-dark d-flex flex-row mb-3 mt-1">
                            Normal Boosts
                            <div class="col d-flex justify-content-end" style="color: var(--green);">
                                x{{profile.boost_xp_multiplier}} XP-Boost
                            </div>
                        </div>
                        <div v-for="boost in profile.boosts_raw_data" :key="boost.name" class="ms-3 mb-2">
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
          total_xp_with_origin: 0,
          unknown_xp_percent: 100,
          text_msg_xp_percent: 0,
          voice_xp_percent: 0,
          boost_xp_percent: 0,
      };
  },
  created() {
      if (this.profile.total_xp != 0) {
          this.total_xp_with_origin = this.profile.text_msg_xp + this.profile.voice_xp + this.profile.boost_xp;
          this.unknown_xp_percent = (this.profile.total_xp - this.total_xp_with_origin) * 100 / this.profile.total_xp;
          this.text_msg_xp_percent = this.profile.text_msg_xp * 100 / this.profile.total_xp;
          this.voice_xp_percent = this.profile.voice_xp * 100 / this.profile.total_xp;
          this.boost_xp_percent = this.profile.boost_xp * 100 / this.profile.total_xp;
      }
  }
});
</script>
