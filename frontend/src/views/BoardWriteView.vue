<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { createPost, fetchPost, updatePost } from '../api/posts'
import { searchPlaces } from '../api/geocode'
import { useCategoryStore } from '../stores/categories'
import { useLocalMetaStore } from '../stores/localMeta'
import TagInput from '../components/common/TagInput.vue'
import PixelIcon from '../components/common/PixelIcon.vue'

const props = defineProps({ id: { type: [String, Number], default: null } })

const router = useRouter()
const { t } = useI18n()
const categoryStore = useCategoryStore()
const metaStore = useLocalMetaStore()

const isEdit = computed(() => !!props.id)
const form = reactive({
  category_ids: [],
  title: '',
  content: '',
  password: '',
  tags: [],
  places: []
})
const error = ref('')
const submitting = ref(false)

const placeQuery = ref('')
const placeResults = ref([])
const placeSearching = ref(false)
const placeDropdownOpen = ref(false)
let placeSearchTimer = null

const toggleCategory = (categoryId) => {
  const index = form.category_ids.indexOf(categoryId)
  if (index !== -1) {
    form.category_ids.splice(index, 1)
  } else {
    form.category_ids.push(categoryId)
  }
}

const onPlaceQueryInput = () => {
  clearTimeout(placeSearchTimer)
  if (!placeQuery.value.trim()) {
    placeResults.value = []
    placeDropdownOpen.value = false
    return
  }
  placeSearchTimer = setTimeout(async () => {
    placeSearching.value = true
    try {
      placeResults.value = await searchPlaces(placeQuery.value)
      placeDropdownOpen.value = true
    } catch {
      placeResults.value = []
    } finally {
      placeSearching.value = false
    }
  }, 400)
}

const addPlace = (item) => {
  const alreadyAdded = form.places.some(
    (place) => place.place_name === item.title && place.address === item.addr1
  )
  if (!alreadyAdded) {
    form.places.push({
      place_name: item.title,
      address: item.addr1,
      map_x: item.map_x,
      map_y: item.map_y
    })
  }
  placeQuery.value = ''
  placeResults.value = []
  placeDropdownOpen.value = false
}

const removePlace = (index) => {
  form.places.splice(index, 1)
}

const movePlace = (index, direction) => {
  const target = index + direction
  if (target < 0 || target >= form.places.length) return
  const places = form.places
  ;[places[index], places[target]] = [places[target], places[index]]
}

onBeforeUnmount(() => clearTimeout(placeSearchTimer))

onMounted(async () => {
  await categoryStore.ensureLoaded()
  if (isEdit.value) {
    const { data } = await fetchPost(props.id)
    form.title = data.title
    form.content = data.content
    form.tags = metaStore.tagsFor(props.id)
    form.category_ids = [...(data.category_ids ?? [])]
    form.places = (data.places ?? []).map((place) => ({
      place_name: place.place_name,
      address: place.address,
      map_x: place.map_x,
      map_y: place.map_y
    }))
  } else {
    const firstCategory = categoryStore.categories[0]?.id
    if (firstCategory) form.category_ids = [firstCategory]
  }
})

