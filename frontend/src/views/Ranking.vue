<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Ranking</h2>
            <span class="text-gray4">View the ranking of you and your Friends</span>
        </div>

        <div class="d-flex text-white bg-gray2">
            
            <div class="d-flex flex-column justify-content-between w-100">
                
                <div class="row profile-cards-loading" v-for="(image, index) in ranking_images" :key="index">
                    <svg class="js-tilt new-js-tilt position-absolute invisible mb-2 p-0" style="width: 600px; height: 100%;" v-html="image"></svg>
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
        if (shown_ranking_divs.length > 1 && this.in_viewport(shown_ranking_divs[shown_ranking_divs.length - 2])) {
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
            if (this.ranking_images.length >= this.total_amount) {
                this.loading = false;
            }
            this.lazy_check();
        });
    }
  },
  updated() {
    ($('.new-js-tilt') as any).tilt({
        scale: 1.05,
        perspective: 1000,
        maxTilt: 15,
    });
    ($('.new-js-tilt') as any).removeClass('new-js-tilt position-absolute invisible');
  },
  mounted() {
    const main_container = document.getElementById('mainSiteContainer');
    if (main_container) {
        this.lazy_subscription = fromEvent((document.getElementById('mainSiteContainer') as any), 'scroll').pipe(debounceTime(100)).subscribe(this.lazy_check);
    }
    this.loading_counter = 0;
    this.ranking_images = [];
    this.load_next_ranking_batch();
  },
  beforeUnmount() {
    if (this.lazy_subscription) {
        this.lazy_subscription.unsubscribe();
    }
  },
});
</script>
