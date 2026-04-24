import request from '@/utils/request'

export const getDashboardOverview = () => request.get('/system/dashboard/overview/')
export const getScoreDistribution = () => request.get('/system/dashboard/score_distribution/')

export const getLogList = (params) => request.get('/system/logs/', { params })
export const getPermissionList = (params) => request.get('/system/permissions/', { params })
export const updatePermission = (id, data) => request.put(`/system/permissions/${id}/`, data)

export const getConfigList = () => request.get('/system/configs/')
export const updateConfig = (key, data) => request.put(`/system/configs/${key}/`, data)

export const getTrainList = () => request.get('/system/model-train/')
export const startTrain = (id) => request.post(`/system/model-train/${id}/start_train/`)
