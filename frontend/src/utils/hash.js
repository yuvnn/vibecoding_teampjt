/**
 * Small deterministic string hash (djb2). Used for client-side heuristics
 * that need a stable "random" bucket from an id — e.g. inferring a region
 * or a cosmetic base like-count when no backend field exists yet.
 */
export function hashCode(value) {
  const str = String(value)
  let hash = 5381
  for (let i = 0; i < str.length; i += 1) {
    hash = (hash * 33) ^ str.charCodeAt(i)
  }
  return Math.abs(hash >>> 0)
}
