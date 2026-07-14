import apiClient from './client'

export const sendChatMessage = (message, sessionId) =>
  apiClient.post('/api/chat', { message, session_id: sessionId })
