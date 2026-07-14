import { ref } from 'vue'
import { fetchTourItems } from '../api/tour'
import { deriveRegionClusters } from '../utils/region'

const TOUR_CONTENT_TYPE_ID = 12
const FOOD_CONTENT_TYPE_ID = 39

// Module-scope singleton: Home/Board both need the same tour+food dataset
// and derived region clusters, so fetch/derive it once per session.
const tourItems = ref([])
const foodItems = ref([])
const clusters = ref([])
let loadingPromise = null

async function ensureTourPlacesLoaded() {
  if (loadingPromise) return loadingPromise
  loadingPromise = Promise.all([
    fetchTourItems({ content_type_id: TOUR_CONTENT_TYPE_ID }),
    fetchTourItems({ content_type_id: FOOD_CONTENT_TYPE_ID })
  ]).then(([tourRes, foodRes]) => {
    tourItems.value = tourRes.data
    foodItems.value = foodRes.data
    clusters.value = deriveRegionClusters([...tourRes.data, ...foodRes.data])
  })
  return loadingPromise
}

export function useTourPlaces() {
  return { tourItems, foodItems, clusters, ensureTourPlacesLoaded }
}
