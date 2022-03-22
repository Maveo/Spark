<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Ranking</h2>
            <span class="text-gray4">View the ranking of you and your Friends</span>
        </div>

        <div class="d-flex text-white bg-gray2" onscroll="console.log('test')">
            
            <div class="d-flex flex-column justify-content-between">
                
                <div class="row profile-cards-loading" v-for="(image, index) in shown_ranking_images" :key="index">
                    <div class="js-tilt new-js-tilt w-100 mb-2">
                        <iframe class="invisible position-absolute" @load="on_iframe_load($event)" scrolling="no" :srcdoc="`<html><head><style>html,body{margin:0}${ranking_style}</style></head><body>${image}</body></html>`">
                        </iframe>
                    </div>
                </div>

                <div v-if="loading" class="row justify-content-center">
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
import { debounceTime, fromEvent } from 'rxjs';

export default defineComponent({
  name: 'Ranking',
  data() {
    return {
        loading: true,
        loading_counter: 0,
        ranking_images: ([] as Array<any>),
        shown_ranking_images: ([] as Array<any>),
        ranking_style: '',
        lazy_subscription: (undefined as any),
        total_amount: 0
    }
  },
  methods: {
    lazy_check() {
        if (!this.loading) {
            return;
        }
        const shown_ranking_divs = document.getElementsByClassName('profile-cards-loading');
        if (shown_ranking_divs.length > 0 && this.in_viewport(shown_ranking_divs[shown_ranking_divs.length - 2])) {
            this.load_next_ranking_batch();
        }
    },
    in_viewport(element: any) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },
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
            ($('.new-js-tilt') as any).tilt({
                scale: 1.05,
                perspective: 1000,
                maxTilt: 15,
            });
            ($('.new-js-tilt') as any).removeClass('new-js-tilt');
        } else if (this.shown_ranking_images.length < this.total_amount) {
            this.lazy_check();
        } else {
            this.loading = false;
        }
    },
    load_next_ranking_batch() {
        const olc = this.loading_counter;
        this.loading_counter += 5;
        api.get_ranking(olc, 5, !this.ranking_style).then((response: AxiosResponse) => {
            console.log(response.data);
            this.ranking_images.push(...response.data.images);
            this.total_amount = response.data.total_amount;
            if (!this.ranking_style) {
                this.ranking_style = response.data.style;
            }
            this.load_next_iframe();
        });
    }
  },
  mounted() {
    const main_container = document.getElementById('mainSiteContainer');
    if (main_container) {
        this.lazy_subscription = fromEvent((document.getElementById('mainSiteContainer') as any), 'scroll').pipe(debounceTime(100)).subscribe(this.lazy_check);
    }
    this.loading_counter = 0;
    this.ranking_images = [];
    this.shown_ranking_images = [];
    this.load_next_ranking_batch();
  },
  beforeUnmount() {
    if (this.lazy_subscription) {
        this.lazy_subscription.unsubscribe();
    }
  },
});
</script>

<style scoped>
.js-tilt:hover iframe {
    z-index: -1;
}
</style>
