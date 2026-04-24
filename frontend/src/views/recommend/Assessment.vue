<template>
  <div>
    <div class="page-card" v-if="!showResult">
      <div class="page-header"><span class="page-title">专业倾向测评</span></div>
      <p style="color:#999;margin-bottom:20px">通过以下测评了解你的专业倾向，帮助选择合适的专业方向。</p>
      <div v-for="(q, idx) in questions" :key="q.id" class="question-item">
        <p class="q-title">{{ idx + 1 }}. {{ q.content }}</p>
        <el-radio-group v-model="answers[q.id]">
          <el-radio v-for="(opt, key) in q.options" :key="key" :value="key" style="display:block;margin:8px 0">
            {{ key }}. {{ opt }}
          </el-radio>
        </el-radio-group>
      </div>
      <el-button type="primary" :loading="loading" :disabled="!allAnswered" @click="handleSubmit" style="margin-top:20px">
        提交测评
      </el-button>
    </div>

    <div v-if="showResult">
      <div class="page-card">
        <div class="page-header"><span class="page-title">测评结果</span></div>
        <el-result icon="success" :title="`你的专业倾向：${resultData.top_dimension}`"
          :sub-title="`推荐专业方向：${resultData.recommended_majors}`">
          <template #extra>
            <el-button type="primary" @click="showResult = false">重新测评</el-button>
            <el-button @click="$router.push('/recommend')">去看推荐</el-button>
          </template>
        </el-result>
        <div style="margin-top:20px">
          <p style="font-weight:600;margin-bottom:12px">各维度得分：</p>
          <div v-for="(val, dim) in resultData.dimensions" :key="dim" style="margin-bottom:8px">
            <span style="display:inline-block;width:80px">{{ dim }}</span>
            <el-progress :percentage="val * 20" :stroke-width="16"
              style="flex:1;display:inline-block;width:calc(100% - 90px)" />
          </div>
        </div>
      </div>

      <div class="page-card" v-if="resultData.matched_items && resultData.matched_items.length">
        <div class="page-header"><span class="page-title">匹配院校与专业</span></div>
        <p style="color:#999;margin-bottom:16px">根据你的测评结果，为你推荐以下院校和专业：</p>
        <el-table :data="resultData.matched_items" stripe>
          <el-table-column label="院校名称" min-width="150">
            <template #default="{ row }">
              <router-link :to="`/universities/${row.university_id}`" class="uni-link">
                {{ row.university_name }}
              </router-link>
              <span v-if="row.is_985" class="tag-985">985</span>
              <span v-if="row.is_211" class="tag-211">211</span>
            </template>
          </el-table-column>
          <el-table-column prop="university_province" label="省份" width="80" />
          <el-table-column prop="major_name" label="推荐专业" min-width="140" />
          <el-table-column prop="major_category" label="学科门类" width="90" />
          <el-table-column label="就业率" width="80" align="center">
            <template #default="{ row }">
              {{ row.employment_rate ? row.employment_rate + '%' : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="平均薪资" width="100" align="center">
            <template #default="{ row }">
              {{ row.avg_salary ? '¥' + row.avg_salary : '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getQuestions, submitAssessment } from '@/api/recommendation'
import { ElMessage } from 'element-plus'

const questions = ref([])
const answers = ref({})
const loading = ref(false)
const showResult = ref(false)
const resultData = ref({})

const allAnswered = computed(() =>
  questions.value.length > 0 && questions.value.every(q => answers.value[q.id])
)

onMounted(async () => {
  try {
    const res = await getQuestions()
    if (res.code === 200) {
      questions.value = res.data
      questions.value.forEach(q => {
        q.options = {
          A: q.option_a,
          B: q.option_b,
          C: q.option_c,
          D: q.option_d
        }
      })
    }
  } catch (e) { /* ignore */ }
})

async function handleSubmit() {
  loading.value = true
  try {
    const res = await submitAssessment({ answers: answers.value })
    if (res.code === 200) {
      resultData.value = res.data
      showResult.value = true
    }
  } catch (e) { /* ignore */ }
  finally { loading.value = false }
}
</script>

<style scoped>
.question-item { margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0; }
.q-title { font-weight: 600; margin-bottom: 8px; }
.uni-link { color: #2c5364; text-decoration: none; font-weight: 500; }
.uni-link:hover { color: #4fd1c5; }
.tag-985, .tag-211 {
  display: inline-block;
  font-size: 11px;
  padding: 1px 5px;
  border-radius: 3px;
  margin-left: 6px;
  color: #fff;
}
.tag-985 { background: #e6553a; }
.tag-211 { background: #2c5364; }
</style>
