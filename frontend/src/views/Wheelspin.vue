<template>
    <div class="container container-large">

        <div class="pb-5">
            <h2>Wheelspin</h2>
            <span class="text-gray4">Win daily prizes</span>
        </div>

        <div class="view-main-card">
            
            <div class="row">

                <div class="col-3 px-4">
                    <h4>Prizes</h4>

                    <div>
                        <div class="bg-gray2 px-3 py-1 mb-2 text-center spark-rounded" style="border: 3px solid gold; background-color: #65c1c4;">
                            <div style="font-size: 1.5rem;">5000 XP</div>
                            <div style="font-size: 0.75rem;">Receive a fixed amount of XP instantly</div>
                        </div>
                        <div class="bg-gray2 px-3 py-1 mb-2 text-center spark-rounded" style="background-color: #ebb55f;">
                            <div style="font-size: 1.5rem;">4x XP-Multiplier</div>
                            <div style="font-size: 0.75rem;">Get a 4x SP-Multiplier for 3 Days</div>
                        </div>
                        <div class="bg-gray2 px-3 py-1 mb-2 text-center spark-rounded" style="background-color: #248d41;">
                            <div style="font-size: 1.5rem;">+1 Usable Boost</div>
                            <div style="font-size: 0.75rem;">1 additional boost to use on the server</div>
                        </div>
                        <div class="bg-gray2 px-3 py-1 mb-2 text-center spark-rounded" style="background-color: #248d41;">
                            <div style="font-size: 1.5rem;">2x XP-Multiplier</div>
                            <div style="font-size: 0.75rem;">Get a 2x XP-Multiplier for 1 Day</div>
                        </div>
                        <div class="bg-gray2 px-3 py-1 mb-2 text-center spark-rounded" style="background-color: var(--grey2);">
                            <div style="font-size: 1.5rem;">Key to the Secret Room</div>
                            <div style="font-size: 0.75rem;">Get access to the Secret Room for 1 Day</div>
                        </div>
                        <div class="bg-gray2 px-3 py-1 mb-2 text-center spark-rounded" style="background-color: var(--grey2);">
                            <div style="font-size: 1.5rem;">+1 Spin</div>
                            <div style="font-size: 0.75rem;">Try again</div>
                        </div>
                    </div>

                </div>
                <div class="col-5 px-4" style="border-left: 1px solid var(--grey2);">

                    <div class="d-flex justify-content-center flex-column mt-4">

                        <div class="d-flex justify-content-center" style="position: relative;">

                            <!-- Triangle outer -->
                            <div style="z-index: 2; position: absolute; top: -20px; width: 50px; height: 50px; border: 30px solid transparent; border-top: 50px solid gold;">

                            </div>

                            <!-- Triangle inner -->
                            <div style="z-index: 2; position: absolute; top: -25px; width: 50px; height: 50px; border: 30px solid transparent; border-top: 50px solid var(--grey1); transform: scale(0.8);">

                            </div>

                            <!-- Wheel -->
                            <div style="background-color: gold; width: 400px; height: 400px; border-radius: 50%; padding: 10px;">
                                <div id="spin_wrapper m-auto">
                                    <svg xmlns="http://www.w3.org/2000/svg" id="spin" width="100%" height="100%" viewBox="0 0 100 100"></svg>
                                </div>
                            </div>

                        </div>

                        <div class="text-center mt-4">
                            <button class="btn btn-secondary btn-nofocus" style="max-width: 100px;" @click.prevent="spark_start_spin" :disabled="!can_spin">Spin</button>
                        </div>

                    </div>

                </div>
                <div class="col-4 px-4" style="border-left: 1px solid var(--grey2);">

                    <div class="mb-4">
                        <h4>Spins</h4>

                        <div class="bg-gray2 px-3 py-1 mb-1 text-center spark-rounded" style="max-width: 200px;">
                            <div style="font-size: 1.5rem; color: var(--green);">∞ Spins</div>
                        </div>
                        <div class="text-gray4">
                            Get your next one instantly.
                        </div>
                    </div>

                    <div>
                        <h4>History</h4>

                        <div>
                            <transition-group name="list-complete">
                                <div v-for="spin in history" :key="spin" class="list-complete-item bg-gray2 px-3 py-2 mb-2 spark-rounded w-100">
                                    <div class="d-flex justify-content-between">
                                        <div style="font-size: 1.5rem;">{{ spin.value }}</div>
                                        <div class="pt-1">{{ spin.timestamp }}</div>
                                    </div>
                                    <div style="font-size: 0.75rem;">Hash: 123456789123456789123456789123456789</div>
                                </div>
                            </transition-group>
                        </div>
                    </div>

                </div>


            </div>

        </div>

    </div>
