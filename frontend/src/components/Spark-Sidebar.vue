<template>
<div ref="sparkSidebarContainer" class="spark-sidebar-container d-flex flex-column flex-shrink-0 text-white">
    <div class="spark-fixed-sidebar d-flex flex-column flex-shrink-0 text-white">
        <div class="d-flex flex-column h-100">
            
            <div @click="toggle_sidebar()" class="d-flex spark-logo-container justify-content-center align-items-center mb-3 text-white text-decoration-none">

                <div class="spark-logo text-center py-3" style="z-index: 0; width: 200px; position: relative;">

                    <!-- Spark Glow -->
                    
                    <div class="d-flex">
                        <div class="position-relative">
                            <div class="spark-logo-glow"></div>
                        </div>
                        <img class="spark-logo-image" style="z-index: 5;" src="../assets/spark-logo.png" alt="Spark Logo">
                        <img class="spark-title-image sidebar-hide-collapsed sidebar-hide-collapsed-hover" style="z-index: 5;" src="../assets/spark-title.png" alt="Spark Title">
                    </div>
                    
                </div>
            </div>
            <ul class="nav nav-pills flex-column justify-content-start flex-grow-1">

                <spark-sidebar-link :route="'/choose-server'" :title="$filters.i18n('CHOOSE_SERVER_TITLE')" emoji="choose-server" :gold_active="false"></spark-sidebar-link>
                
                <li>
                    <a class="nav-link text-white" style="pointer-events: none;">
                        <div class="d-flex align-items-center">
                            <img class="sidebar-server-image" :src="selected_server.icon_url ? selected_server.icon_url : 'https://cdn.discordapp.com/embed/avatars/1.png'" alt=" ">
                            <div class="sidebar-hide-collapsed text-truncate" style="padding-left: 0.5rem;">
                                {{selected_server.name}}
                            </div>
                        </div>
                    </a>
                </li>

                <hr>


                <spark-sidebar-link v-if="selected_server.active_modules.includes('levelsystem')" :route="'/ranking/' + selected_server.id" :title="$filters.i18n('RANKING_TITLE')" emoji="ranking"></spark-sidebar-link>

                <hr v-if="selected_server.active_modules.includes('levelsystem')">

                <spark-sidebar-link :route="'/your-profile/' + selected_server.id" :title="$filters.i18n('YOUR_PROFILE_TITLE')" emoji="profile"></spark-sidebar-link>
                <spark-sidebar-link v-if="selected_server.active_modules.includes('boost') || selected_server.active_modules.includes('promo')" :route="'/boosts/' + selected_server.id" :title="$filters.i18n('BOOST_TITLE')" emoji="boosts"></spark-sidebar-link>
                <spark-sidebar-link v-if="selected_server.active_modules.includes('wheelspin')" :route="'/wheelspin/' + selected_server.id" :title="$filters.i18n('WHEELSPIN_TITLE')" emoji="wheelspin"></spark-sidebar-link>
                <spark-sidebar-link v-if="selected_server.active_modules.includes('inventory')" :route="'/inventory/' + selected_server.id" :title="$filters.i18n('INVENTORY_TITLE')" emoji="inventory"></spark-sidebar-link>
                <spark-sidebar-link v-if="selected_server.active_modules.includes('store')" :route="'/store/' + selected_server.id" :title="$filters.i18n('STORE_TITLE')" emoji="store"></spark-sidebar-link>
            </ul>
            <ul class="nav nav-pills flex-column justify-content-start">
                <spark-sidebar-link v-if="profile.is_admin && selected_server.active_modules.includes('inventory')" :route="'/inventory-system/' + selected_server.id" :title="$filters.i18n('INVENTORY_SYSTEM_TITLE')" emoji="inventory-system"></spark-sidebar-link>
                <spark-sidebar-link v-if="profile.is_admin" :route="'/admin-tools/' + selected_server.id" :title="$filters.i18n('ADMIN_TOOLS_TITLE')" emoji="admin-tools"></spark-sidebar-link>
                <spark-sidebar-link v-if="profile.is_admin" :route="'/server-modules/' + selected_server.id" :title="$filters.i18n('SERVER_MODULES_TITLE')" emoji="server-modules"></spark-sidebar-link>
                <spark-sidebar-link v-if="profile.is_admin" :route="'/server-settings/' + selected_server.id" :title="$filters.i18n('SERVER_SETTINGS_TITLE')" emoji="server-settings"></spark-sidebar-link>
            </ul>
            
            <hr>

            <div class="dropdown show ">
                <a class="text-white sidebar-dropdown text-decoration-none d-flex align-items-center" role="button" id="dropdownMenuLink" data-bs-toggle="dropdown">
                    <div class="d-flex flex-row">
                        <img :src="profile.member.avatar_url" alt="" class="rounded-circle" width="30" height="30">
                        <strong class="sidebar-hide-collapsed align-self-center ms-2">{{profile.member.name}}</strong>
                    </div>
                    <div class="sidebar-hide-collapsed">
                        <i class="fas fa-fw fa-ellipsis-v"></i>
                    </div>
                </a>

                <div class="dropdown-menu dropdown-menu-end shadow text-center rounded-1rem">
                    <h6 class="dropdown-header text-wrap m-auto" style="max-width: 145px;">{{ $filters.i18n('SIGNED_IN_AS', [profile.member.name]) }}</h6>
                    <div class="dropdown-divider"></div>
                    <router-link v-if="profile.is_super_admin" class="dropdown-item text-white" :to="'/super-admin/' + selected_server.id">{{ $filters.i18n('SUPER_ADMIN_TITLE') }}</router-link>
                    <router-link class="dropdown-item text-white" :to="'/help/' + selected_server.id">{{ $filters.i18n('HELP') }}</router-link>
                    <a class="dropdown-item text-white" href="https://github.com/Maveo/Spark">GitHub</a>
                    <div class="dropdown-divider"></div>
                    <a class="dropdown-item text-danger" href="#" @click="logout">{{ $filters.i18n('LOGOUT') }}</a>
                </div>
            </div>

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
  mounted() {
      if (window.innerWidth < 1000) {
        (this.$refs['sparkSidebarContainer'] as HTMLElement).classList.add('sidebar-collapsed');
      }
  },
  methods: {
    toggle_sidebar() {
        (this.$refs['sparkSidebarContainer'] as HTMLElement).classList.toggle('sidebar-collapsed');
    },
    logout()
    {
        console.log('Logging out...');
        store.commit('logout');
    }
  }
});
</script>
