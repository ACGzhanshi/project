import request from '@/utils/request'

export const login = (data) => request.post('/users/auth/login/', data)
export const register = (data) => request.post('/users/auth/register/', data)
export const getUserInfo = () => request.get('/users/auth/info/')
export const updateProfile = (data) => request.put('/users/auth/update_profile/', data)
export const changePassword = (data) => request.post('/users/auth/change_password/', data)

/* 用户管理（管理员） */
export const getUserList = (params) => request.get('/users/manage/', { params })
export const toggleUserStatus = (id) => request.post(`/users/manage/${id}/toggle_status/`)
export const resetUserPassword = (id) => request.post(`/users/manage/${id}/reset_password/`)
export const createUser = (data) => request.post('/users/manage/', data)
export const updateUser = (id, data) => request.put(`/users/manage/${id}/`, data)
export const deleteUser = (id) => request.delete(`/users/manage/${id}/`)
