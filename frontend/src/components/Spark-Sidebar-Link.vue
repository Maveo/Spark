<template>
    <li>
        <router-link v-slot="{isActive}" class="nav-link text-white dark-hover" :to="route">
            <div class="d-flex">
                <div class="d-flex justify-content-start align-items-center">
                    <svg :class="['emoji', 'emoji-'+emoji, isActive && gold_active ? 'emoji-gold' : '']"></svg>
                </div>
                <div class="sidebar-hide-collapsed">
                    <div :class="isActive?'ms-2':'text-gray3 ms-2'">{{ title }}</div>
                </div>
            </div>
        </router-link>
    </li>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'SparkSidebar',
  props: {
    title: String,
    emoji: String,
    gold_active: {
      type: Boolean,
      default: true
    },
    route: String
  },
});
</script>
