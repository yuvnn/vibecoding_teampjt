import { createI18n } from 'vue-i18n'
import ko from './locales/ko.json'
import en from './locales/en.json'

const STORAGE_KEY = 'localhub-locale'

export const SUPPORTED_LOCALES = ['ko', 'en']

const savedLocale = localStorage.getItem(STORAGE_KEY)
const initialLocale = SUPPORTED_LOCALES.includes(savedLocale) ? savedLocale : 'ko'

const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'ko',
  messages: { ko, en }
})

export function setLocale(locale) {
  if (!SUPPORTED_LOCALES.includes(locale)) return
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
  document.documentElement.setAttribute('lang', locale)
}

export function toggleLocale() {
  const current = i18n.global.locale.value
  const next = current === 'ko' ? 'en' : 'ko'
  setLocale(next)
  return next
}

export default i18n
