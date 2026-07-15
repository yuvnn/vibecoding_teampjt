import { hashCode } from './hash'

/**
 * Posts have no geo column and tour_items are only seeded for one region
 * (대전_충청권), so "5개 지역" is approximated on the client: the 5
 * most common 시/군/구 clusters found in tour_items' addr1, used both as
 * map pin clusters and as a bucket to (heuristically) place posts into.
 * See plan doc for the constraint this works around.
 */

function extractRegionLabel(addr1) {
  if (!addr1) return null
  const tokens = addr1.trim().split(/\s+/)
  if (tokens.length === 0) return null
  const [first, second] = tokens
  if (second && /(시|군|구)$/.test(second) && second !== first) {
    return `${first} ${second}`
  }
  return first || null
}

export function deriveRegionClusters(tourItems, limit = 5) {
  const groups = new Map()

  tourItems.forEach((item) => {
    const label = extractRegionLabel(item.addr1)
    if (!label) return
    const lat = Number(item.map_y)
    const lng = Number(item.map_x)
    if (!groups.has(label)) {
      groups.set(label, { label, count: 0, sumLat: 0, sumLng: 0, coordCount: 0 })
    }
    const group = groups.get(label)
    group.count += 1
    if (Number.isFinite(lat) && Number.isFinite(lng)) {
      group.sumLat += lat
      group.sumLng += lng
      group.coordCount += 1
    }
  })

  return [...groups.values()]
    .filter((group) => group.coordCount > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, limit)
    .map((group, index) => ({
      id: `region-${index}`,
      label: group.label,
      lat: group.sumLat / group.coordCount,
      lng: group.sumLng / group.coordCount
    }))
}

const PROVINCE_SUFFIX = /(특별시|광역시|특별자치시|특별자치도|도)$/
const CITY_SUFFIX = /(시|군|구)$/

/**
 * Nominatim's display_name is comma-separated and ordered fine→coarse
 * (e.g. "경복궁, 청운효자동, 종로구, 서울특별시, 03045, 대한민국"), unlike
 * TourAPI's space-separated addr1 ("대전광역시 유성구 ..."). Scan the comma
 * parts for a province-level and city-level token instead of assuming a
 * fixed position.
 */
function extractRegionLabelFromFreeAddress(address) {
  if (!address) return null
  const parts = address
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
  const province = parts.find((part) => PROVINCE_SUFFIX.test(part))
  const city = parts.find((part) => CITY_SUFFIX.test(part) && part !== province)
  if (province && city) return `${province} ${city}`
  return province || city || null
}

/**
 * Region label to *display* on a post card/detail page. Prefers the real
 * address of an actually-attached place (accurate) over the old
 * keyword-match/hash-bucket heuristic (an approximation used only when a
 * post has no attached place to go on).
 */
export function regionLabelForPost(post, clusters) {
  const address = post.places?.[0]?.address
  const fromPlace = extractRegionLabelFromFreeAddress(address)
  if (fromPlace) return fromPlace
  return inferPostRegion(post, clusters)?.label ?? ''
}

export function inferPostRegion(post, clusters) {
  if (!clusters.length) return null

  const haystack = `${post.title ?? ''} ${post.content ?? ''}`
  const matched = clusters.find((cluster) => {
    const parts = cluster.label.split(/\s+/)
    return parts.some((part) => part.length >= 2 && haystack.includes(part))
  })
  if (matched) return matched

  const bucket = hashCode(post.id) % clusters.length
  return clusters[bucket]
}

export function groupPostsByRegion(posts, clusters) {
  const counts = new Map(clusters.map((cluster) => [cluster.id, { cluster, posts: [] }]))
  posts.forEach((post) => {
    const region = inferPostRegion(post, clusters)
    if (!region) return
    counts.get(region.id)?.posts.push(post)
  })
  return [...counts.values()]
}
