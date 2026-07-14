/**
 * Loads the Kakao Share SDK on demand via VITE_KAKAO_APP_KEY.
 * No npm package is used — Kakao ships this as a plain <script> tag. If the
 * key is missing, callers should show a setup notice instead of failing.
 */

const KAKAO_APP_KEY = import.meta.env.VITE_KAKAO_APP_KEY

export function hasKakaoKey() {
  return Boolean(KAKAO_APP_KEY)
}

let sharePromise = null

function loadKakaoShareSdk() {
  if (!KAKAO_APP_KEY) return Promise.reject(new Error('VITE_KAKAO_APP_KEY is not set'))
  if (sharePromise) return sharePromise

  sharePromise = new Promise((resolve, reject) => {
    const ready = () => {
      if (!window.Kakao.isInitialized()) window.Kakao.init(KAKAO_APP_KEY)
      resolve(window.Kakao)
    }
    if (window.Kakao) {
      ready()
      return
    }
    const script = document.createElement('script')
    script.src = 'https://developers.kakao.com/sdk/js/kakao.js'
    script.onload = ready
    script.onerror = () => reject(new Error('Failed to load Kakao Share SDK'))
    document.head.appendChild(script)
  })
  return sharePromise
}

export async function shareToKakao({ title, description, url }) {
  const Kakao = await loadKakaoShareSdk()
  Kakao.Share.sendDefault({
    objectType: 'text',
    text: description ? `${title}\n${description}` : title,
    link: { mobileWebUrl: url, webUrl: url }
  })
}
