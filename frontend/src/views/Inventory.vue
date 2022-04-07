<template>
  <div class="container container-large">
    <div class="pb-5">
      <h2>Inventory</h2>
      <span class="text-gray4">Items you have and do not have.</span>
    </div>

    <div v-if="loading" class="view-main-card text-center">
      <span
        class="spinner-border spinner-border-lg mb-1 me-2"
        role="status"
        aria-hidden="true"
      ></span>
    </div>
    <template v-if="!loading">
      <div
        v-for="(item, item_type_id) in inventory"
        :key="item_type_id"
        class="view-main-card mb-3 me-3 p-3"
      >
        <div class="d-flex">
          <div class="d-xl-block">
              <h1>{{ item.rarity_name }}</h1>
          </div>
          <div class="ps-3 d-flex flex-column justify-content-center">
            <h4 class="server-font-size">{{ item.item_name }} x{{ item.item_amount }}</h4>
            <button @click="use_item(item_type_id)" v-if="item.item_equippable || item.item_useable" class="mt-2 btn btn-success btn-sm w-100 font-weight-bold">
                <template v-if="item.item_equippable">
                    <template v-if="item.item_equipped">
                        Unequip
                    </template>
                    <template v-else>
                        Equip
                    </template>
                </template>
                <template v-else-if="item.item_useable">
                    Use
                </template>
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import api from "@/services/api";
import { AxiosError } from "axios";

export default defineComponent({
  name: "Inventory",
  data() {
    return {
      loading: true,
      inventory: {},
    };
  },
  created() {
    this.update_inventory();
  },
  methods: {
    update_inventory() {
        this.loading = true;
        api.get_inventory().then((response) => {
            console.log(response.data);
            this.inventory = response.data.inventory;
            this.loading = false;
        }).catch((e: AxiosError) => {
            if (e.response) {
                console.log(e.response);
            }
        });
    },
    use_item(item_type_id: number) {
        this.loading = true;
        api.use_item(item_type_id, 1).then(() => {
            this.update_inventory();
        }).catch((e: AxiosError) => {
            if (e.response) {
                console.log(e.response);
            }
        });
    },
  },
});
</script>


