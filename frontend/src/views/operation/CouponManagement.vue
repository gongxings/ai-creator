<template>
  <div class="coupon-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>优惠券管理</span>
          <el-button type="primary" @click="showCreateDialog">创建优惠券</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm">
        <el-form-item label="优惠券类型">
          <el-select v-model="searchForm.coupon_type" placeholder="全部" clearable>
            <el-option label="充值优惠券" value="recharge" />
            <el-option label="会员优惠券" value="membership" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadCoupons">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="coupons" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="code" label="优惠券码" />
        <el-table-column prop="name" label="优惠券名称" />
        <el-table-column prop="coupon_type" label="类型">
          <template #default="{ row }">
            <el-tag v-if="row.coupon_type === 'recharge'">充值优惠券</el-tag>
            <el-tag v-else type="success">会员优惠券</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="discount_value" label="折扣">
          <template #default="{ row }">
            <span v-if="row.discount_type === 'fixed'">{{ row.discount_value }}元</span>
            <span v-else>{{ row.discount_value }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="使用情况">
          <template #default="{ row }">
            {{ row.used_quantity }} / {{ row.total_quantity }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag v-if="row.is_active" type="success">启用</el-tag>
            <el-tag v-else type="danger">禁用</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewCoupon(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editCoupon(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCoupon(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, prev, pager, next"
        @current-change="loadCoupons"
      />
    </el-card>

    <!-- 创建/编辑优惠券对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="couponForm" label-width="120px">
        <el-form-item label="优惠券码" required>
          <el-input v-model="couponForm.code" />
        </el-form-item>
        <el-form-item label="优惠券名称" required>
          <el-input v-model="couponForm.name" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="couponForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="优惠券类型" required>
          <el-select v-model="couponForm.coupon_type">
            <el-option label="充值优惠券" value="recharge" />
            <el-option label="会员优惠券" value="membership" />
          </el-select>
        </el-form-item>
        <el-form-item label="折扣类型" required>
          <el-select v-model="couponForm.discount_type">
            <el-option label="固定金额" value="fixed" />
            <el-option label="百分比" value="percentage" />
          </el-select>
        </el-form-item>
        <el-form-item label="折扣值" required>
          <el-input-number v-model="couponForm.discount_value" :min="0" />
        </el-form-item>
        <el-form-item label="最低消费金额" required>
          <el-input-number v-model="couponForm.min_amount" :min="0" />
        </el-form-item>
        <el-form-item label="最大折扣金额">
          <el-input-number v-model="couponForm.max_discount" :min="0" />
        </el-form-item>
        <el-form-item label="发行数量" required>
          <el-input-number v-model="couponForm.total_quantity" :min="1" />
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker
            v-model="couponForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
          />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-date-picker
            v-model="couponForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCoupon">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as operationApi from '@/api/operation'

const coupons = ref<operationApi.Coupon[]>([])
const searchForm = reactive({
  coupon_type: '',
  is_active: undefined as boolean | undefined,
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const dialogVisible = ref(false)
const dialogTitle = ref('创建优惠券')
const couponForm = reactive({
  id: 0,
  code: '',
  name: '',
  description: '',
  coupon_type: 'recharge',
  discount_type: 'fixed',
  discount_value: 0,
  min_amount: 0,
  max_discount: undefined as number | undefined,
  total_quantity: 100,
  start_time: '',
  end_time: '',
})

const loadCoupons = async () => {
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm,
    }
    const response = await operationApi.getCoupons(params)
    coupons.value = response.data
    pagination.total = response.data.length
  } catch (error) {
    ElMessage.error('加载优惠券列表失败')
  }
}

const showCreateDialog = () => {
  dialogTitle.value = '创建优惠券'
  resetForm()
  dialogVisible.value = true
}

const viewCoupon = (coupon: operationApi.Coupon) => {
  ElMessageBox.alert(
    `<p><strong>优惠券码：</strong>${coupon.code}</p>
     <p><strong>优惠券名称：</strong>${coupon.name}</p>
     <p><strong>描述：</strong>${coupon.description}</p>
     <p><strong>折扣：</strong>${coupon.discount_type === 'fixed' ? coupon.discount_value + '元' : coupon.discount_value + '%'}</p>
     <p><strong>使用情况：</strong>${coupon.used_quantity} / ${coupon.total_quantity}</p>`,
    '优惠券详情',
    {
      dangerouslyUseHTMLString: true,
    }
  )
}

const editCoupon = (coupon: operationApi.Coupon) => {
  dialogTitle.value = '编辑优惠券'
  Object.assign(couponForm, coupon)
  dialogVisible.value = true
}

const deleteCoupon = async (coupon: operationApi.Coupon) => {
  try {
    await ElMessageBox.confirm('确定要删除这个优惠券吗？', '提示', {
      type: 'warning',
    })
    await operationApi.deleteCoupon(coupon.id)
    ElMessage.success('删除成功')
    loadCoupons()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveCoupon = async () => {
  try {
    if (couponForm.id) {
      await operationApi.updateCoupon(couponForm.id, couponForm)
      ElMessage.success('更新成功')
    } else {
      await operationApi.createCoupon(couponForm)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadCoupons()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const resetForm = () => {
  couponForm.id = 0
  couponForm.code = ''
  couponForm.name = ''
  couponForm.description = ''
  couponForm.coupon_type = 'recharge'
  couponForm.discount_type = 'fixed'
  couponForm.discount_value = 0
  couponForm.min_amount = 0
  couponForm.max_discount = undefined
  couponForm.total_quantity = 100
  couponForm.start_time = ''
  couponForm.end_time = ''
}

onMounted(() => {
  loadCoupons()
})
</script>

<style scoped>
.coupon-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
