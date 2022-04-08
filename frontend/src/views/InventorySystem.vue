<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>{{ $filters.i18n('INVENTORY_SYSTEM_TITLE') }}</h2>
            <span class="text-gray4">{{ $filters.i18n('INVENTORY_SYSTEM_SUBTITLE') }}</span>
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
                                            <button type="button" @click="edit_rarity(rarity, index)" data-bs-toggle="modal" data-bs-target="#createEditItemRarityModal" class="btn btn-info btn-sm col m-1">
                                                <i class="fas fa-fw fa-pen"></i>
                                            </button>
                                            <button type="button" :disabled="index == 0" class="btn btn-info btn-sm col m-1" @click="change_rarity_order(index, -1)">
                                                <i class="fas fa-fw fa-arrow-up"></i>
                                            </button>
                                            <button type="button" :disabled="index == Object.keys(rarities).length - 1" class="btn btn-info btn-sm col m-1" @click="change_rarity_order(index, 1)">
                                                <i class="fas fa-fw fa-arrow-down"></i>
                                            </button>
                                            <button type="button" class="btn btn-danger btn-sm col m-1" @click="remove_rarity(rarity)">
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

                    <button @click="create_rarity()" type="button" class="btn btn-sm btn-success" data-bs-toggle="modal" data-bs-target="#createEditItemRarityModal">
                        Create Item Rarity
                    </button>

                    <div class="modal fade" id="createEditItemRarityModal" tabindex="-1" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content bg-dark p-4">
                                <h4>Item Rarity</h4>
                                <form @submit.prevent="edit_rarity_submit()">
                                    <div class="mb-2">   
                                        <div class="input-group">
                                            <input v-model="edit_create_rarity.name" type="text" class="form-control form-control-sm font-weight-bold" placeholder="Name" required>
                                        </div>
                                    </div>
                                    <div class="mb-2">   
                                        <div class="input-group">
                                            <input v-model="edit_create_rarity.foreground_color" type="text" class="form-control form-control-sm font-weight-bold" placeholder="Foreground Color" required>
                                        </div>
                                    </div>
                                    <div class="mb-2">   
                                        <div class="input-group">
                                            <input v-model="edit_create_rarity.background_color" type="text" class="form-control form-control-sm font-weight-bold" placeholder="Background Color" required>
                                        </div>
                                    </div>
                                    <div class="">
                                        <button type="submit" class="btn btn-success btn-sm w-100 font-weight-bold">
                                            {{edit_create_rarity_text}}
                                        </button>
                                    </div>
                                </form>
                                
                                <button id="closeCreateEditItemRarityModal" class="d-none" data-bs-dismiss="modal"></button>
                            </div>
                        </div>
                    </div>
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
                                            <button @click="edit_item_type(item)" type="button" class="btn btn-info btn-sm col m-1" data-bs-toggle="modal" data-bs-target="#createEditItemTypeModal">
                                                <i class="fas fa-fw fa-pen"></i>
                                            </button>
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
                    <button @click="create_item_type()" type="button" class="btn btn-sm btn-success" data-bs-toggle="modal" data-bs-target="#createEditItemTypeModal">
                        Create Item Type
                    </button>

                    <div class="modal fade" id="createEditItemTypeModal" tabindex="-1" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content bg-dark p-4">
                                <h4>Item Type</h4>
                                <form @submit.prevent="edit_item_type_submit()">
                                    <div class="mb-2">   
                                        <div class="input-group input-group-sm">
                                            <span class="input-group-text">Name</span>
                                            <input v-model="edit_create_item_type.name" type="text" class="form-control form-control-sm font-weight-bold" placeholder="Name" required>
                                        </div>
                                    </div>
                                    <div class="mb-2">   
                                        <div class="input-group input-group-sm">
                                            <span class="input-group-text">Rarity</span>
                                            <select v-model="edit_create_item_type.rarity_id" class="form-select form-select-sm" required>
                                                <option value="" disabled selected hidden>Choose rarity...</option>
                                                <option :value="rarity.id" v-for="(rarity, index) in rarities" :key="rarity.id">{{index + 1}}. {{rarity.name}}</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="mb-2">   
                                        <div class="form-check form-check-inline">
                                            <input v-model="edit_create_item_type.always_visible" class="form-check-input" type="checkbox" id="alwaysVisibleCheckbox">
                                            <label class="form-check-label" for="alwaysVisibleCheckbox">
                                                Always visible
                                            </label>
                                        </div>
                                        <div class="form-check form-check-inline">
                                            <input v-model="edit_create_item_type.tradable" class="form-check-input" type="checkbox" value="" id="tradableCheckbox">
                                            <label class="form-check-label" for="tradableCheckbox">
                                                Tradable
                                            </label>
                                        </div>
                                        <div class="form-check form-check-inline">
                                            <input v-model="edit_create_item_type.equippable" class="form-check-input" type="checkbox" value="" id="equippableCheckbox">
                                            <label class="form-check-label" for="equippableCheckbox">
                                                Equippable
                                            </label>
                                        </div>
                                    </div>
                                    <div class="mb-2">   
                                        <div class="input-group input-group-sm">
                                            <button type="button" class="btn btn-secondary" :class="{'active': edit_create_item_type.useable == -1}" @click="edit_create_item_type.useable = -1">
                                                Force use
                                            </button>
                                            <button type="button" class="btn btn-secondary" :class="{'active': edit_create_item_type.useable == 0}" @click="edit_create_item_type.useable = 0">
                                                Not Useable
                                            </button>
                                            <button type="button" class="btn btn-secondary" :class="{'active': edit_create_item_type.useable == 1}" @click="edit_create_item_type.useable = 1">
                                                Useable Once
                                            </button>
                                            <button type="button" class="btn btn-secondary" :class="{'active': edit_create_item_type.useable == 2}" @click="edit_create_item_type.useable = 2">
                                                Infinite use
                                            </button>
                                        </div>
                                    </div>
                                    <template v-for="(action, index) in edit_create_item_type.actions" :key="index">
                                        <div class="mb-2 d-flex">   
                                            <div class="input-group input-group-sm me-1">
                                                <span class="input-group-text">Action</span>
                                                <select v-model="action.action" class="form-select form-select-sm" required>
                                                    <option value="" selected>Choose action...</option>
                                                    <option :value="action_id" v-for="(iaction, action_id) in action.action_options" :key="action_id">{{iaction.name}}</option>
                                                </select>
                                            </div>
                                            <button type="button" class="btn btn-danger btn-sm" @click="edit_create_item_type.actions.splice(index, 1)">
                                                <i class="fas fa-fw fa-trash"></i>
                                            </button>
                                        </div>
                                        <template v-for="(iaction, action_id) in action.action_options" :key="action_id">
                                            <template v-if="action.action == action_id">
                                                <div v-for="(option, id) in iaction.options" :key="id" class="mb-2">
                                                    <div class="input-group input-group-sm">
                                                        <span class="input-group-text">{{option.description}}</span>
                                                        <input v-if="option.type == 'int'" v-model="option.value" type="number" class="form-control form-control-sm font-weight-bold" required>
                                                        <input v-if="option.type == 'float'" v-model="option.value" type="number" step="0.0001" class="form-control form-control-sm font-weight-bold" required>
                                                        <input v-else-if="option.type == 'str'" v-model="option.value" type="text" class="form-control form-control-sm font-weight-bold" required>
                                                        <textarea v-else-if="option.type == 'text'" v-model="option.value" type="text" rows="4" class="form-control form-control-sm font-weight-bold" required />
                                                    </div>
                                                </div>
                                            </template>
                                        </template>
                                    </template>
                                    <div class="mb-2">
                                        <button type="button" class="btn btn-success btn-sm font-weight-bold" @click="add_edit_create_item_type_action()">
                                            Add action
                                        </button>
                                    </div>
                                    <div class="">
                                        <button type="submit" class="btn btn-success btn-sm w-100 font-weight-bold">
                                            {{edit_create_item_type_text}}
                                        </button>
                                    </div>
                                </form>
                                
                                <button id="closeCreateEditItemTypeModal" class="d-none" data-bs-dismiss="modal"></button>
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
        edit_create_rarity: ({} as any),
        edit_create_rarity_text: '',
        loading_item_types: true,
        item_types: [],
        item_action_options: ({} as any),
        edit_create_item_type: ({} as any),
        edit_create_item_type_text: ''
    }
  },
  mounted() {
      this.create_rarity();
      this.create_item_type();
      this.update_rarities();
      this.update_item_types();
      api.get_item_action_options().then((response: AxiosResponse) => {
            this.item_action_options = response.data.actions;
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
    create_rarity() {
        this.edit_create_rarity = {
            name: '',
            foreground_color: '',
            background_color: '',
        };
        this.edit_create_rarity_text = 'Create Rarity';
    },
    edit_rarity(rarity: any, index: number) {
        this.edit_create_rarity = rarity;
        this.edit_create_rarity_text = `Edit Rarity (${index}. ${rarity.name})`;
    },
    edit_rarity_submit() {
        document.getElementById('closeCreateEditItemRarityModal')?.click();
        console.log(this.edit_create_rarity);
        api.edit_rarity(this.edit_create_rarity).then(() => {
            Toast.fire({
                icon: 'success',
                text: 'Successful',
            });
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
    create_item_type() {
        this.edit_create_item_type = {
            name: '',
            rarity_id: '',
            useable: -1,
            always_visible: false,
            tradable: false,
            equippable: false,
            actions: [],
        };
        this.edit_create_item_type_text = 'Create Item Type';
    },
    edit_item_type(item: any) {
        console.log(item);
        this.edit_create_item_type = item;
        for (let action of this.edit_create_item_type.actions) {
            let new_action_options = JSON.parse(JSON.stringify(this.item_action_options));
            for (let option_key of Object.keys(action.action_options)) {
                new_action_options[action.action].options[option_key].value = action.action_options[option_key];
            }
            action.action_options = new_action_options;
        }
        this.edit_create_item_type_text=`Edit Item (ID: ${item.id})`;
    },
    add_edit_create_item_type_action() {
        this.edit_create_item_type.actions.push({
            action: '',
            action_options: JSON.parse(JSON.stringify(this.item_action_options))
        });
    },
    edit_item_type_submit() {
        document.getElementById('closeCreateEditItemTypeModal')?.click();
        for (let action of this.edit_create_item_type.actions) {
            action.action_options = action.action_options[action.action].options;
        }
        api.edit_item_type(
            this.edit_create_item_type
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
  }
});
</script>
