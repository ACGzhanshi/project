import request from '@/utils/request'

export const getFormList = (params) => request.get('/volunteer/forms/', { params })
export const createForm = (data) => request.post('/volunteer/forms/', data)
export const getFormDetail = (id) => request.get(`/volunteer/forms/${id}/`)
export const deleteForm = (id) => request.delete(`/volunteer/forms/${id}/`)
export const analyzeForm = (id) => request.post(`/volunteer/forms/${id}/analyze/`)
export const addItem = (id, data) => request.post(`/volunteer/forms/${id}/add_item/`, data)
export const removeItem = (id, itemId) => request.post(`/volunteer/forms/${id}/remove_item/`, { item_id: itemId })
export function updateForm(id, data) {
  return request({
    url: `/volunteer/forms/${id}/`,
    method: 'patch', // 使用 patch 局部更新
    data
  })
}
