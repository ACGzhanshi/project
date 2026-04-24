import request from '@/utils/request'

export const getQuestionList = (params) => request.get('/recommendation/questions/', { params })
export const createQuestion = (data) => request.post('/recommendation/questions/', data)
export const updateQuestion = (id, data) => request.patch(`/recommendation/questions/${id}/`, data)
export const deleteQuestion = (id) => request.delete(`/recommendation/questions/${id}/`)