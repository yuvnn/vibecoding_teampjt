import apiClient from './client'

export const fetchPosts = (params) => apiClient.get('/api/posts', { params })
export const fetchPost = (postId) => apiClient.get(`/api/posts/${postId}`)
export const createPost = (payload) => apiClient.post('/api/posts', payload)
export const updatePost = (postId, payload) => apiClient.put(`/api/posts/${postId}`, payload)
export const deletePost = (postId, password) =>
  apiClient.delete(`/api/posts/${postId}`, { data: { password } })
