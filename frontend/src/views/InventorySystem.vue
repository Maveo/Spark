<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Inventory System</h2>
            <span class="text-gray4">Create your own Inventory System!</span>
        </div>

        <div class="view-main-card">
            <div class="row mb-4">
                <div class="col-lg-8 mb-2">
                    <h4 class="px-2 mb-3">Rarities</h4>
                    <a href="#" class="btn btn-nofocus text-white text-nowrap btn-toggle collapsed" data-bs-toggle="collapse" data-bs-target="#collapseRarities">
                        <i class="fas fa-fw toggle-icon"></i>
                        Show
                    </a>
                    
                    <div class="collapse" id="collapseRarities">
                        <div class="">
                            <div>
                                <i class="fas fa-exclamation-circle"></i>
                                Change design in settings
                            </div>
                            <div v-if="loading_rarities">
                                <div class="p-3 mb-2 text-center w-100">
                                    <span class="spinner-border spinner-border-lg" role="status" aria-hidden="true"></span>
                                </div>
                            </div>
                            <template v-else>
                                <div v-for="(rarity, index) in rarities" :key="index" class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div class="row me-3">
                                            <h5 class="m-0 text-nowrap">
                                                {{index + 1}}.
                                                <img :src="'data:image/png;base64, ' + rarity.image">
                                            </h5>
                                        </div>
                                        <div class="row">
                                            <button :disabled="index == 0" class="btn btn-info btn-sm col m-1" @click="change_rarity_order(index, -1)">
                                                <i class="fas fa-fw fa-arrow-up"></i>
                                            </button>
                                            <button :disabled="index == Object.keys(rarities).length - 1" class="btn btn-info btn-sm col m-1" @click="change_rarity_order(index, 1)">
                                                <i class="fas fa-fw fa-arrow-down"></i>
                                            </button>
                                            <button class="btn btn-danger btn-sm col m-1" @click="remove_rarity(rarity)">
                                                <i class="fas fa-fw fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </template>
                            <div class="d-flex justify-content-end">
                                <button :disabled="!changed_rarity_order" @click="save_rarity_order()" class="btn btn-success font-weight-bold">
                                    Save Order
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4" style="max-width: 400px;">
                    <h4 class="px-2 mb-3">Add Rarity</h4>
                    <form @submit.prevent="add_rarity()">
                        <div class="mb-2">   
                            <div class="input-group">
                                <input v-model="add_rarity_name" type="text" class="form-control form-control-sm font-weight-bold" placeholder="Name" required>
                            </div>
                        </div>
                        <div class="mb-2">   
                            <div class="input-group">
                                <input v-model="add_rarity_foreground_color" type="text" class="form-control form-control-sm font-weight-bold" placeholder="Foreground Color" required>
                            </div>
                        </div>
                        <div class="mb-2">   
                            <div class="input-group">
                                <input v-model="add_rarity_background_color" type="text" class="form-control form-control-sm font-weight-bold" placeholder="Background Color" required>
                            </div>
                        </div>
                        <div class="">
                            <button type="submit" class="btn btn-success btn-sm w-100 font-weight-bold">
                                Add Rarity
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col">
                    <h4 class="px-2 mb-3">Item Types</h4>
                    <a href="#" class="btn btn-nofocus text-white text-nowrap btn-toggle collapsed" data-bs-toggle="collapse" data-bs-target="#collapseItemTypes">
                        <i class="fas fa-fw toggle-icon"></i>
                        Show
                    </a>
                    <div class="collapse" id="collapseItemTypes">
                        <div class="">
                            <div v-if="loading_item_types">
                                <div class="p-3 mb-2 text-center w-100">
                                    <span class="spinner-border spinner-border-lg" role="status" aria-hidden="true"></span>
                                </div>
                            </div>
                            <template v-else>
                                <div v-for="item in item_types" :key="item.id" class="spark-rounded bg-gray2 py-2 px-4 mb-1">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div class="row me-3">
                                            <h5 class="m-0 text-nowrap">
                                                ID:{{item.id}}
                                                <img :src="'data:image/png;base64, ' + get_rarity_by_id(item.rarity_id)?.image">
                                                {{item.name}}                                                
                                            </h5>
                                        </div>
                                        <div class="row">
                                            <button class="btn btn-danger btn-sm col m-1" @click="remove_item_type(item)">
                                                <i class="fas fa-fw fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <h4 class="px-2 mb-3">Create Item Type</h4>
                    <form @submit.prevent="create_item_type()">
                        <div class="mb-2">   
                            <div class="input-group input-group-sm">
                                <span class="input-group-text">Name</span>
                                <input v-model="create_item_name" type="text" class="form-control form-control-sm font-weight-bold" placeholder="Name" required>
                            </div>
                        </div>
                        <div class="mb-2">   
                            <div class="input-group input-group-sm">
                                <span class="input-group-text">Rarity</span>
                                <select v-model="create_item_rarity" class="form-select form-select-sm" required>
                                    <option value="" disabled selected hidden>Choose rarity...</option>
                                    <option :value="rarity.id" v-for="(rarity, index) in rarities" :key="rarity.id">{{index + 1}}. {{rarity.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="mb-2">   
                            <div class="form-check form-check-inline">
                                <input v-model="create_item_always_visible" class="form-check-input" type="checkbox" id="alwaysVisibleCheckbox">
                                <label class="form-check-label" for="alwaysVisibleCheckbox">
                                    Always visible
                                </label>
                            </div>
                            <div class="form-check form-check-inline">
                                <input v-model="create_item_tradable" class="form-check-input" type="checkbox" value="" id="tradableCheckbox">
                                <label class="form-check-label" for="tradableCheckbox">
                                    Tradable
                                </label>
                            </div>
                        </div>
                        <div class="mb-2">   
                            <div class="input-group input-group-sm">
                                <button type="button" class="btn btn-secondary" :class="{'active': create_item_useable == -1}" @click="create_item_useable = -1">
                                    Force use
                                </button>
                                <button type="button" class="btn btn-secondary" :class="{'active': create_item_useable == 0}" @click="create_item_useable = 0">
                                    Not Useable
                                </button>
                                <button type="button" class="btn btn-secondary" :class="{'active': create_item_useable == 1}" @click="create_item_useable = 1">
                                    Useable Once
                                </button>
                                <button type="button" class="btn btn-secondary" :class="{'active': create_item_useable == 2}" @click="create_item_useable = 2">
                                    Infinite use
                                </button>
                            </div>
                            <!-- <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                                <input type="radio" class="btn-check" name="btnradio" id="btnradio1" autocomplete="off" checked>
                                <label class="btn btn-primary" for="btnradio1">Radio 1</label>

                                <input type="radio" class="btn-check" name="btnradio" id="btnradio2" autocomplete="off">
                                <label class="btn btn-primary" for="btnradio2">Radio 2</label>

                                <input type="radio" class="btn-check" name="btnradio" id="btnradio3" autocomplete="off">
                                <label class="btn btn-primary" for="btnradio3">Radio 3</label>
                            </div> -->
                        </div>
                        <div class="mb-2">   
                            <div class="input-group input-group-sm">
                                <span class="input-group-text">Expires after x Hours</span>
                                <input v-model="create_item_expiration" type="number" min="-1" class="form-control form-control-sm font-weight-bold" placeholder="-1" required>
                            </div>
                        </div>
                        <div class="mb-2">   
                            <div class="input-group input-group-sm">
                                <span class="input-group-text">Action</span>
                                <select v-model="create_item_action" class="form-select form-select-sm">
                                    <option value="" selected>No action</option>
                                    <option :value="action_id" v-for="(action, action_id) in create_item_action_options" :key="action_id">{{action.name}}</option>
                                </select>
                            </div>
                        </div>
                        <template v-for="(action, action_id) in create_item_action_options" :key="action_id">
                            <template v-if="create_item_action == action_id">
                                <div v-for="(option, id) in action.options" :key="id" class="mb-2">   
                                    <div class="input-group input-group-sm">
                                        <span class="input-group-text">{{option.description}}</span>
                                        <input v-if="option.type == 'int'" v-model="option.value" type="number" class="form-control form-control-sm font-weight-bold" required>
                                        <input v-if="option.type == 'str'" v-model="option.value" type="text" class="form-control form-control-sm font-weight-bold" required>
                                    </div>
                                </div>
                            </template>
                        </template>
                        <div class="">
                            <button type="submit" class="btn btn-success btn-sm w-100 font-weight-bold">
                                Create Item Type
                            </button>
                        </div>
                    </form>
                </div>
            </div>            
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import api from '@/services/api';
import { AxiosResponse } from "axios";

// eslint-disable-next-line @typescript-eslint/no-var-requires
let Swal = require('sweetalert2/src/sweetalert2.js').default;

const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
});

