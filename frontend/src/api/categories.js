import apiClient from './client'

export const fetchCategories = () => apiClient.get('/api/categories')
