<template>
  <div class="container container-large">
    <div class="pb-5">
      <h2>{{ $filters.i18n('WHEELSPIN_TITLE') }}</h2>
      <span class="text-gray4">{{ $filters.i18n('WHEELSPIN_SUBTITLE') }}</span>
    </div>

    <div class="view-main-card">
      <div class="row">
        <div class="col-xxl-3 px-4">
          <h4>{{ $filters.i18n('WHEELSPIN_PRIZES') }}</h4>
          <div v-if="wheelspin_loading" class="spinner-border"></div>
          <div v-else>
            <div
              v-for="item in wheelspin"
              :key="item.id"
              class="px-3 py-1 mb-2 text-center spark-rounded"
              :style="'background-image: ' + item.background_color_html"
            >
              <h2
                class="background-text"
                :style="'background-image: ' + item.foreground_color_html"
              >
                {{ item.name }}
              </h2>
            </div>
          </div>
        </div>
        <div class="col-xxl-5 px-4">
          <div class="d-none d-xxl-block vertical-divider"></div>
          <div
            v-if="!wheelspin_loading"
            class="d-flex justify-content-center flex-column mt-4"
          >
            <div
              class="d-flex justify-content-center"
              style="position: relative"
            >
              <!-- Triangle outer -->
              <div
                style="
                  z-index: 2;
                  position: absolute;
                  top: -20px;
                  width: 50px;
                  height: 50px;
                  border: 30px solid transparent;
                  border-top: 50px solid gold;
                "
              ></div>

              <!-- Triangle inner -->
              <div
                style="
                  z-index: 2;
                  position: absolute;
                  top: -25px;
                  width: 50px;
                  height: 50px;
                  border: 30px solid transparent;
                  border-top: 50px solid var(--grey1);
                  transform: scale(0.8);
                "
              ></div>

              <!-- Wheel -->
              <div
                style="
                  background-color: gold;
                  width: 400px;
                  border-radius: 50%;
                  padding: 10px;
                "
              >
                <div id="spin_wrapper m-auto">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    id="spin"
                    width="100%"
                    height="100%"
                    viewBox="0 0 100 100"
                  ></svg>
                </div>
              </div>
            </div>

            <div class="text-center mt-4">
              <button
                class="btn btn-secondary btn-nofocus"
                style="max-width: 100px"
                @click.prevent="spark_start_spin"
                :disabled="!can_spin"
              >
                {{ $filters.i18n('WHEELSPIN_SPIN') }}
              </button>
            </div>
          </div>
        </div>
        <div class="col-xxl-4 px-4">
          <div class="d-none d-xxl-block vertical-divider"></div>

          <div class="mb-4">
            <h4>{{ $filters.i18n('WHEELSPIN_SPINS') }}</h4>

            <div
              class="bg-gray2 px-3 py-1 mb-1 text-center spark-rounded"
              style="max-width: 200px"
            >
              <div v-if="free_wheelspin_in <= 0" style="font-size: 1.5rem">
                {{ $filters.i18n('WHEELSPIN_FREE_SPIN') }}
              </div>
              <div v-else style="font-size: 1.5rem">
                {{ $filters.i18n('WHEELSPIN_AVAILABLE_SPINS', [wheelspins_available]) }}
              </div>
            </div>
            <div v-if="free_wheelspin_in > 0" class="text-gray4">
              {{ $filters.i18n('WHEELSPIN_NEXT_FREE', [+(free_wheelspin_in / 3600).toFixed(0) + 1]) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="profile.is_admin" class="view-main-card mt-3">
      <h4 class="px-2 mb-3">Setup</h4>
      <a
        href="#"
        class="btn btn-nofocus text-white text-nowrap btn-toggle collapsed"
        data-bs-toggle="collapse"
        data-bs-target="#collapseWheelspinSetup"
      >
        <i class="fas fa-fw toggle-icon"></i>
        Show
      </a>

      <form
        @submit.prevent="set_probabilities()"
        class="collapse"
        id="collapseWheelspinSetup"
      >
        <div v-for="(value, index) in admin_items_probabilities" :key="index">
          <div class="d-flex justify-content-center mb-2">
            <span class="text-nowrap">ID: {{value.id}}</span>
            <div class="input-group input-group-sm">
              <span class="input-group-text">Item Type</span>
              <select
                v-model="value.item_type_id"
                class="form-select form-select-sm"
                required
              >
                <option value="" disabled selected hidden>
                  Choose Item type...
                </option>
                <option
                  :value="item_type.id"
                  v-for="item_type in admin_item_types"
                  :key="item_type.id"
                >
                  ID: {{ item_type.id }} | {{ item_type.name }}
                </option>
              </select>
            </div>
            <div class="input-group input-group-sm">
              <span class="input-group-text">Probability</span>
              <input
                v-model="value.probability"
                type="number"
                step="0.0001"
                class="form-control form-control-sm font-weight-bold"
                placeholder="1"
                required
              />
            </div>
            <div class="input-group input-group-sm">
              <span class="input-group-text">Amount</span>
              <input
                v-model="value.amount"
                type="number"
                step="0.0001"
                class="form-control form-control-sm font-weight-bold"
                placeholder="1"
                required
              />
            </div>
            <div class="form-check form-check-inline">
              <input
                v-model="value.sound"
                class="form-check-input"
                type="checkbox"
                :id="'playSound' + index"
              />
              <label class="form-check-label" :for="'playSound' + index">
                Sound
              </label>
            </div>
            <button
              :disabled="admin_items_loading || index == 0"
              type="button"
              class="btn btn-sm btn-info ms-2"
              @click="change_admin_items_probabilities_order(index, -1)"
            >
              <i class="fas fa-fw fa-arrow-up"></i>
            </button>
            <button
              :disabled="admin_items_loading || index == admin_items_probabilities.length - 1"
              type="button"
              class="btn btn-sm btn-info ms-2"
              @click="change_admin_items_probabilities_order(index, 1)"
            >
              <i class="fas fa-fw fa-arrow-down"></i>
            </button>
            <button
              :disabled="admin_items_loading"
              type="button"
              class="btn btn-sm btn-danger ms-2"
              @click="admin_items_probabilities.splice(index, 1)"
            >
              <i class="fas fa-fw fa-trash"></i>
            </button>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <button
              type="button"
              :disabled="admin_items_loading"
              class="w-100 btn btn-info btn-sm"
              @click="
                admin_items_probabilities.push({
                  item_type_id: '',
                  probability: 1,
                  amount: 1,
                  sound: false,
                })
              "
            >
              <i class="fas fa-fw fa-plus"></i>
            </button>
          </div>
          <div class="col">
            <button
              type="submit"
              :disabled="admin_items_loading"
              class="w-100 btn btn-success btn-sm"
            >
              Save
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import { Howl, Howler } from "howler";

import Confetti from "canvas-confetti";
import $ from "jquery";
import api from "@/services/api";
import { AxiosResponse } from "axios";
import store from "@/store";

// eslint-disable-next-line @typescript-eslint/no-var-requires
let Swal = require("sweetalert2/src/sweetalert2.js").default;

const Toast = Swal.mixin({
  toast: true,
  position: "top-end",
  showConfirmButton: false,
  timer: 3000,
});

export default defineComponent({
  name: "Wheelspin",
  data() {
    return {
      wheelspin_loading: true,
      free_wheelspin_in: 1,
      wheelspins_available: 0,
      wheelspin: [] as any,
      profile: store.state.profile,
      admin_items_loading: true,
      admin_item_types: [],
      admin_items_probabilities: [],
      can_spin: false,
    };
  },
  created() {
    this.update_wheelspin();

    if (this.profile.is_admin) {
      this.update_admin_wheelspin();
    }
  },
  methods: {
    update_admin_wheelspin() {
        api
        .get_item_types()
        .then((response: AxiosResponse) => {
          this.admin_item_types = response.data.item_types;
        })
        .catch((error) => {
          Toast.fire({
            icon: "error",
            text: error.response.data.description,
          });
        });
      this.admin_items_loading = true;
      api
        .get_wheelspin_admin()
        .then((response: AxiosResponse) => {
          this.admin_items_probabilities = response.data.wheelspin;
          this.admin_items_loading = false;
        })
        .catch((error) => {
          Toast.fire({
            icon: "error",
            text: error.response.data.description,
          });
          this.admin_items_loading = false;
        });
    },
    update_wheelspin() {
        this.wheelspin_loading = true;
    api
      .get_wheelspin()
      .then((response: AxiosResponse) => {
        this.wheelspin = response.data.wheelspin;
        this.update_can_spin(() => {
          this.wheelspin_loading = false;
          this.setup_wheelspin();
        });
      })
      .catch((error) => {
        Toast.fire({
          icon: "error",
          text: error.response.data.description,
        });
        this.wheelspin_loading = false;
      });
    },
    update_can_spin(cb: any = undefined) {
      api
        .can_wheelspin()
        .then((response: AxiosResponse) => {
          this.wheelspins_available = response.data.wheelspins_available;
          this.free_wheelspin_in = response.data.free_wheelspin_in;
          this.can_spin =
            this.wheelspins_available >= 1 || this.free_wheelspin_in <= 0;
          if (cb) cb();
        })
        .catch((error) => {
          Toast.fire({
            icon: "error",
            text: error.response.data.description,
          });
          this.wheelspin_loading = false;
        });
    },
    change_admin_items_probabilities_order(index: number, change: number) {
        let t = this.admin_items_probabilities[index];
        this.admin_items_probabilities[index] = this.admin_items_probabilities[index + change];
        this.admin_items_probabilities[index + change] = t;
    },
    set_probabilities() {
      this.admin_items_loading = true;

      api
        .set_wheelspin(this.admin_items_probabilities)
        .then(() => {
          Toast.fire({
            icon: "success",
            text: "Successful",
          });
          this.update_admin_wheelspin();
          this.update_wheelspin();
        })
        .catch((error) => {
          Toast.fire({
            icon: "error",
            text: error.response.data.description,
          });
          this.update_admin_wheelspin();
        });
    },
    setup_wheelspin() {
      // eslint-disable-next-line @typescript-eslint/no-this-alias
      const that = this;

      (window as any).requestAnimFrame = (function () {
        return (
          window.requestAnimationFrame ||
          (window as any).webkitRequestAnimationFrame ||
          (window as any).mozRequestAnimationFrame ||
          function (callback: any) {
            window.setTimeout(callback, 1000 / 60);
          }
        );
      })();

      function polarToCartesian(
        centerX: any,
        centerY: any,
        radius: any,
        angleInDegrees: any
      ) {
        var angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
        return {
          x: centerX + radius * Math.cos(angleInRadians),
          y: centerY + radius * Math.sin(angleInRadians),
        };
      }
      function arcPath(
        x: any,
        y: any,
        radius: any,
        endradius: any,
        startAngle: any,
        endAngle: any
      ) {
        var start = polarToCartesian(x, y, radius, endAngle);
        var end = polarToCartesian(x, y, radius, startAngle);
        var start2 = polarToCartesian(x, y, endradius, endAngle);
        var end2 = polarToCartesian(x, y, endradius, startAngle);
        var largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
        var d = [
          "M",
          start.x,
          start.y,
          "A",
          radius,
          radius,
          0,
          largeArcFlag,
          0,
          end.x,
          end.y,
          "L",
          end2.x,
          end2.y,
          "A",
          endradius,
          endradius,
          0,
          largeArcFlag,
          1,
          start2.x,
          start2.y,
          "Z",
        ].join(" ");
        return d;
      }

      var spin = {
        slots: this.wheelspin,
        progress: 0,
        result_slot: 0,
        result_degree: 0,
        duration: 1000,
        // only use full rotations or else the result is not correct
        rotations: 10,
        degree: 0,
        obj: null,
      };

      var spin_anim = function () {
        if (spin.progress >= 1) {
            spin_stop();
            return;
        }
        spin.progress += 1 / spin.duration;
        var sqt = spin.progress * spin.progress;
        spin.degree = filter_degree((spin.result_degree + (spin.rotations * 360)) * (sqt / (2.0 * (sqt - spin.progress) + 1.0)));
        (spin as any).obj.css("transform", "rotate(" + spin.degree + "deg)");
        (window as any).requestAnimFrame(spin_anim);
      };

      function filter_degree(d: any) {
        while (d < 0) {
          d += 360;
        }
        return d % 360;
      }

      function spin_start(result: number) {
        spin.result_slot = 0;
        for (var i = 0; i < spin.slots.length; i++) {
          if (result == spin.slots[i].id) {
            spin.result_slot = i;
          }
        }
        spin.result_degree = 360 - filter_degree((spin.result_slot + 0.5) * (360/spin.slots.length));

        spin.progress = 0;
        that.can_spin = false;
        spin_anim();
      }
      (window as any).spin_start = spin_start;

      function spin_stop() {
        if (spin.slots[spin.result_slot].sound) {
          that.playSound();
        }

        that.update_can_spin();
      }

      $(function () {
        (spin as any).obj = $("#spin");

        var slot_count = spin.slots.length;
        var svg = "<defs>";
        for (var i = 0; i < slot_count; i++) {
          svg =
            svg +
            spin.slots[i].foreground_color_svg +
            spin.slots[i].background_color_svg;
        }
        svg = svg + "</defs>";
        var t: any = 0;
        for (i = 0; i < slot_count; i++) {
          t = polarToCartesian(50, 50, 30, (i + 0.5) * (360 / slot_count));
          svg =
            svg +
            '<path d="' +
            arcPath(
              50,
              50,
              0,
              50,
              i * (360 / slot_count),
              (i + 1) * (360 / slot_count)
            ) +
            '" fill="url(#' +
            spin.slots[i].background_color_id +
            ')" stroke="#ffffff" stroke-width="0" />';
          svg =
            svg +
            '<text font-size="6" x="' +
            t.x +
            '" y="' +
            t.y +
            '" fill="url(#' +
            spin.slots[i].foreground_color_id +
            ')" font-style="bold" font-family="Arial" alignment-baseline="central" text-anchor="middle" transform="rotate(' +
            (1 * ((i + 0.5) * (360 / slot_count)) + 90) +
            " " +
            t.x +
            "," +
            t.y +
            ') translate(0,1.6)">' +
            spin.slots[i].name +
            "</text>";
        }
        $("#spin").html(svg);
      });
    },
    spark_start_spin() {
      api
        .spin_wheel()
        .then((response: AxiosResponse) => {
          console.log(response.data);
          (window as any).spin_start(response.data.result);
        })
        .catch((error) => {
          Toast.fire({
            icon: "error",
            text: error.response.data.description,
          });
        });
    },
    playSound() {
      Howler.volume(0.2);
      var sound = new Howl({
        src: [
          require("@/assets/sfx/209578__zott820__cash-register-purchase.wav"),
        ],
        html5: true,
      });

      sound.play();

      this.fireConfetti();
    },

    fireConfetti() {
      var count = 200;
      var defaults = {
        origin: { y: 0.5, x: 0.55 },
      };

      function fire(particleRatio: any, opts: any) {
        Confetti(
          Object.assign({}, defaults, opts, {
            particleCount: Math.floor(count * particleRatio),
          })
        );
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
        scalar: 0.8,
      });
      fire(0.1, {
        spread: 120,
        startVelocity: 25,
        decay: 0.92,
        scalar: 1.2,
      });
      fire(0.1, {
        spread: 120,
        startVelocity: 45,
      });
    },
  },
});
</script>

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
  box-shadow: 0px 2px 5px 1px rgba(0, 0, 0, 0.3);
  transform: translate(50%, 50%);
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