const submit = async () => {
  error.value = ''
  if (!form.category_ids.length) {
    error.value = t('board.write.categoryRequired')
    return
  }
  submitting.value = true
  const payload = {
    category_ids: form.category_ids,
    title: form.title,
    content: form.content,
    password: form.password,
    places: form.places
  }
  try {
    if (isEdit.value) {
      const { data } = await updatePost(props.id, payload)
      metaStore.setTags(props.id, form.tags)
      router.push(`/board/${data.id}`)
    } else {
      const { data } = await createPost(payload)
      metaStore.setTags(data.id, form.tags)
      router.push(`/board/${data.id}`)
    }
  } catch (err) {
    error.value = err.response?.data?.detail ?? t('common.errorGeneric')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}
</script>

<template>
  <section class="board-write">
    <div class="write-card panel">
      <div class="write-card-header">
        <button type="button" class="btn btn-ghost btn-icon" :title="t('common.back')" @click="goBack">
          <PixelIcon name="arrowLeft" :size="16" />
        </button>
        <h1 class="page-title">{{ isEdit ? t('board.write.titleEdit') : t('board.write.titleNew') }}</h1>
      </div>
      <p v-if="error" class="error">{{ error }}</p>

      <form class="write-form" @submit.prevent="submit">
      <div class="field">
        <label>{{ t('board.category') }}</label>
        <div class="category-checks">
          <label v-for="category in categoryStore.categories" :key="category.id" class="category-check">
            <input
              type="checkbox"
              :checked="form.category_ids.includes(category.id)"
              @change="toggleCategory(category.id)"
            />
            {{ category.name }}
          </label>
        </div>
      </div>

      <div class="field">
        <label>{{ t('board.write.fieldTitle') }}</label>
        <input v-model="form.title" required maxlength="255" />
      </div>

      <div class="field">
        <label>{{ t('board.write.fieldContent') }}</label>
        <textarea v-model="form.content" required></textarea>
      </div>

      <div class="field">
        <label>{{ t('board.write.fieldTags') }}</label>
        <TagInput v-model="form.tags" :placeholder="t('board.detail.addTagPlaceholder')" />
        <p class="field-hint">{{ t('board.write.tagsHint') }}</p>
      </div>

      <div class="field">
        <label>{{ t('board.write.fieldPlace') }}</label>
        <ol v-if="form.places.length" class="place-chip-list">
          <li v-for="(place, index) in form.places" :key="`${place.place_name}-${index}`" class="place-chip">
            <span class="place-index">{{ index + 1 }}</span>
            <PixelIcon name="pin" :size="13" />
            <div class="place-chip-body">
              <strong>{{ place.place_name }}</strong>
              <span>{{ place.address }}</span>
            </div>
            <div class="place-chip-actions">
              <button
                type="button"
                class="btn-icon"
                :disabled="index === 0"
                :title="t('board.write.moveUp')"
                @click="movePlace(index, -1)"
              >
                ▲
              </button>
              <button
                type="button"
                class="btn-icon"
                :disabled="index === form.places.length - 1"
                :title="t('board.write.moveDown')"
                @click="movePlace(index, 1)"
              >
                ▼
              </button>
              <button type="button" class="btn-icon" :title="t('common.delete')" @click="removePlace(index)">×</button>
            </div>
          </li>
        </ol>
        <div class="place-picker">
          <input
            v-model="placeQuery"
            type="text"
            :placeholder="t('board.write.placeSearchPlaceholder')"
            @input="onPlaceQueryInput"
            @focus="placeDropdownOpen = placeResults.length > 0"
          />
          <ul v-if="placeDropdownOpen && placeResults.length" class="place-dropdown">
            <li v-for="item in placeResults" :key="item.id" @click="addPlace(item)">
              <strong>{{ item.title }}</strong>
              <span>{{ item.addr1 }}</span>
            </li>
          </ul>
          <p v-else-if="placeSearching" class="field-hint">{{ t('common.loading') }}</p>
        </div>
      </div>

      <div class="field">
        <label>{{ isEdit ? t('board.write.fieldPasswordEdit') : t('board.write.fieldPassword') }}</label>
        <input v-model="form.password" type="password" required />
      </div>

      <button type="submit" class="btn btn-primary" :disabled="submitting">
        {{ isEdit ? t('board.write.submitEdit') : t('board.write.submitNew') }}
      </button>
      </form>
    </div>
  </section>
</template>

<style scoped>
.board-write {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--header-height) - 120px);
}

.write-card {
  width: 100%;
  max-width: 640px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.write-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.write-card-header .page-title {
  margin: 0;
}

.write-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-hint {
  margin: 0;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.category-checks {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
}

.category-check {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.88rem;
  color: var(--color-text);
  cursor: pointer;
}

.category-check input {
  width: auto;
  padding: 0;
}

.place-chip-list {
  list-style: none;
  margin: 0 0 10px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.place-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 2px solid var(--color-shadow, #4a3728);
  border-radius: 4px;
  background: var(--color-primary-soft);
}

.place-chip-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.85rem;
}

.place-chip-body span {
  font-size: 0.76rem;
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.place-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-primary-dark);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
}

.place-chip-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.place-chip-actions .btn-icon {
  font-size: 0.68rem;
  padding: 4px 6px;
}

.place-chip-actions .btn-icon:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.place-picker {
  position: relative;
  width: 100%;
}

.place-picker input {
  width: 100%;
}

.place-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 10;
  margin: 0;
  padding: 6px;
  list-style: none;
  max-height: 220px;
  overflow-y: auto;
  background: var(--color-surface);
  border: 2px solid var(--color-shadow, #4a3728);
  border-radius: 4px;
  box-shadow: 3px 3px 0 var(--color-shadow, #4a3728);
}

.place-dropdown li {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.place-dropdown li:hover {
  background: var(--color-surface-alt);
}

.place-dropdown li span {
  font-size: 0.74rem;
  color: var(--color-text-muted);
}

.write-form button {
  align-self: flex-start;
}
</style>
