<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-aside">
      <div class="logo">
        <el-icon :size="24"><School /></el-icon>
        <span v-show="!isCollapse">高考志愿平台</span>
      </div>
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        router
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#fff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>首页概览</span>
        </el-menu-item>
        <el-menu-item index="/universities">
          <el-icon><OfficeBuilding /></el-icon>
          <span>院校查询</span>
        </el-menu-item>
        <el-menu-item index="/majors">
          <el-icon><Reading /></el-icon>
          <span>专业查询</span>
        </el-menu-item>
        <el-menu-item index="/recommend">
          <el-icon><MagicStick /></el-icon>
          <span>智能推荐</span>
        </el-menu-item>
        <el-menu-item index="/assessment">
          <el-icon><Document /></el-icon>
          <span>专业测评</span>
        </el-menu-item>
        <el-menu-item index="/volunteer">
          <el-icon><Edit /></el-icon>
          <span>志愿填报</span>
        </el-menu-item>

        <el-sub-menu index="/admin" v-if="userStore.isAdmin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>

          <template v-if="userStore.role === 'sys_admin'">
            <el-menu-item index="/admin/users">用户管理</el-menu-item>
            <el-menu-item index="/admin/logs">操作日志</el-menu-item>
            <el-menu-item index="/admin/universities">院校专业信息管理</el-menu-item>
            <el-menu-item index="/admin/assessment">专业测评问卷管理</el-menu-item>
          </template>

          <el-menu-item index="/admin/crawler">数据采集</el-menu-item>
          <el-menu-item index="/admin/model">模型训练</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
          <Fold v-if="!isCollapse" /><Expand v-else />
        </el-icon>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="userStore.userInfo?.avatar">
                {{ userStore.userInfo?.username?.charAt(0) }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()
const isCollapse = ref(false)

function handleCommand(cmd) {
  if (cmd === 'logout') {
    userStore.logout()
  } else if (cmd === 'profile') {
    router.push('/profile')
  }
}
</script>

<style lang="scss">
.app-layout { height: 100vh; }
.app-aside {
  background: linear-gradient(180deg, #0f2027 0%, #203a43 60%, #2c5364 100%);
  transition: width 0.3s;
  overflow: hidden;

  .logo {
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #fff;
    font-size: 15px;
    font-weight: 600;
    white-space: nowrap;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    letter-spacing: 1px;
  }

  .el-menu {
    border-right: none;
    background: transparent !important;
  }

  .el-menu-item,
  .el-sub-menu__title {
    color: rgba(255, 255, 255, 0.6) !important;
    border-radius: 8px;
    margin: 2px 8px;
    transition: all 0.2s;

    &:hover {
      background: rgba(255, 255, 255, 0.08) !important;
      color: #fff !important;
    }
  }

  .el-menu-item.is-active {
    background: rgba(79, 209, 197, 0.15) !important;
    color: #4fd1c5 !important;
  }

  .el-sub-menu.is-opened .el-sub-menu__title {
    color: rgba(255, 255, 255, 0.85) !important;
  }
}

.app-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  padding: 0 24px;
  height: 56px;
  border-bottom: 1px solid #edf2f7;

  .collapse-btn {
    font-size: 20px;
    cursor: pointer;
    color: #718096;
    transition: color 0.2s;

    &:hover { color: #2c5364; }
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
  }

  .username {
    font-size: 14px;
    color: #4a5568;
    font-weight: 500;
  }
}

.app-main {
  background: #f7f8fc;
  padding: 24px;
  overflow-y: auto;
}
</style>