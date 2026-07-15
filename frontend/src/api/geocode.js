import axios from 'axios'

const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'

/**
 * Real-world place/address search via OpenStreetMap's free Nominatim API —
 * no API key needed, consistent with the app's Leaflet+OSM map stack.
 * Unlike /api/tour/items (which only covers the curated TourAPI dataset for
 * 5 regions), this can find any address or named place in Korea.
 */
export async function searchPlaces(query) {
  const trimmed = query.trim()
  if (!trimmed) return []

  const { data } = await axios.get(NOMINATIM_URL, {
    params: {
      format: 'jsonv2',
      q: trimmed,
      addressdetails: 1,
      limit: 8,
      countrycodes: 'kr',
      // Without this, Nominatim sometimes returns English place/road names
      // for Korean addresses, which breaks any Korean-keyword region
      // matching done on the result (e.g. board region filtering).
      'accept-language': 'ko'
    }
  })

  return data.map((item) => ({
    id: item.place_id,
    title: item.name || item.display_name.split(',')[0],
    addr1: item.display_name,
    map_x: Number(item.lon),
    map_y: Number(item.lat)
  }))
}
