<template>
  <div class="page-card">
    <div class="page-header">
      <span class="page-title">数据采集任务</span>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="name" label="任务名称" min-width="160" />
      <el-table-column prop="type_display" label="数据类型" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType[row.status]" size="small">{{ row.status_display || row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_count" label="总数" width="80" align="center" />
      <el-table-column prop="success_count" label="成功" width="80" align="center" />
      <el-table-column prop="fail_count" label="失败" width="80" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="200" align="center">
        <template #default="{ row }">
          <el-button
            v-if="row.status !== 'running'"
            type="primary"
            size="small"
            :icon="VideoPlay"
            @click="startTask(row)"
            :loading="row._starting"
          >启动</el-button>
          <el-button
            v-if="row.status === 'running'"
            type="danger"
            size="small"
            :icon="VideoPause"
            @click="stopTask(row)"
            :loading="row._stopping"
          >停止</el-button>
          <el-button type="info" size="small" plain @click="viewLog(row)">日志</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 日志弹窗 -->
    <el-dialog v-model="logVisible" :title="`任务日志 - ${logTask?.name || ''}`" width="600px">
      <div class="log-status" v-if="logTask">
        状态：<el-tag :type="statusType[logTask.status]" size="small">{{ logTask.status_display || logTask.status }}</el-tag>
      </div>
      <pre class="log-content">{{ logContent || '暂无日志' }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const list = ref([])
const statusType = { pending: 'info', running: 'warning', success: 'success', failed: 'danger' }
const logVisible = ref(false)
const logTask = ref(null)
const logContent = ref('')

async function loadList() {
  loading.value = true
  try {
    const res = await request.get('/crawler/tasks/')
    list.value = (res.results || res.data || []).map(item => ({
      ...item,
      _starting: false,
      _stopping: false
    }))
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}

async function startTask(row) {
  row._starting = true
  try {
    const res = await request.post(`/crawler/tasks/${row.id}/start/`)
    if (res.code === 200) {
      ElMessage.success('任务已启动')
      // 轮询刷新状态
      pollStatus(row.id)
    } else {
      ElMessage.warning(res.message || '启动失败')
    }
  } catch (e) { /* ignore */ }
  finally { row._starting = false }
}

async function stopTask(row) {
  row._stopping = true
  try {
    const res = await request.post(`/crawler/tasks/${row.id}/stop/`)
    if (res.code === 200) {
      ElMessage.success('任务已停止')
      loadList()
    } else {
      ElMessage.warning(res.message || '停止失败')
    }
  } catch (e) { /* ignore */ }
  finally { row._stopping = false }
}

async function viewLog(row) {
  logTask.value = row
  logVisible.value = true
  try {
    const res = await request.get(`/crawler/tasks/${row.id}/logs/`)
    if (res.code === 200) {
      logContent.value = res.data.log
    }
  } catch (e) { logContent.value = '获取日志失败' }
}

function pollStatus(taskId) {
  let count = 0
  const timer = setInterval(async () => {
    count++
    if (count > 30) { clearInterval(timer); return }
    try {
      const res = await request.get(`/crawler/tasks/${taskId}/logs/`)
      if (res.code === 200) {
        const item = list.value.find(i => i.id === taskId)
        if (item) {
          item.status = res.data.status
        }
        if (res.data.status === 'success' || res.data.status === 'failed') {
          clearInterval(timer)
          loadList()
        }
      }
    } catch (e) { clearInterval(timer) }
  }, 2000)
}

onMounted(loadList)
</script>

<style scoped>
.log-status {
  margin-bottom: 12px;
}
.log-content {
  background: #1a202c;
  color: #a0aec0;
  padding: 16px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Consolas', 'Monaco', monospace;
}
</style>
