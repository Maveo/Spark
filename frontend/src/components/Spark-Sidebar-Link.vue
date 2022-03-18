<template>
    <li>
        <router-link v-slot="{isActive}" class="nav-link text-white dark-hover" :to="route">
            <div class="d-flex">
                <div class="d-flex justify-content-left align-items-end" style="width: 28px;">
                    <svg :class="[isActive ? 'd-none' : 'd-inline', 'emoji', 'emoji-'+emoji]"></svg>
                    <svg v-if="isActive" :class="['emoji', 'emoji-'+emoji, 'emoji-gold']"></svg>
                </div>
                <div>
                    <div v-if="!isActive" class="text-gray3">{{ title }}</div>
                    <div v-if="isActive">{{ title }}</div>
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
    route: String
  },
});
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
