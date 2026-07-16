import { defineStore } from 'pinia'
import { watch } from 'vue'
import { useRegionStore } from './region'

// Representative city coordinates for each selectable region.
const REGION_COORDS = {
  대전_충청권: { lat: 36.3504, lon: 127.3845 },
  서울: { lat: 37.5665, lon: 126.978 },
  구미_경북권: { lat: 36.1195, lon: 128.3446 },
  광주_전라권: { lat: 35.1595, lon: 126.8526 },
  부산: { lat: 35.1796, lon: 129.0756 }
}
const DEFAULT_COORDS = REGION_COORDS.대전_충청권
const REFRESH_INTERVAL_MS = 30 * 60 * 1000

function classifyIcon(code) {
  if (code === 0) return 'sun'
  if ([45, 48, 1, 2, 3, 71, 73, 75, 77, 85, 86].includes(code)) return 'cloud'
  return 'rain'
}

export const useWeatherStore = defineStore('weather', {
  state: () => ({
    temperature: null,
    icon: 'sun',
    started: false
  }),
  getters: {
    // A simple travel-suitability read: rain calls for an umbrella regardless
    // of temperature; otherwise it's the temperature that decides.
    suitability: (state) => {
      if (state.temperature === null) return null
      if (state.icon === 'rain') return 'umbrella'
      if (state.temperature < 0 || state.temperature > 33) return 'unsuitable'
      return 'suitable'
    }
  },
  actions: {
    async fetchNow() {
      const regionStore = useRegionStore()
      const { lat, lon } = REGION_COORDS[regionStore.selectedRegion] ?? DEFAULT_COORDS
      try {
        const res = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,weather_code&timezone=Asia%2FSeoul`
        )
        if (!res.ok) throw new Error('weather fetch failed')
        const data = await res.json()
        this.temperature = Math.round(data.current.temperature_2m)
        this.icon = classifyIcon(data.current.weather_code)
      } catch {
        // silent: weather badge just stays hidden until next refresh
      }
    },
    startPolling() {
      if (this.started) return
      this.started = true
      const regionStore = useRegionStore()
      watch(
        () => regionStore.selectedRegion,
        () => this.fetchNow()
      )
      this.fetchNow()
      setInterval(() => this.fetchNow(), REFRESH_INTERVAL_MS)
    }
  }
})
