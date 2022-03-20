<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Ranking</h2>
            <span class="text-gray4">View the ranking of you and your Friends</span>
        </div>

        <div class="d-flex text-white bg-gray2">
            
            <div class="d-flex flex-column justify-content-between">
                
                <div class="row" v-for="(image, index) in shown_ranking_images" :key="index">
                    <div class="js-tilt w-100 mb-2">
                        <iframe class="invisible position-absolute" @load="on_iframe_load($event)" scrolling="no" :srcdoc="`<html><head><style>html,body{margin:0}${ranking_style}</style></head><body>${image}</body></html>`">
                        </iframe>
                    </div>
                </div>

                <div v-if="loading" class="row">
                    <div class="shadow bg-gray1 spark-rounded p-3 mb-2 text-center" style="width: 500px;">
                        <span class="spinner-border spinner-border-lg" role="status" aria-hidden="true"></span>
                    </div>
                </div>

            </div>
        </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import $ from "jquery";
require('tilt.js/dest/tilt.jquery.min.js');
import api from '@/services/api';
import { AxiosResponse } from 'axios';

export default defineComponent({
  name: 'Ranking',
  data() {
    return {
        loading: true,
        ranking_images: [],
        shown_ranking_images: [],
        ranking_style: ''
    }
  },
  methods: {
    on_iframe_load(event: any) {
        const iframe = event.target ? event.target : event.path[0];
        iframe.width  = iframe.contentWindow.document.body.scrollWidth;
        iframe.height = iframe.contentWindow.document.body.scrollHeight;
        iframe.classList.remove('invisible');
        iframe.classList.remove('position-absolute');
        this.load_next_iframe();
    },
    load_next_iframe() {
        if (this.ranking_images.length > this.shown_ranking_images.length) {
            this.shown_ranking_images.push(this.ranking_images[this.shown_ranking_images.length]);
        } else {
            this.loading = false;
        }
    }
  },
  created() {
    api.get_ranking().then((response: AxiosResponse) => {
        console.log(response.data);
        this.ranking_images = response.data.images;
        this.shown_ranking_images = [];
        this.ranking_style = response.data.style;
        this.load_next_iframe();
    });
  },
  updated() {
    ($('.js-tilt') as any).tilt({
        scale: 1.05,
        perspective: 1000,
        maxTilt: 15,
    });
    
  },
});
</script>

<style scoped>
.js-tilt:hover iframe {
    z-index: -1;
}
</style>
