<script setup>
import { computed } from 'vue'
import { pixelIconCells } from '../../utils/pixelIcons'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: Number, default: 16 },
  color: { type: String, default: 'currentColor' }
})

const unit = computed(() => props.size / 8)
const cells = computed(() => pixelIconCells(props.name))
</script>

<template>
  <svg
    class="pixel-icon"
    :width="size"
    :height="size"
    :viewBox="`0 0 ${size} ${size}`"
    shape-rendering="crispEdges"
    aria-hidden="true"
  >
    <rect
      v-for="([x, y], index) in cells"
      :key="index"
      :x="x * unit"
      :y="y * unit"
      :width="unit"
      :height="unit"
      :fill="color"
    />
  </svg>
</template>

<style scoped>
.pixel-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