</template>

<style scoped>
#spin_wrapper {
	/* position: fixed; */
	top: 50%;
	left: 50%;
	width: 300px;
	height: 300px;
	margin-top: -150px;
	margin-left: -150px;
	border-radius: 50%;
	background: #ffffff;
	border: 2px solid #ffffff;
	box-shadow: 0px 2px 5px 1px rgba(0,0,0, 0.3);
    transform: translate(50%,50%);
}

#spin {
	transform-origin: 50% 50%;
}

.list-complete-item {
  transition: all 0.8s ease;
  display: inline-block;
}

.list-complete-enter-from,
.list-complete-leave-to {
  opacity: 0;
}

</style>

<script lang="ts">
import { defineComponent } from 'vue';
// import HelloWorld from '@/components/HelloWorld.vue'; // @ is an alias to /src

import {Howl, Howler} from 'howler';

// const confetti = require('canvas-confetti');
import Confetti from 'canvas-confetti';
import $ from 'jquery';
require('jquery-ui/ui/effect')

import moment from 'moment';

export default defineComponent({
  name: 'Wheelspin',
  components: {
    // HelloWorld,
  },
  data()
  {
      return {
          can_spin: true,
          history: [
              {
                value: '+1 Boost',
                timestamp: '2021-10-01 15:00:00'
              }
          ]
      }
  },
  created()
  {

      const that = this;

        (<any>window).requestAnimFrame = (function(){
            return  window.requestAnimationFrame       ||
                window.webkitRequestAnimationFrame ||
                (<any>window).mozRequestAnimationFrame    ||
                function(callback){window.setTimeout(callback, 1000 / 60);};
        })();


    function polarToCartesian(centerX:any, centerY:any, radius:any, angleInDegrees:any) {
        var angleInRadians = (angleInDegrees-90) * Math.PI / 180.0;
        return {
            x: centerX + (radius * Math.cos(angleInRadians)),
            y: centerY + (radius * Math.sin(angleInRadians))
        };
    }
    function arcPath(x:any, y:any, radius:any, endradius:any, startAngle:any, endAngle:any) {
        var start = polarToCartesian(x, y, radius, endAngle);
        var end = polarToCartesian(x, y, radius, startAngle);
        var start2 = polarToCartesian(x, y, endradius, endAngle);
        var end2 = polarToCartesian(x, y, endradius, startAngle);
        var largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
        var d = [
            "M", start.x, start.y, 
            "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y,
            "L", end2.x, end2.y,
            "A", endradius, endradius, 0, largeArcFlag, 1, start2.x, start2.y,
            "Z"
        ].join(" ");
        return d;
    }

    var spin = {
        slots: [
            {value:'5000 XP', color: '#65c1c4'},
            {value:'X', color: '#d44040'},
            {value:'2x Multiplier', color: '#248d41'},
            {value:'Secret Key', color: '#444951'},
            {value:'4x Multiplier', color: '#ebb55f'},
            {value:'X', color: '#d44040'},
            {value:'+1 Boost', color: '#248d41'},
            {value:'+1 Spin', color: '#444951'},
        ],
        speed: 0,
        spinSpeed: 10,
        degree: 0,
        obj: null,
        stop: false,
        min_duration: 3000,
        max_duration: 8000,
        rand_speed: 0,
    };

    var spin_anim = function(){
        if ( spin.stop ) { return true; }
        spin.degree = filter_degree(spin.degree + spin.speed);
        (<any>spin).obj.css('transform', 'rotate(' + spin.degree + 'deg)');
        (<any>window).requestAnimFrame(spin_anim);
    };

    function filter_degree(d:any) {
        while (d<0){
            d += 360;
        }
        return (d%360);
    }

    function spin_start() {
        that.can_spin = false;
        spin.stop = false;
        spin_anim();
        spin.rand_speed = Math.random();
        $( spin ).animate({speed: spin.spinSpeed}, 0.15*spin.min_duration, "easeInBack", function(){
            $( spin ).animate({speed: 0}, (spin.min_duration + (spin.max_duration-spin.min_duration)*spin.rand_speed), "easeOutSine", function(){
                spin_stop();
            });
        });
    }
    (<any>window).spin_start = spin_start;

    function spin_stop() {
        spin.stop = true;
        var values = (<any>spin).obj.css('transform'),
            values = values.split('(')[1],
            values = values.split(')')[0],
            values = values.split(',');
        var d = filter_degree( Math.atan2(values[1], values[0]) * (180/Math.PI) );
        var p = (360/spin.slots.length);
        var slot = Math.floor((360-d) / p);
        console.log(d + ' => slot #' + slot + ' => ' + spin.slots[slot].value );

        // alert( spin.slots[slot].value );
        console.log('You spinned: ' + spin.slots[slot].value);

        that.playSound(spin.slots[slot].value);
    }

    $(document).ready(function(){
        (<any>spin).obj = $('#spin');
        
        var slot_count = spin.slots.length;
        var svg = '';
        var t:any = 0;
        for (var i=0; i<slot_count; i++) {
            // t = polarToCartesian(50, 50, 30, ((i+0.5)*(360/slot_count)) );
            t = polarToCartesian(50, 50, 30, ((i+0.5)*(360/slot_count)) );
            svg = svg + '<path d="' + arcPath(50,50, 0, 50, (i*(360/slot_count)), ((i+1)*(360/slot_count))) + '" fill="' + spin.slots[i].color + '" stroke="#ffffff" stroke-width="0" />';
            // svg = svg + '<text font-size="6" x="' + t.x + '" y="' + t.y + '" fill="#000000" font-style="bold" font-family="Arial" alignment-baseline="central" text-anchor="middle" transform="rotate(' + (1*((i+0.5)*(360/slot_count))) + ' ' + t.x + ',' + t.y + ')" stroke="#000000" stroke-width="1" opacity="0.3">' + spin.slots[i].value + '</text>';
            // svg = svg + '<text font-size="6" x="' + t.x + '" y="' + t.y + '" fill="#ffffff" font-style="bold" font-family="Arial" alignment-baseline="central" text-anchor="middle" transform="rotate(' + (1*((i+0.5)*(360/slot_count))) + ' ' + t.x + ',' + t.y + ')">' + spin.slots[i].value + '</text>';
            svg = svg + '<text font-size="6" x="' + t.x + '" y="' + t.y + '" fill="#ffffff" font-style="bold" font-family="Arial" alignment-baseline="central" text-anchor="middle" transform="rotate(' + ((1*((i+0.5)*(360/slot_count)))+90) + ' ' + (t.x) + ',' + (t.y) + ') translate(0,1.6)">' + spin.slots[i].value + '</text>';
        }
        $('#spin').html( svg );
        
        spin.degree = Math.random()*360;
        (<any>spin).obj.css('transform', 'rotate(' + spin.degree + 'deg)');

        $('#start').click(function(e:any){
            e.preventDefault();
            spin_start();
        });
        $('#stop').click(function(e:any){
            e.preventDefault();
            spin_stop();
        });
    });

  },
  methods:
  {
      addHistory(value:any, timestamp:any) {
      this.history.splice(0, 0, { value, timestamp  })
    },
    removeHistory() {
      this.history.splice(this.history.length-1, 1)
    },
      spark_start_spin()
      {
        (<any>window).spin_start();
      },
      playSound(result: any)
      {
            if (this.history.length >= 3)
            {
                this.removeHistory();
            }
            this.addHistory(result, moment().format('YYYY-MM-DD HH:mm:ss'));

            if (result != 'X')
            {
                Howler.volume(0.2);
                var sound = new Howl({
                    src: [ require('@/assets/sfx/209578__zott820__cash-register-purchase.wav') ],
                    html5: true
                });
    
                sound.play();
    
                this.fireConfetti();
            }

            this.can_spin = true;

      },

      fireConfetti()
      {
          var count = 200;
        var defaults = {
            origin: { y: 0.5, x: 0.55 }
        };

        function fire(particleRatio: any, opts: any) {
            Confetti(Object.assign({}, defaults, opts, {
                particleCount: Math.floor(count * particleRatio)
            }));
        }

        fire(0.25, {
            spread: 26,
            startVelocity: 55,
        });
        fire(0.2, {
            spread: 60,
        });
        fire(0.35, {
            spread: 100,
            decay: 0.91,
            scalar: 0.8
        });
        fire(0.1, {
            spread: 120,
            startVelocity: 25,
            decay: 0.92,
            scalar: 1.2
        });
        fire(0.1, {
            spread: 120,
            startVelocity: 45,
        });
      }
  }
});
</script>
