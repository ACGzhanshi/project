import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue'), meta: { guest: true } },
  {
    path: '/',
    component: () => import('@/layout/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      // 学生/公共界面 (无需特殊 role)
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '首页概览' } },
      { path: 'universities', name: 'Universities', component: () => import('@/views/university/List.vue'), meta: { title: '院校查询' } },
      { path: 'universities/:id', name: 'UniversityDetail', component: () => import('@/views/university/Detail.vue'), meta: { title: '院校详情' } },
      { path: 'majors', name: 'Majors', component: () => import('@/views/major/List.vue'), meta: { title: '专业查询' } },
      { path: 'recommend', name: 'Recommend', component: () => import('@/views/recommend/Index.vue'), meta: { title: '智能推荐' } },
      { path: 'assessment', name: 'Assessment', component: () => import('@/views/recommend/Assessment.vue'), meta: { title: '专业测评' } },
      { path: 'volunteer', name: 'Volunteer', component: () => import('@/views/volunteer/List.vue'), meta: { title: '志愿填报' } },
      { path: 'volunteer/:id', name: 'VolunteerDetail', component: () => import('@/views/volunteer/Detail.vue'), meta: { title: '志愿详情' } },
      { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心' } },

      // ================= 管理员专属界面 (精确划分角色) =================

      // 1. 只有超级管理员 (sys_admin) 才能进的页面
      { path: 'admin/users', name: 'AdminUsers', component: () => import('@/views/admin/Users.vue'), meta: { title: '用户管理', roles: ['sys_admin'] } },
      { path: 'admin/logs', name: 'AdminLogs', component: () => import('@/views/admin/Logs.vue'), meta: { title: '操作日志', roles: ['sys_admin'] } },
      { path: 'admin/universities', name: 'AdminUniversities', component: () => import('@/views/admin/Universities.vue'), meta: { title: '院校专业信息管理', roles: ['sys_admin'] } },
      { path: 'admin/assessment', name: 'AdminAssessment', component: () => import('@/views/admin/AssessmentAdmin.vue'), meta: { title: '测评问卷管理', roles: ['sys_admin'] } },

      // 2. 数据管理员 (data_admin) 和超级管理员都能进的页面
      { path: 'admin/crawler', name: 'AdminCrawler', component: () => import('@/views/admin/Crawler.vue'), meta: { title: '数据采集', roles: ['sys_admin', 'data_admin'] } },
      { path: 'admin/model', name: 'AdminModel', component: () => import('@/views/admin/Model.vue'), meta: { title: '模型训练', roles: ['sys_admin', 'data_admin'] } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 增强版路由拦截器
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 安全地解析当前用户角色
  const userJson = localStorage.getItem('user')
  let userRole = ''
  try {
    const user = userJson ? JSON.parse(userJson) : null
    userRole = user ? user.role : ''
  } catch (e) {
    userRole = ''
  }

  if (to.meta.guest) {
    token ? next('/') : next()
  } else if (!token) {
    next('/login')
  } else if (to.meta.roles && !to.meta.roles.includes(userRole)) {
    // 🚨 越权拦截：如果该页面需要特定角色，而当前用户角色不在允许列表中
    console.warn(`[越权拦截] 尝试访问: ${to.path}, 你的角色: ${userRole}, 允许的角色: ${to.meta.roles}`)
    next('/')
  } else {
    next()
  }
})

export default router