export default defineComponent({
  name: "Inventory System",
  data() {
    return {
        loading_rarities: true,
        rarities: ([] as any),
        changed_rarity_order: false,
        add_rarity_name: '',
        add_rarity_foreground_color: '',
        add_rarity_background_color: '',
        loading_item_types: true,
        item_types: [],
        create_item_name: '',
        create_item_rarity: '',
        create_item_always_visible: false,
        create_item_tradable: false,
        create_item_useable: -1,
        create_item_expiration: -1,
        create_item_action: '',
        create_item_action_options: ({} as any),
    }
  },
  mounted() {
      this.update_rarities();
      this.update_item_types();
      api.get_item_action_options().then((response: AxiosResponse) => {
            this.create_item_action_options = response.data.actions;
        }).catch((error) => {
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
  },
  methods: {
    get_rarity_by_id(id: number) {
        for (let rarity of this.rarities) {
            if (rarity.id == id) {
                return rarity;
            }
        }
    },
    update_rarities() {
        this.changed_rarity_order = false;
        this.loading_rarities = true;
        api.get_rarities().then((response: AxiosResponse) => {
            this.rarities = Object.values(response.data.rarities);
            this.loading_rarities = false;
        }).catch((error) => {
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
            this.loading_rarities = false;
        });
    },
    add_rarity() {
        api.add_rarity(this.add_rarity_name, this.add_rarity_foreground_color, this.add_rarity_background_color).then(() => {
            Toast.fire({
                icon: 'success',
                text: 'Successful',
            });
            this.add_rarity_name = '';
            this.add_rarity_foreground_color = '';
            this.add_rarity_background_color = '';
            this.update_rarities();
        }).catch((error) => {
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
    },
    remove_rarity(rarity: any) {
        Swal.fire({
            title: "Are you sure?",
            text: `Do you really, really want to delete the rarity: ${rarity.name}? This will also delete ALL ITEMS and ITEM TYPES with this rarity!`,
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            confirmButtonText: "Yes, yeet it!",
            cancelButtonText: "No, cancel!",
        }).then((reset: any) => {
            if (reset.isConfirmed) {
                api.remove_rarity(rarity.id).then(() => {
                    Toast.fire({
                        icon: 'success',
                        text: 'Successfully removed',
                    });
                    this.update_rarities();
                    this.update_item_types();
                }).catch((error) => {
                    Toast.fire({
                        icon: 'error',
                        text: error.response.data.description,
                    });
                });
            }
        });
    },
    change_rarity_order(rarity_index: number, change: number) {
        this.changed_rarity_order = true;
        const t = this.rarities[+rarity_index + change];
        this.rarities[+rarity_index + change] = this.rarities[+rarity_index];
        this.rarities[+rarity_index] = t;
    },
    save_rarity_order() {
        api.set_rarity_order(
            Object.fromEntries(this.rarities.map((v: any, i: any) => [i, (v as any).id]))
        ).then(() => {
            Toast.fire({
                icon: 'success',
                text: 'Successfully removed',
            });
            this.update_rarities();
        }).catch((error) => {
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
    },
    update_item_types() {
        this.loading_item_types = true;
        api.get_item_types().then((response: AxiosResponse) => {
            this.item_types = response.data.item_types;
            this.loading_item_types = false;
        }).catch((error) => {
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
    },
    remove_item_type(item_type: any) {
        Swal.fire({
            title: "Are you sure?",
            text: `Do you really, really want to delete the item type: ${item_type.name}? This will also delete ALL ITEMS with this item type!`,
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            confirmButtonText: "Yes, yeet it!",
            cancelButtonText: "No, cancel!",
        }).then((reset: any) => {
            if (reset.isConfirmed) {
                api.remove_item_type(item_type.id).then(() => {
                    Toast.fire({
                        icon: 'success',
                        text: 'Successfully removed',
                    });
                    this.update_item_types();
                }).catch((error) => {
                    Toast.fire({
                        icon: 'error',
                        text: error.response.data.description,
                    });
                });
            }
        });
    },
    create_item_type() {
        let item_action_options = {};
        if (this.create_item_action) {
            item_action_options = this.create_item_action_options[this.create_item_action].options;
        }
        api.create_item_type(
            this.create_item_name,
            +this.create_item_rarity,
            this.create_item_always_visible,
            this.create_item_tradable,
            this.create_item_useable,
            this.create_item_expiration,
            this.create_item_action,
            item_action_options
        ).then(() => {
            Toast.fire({
                icon: 'success',
                text: 'Successfully created item type',
            });
            this.update_item_types();
        }).catch((error) => {
            Toast.fire({
                icon: 'error',
                text: error.response.data.description,
            });
        });
    }
  }
});
</script>
