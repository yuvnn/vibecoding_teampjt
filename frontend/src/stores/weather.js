import { defineStore } from 'pinia'

const LAT = 36.3504
const LON = 127.3845
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
  actions: {
    async fetchNow() {
      try {
        const res = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current=temperature_2m,weather_code&timezone=Asia%2FSeoul`
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
      this.fetchNow()
      setInterval(() => this.fetchNow(), REFRESH_INTERVAL_MS)
    }
  }
})
