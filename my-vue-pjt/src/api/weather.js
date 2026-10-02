import axios from 'axios'

// 서울 시청 좌표
const SEOUL = { latitude: 37.5665, longitude: 126.978 }

export async function fetchSeoulWeather() {
  const { data } = await axios.get('https://api.open-meteo.com/v1/forecast', {
    params: { ...SEOUL, current_weather: true, timezone: 'Asia/Seoul' },
  })
  return data.current_weather
}

// WMO Weather Code -> 날씨 설명 + 추천 장르(TMDB 장르 ID)
// https://open-meteo.com/en/docs#weathervariables
const WEATHER_GENRE_RULES = [
  { codes: [0], label: '맑음', icon: '☀️', genre: { id: 12, name: '모험' } },
  { codes: [1, 2, 3], label: '구름 조금/흐림', icon: '⛅', genre: { id: 35, name: '코미디' } },
  { codes: [45, 48], label: '안개', icon: '🌫️', genre: { id: 9648, name: '미스터리' } },
  { codes: [51, 53, 55, 56, 57], label: '이슬비', icon: '🌦️', genre: { id: 18, name: '드라마' } },
  { codes: [61, 63, 65, 66, 67, 80, 81, 82], label: '비', icon: '🌧️', genre: { id: 27, name: '공포' } },
  { codes: [71, 73, 75, 77, 85, 86], label: '눈', icon: '❄️', genre: { id: 10749, name: '로맨스' } },
  { codes: [95, 96, 99], label: '뇌우', icon: '⛈️', genre: { id: 53, name: '스릴러' } },
]

const DEFAULT_RULE = { label: '알 수 없음', icon: '🌈', genre: { id: 16, name: '애니메이션' } }

export function matchWeatherGenre(weatherCode) {
  return WEATHER_GENRE_RULES.find((rule) => rule.codes.includes(weatherCode)) ?? DEFAULT_RULE
}
