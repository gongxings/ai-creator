import request from './request'

// 积分相关接口
export interface CreditBalance {
  credits: number
  is_member: boolean
  member_expired_at: string | null
}

export interface CreditTransaction {
  id: number
  user_id: number
  type: string
  amount: number
  balance_after: number
  description: string
  related_order_id: number | null
  created_at: string
}

export interface CreditPrice {
  id: number
  amount: number
  price: number
  bonus: number
  is_active: boolean
  sort_order: number
}

export interface RechargeOrder {
  id: number
  user_id: number
  order_no: string
  amount: number
  bonus: number
  total_amount: number
  price: number
  payment_method: string
  payment_status: string
  paid_at: string | null
  created_at: string
}

export interface MembershipPrice {
  id: number
  membership_type: string
  duration_days: number
  price: number
  original_price: number
  is_active: boolean
  sort_order: number
}

export interface MembershipOrder {
  id: number
  user_id: number
  order_no: string
  membership_type: string
  duration_days: number
  price: number
  payment_method: string
  payment_status: string
  start_date: string | null
  end_date: string | null
  paid_at: string | null
  created_at: string
}

export interface CreditStatistics {
  total_recharge: number
  total_consume: number
  total_refund: number
  current_balance: number
}

export interface MembershipStatistics {
  total_orders: number
  active_membership: boolean
  expired_at: string | null
  days_remaining: number
}

// 获取用户积分余额
export const getCreditBalance = () => {
  return request.get<CreditBalance>('/v1/credit/balance')
}

// 获取积分交易记录
export const getCreditTransactions = (params?: {
  skip?: number
  limit?: number
  type?: string
}) => {
  return request.get<CreditTransaction[]>('/v1/credit/transactions', { params })
}

// 获取积分统计
export const getCreditStatistics = () => {
  return request.get<CreditStatistics>('/v1/credit/statistics')
}

// 获取积分价格列表
export const getCreditPrices = () => {
  return request.get<CreditPrice[]>('/v1/credit/prices')
}

// 创建充值订单
export const createRechargeOrder = (data: {
  price_id: number
  payment_method: string
}) => {
  return request.post<RechargeOrder>('/v1/credit/recharge', data)
}

// 获取充值订单列表
export const getRechargeOrders = (params?: {
  skip?: number
  limit?: number
  status?: string
}) => {
  return request.get<RechargeOrder[]>('/v1/credit/recharge/orders', { params })
}

// 获取充值订单详情
export const getRechargeOrder = (orderId: number) => {
  return request.get<RechargeOrder>(`/v1/credit/recharge/orders/${orderId}`)
}

// 获取会员价格列表
export const getMembershipPrices = () => {
  return request.get<MembershipPrice[]>('/v1/credit/membership/prices')
}

// 创建会员订单
export const createMembershipOrder = (data: {
  price_id: number
  payment_method: string
}) => {
  return request.post<MembershipOrder>('/v1/credit/membership', data)
}

// 获取会员订单列表
export const getMembershipOrders = (params?: {
  skip?: number
  limit?: number
  status?: string
}) => {
  return request.get<MembershipOrder[]>('/v1/credit/membership/orders', { params })
}

// 获取会员订单详情
export const getMembershipOrder = (orderId: number) => {
  return request.get<MembershipOrder>(`/v1/credit/membership/orders/${orderId}`)
}

// 获取会员统计
export const getMembershipStatistics = () => {
  return request.get<MembershipStatistics>('/v1/credit/membership/statistics')
}

// 支付回调（模拟支付成功）
export const simulatePayment = (data: {
  order_type: 'recharge' | 'membership'
  order_no: string
}) => {
  return request.post('/v1/credit/payment/callback', data)
}
