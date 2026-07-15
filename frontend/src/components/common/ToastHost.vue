<script setup>
import { useToastStore } from '../../stores/toast'

const toastStore = useToastStore()

const handleClick = (toast) => {
  toast.onClick?.()
  toastStore.dismiss(toast.id)
}
</script>

<template>
  <div class="toast-host" role="status" aria-live="polite">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toastStore.items"
        :key="toast.id"
        class="toast"
        :class="`toast--${toast.type}`"
        @click="handleClick(toast)"
      >
        <span>{{ toast.message }}</span>
        <button type="button" class="toast-close" @click.stop="toastStore.dismiss(toast.id)">
          ×
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-host {
  position: fixed;
  top: 76px;
  right: 20px;
  z-index: 90;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 320px;
}

.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  box-shadow: var(--shadow-md);
  font-size: 0.88rem;
  color: var(--color-text);
  cursor: pointer;
}

.toast--success {
  border-color: color-mix(in srgb, var(--color-success) 40%, var(--color-border));
}

.toast-close {
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(16px);
}

@media (max-width: 640px) {
  .toast-host {
    right: 12px;
    left: 12px;
    max-width: none;
  }
}
</style>
