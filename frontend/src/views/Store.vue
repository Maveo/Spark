<template>
  <div class="container container-large">
    <div class="pb-5">
      <h2>Store</h2>
      <span class="text-gray4">Buy or Sell stuff you do not need.</span>
    </div>

    <div class="view-main-card text-center">
      <span
        v-if="loading"
        class="spinner-border spinner-border-lg mb-1 me-2"
        role="status"
        aria-hidden="true"
      ></span>
      <div v-else class="row">
        <div v-for="offer in store" :key="offer.id" class="col bg-gray2 m-2 p-3 spark-rounded">
            <h4 class="my-2">Pay</h4>
            <div class="spark-rounded" :style="'background-image: ' + offer.from_background_color_html">
                <h2 class="m-0 px-2 text-nowrap background-text" :style="'background-image: ' + offer.from_foreground_color_html">
                    x{{offer.from_item_amount}} {{offer.from_item_type.name}}
                </h2>
            </div>
            (you have x{{inventory_amount(offer.from_item_type.id)}})
            <h4 class="my-2">to get</h4>
            <div class="spark-rounded" :style="'background-image: ' + offer.to_background_color_html">
                <h2 class="m-0 px-2 text-nowrap background-text" :style="'background-image: ' + offer.to_foreground_color_html">
                   x{{offer.to_item_amount}} {{offer.to_item_type.name}}
                </h2>
            </div>
            (you have x{{inventory_amount(offer.to_item_type.id)}})
            <button :disabled="offer.from_item_amount > inventory_amount(offer.from_item_type.id)" @click="buy_offer(offer.id)" type="submit" class="mt-2 btn btn-success btn-sm w-100 font-weight-bold">
                Buy
            </button>
        </div>
      </div>
    </div>

    <div v-if="profile.is_admin" class="view-main-card mt-3">
      <h4 class="px-2 mb-3">Setup</h4>
      <a
        href="#"
        class="btn btn-nofocus text-white text-nowrap btn-toggle collapsed"
        data-bs-toggle="collapse"
        data-bs-target="#collapseStoreSetup"
      >
        <i class="fas fa-fw toggle-icon"></i>
        Show
      </a>

      <form
        @submit.prevent="set_store()"
        class="collapse"
        id="collapseStoreSetup"
      >
        <div v-for="(value, index) in admin_store_items" :key="index">
          <div class="d-flex justify-content-center mb-2">
            <span class="text-nowrap">ID: {{ value.id }}</span>
            <div class="input-group input-group-sm">
              <span class="input-group-text">Amount</span>
              <input
                v-model="value.from_item_amount"
                type="number"
                step="0.0001"
                class="form-control form-control-sm font-weight-bold"
                placeholder="1"
                required
              />
            </div>
            <div class="input-group input-group-sm">
              <span class="input-group-text">From Item</span>
              <select
                v-model="value.from_item_id"
                class="form-select form-select-sm"
                required
              >
                <option value="" disabled selected hidden>
                  Choose Item type...
                </option>
                <option
                  :value="item_type.id"
                  v-for="item_type in admin_item_types"
                  :key="item_type.id"
                >
                  ID: {{ item_type.id }} | {{ item_type.name }}
                </option>
              </select>
            </div>
            <span class="mx-2">buys</span>
            <div class="input-group input-group-sm">
              <span class="input-group-text">Amount</span>
              <input
                v-model="value.to_item_amount"
                type="number"
                step="0.0001"
                class="form-control form-control-sm font-weight-bold"
                placeholder="1"
                required
              />
            </div>
            <div class="input-group input-group-sm">
              <span class="input-group-text">Of Item</span>
              <select
                v-model="value.to_item_id"
                class="form-select form-select-sm"
                required
              >
                <option value="" disabled selected hidden>
                  Choose Item type...
                </option>
                <option
                  :value="item_type.id"
                  v-for="item_type in admin_item_types"
                  :key="item_type.id"
                >
                  ID: {{ item_type.id }} | {{ item_type.name }}
                </option>
              </select>
            </div>
            <button
              :disabled="admin_items_loading"
              class="btn btn-sm btn-danger ms-2"
              @click="admin_store_items.splice(index, 1)"
            >
              <i class="fas fa-fw fa-trash"></i>
            </button>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <button
              type="button"
              :disabled="admin_items_loading"
              class="w-100 btn btn-info btn-sm"
              @click="
                admin_store_items.push({
                  from_item_id: '',
                  from_item_amount: 0,
                  to_item_id: '',
                  to_item_amount: 0,
                })
              "
            >
              <i class="fas fa-fw fa-plus"></i>
            </button>
          </div>
          <div class="col">
            <button
              type="submit"
              :disabled="admin_items_loading"
              class="w-100 btn btn-success btn-sm"
            >
              Save
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import api from "@/services/api";
import store from "@/store";
import { AxiosResponse } from "axios";
import { defineComponent } from "vue";

// eslint-disable-next-line @typescript-eslint/no-var-requires
let Swal = require("sweetalert2/src/sweetalert2.js").default;

const Toast = Swal.mixin({
  toast: true,
  position: "top-end",
  showConfirmButton: false,
  timer: 3000,
});

export default defineComponent({
  name: "Choose Server",
  data() {
    return {
      profile: store.state.profile,
      loading: true,
      store: [],
      inventory: [],
      admin_items_loading: true,
      admin_store_items: [] as any,
      admin_item_types: [] as any,
    };
  },
  created() {
    this.update_store();
    if (this.profile.is_admin) {
        this.update_admin();
    }
  },
  methods: {
    inventory_amount(id: number) {
        return (id in this.inventory) ? this.inventory[id]['item_amount'] : 0;
    },
    update_store(loading = true) {
      if (loading) this.loading = true;
      api.get_inventory().then((response: AxiosResponse) => {
        this.inventory = response.data.inventory;
        api.get_store().then((response: AxiosResponse) => {
            this.store = response.data.store;
            if (this.profile.is_admin) {
                this.admin_store_items = [...this.store];
            }
            if (loading) this.loading = false;
        }).catch((error) => {
            Toast.fire({
                icon: "error",
                text: error.response.data.description,
            });
            });
        }).catch((error) => {
            Toast.fire({
                icon: "error",
                text: error.response.data.description,
            });
        });
    },
    buy_offer(offer_id: number) {
        api.buy_offer(offer_id, 1).then(() => {
            Toast.fire({
                icon: "success",
                text: "Successful",
            });
            this.update_store(false);
        }).catch((error) => {
            Toast.fire({
                icon: "error",
                text: error.response.data.description,
            });
        });
    },
    update_admin() {
        this.admin_items_loading = true;
        api.get_item_types().then((response: AxiosResponse) => {
          this.admin_item_types = response.data.item_types;
          this.admin_items_loading = false;
        }).catch((error) => {
          Toast.fire({
            icon: "error",
            text: error.response.data.description,
          });
        });
    },
    set_store() {
        console.log(this.admin_store_items);
        api.set_store(this.admin_store_items).then(() => {
          Toast.fire({
            icon: "success",
            text: "Successful",
          });
          this.update_store();
        })
        .catch((error) => {
          Toast.fire({
            icon: "error",
            text: error.response.data.description,
          });
        });
    }
  },
});
</script>
