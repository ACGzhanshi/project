<template>
  <div>
    <div class="page-card">
      <div class="page-header">
        <span class="page-title">系统操作日志</span>
        <div class="filter-container">
          <el-input
            v-model="listQuery.search"
            placeholder="搜索模块 / 动作 / 用户名 / IP"
            style="width: 250px; margin-right: 10px;"
            clearable
            @clear="handleFilter"
            @keyup.enter="handleFilter"
          />
          <el-button type="primary" icon="Search" @click="handleFilter">搜索</el-button>
        </div>
      </div>

<el-table :data="list" v-loading="loading" stripe border>
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="action" label="动作" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)" size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情内容" min-width="200" />
        <el-table-column prop="ip_address" label="IP地址" width="130" />
        <el-table-column prop="created_at" label="操作时间" width="180" />
      </el-table>

      <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
        <el-pagination
          v-model:current-page="listQuery.page"
          v-model:page-size="listQuery.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchList"
          @current-change="fetchList"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request' // 或者你封装的 api/system.js 中的方法

const loading = ref(false)
const list = ref([])
const total = ref(0) // 总条数

// 🚀 查询参数对象
const listQuery = reactive({
  page: 1,
  page_size: 15,
  search: ''
})

function getActionType(action) {
  if (action.includes('新增') || action.includes('创建') || action.includes('登录')) return 'success'
  if (action.includes('删除')) return 'danger'
  if (action.includes('修改') || action.includes('更新')) return 'warning'
  return 'info'
}

async function fetchList() {
  loading.value = true
  try {
    // 附带分页和搜索参数
    const res = await request.get('/system/logs/', { params: listQuery })
    // DRF 分页标准结构为 { count: X, results: [...] }
    list.value = res.data?.results || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch (e) {
    /* ignore */
  } finally {
    loading.value = false
  }
}

// 触发搜索（重置回第一页）
function handleFilter() {
  listQuery.page = 1
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.filter-container {
  display: flex;
  align-items: center;
}
</style>