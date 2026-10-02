import axios from 'axios'

const youtube = axios.create({
  baseURL: 'https://www.googleapis.com/youtube/v3',
  params: {
    key: import.meta.env.VITE_YOUTUBE_API_KEY,
    part: 'snippet',
    type: 'video',
  },
})

export async function searchVideos(query, maxResults = 12) {
  const { data } = await youtube.get('/search', { params: { q: query, maxResults } })
  return data.items
}

export function getEmbedUrl(videoId) {
  return `https://www.youtube.com/embed/${videoId}?autoplay=1`
}
