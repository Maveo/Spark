<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Wallet</h2>
            <span class="text-gray4">Overview of your Server Currency Account</span>
        </div>

        <div class="view-main-card p-5">
            
            <div class="row">

                <div class="col-12 col-xl-3 px-5">
                    <h4>Balance</h4>

                    <div class="bg-success mb-3 py-1 px-3 spark-rounded" style="box-shadow: 0 0 2rem #28a745aa !important;">
                        <div class="d-flex justify-content-between" style="font-size: 2rem;">
                            <span>€</span>
                            <span>13.282.533</span>
                        </div>
                    </div>

                    <div>
                        <div class="d-flex justify-content-between align-items-end bg-gray2 px-3 py-1 mb-2 spark-rounded">
                            <div>
                                <div class="text-success" style="font-size: 1.25rem;">+ 200€</div>
                                <div class="text-gray4">vor 2 Std.</div>
                            </div>
                            <div>
                                <div class="text-gold" style="font-size: 1.1rem;">von Seb</div>
                                <div class="text-right text-gray4">#5289</div>
                            </div>
                        </div>
                        <div class="d-flex justify-content-between align-items-end bg-gray2 px-3 py-1 mb-2 spark-rounded" style="border: 2px solid gold;">
                            <div>
                                <div class="text-success" style="font-size: 1.25rem;">+ 100€</div>
                                <div class="text-gray4">vor 1 Tag</div>
                            </div>
                            <div>
                                <div style="color: gold; font-size: 1.1rem;">Aktivitätsbonus</div>
                                <div class="text-right text-gray4">Server</div>
                            </div>
                        </div>
                    </div>

                </div>
                <div class="col-12 col-xl-5 px-5" style="border-left: 1px solid var(--grey2);">
                    <div class="d-flex align-items-end">
                        <h4>Exchange</h4>
                        <span class="text-gray4 mb-2 ms-2">Convert your XP to Currency</span>
                    </div>

                    <div>

                        <div class="bg-gray2 p-3 spark-rounded">
                            <div class="d-flex justify-content-between">
                                <div>
                                    Current XP:
                                </div>
                                <div>
                                    1602/2850 XP
                                </div>
                            </div>
                            <div class="progress" style="height: 10px;">
                                <div class="progress-bar bg-warning" role="progressbar" style="width: 25%;"></div>
                            </div>
                        </div>

                        <div style="position: relative;" class="d-flex justify-content-center">
                            <div>
                                <div style="position: absolute; height: 100%; width: 5px; top: 0; bottom: 0; left: 50%; transform: translate(-50%, 5px); background-image: linear-gradient(var(--green) 33%, rgba(255,255,255,0) 0%);
background-position: right;
background-size: 5px 16px;
background-repeat: repeat-y;">

                                </div>
                            </div>
                            <div class="p-2 px-4 mx-5 my-5 d-flex align-items-center spark-rounded" style="z-index: 10; max-width: 300px; background-color: #2a2a2c;">
                                <div>Convert</div>
                                <input type="number" class="form-control form-control-sm mx-4 font-weight-bold" value="1000">
                                <div>XP</div>
                            </div>
                        </div>

                        <div class="progress spark-rounded" style="height: 2.5rem;">
                            <div class="progress-bar bg-success text-left" role="progressbar" style="width: 35%; font-size: 1.75rem;">
                                <div class="ps-3">
                                    +200€
                                </div>
                            </div>
                        </div>
                        <div class="text-small text-gray3">
                            Daily limit: 400€
                        </div>

                        <div class="bg-gray2 p-3 mt-3 mb-3 spark-rounded">
                            <div class="d-flex justify-content-between">
                                <div>
                                    New XP:
                                </div>
                                <div>
                                    1602/2850 XP
                                </div>
                            </div>
                            <div class="progress" style="height: 10px;">
                                <div class="progress-bar bg-warning" role="progressbar" style="width: 25%;"></div>
                            </div>
                        </div>

                        <div class="d-flex justify-content-center">
                            <button class="btn btn-light">
                                Convert
                            </button>
                        </div>

                    </div>

                </div>
                <div class="col-12 col-xl-4 px-5" style="border-left: 1px solid var(--grey2);">

                    <h4>Bonuses</h4>

                    <div class="bg-gray2 mb-3 py-1 px-3 spark-rounded" style="border: 2px solid gold;">
                        <div>Connect to a voice-channel 7 days in a row</div>
                        <div class="d-flex justify-content-between align-items-center" style="font-size: 1.25rem;">
                            <div>
                                Reward:
                                <div class="badge badge-success">
                                    100€
                                </div>
                            </div>
                            <div>
                                <div class="badge bg-gray1">
                                    2/7 Days
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

            </div>

        </div>

    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
// import HelloWorld from '@/components/HelloWorld.vue'; // @ is an alias to /src

export default defineComponent({
  name: 'Wallet',
  components: {
    // HelloWorld,
  },
});
</script>
