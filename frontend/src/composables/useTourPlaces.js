import { reactive, ref, watch } from 'vue'
import { fetchTourItems } from '../api/tour'
import { deriveRegionClusters } from '../utils/region'
import { useRegionStore } from '../stores/region'
import { TOUR_CONTENT_TYPES } from '../utils/tourContentTypes'

// Module-scope singleton: Home/Board both need the same tour dataset (all
// content types) and derived region clusters, so fetch/derive it once per
// session and refetch only when the header's region selector changes.
const itemsByType = reactive(Object.fromEntries(TOUR_CONTENT_TYPES.map((t) => [t.key, []])))
const clusters = ref([])
let loadedForRegion = null
let loadingPromise = null

async function loadForRegion(region) {
  loadingPromise = Promise.all(
    TOUR_CONTENT_TYPES.map((type) => fetchTourItems({ content_type_id: type.id, region }))
  ).then((responses) => {
    responses.forEach((res, index) => {
      itemsByType[TOUR_CONTENT_TYPES[index].key] = res.data
    })
    clusters.value = deriveRegionClusters(responses.flatMap((res) => res.data))
    loadedForRegion = region
  })
  return loadingPromise
}

function ensureTourPlacesLoaded() {
  const regionStore = useRegionStore()
  if (loadedForRegion === regionStore.selectedRegion) return loadingPromise ?? Promise.resolve()
  return loadForRegion(regionStore.selectedRegion)
}

let watcherStarted = false
function startRegionWatcher() {
  if (watcherStarted) return
  watcherStarted = true
  const regionStore = useRegionStore()
  watch(
    () => regionStore.selectedRegion,
    (region) => loadForRegion(region)
  )
}

export function useTourPlaces() {
  startRegionWatcher()
  return { itemsByType, clusters, ensureTourPlacesLoaded }
}
