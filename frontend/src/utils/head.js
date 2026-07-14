/**
 * Best-effort document head updates for the browser tab / generic link
 * previews. This is a pure SPA (no SSR/prerendering), so crawlers that
 * don't execute JS — like KakaoTalk's link-preview bot — never see these
 * tags. KakaoTalk sharing instead goes through the Kakao Share SDK
 * (utils/kakao.js), which sends its own title/description explicitly.
 */

export const DEFAULT_TITLE = 'LocalHub'

function setMetaTag(attr, key, content) {
  if (!content) return
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

export function setPageHead({ title, description }) {
  if (title) document.title = `${title} · ${DEFAULT_TITLE}`
  setMetaTag('name', 'description', description)
  setMetaTag('property', 'og:title', title)
  setMetaTag('property', 'og:description', description)
  setMetaTag('property', 'og:url', window.location.href)
}

export function resetPageHead() {
  document.title = DEFAULT_TITLE
}
