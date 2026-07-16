import apiClient from './client'

export const fetchTourItems = (params) => apiClient.get('/api/tour/items', { params })
export const fetchTourItem = (contentId) => apiClient.get(`/api/tour/items/${contentId}`)
export const fetchRandomTourItems = (params) => apiClient.get('/api/tour/items/random', { params })
