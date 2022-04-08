<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>{{ $filters.i18n('HELP') }}</h2>
            <span class="text-gray4">{{ $filters.i18n('HELP_SUBTITLE') }}</span>
        </div>

        <div class="view-main-card">
            Please send help lol...
        </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "Help",
  mounted() {
      window.location.href = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
  }
});
</script>
