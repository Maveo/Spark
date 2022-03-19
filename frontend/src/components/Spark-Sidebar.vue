<template>
  <div class="d-flex flex-column h-100">
    
    <div class="d-flex justify-content-center align-items-center mb-3 text-white text-decoration-none">

        <div class="spark-logo text-center py-3" style="z-index: 0; width: 200px; position: relative;">

            <!-- Spark Glow -->
            <div class="spark-logo-glow" style="z-index: -1; filter: blur(20px); transition: opacity .5s ease-in-out; left: 5px; top: 50%; border-radius: 50%; transform: translate(0,-50%); position: absolute; width: 50px; height: 50px; background: linear-gradient(135deg, #FFEF26, #ff8800);">

            </div>

            <div>
                <img style="z-index: 5;" src="../assets/spark-logo.svg" alt="Spark Logo">
            </div>
            
        </div>
    </div>
    <ul class="nav nav-pills flex-column justify-content-start flex-grow-1">
        <spark-sidebar-link :route="'/choose-server'" title="Choose Server" emoji="choose-server" :gold_active="false"></spark-sidebar-link>
        
        <li>
            <a href="#" class="nav-link text-white" style="pointer-events: none;">
                <div class="d-flex align-items-center">
                    <img style="border-radius: 50%; max-width: 50px;" :src="selected_server.icon_url" alt=" ">
                    <div style="padding-left: 0.5rem;">
                        {{selected_server.name}}
                    </div>
                </div>
            </a>
        </li>

        <hr>


        <spark-sidebar-link v-if="selected_server.active_modules.includes('levelsystem')" :route="'/ranking/' + selected_server.id" title="Ranking" emoji="ranking"></spark-sidebar-link>

        <hr v-if="selected_server.active_modules.includes('levelsystem')">

        <spark-sidebar-link :route="'/your-profile/' + selected_server.id" title="Your Profile" emoji="profile"></spark-sidebar-link>
        <spark-sidebar-link v-if="selected_server.active_modules.includes('boost') || selected_server.active_modules.includes('promo')" :route="'/boosts/' + selected_server.id" title="Boosts" emoji="boosts"></spark-sidebar-link>
    </ul>
    <ul class="nav nav-pills flex-column justify-content-start">
        <spark-sidebar-link v-if="profile.is_admin" :route="'/admin-tools/' + selected_server.id" title="Admin Tools" emoji="boosts"></spark-sidebar-link>
        <spark-sidebar-link v-if="profile.is_admin" :route="'/server-modules/' + selected_server.id" title="Server Modules" emoji="server-settings"></spark-sidebar-link>
        <spark-sidebar-link v-if="profile.is_admin" :route="'/server-settings/' + selected_server.id" title="Server Settings" emoji="server-settings"></spark-sidebar-link>
    </ul>
    
    <hr>

    <div class="dropdown show px-3">
        <a class="text-white text-decoration-none d-flex justify-content-between align-items-center" href="#" role="button" id="dropdownMenuLink" data-bs-toggle="dropdown">
            <div>
                <img :src="profile.member.avatar_url" alt="" class="rounded-circle me-2" width="32" height="32">
                <strong>{{profile.member.name}}</strong>
            </div>
            <div>
                <i class="fas fa-fw fa-ellipsis-v"></i>
            </div>
        </a>

        <div class="dropdown-menu dropdown-menu-end shadow text-center rounded-1rem">
            <h6 class="dropdown-header text-gray2">Signed in as<br />{{profile.member.name}}</h6>
            <div class="dropdown-divider"></div>
            <router-link v-if="profile.is_super_admin" class="dropdown-item text-white" :to="'/super-admin/' + selected_server.id">Super Admin</router-link>
            <a class="dropdown-item text-white" href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">Help</a>
            <a class="dropdown-item text-white" href="https://github.com/Maveo/Spark">GitHub</a>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item text-danger" href="#" @click="logout">Logout</a>
        </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

import SparkSidebarLink from '@/components/Spark-Sidebar-Link.vue';

import store from '@/store';

export default defineComponent({
  name: 'SparkSidebar',
  data() {
    return {
        selected_server: store.state.selected_server,
        profile: store.state.profile,
    }
  },
  components: {
    SparkSidebarLink
  },
  methods: {
    logout()
    {
        console.log('Logging out...');
        store.commit('logout');
    }
  }
});
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
