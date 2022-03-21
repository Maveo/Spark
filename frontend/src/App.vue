<template>
  <!-- Global loading overlay -->
  <div v-if="global_loading()" class="global-loading-overlay">
    <span class="spinner-border" role="status" aria-hidden="true"></span>
  </div>
  <main v-if="selected_server()" class="main">
    <!-- Sidebar -->
    <sparksidebar></sparksidebar>

    <!-- Main Site Container -->
    <div class="d-flex flex-column flex-grow-1">
      <div id="mainSiteContainer" class="py-5 px-0 p-lg-5 overflow-auto">
        <router-view v-slot="{ Component }">
          <transition name="route" mode="out-in">
            <component :is="Component"></component>
          </transition>
        </router-view>
      </div>
    </div>
  </main>
  <main v-if="!selected_server()">
    <div class="p-5 overflow-auto">
      <router-view v-slot="{ Component }">
        <component :is="Component"></component>
      </router-view>
    </div>
  </main>
</template>

<script lang="ts">
import sparksidebar from "./components/Spark-Sidebar.vue";

import store from "@/store";

export default {
  components: {
    sparksidebar,
  },
  methods: {
    selected_server(): boolean {
      return !!store.state.persistant.token && !!store.state.selected_server.id;
    },
    global_loading(): boolean {
      return store.state.global_loading;
    },
  },
};
</script>

<style>
    @import './app.css';
</style>