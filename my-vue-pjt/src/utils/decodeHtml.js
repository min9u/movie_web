// Youtube API 응답의 title 은 &#39; &quot; 처럼 HTML 엔티티로 인코딩되어 있음
export function decodeHtml(text = '') {
  return new DOMParser().parseFromString(text, 'text/html').documentElement.textContent
}
