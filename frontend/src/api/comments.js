import apiClient from './client'

export const fetchComments = (postId) => apiClient.get(`/api/posts/${postId}/comments`)
export const createComment = (postId, payload) =>
  apiClient.post(`/api/posts/${postId}/comments`, payload)
export const deleteComment = (commentId, password) =>
  apiClient.delete(`/api/comments/${commentId}`, { data: { password } })
