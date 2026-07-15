import { defineStore } from 'pinia'

const STORAGE_KEY = 'localhub-region'

// Matches data/raw/<folder> and tour_masters.region exactly — the backend
// has all 5 regions loaded, so these are real, selectable datasets.
export const REGIONS = [
  { code: '대전_충청권', label: '대전·충청권' },
  { code: '서울', label: '서울' },
  { code: '구미_경북권', label: '구미·경북권' },
  { code: '광주_전라권', label: '광주·전라권' },
  { code: '부산', label: '부산' }
]

const DEFAULT_REGION = REGIONS[0].code

function loadInitial() {
  let saved = null
  try {
    saved = localStorage.getItem(STORAGE_KEY)
  } catch {
    saved = null
  }
  return REGIONS.some((r) => r.code === saved) ? saved : DEFAULT_REGION
}

export const useRegionStore = defineStore('region', {
  state: () => ({
    selectedRegion: loadInitial()
  }),
  getters: {
    selectedLabel: (state) => REGIONS.find((r) => r.code === state.selectedRegion)?.label ?? state.selectedRegion
  },
  actions: {
    setRegion(code) {
      if (!REGIONS.some((r) => r.code === code)) return
      this.selectedRegion = code
      try {
        localStorage.setItem(STORAGE_KEY, code)
      } catch {
        // Ignore storage failures; selection still works for the session.
      }
    }
  }
})
