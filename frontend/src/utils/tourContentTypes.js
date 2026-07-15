// TourAPI 4.0 contentTypeId values, matched to data/raw/<region>/*.json files.
// `key` doubles as the pin/layer identifier used across TourMap + HomeView,
// `icon` is a PIXEL_ICONS name, `labelKey` is the i18n key under `home.*`.
export const TOUR_CONTENT_TYPES = [
  { id: 12, key: 'tour', icon: 'pin', labelKey: 'home.layerTour', defaultOn: true },
  { id: 39, key: 'food', icon: 'apple', labelKey: 'home.layerFood', defaultOn: true },
  { id: 28, key: 'leports', icon: 'sport', labelKey: 'home.layerLeports', defaultOn: false },
  { id: 14, key: 'culture', icon: 'culture', labelKey: 'home.layerCulture', defaultOn: false },
  { id: 38, key: 'shopping', icon: 'shopping', labelKey: 'home.layerShopping', defaultOn: false },
  { id: 32, key: 'stay', icon: 'stay', labelKey: 'home.layerStay', defaultOn: false },
  { id: 25, key: 'course', icon: 'course', labelKey: 'home.layerCourse', defaultOn: false },
  { id: 15, key: 'festival', icon: 'star', labelKey: 'home.layerFestival', defaultOn: false }
]

export const iconForType = (key) => TOUR_CONTENT_TYPES.find((t) => t.key === key)?.icon ?? 'pin'
