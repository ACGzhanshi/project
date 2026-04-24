import request from '@/utils/request'

// ================= 院校管理 =================
export const getUniversityList = (params) => request.get('/universities/list/', { params })
export const getUniversityDetail = (id) => request.get(`/universities/list/${id}/`)

// 👇 就是这三行，必须把 info 改成 list 才能和后端 ModelViewSet 对齐
export const createUniversity = (data) => request.post('/universities/list/', data)
export const updateUniversity = (id, data) => request.patch(`/universities/list/${id}/`, data)
export const deleteUniversity = (id) => request.delete(`/universities/list/${id}/`)

export const compareUniversities = (ids) => request.get('/universities/list/compare/', { params: { ids } })
export const getUniversityProvinces = () => request.get('/universities/list/provinces/')


// ================= 专业、分数线相关 =================
export const getMajorList = (params) => request.get('/universities/majors/', { params })
export const createMajor = (data) => request.post('/universities/majors/', data)
export const updateMajor = (id, data) => request.patch(`/universities/majors/${id}/`, data)
export const deleteMajor = (id) => request.delete(`/universities/majors/${id}/`)
export function getAdmissionScores(params) {
  return request({
    url: '/universities/scores/',
    method: 'get',
    params
  })
}


export const getScoreTrend = (params) => request.get('/universities/scores/trend/', { params })
export const getPlanList = (params) => request.get('/universities/plans/', { params })
export const getUniversityScoreTrends = (id, params) => request.get(`/universities/list/${id}/score_trends/`, { params })
export const getScoreList = (params) => request.get('/universities/scores/', { params })
export const getProvinces = () => request.get('/universities/list/provinces/')
// 新增分数线/计划
export const createScore = (data) => request.post('/universities/scores/', data)

// 修改分数线/计划 (使用 patch 局部更新)
export const updateScore = (id, data) => request.patch(`/universities/scores/${id}/`, data)

// 删除分数线/计划
export const deleteScore = (id) => request.delete(`/universities/scores/${id}/`)