<template>
  <div class="admin-users">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-input
            v-model="keyword"
            placeholder="搜索用户名/邮箱"
            style="width: 300px"
            clearable
            @clear="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>
      </template>

      <el-table :data="users" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="nickname" label="昵称" width="100" />
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="credits" label="积分" width="80" />
        <el-table-column prop="total_creations" label="创作数" width="80" />
        <el-table-column prop="created_at" label="注册时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
            <el-button type="warning" size="small" @click="handleResetModels(row)">
              重置模型
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadUsers"
        @size-change="loadUsers"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 用户详情对话框 -->
    <el-dialog v-model="detailVisible" title="用户详情" width="900px">
      <el-descriptions :column="2" border v-if="currentUser">
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentUser.email }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ currentUser.nickname || '-' }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ currentUser.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag>{{ currentUser.role }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUser.status === 'active' ? 'success' : 'danger'">
            {{ currentUser.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="积分">{{ currentUser.credits }}</el-descriptions-item>
        <el-descriptions-item label="每日配额">{{ currentUser.daily_quota }}</el-descriptions-item>
        <el-descriptions-item label="总创作数">{{ currentUser.total_creations }}</el-descriptions-item>
        <el-descriptions-item label="会员状态">
          {{ currentUser.is_member ? '是' : '否' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider>AI 模型 ({{ aiModels.length }})</el-divider>
      
      <el-table :data="aiModels" max-height="400">
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="provider" label="提供商" width="120" />
        <el-table-column prop="model_name" label="模型" width="150" />
        <el-table-column prop="system_default_source" label="来源" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.system_default_source" type="warning">系统默认</el-tag>
            <el-tag v-else>自定义</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-divider>使用统计</el-divider>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="总请求数">{{ usageStats.total_requests }}</el-descriptions-item>
        <el-descriptions-item label="总 Token 数">{{ (usageStats.total_tokens / 10000).toFixed(2) }} 万</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserList, getUserDetail, resetUserModels } from '@/api/adminUsers'

const loading = ref(false)
const users = ref<any[]>([])
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const detailVisible = ref(false)
const currentUser = ref<any>(null)
const aiModels = ref<any[]>([])
const usageStats = ref({ total_requests: 0, total_tokens: 0 })

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getUserList({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: keyword.value
    })
    users.value = res.data.users
    total.value = res.data.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

// 查看详情
const handleViewDetail = async (user: any) => {
  try {
    const res = await getUserDetail(user.id)
    currentUser.value = res.data.user
    aiModels.value = res.data.ai_models
    usageStats.value = res.data.usage_stats
    detailVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '加载详情失败')
  }
}

// 重置模型
const handleResetModels = async (user: any) => {
  try {
    await ElMessageBox.confirm(`确定要重置用户 "${user.username}" 的模型吗？`, '警告', {
      type: 'warning'
    })
    
    await resetUserModels(user.id)
    ElMessage.success('重置成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '重置失败')
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-users {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
