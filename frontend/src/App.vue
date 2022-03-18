<template>
  <!-- Global loading overlay -->
  <div v-if="global_loading()" class="global-loading-overlay">
    <span class="spinner-border" role="status" aria-hidden="true"></span>
  </div>
  <main v-if="selected_server()" class="main">
    <!-- Sidebar Container -->
    <div
      class="
        spark-sidebar-container
        d-flex
        flex-column flex-shrink-0
        p-3
        text-white
      "
    >
      <sparksidebar></sparksidebar>
    </div>

    <!-- Main Site Container -->
    <div class="d-flex flex-column flex-grow-1">
      <div class="p-5 overflow-auto">
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
import sparknavbar from "./components/Spark-Navbar.vue";

import store from "@/store";

export default {
  components: {
    sparksidebar,
    sparknavbar,
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
/* route transition */
.route-enter-from {
  opacity: 0;
  /* transform: translateY(50px); */
  margin-top: -25px;
}

.route-enter-active {
  transition: all 250ms ease-out;
}

.route-leave-to {
  opacity: 0;
  /* transform: translateY(-50px); */
  margin-top: 25px;
}

.route-leave-active {
  transition: all 250ms ease-in;
}

.btn-nofocus:focus {
  box-shadow: none !important;
}

.router-view {
  min-height: 100vh;
}

.container-large {
  max-width: 1400px !important;
}

.main {
  display: flex;
  flex-wrap: nowrap;
  height: 100vh;
  height: -webkit-fill-available;
  max-height: 100vh;
  overflow-x: auto;
  overflow-y: hidden;
}

.bg-lightgray {
  background-color: hsl(214, 31%, 25%);
  color: gray;
}

.view-main-card {
  background-color: var(--grey1);
  border-radius: 1rem;
  padding: 1rem !important;
  color: white !important;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.spark-sidebar-container {
  background-color: #303237;
  width: 325px;
}

.global-loading-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    z-index: 9999;
    backdrop-filter: blur(5px);
    background-color: rgba(0, 0, 0, 0.5);
    vertical-align: middle;
    text-align: center;
}

.global-loading-overlay > .spinner-border {
    margin-top: 45vh;
    width: 4rem;
    height: 4rem;
    border: 0.5em solid var(--grey2);
    border-right-color: transparent;
}

:root {
  --black: #000000;
  --light-black: #17181a;
  --dark-grey: #2a2a2c;
  --grey1: #303237;
  --grey2: #454951;
  --grey3: #9fa5ad;
  --grey4: #b7bec5;

  --stg-orange: #d98e4c;
  --stg-yellow: #ffde07;

  --purple: #a654e9;
  --blue: #67a1ff;
  --cyan: #76ffed;
  --green: #2fac66;

  --font-regular: "regular";
  --font-bold: "bold";
}

.xp-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

/* Chrome fix */
html,
body,
.main {
  min-height: 100vh;
}

:root {
  --font-family-sans-serif: "Product Sans", "Segoe UI", "Helvetica Neue", Arial,
    "Noto Sans", sans-serif !important;
}
body {
  /* font-size: 17px !important; */
  font-family: var(--font-family-sans-serif) !important;
}

.nav-link {
  transition: color 250ms ease-in-out, background-color 250ms ease-in-out,
    border-color 250ms ease-in-out;
}

.router-link-active {
  background-color: var(--grey2);
}
.router-link-active:hover {
  background: var(--grey2) !important;
  color: white !important;
}

.bg-purple {
  background-color: #a654e9 !important;
}
.bg-blue {
  background-color: #67a1ff !important;
}
.bg-cyan {
  background-color: #76ffed !important;
}
.bg-green {
  background-color: #2fac66 !important;
}

.bg-gray1 {
  background-color: var(--grey1);
}
.bg-gray2 {
  background-color: var(--grey2);
}
.bg-gray2-important {
  background-color: var(--grey2) !important;
}
.bg-gray3 {
  background-color: var(--grey3);
}
.bg-gray4 {
  background-color: var(--grey4);
}

.text-gray1 {
  color: var(--grey1);
}
.text-gray2 {
  color: var(--grey2);
}
.text-gray3 {
  color: var(--grey3);
}
.text-gray4 {
  color: var(--grey4);
}

.default-gradient {
  background-image: linear-gradient(
    to right,
    var(--stg-orange),
    var(--stg-yellow)
  );
}
.vl {
  background-color: var(--grey2);
  width: 2px;
  border-radius: 1px;
}
.hl {
  background-color: var(--grey2);
  height: 2px;
  border-radius: 1px;
}
.hr {
  border-color: var(--grey2) !important;
  background-color: var(--grey2) !important;
  border-radius: 4px;
  width: 100% !important;
}
hr {
  border-color: var(--grey2) !important;
  background-color: var(--grey2) !important;
  border-radius: 4px;
}
h1,
h2 {
  color: white;
  font-weight: 600 !important;
  letter-spacing: 1px;
}
h3,
h4,
h5 {
  color: white;
  letter-spacing: 1px;
}
p {
  color: white;
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.p-decent {
  color: var(--grey4);
}
.p-decent-small {
  color: var(--grey4);
  font-size: small;
}
.text-field-dark {
  font-size: 18px;
  color: white;
  background-color: var(--dark-grey);
  padding: 8px 16px;
  border-radius: 0.5rem;
}
.dark-hover:hover:not(.btn-secondary) {
  background-color: var(--dark-grey);
}
.btn-secondary {
  background-color: var(--dark-grey);
  padding: 8px 16px;
  border-radius: 0.5rem;
  border-color: transparent;
}
.btn-check:focus + .btn-secondary,
.btn-secondary:focus {
  color: #fff;
  background-color: #5c636a;
  border-color: transparent;
  box-shadow: transparent;
}

hr {
  width: 100%;
}

.dropdown-menu {
  background-color: var(--grey1) !important;
}
.dropdown-item:hover {
  background-color: var(--grey2) !important;
}
.dropdown-divider {
  border-top: 1px solid var(--grey2) !important;
  width: 80%;
  position: relative;
  transform: translate(-50%, 0);
  left: 50%;
}

.spark-rounded {
  border-radius: 0.5rem;
}

textarea {
    border-radius: 0.5rem;
}

textarea.is-invalid {
    box-shadow: 0 0 0.5rem 0.2rem var(--danger);
}

/* a {
  color: var(--grey3);
  text-decoration: underline;
}
a:hover {
  background-image: linear-gradient(to right, var(--stg-yellow), var(--stg-orange)) !important;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-color: transparent;
  color: var(--stg-yellow) !important;
} */

/* .nav-link {
  color: #ffffff;
}
.nav-link-bg {
  background: none;
  border-radius: 0.5rem;
}
.nav-link-bg.active {
  background-color: var(--grey2);
}
.nav-link-bg.active:hover, .nav-link-bg.active:focus {
  filter: brightness(130%);
  transition: filter 0.15s ease-in-out;
}
.nav-link:hover, .nav-link:focus {
  background-image: linear-gradient(to right, var(--stg-yellow), var(--stg-orange)) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent;
  background-color: transparent;
  color: var(--stg-yellow);
}
.nav-link.active:hover, .nav-link.active:focus {
  -webkit-background-clip: border-box;
  -webkit-text-fill-color: white;
}
.nav-item-text:hover, .nav-item-text:focus {
  background-image: linear-gradient(to right, var(--stg-yellow), var(--stg-orange));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-color: transparent;
} */

.dropdown-item {
  color: #f3f3f3;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out,
    border-color 0.15s ease-in-out;
}

/* .dropdown-toggle::after {
  border-top: 0.3em solid var(--grey3);
}
.dropdown-menu {
  background-color: rgba(255, 255, 255, 0);
  backdrop-filter: blur(10px);
  color: #ffffff;
  border-radius: 0.5rem;
}
.dropdown-menu-right {
  right: 0;
}
.dropdown-item:hover, .dropdown-item:focus {
  background-image:linear-gradient(to right, var(--stg-yellow), var(--stg-orange));
 -webkit-text-fill-color: transparent;
  background-color: transparent;
  color: var(--stg-yellow);
}
.dropdown-item.active, .dropdown-item:active {
  color: var(--grey1);
  background-image: linear-gradient(to right, var(--stg-yellow), var(--stg-orange));
}
.dropdown-item.active:hover, .dropdown-item:active:hover {
  -webkit-text-fill-color: black;
  filter: brightness(130%);
} */

.spark-logo .spark-logo-glow {
  opacity: 0;
}

.spark-logo:hover .spark-logo-glow {
  opacity: 1;
}

.vertical-divider {
    position: absolute;
    height: 100%;
    left: 0;
    border-left: 1px solid var(--grey2);
}

.emoji {
  width: 20px;
  height: 20px;
  /* stroke: none; */
  /* vertical-align: -22%; */
  background-size: cover;
}
.emoji-profile {
  background: url("./assets/icons/profile.svg") no-repeat;
  margin-left: 2px !important;
}
.emoji-profile.emoji-gold {
  background: url("./assets/icons/profile-gold.svg") no-repeat;
}
.emoji-choose-server {
  background: url("./assets/icons/choose-server.svg") no-repeat;
  margin-bottom: 1px;
}
.emoji-choose-server.emoji-gold {
  background: url("./assets/icons/choose-server-gold.svg") no-repeat;
}
.emoji-wallet {
  background: url("./assets/icons/wallet.svg") no-repeat;
  margin-top: 5px;
}
.emoji-wallet.emoji-gold {
  background: url("./assets/icons/wallet-gold.svg") no-repeat;
}
.emoji-wheelspin {
  background: url("./assets/icons/wheelspin.svg") no-repeat;
}
.emoji-wheelspin.emoji-gold {
  background: url("./assets/icons/wheelspin-gold.svg") no-repeat;
}
.emoji-promo-code {
  background: url("./assets/icons/promo-code.svg") no-repeat;
  margin-top: 7px !important;
  margin-left: 2px !important;
}
.emoji-promo-code.emoji-gold {
  background: url("./assets/icons/promo-code-gold.svg") no-repeat;
}
.emoji-profile-card {
  background: url("./assets/icons/profile-card.svg") no-repeat;
  margin-top: 5px !important;
}
.emoji-profile-card.emoji-gold {
  background: url("./assets/icons/profile-card-gold.svg") no-repeat;
}
.emoji-server-settings {
  background: url("./assets/icons/server-settings.svg") no-repeat;
}
.emoji-server-settings.emoji-gold {
  background: url("./assets/icons/server-settings-gold.svg") no-repeat;
}
.emoji-ranking {
  background: url("./assets/icons/ranking.svg") no-repeat;
  margin-bottom: 2px;
}
.emoji-ranking.emoji-gold {
  background: url("./assets/icons/ranking-gold.svg") no-repeat;
}
.emoji-boosts {
  background: url("./assets/icons/boosts.svg") no-repeat;
  margin-bottom: 2px;
  margin-left: 2px;
}
.emoji-boosts.emoji-gold {
  background: url("./assets/icons/boosts-gold.svg") no-repeat;
}
</style>
