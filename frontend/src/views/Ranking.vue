<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Ranking</h2>
            <span class="text-gray4">View the ranking of you and your Friends</span>
        </div>

        <div class="text-white bg-gray2">
            
            <div class="d-flex flex-column justify-content-between">
                
                <div class="row" v-for="user in ranking" :key="user.member.id" style="min-width: 400px; max-width: 700px;">
                    <div class="col-12">
                        
                        <div class="d-flex">

                            <div class="js-tilt w-100 shadow bg-gray1 spark-rounded p-3 mb-2">
                                <div class="d-flex">
                                    <div style="width: 100px; height: 100px; margin-right: 1rem;">
                                        <img class="rounded-circle" v-lazy="{src: user.avatar_url, loading: 'https://cdn.discordapp.com/embed/avatars/1.png'}" style="max-width: 100px;">
                                    </div>
                                    <div class="flex-grow-1 d-flex flex-column justify-content-between">
                                        <div>
                                            <div class="d-flex justify-content-between">
                                                <h4 class="mb-0">{{user.name}}</h4>
                                                <h4 class="mb-0">#{{user.rank}}</h4>
                                            </div>
                                        </div>
                                        <div>
                                            <div class="d-flex justify-content-between align-items-end">
                                                <div>
                                                    <span class="text-gray3">Level:</span>
                                                    <span style="font-size: 1.5em; padding-left: 0.25em;">{{user.lvl}}</span>
                                                </div>
                                                <div>
                                                    <span class="text-gray3">{{user.xp}} / {{user.max_xp}} XP</span>
                                                </div>
                                            </div>
                                            <div class="progress" style="border-radius: 3rem;">
                                                <div class="progress-bar default-gradient" role="progressbar" :style="{'width': ''+(user.xp_percentage*100)+'%'}"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <!-- <div class="flex-grow-1 d-flex align-items-center">
                                <div class="w-100" style="height: 2px; background-color: #6c757d;">
                                </div>
                            </div> -->
                        </div>


                    </div>
                    <!-- <div class="col-6">

                        <div class="d-flex align-items-center h-100">
                            <div>

                                <div class="h-100 d-flex justify-content-start align-items-center">
                                    <table class="ms-3 ms-xl-0">
                                        <tbody>
                                            <tr>
                                                <td><h6 class="text-muted mb-0">Best Place:</h6></td>
                                                <td class="ps-3 text-right">#3</td>
                                            </tr>
                                            <tr>
                                                <td><h6 class="text-muted mb-0">Weekly change:</h6></td>
                                                <td class="ps-3 text-success text-right"><i class="fas fa-fw fa-chevron-up"></i> 5</td>
                                            </tr>
                                            <tr>
                                                <td><h6 class="text-muted mb-0">Days active:</h6></td>
                                                <td class="ps-3 text-right">27</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>

                            </div>
                            <div class="d-flex align-items-center mx-4" style="width: 50px;">
                                <div class="w-100" style="height: 2px; background-color: #6c757d;">
                                </div>
                            </div>
                            <div>

                                <div class="h-100 d-flex justify-content-start align-items-center">
                                    <table class="ms-3 ms-xl-0">
                                        <tbody>
                                            <tr>
                                                <td><h6 class="text-muted mb-0">XP until Level-UP:</h6></td>
                                                <td class="ps-3 text-right">234</td>
                                            </tr>
                                            <tr>
                                                <td><h6 class="text-muted mb-0">XP gained this week:</h6></td>
                                                <td class="ps-3 text-right">487</td>
                                            </tr>
                                            <tr>
                                                <td><h6 class="text-muted mb-0">Total XP gained:</h6></td>
                                                <td class="ps-3 text-right">4789</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>

                            </div>
                        </div>

                    </div> -->
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
        ranking: [],
    }
  },
  created() {
    api.get_ranking().then((response: AxiosResponse) => {
        console.log(response.data);
        this.ranking = response.data;
        this.loading = false;
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
