import apiClient from './client'

export const createChatRoom = (sessionId) =>
  apiClient.post('/api/chatbot/rooms', { session_uuid: sessionId })

export const sendChatMessage = (roomId, message, region) =>
  apiClient.post(`/api/chatbot/rooms/${roomId}/messages`, { message, region })
