<template>
  <div class="container container-large">
    <div class="pb-5">
      <h2>Choose Server</h2>
      <span class="text-gray4">Choose a server on which you will click.</span>
    </div>

    <div v-if="loading" class="view-main-card text-center">
      <span
        class="spinner-border spinner-border-lg mb-1 me-2"
        role="status"
        aria-hidden="true"
      ></span>
    </div>
    <template v-if="!loading">
      <button
        v-for="server in servers"
        :key="server.id"
        @click="choose_server(server)"
        class="view-main-card mb-3 me-3 p-3"
      >
        <div class="d-flex">
          <div class="d-xl-block">
            <img
              class="rounded-circle server-icon-width"
              v-lazy="{src: server.icon_url ? server.icon_url : 'https://cdn.discordapp.com/embed/avatars/1.png', loading: 'https://cdn.discordapp.com/embed/avatars/1.png'}"
            />
          </div>
          <div class="ps-3 d-flex flex-column justify-content-center">
            <h4 class="server-font-size">{{ server.name }}</h4>
          </div>
        </div>
      </button>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import api from "@/services/api";
import store from "@/store";
import router from "@/router";
import { AxiosError } from "axios";

export default defineComponent({
  name: "Choose Server",
  data() {
    return {
      loading: true,
      servers: [],
    };
  },
  created() {
    api
      .get_guilds()
      .then((response) => {
        console.log(response.data);
        this.servers = response.data.guilds;
        this.loading = false;
      })
      .catch((e: AxiosError) => {
        if (e.response) {
          console.log(e.response);
        }
        store.commit("logout");
        router.push("/login");
      });
  },
  methods: {
    choose_server(server: any) {
      console.log("choose server: " + server);
      store.commit("choose_server", server.id);
      router.push({ path: `/your-profile/${server.id}` });
    },
  },
});
</script>

<style scoped>
.server-icon-width {
  max-width: 100px;
}

@media only screen and (max-width: 576px) {
  .server-icon-width {
    max-width: 70px;
  }

  .server-font-size {
    font-size: 1.2rem;
  }
}

@media only screen and (max-width: 400px) {
  .server-icon-width {
    max-width: 40px;
  }

    .server-font-size {
    font-size: 0.9rem;
  }
}
</style>
