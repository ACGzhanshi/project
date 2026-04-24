import request from '@/utils/request'

export const smartMatch = (data) => request.post('/recommendation/recommend/smart_match/', data)
export const aiAnalyze = (data) => request.post('/recommendation/recommend/ai_analyze/', data)
export const getRecommendHistory = (params) => request.get('/recommendation/recommend/history/', { params })

export const getQuestions = () => request.get('/recommendation/assessment/questions/')
export const submitAssessment = (data) => request.post('/recommendation/assessment/submit/', data)
export const getMyResults = () => request.get('/recommendation/assessment/my_results/')
export function sendAiChat(data) {
  return request({
    url: '/recommendation/ai_chat/',
    method: 'post',
    data
  })
}