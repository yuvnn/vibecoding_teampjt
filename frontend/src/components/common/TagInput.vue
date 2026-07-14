<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  placeholder: { type: String, default: '' }
})
const emit = defineEmits(['update:modelValue'])

const draft = ref('')

const addTag = () => {
  const value = draft.value.trim().replace(/^#/, '')
  if (!value) return
  if (!props.modelValue.includes(value)) {
    emit('update:modelValue', [...props.modelValue, value])
  }
  draft.value = ''
}

const removeTag = (tag) => {
  emit('update:modelValue', props.modelValue.filter((t) => t !== tag))
}

const onBackspace = () => {
  if (draft.value) return
  if (!props.modelValue.length) return
  emit('update:modelValue', props.modelValue.slice(0, -1))
}
</script>

<template>
  <div class="tag-input">
    <span v-for="tag in modelValue" :key="tag" class="tag-chip tag-chip--removable">
      {{ tag }}
      <button type="button" class="tag-chip-remove" @click="removeTag(tag)" :aria-label="`${tag} 제거`">
        ×
      </button>
    </span>
    <input
      v-model="draft"
      type="text"
      :placeholder="placeholder"
      @keydown.enter.prevent="addTag"
      @keydown.delete="onBackspace"
      @blur="addTag"
    />
  </div>
</template>

<style scoped>
.tag-input {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
}

.tag-input input {
  flex: 1;
  min-width: 120px;
  border: none;
  padding: 4px;
}

.tag-input input:focus {
  box-shadow: none;
}

.tag-chip--removable {
  background: var(--color-primary-soft);
  color: var(--color-primary-dark);
  border-color: transparent;
}

.tag-chip-remove {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 0.95rem;
  line-height: 1;
  padding: 0;
  opacity: 0.7;
}

.tag-chip-remove:hover {
  opacity: 1;
}
</style>
