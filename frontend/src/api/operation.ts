import request from './request'

// 活动相关接口
export interface Activity {
  id: number
  title: string
  description: string
  activity_type: string
  status: string
  reward_type: string
  reward_amount: number
  start_time: string
  end_time: string
  max_participants: number | null
  current_participants: number
  rules: any
  created_at: string
}

export interface ActivityParticipation {
  id: number
  activity_id: number
  user_id: number
  reward_amount: number
  participated_at: string
}

// 优惠券相关接口
export interface Coupon {
  id: number
  code: string
  name: string
  description: string
  coupon_type: string
  discount_type: string
  discount_value: number
  min_amount: number
  max_discount: number | null
  total_quantity: number
  used_quantity: number
  start_time: string
  end_time: string
  is_active: boolean
  created_at: string
}

export interface UserCoupon {
  id: number
  user_id: number
  coupon_id: number
  coupon: Coupon
  status: string
  received_at: string
  used_at: string | null
  expired_at: string
}

// 推广相关接口
export interface ReferralRecord {
  id: number
  referrer_id: number
  referred_id: number
  referral_type: string
  reward_amount: number
  status: string
  created_at: string
  rewarded_at: string | null
}

export interface ReferralStatistics {
  total_referrals: number
  total_rewards: number
  pending_rewards: number
  referral_code: string
}

// 统计相关接口
export interface OperationStatistics {
  date: string
  new_users: number
  active_users: number
  recharge_amount: number
  recharge_count: number
  membership_amount: number
  membership_count: number
  credit_consume: number
  generation_count: number
  activity_participants: number
  coupon_used: number
  referral_count: number
  referral_rewards: number
}

// 活动管理
export const getActivities = (params?: {
  skip?: number
  limit?: number
  status?: string
  activity_type?: string
}) => {
  return request.get<Activity[]>('/api/v1/operation/activities', { params })
}

export const getActivity = (activityId: number) => {
  return request.get<Activity>(`/api/v1/operation/activities/${activityId}`)
}

export const createActivity = (data: {
  title: string
  description: string
  activity_type: string
  reward_type: string
  reward_amount: number
  start_time: string
  end_time: string
  max_participants?: number
  rules?: any
}) => {
  return request.post<Activity>('/api/v1/operation/activities', data)
}

export const updateActivity = (activityId: number, data: Partial<Activity>) => {
  return request.put<Activity>(`/api/v1/operation/activities/${activityId}`, data)
}

export const deleteActivity = (activityId: number) => {
  return request.delete(`/api/v1/operation/activities/${activityId}`)
}

export const participateActivity = (activityId: number) => {
  return request.post<ActivityParticipation>(`/api/v1/operation/activities/${activityId}/participate`)
}

export const getActivityParticipations = (activityId: number, params?: {
  skip?: number
  limit?: number
}) => {
  return request.get<ActivityParticipation[]>(`/api/v1/operation/activities/${activityId}/participations`, { params })
}

// 优惠券管理
export const getCoupons = (params?: {
  skip?: number
  limit?: number
  coupon_type?: string
  is_active?: boolean
}) => {
  return request.get<Coupon[]>('/api/v1/operation/coupons', { params })
}

export const getCoupon = (couponId: number) => {
  return request.get<Coupon>(`/api/v1/operation/coupons/${couponId}`)
}

export const createCoupon = (data: {
  code: string
  name: string
  description: string
  coupon_type: string
  discount_type: string
  discount_value: number
  min_amount: number
  max_discount?: number
  total_quantity: number
  start_time: string
  end_time: string
}) => {
  return request.post<Coupon>('/api/v1/operation/coupons', data)
}

export const updateCoupon = (couponId: number, data: Partial<Coupon>) => {
  return request.put<Coupon>(`/api/v1/operation/coupons/${couponId}`, data)
}

export const deleteCoupon = (couponId: number) => {
  return request.delete(`/api/v1/operation/coupons/${couponId}`)
}

export const receiveCoupon = (couponId: number) => {
  return request.post<UserCoupon>(`/api/v1/operation/coupons/${couponId}/receive`)
}

export const getUserCoupons = (params?: {
  skip?: number
  limit?: number
  status?: string
}) => {
  return request.get<UserCoupon[]>('/api/v1/operation/coupons/my', { params })
}

// 推广管理
export const getReferralCode = () => {
  return request.get<{ referral_code: string }>('/api/v1/operation/referral/code')
}

export const getReferralRecords = (params?: {
  skip?: number
  limit?: number
  status?: string
}) => {
  return request.get<ReferralRecord[]>('/api/v1/operation/referral/records', { params })
}

export const getReferralStatistics = () => {
  return request.get<ReferralStatistics>('/api/v1/operation/referral/statistics')
}

// 数据统计
export const getOperationStatistics = (params?: {
  start_date?: string
  end_date?: string
}) => {
  return request.get<OperationStatistics[]>('/api/v1/operation/statistics', { params })
}

export const getDashboardStatistics = () => {
  return request.get<{
    today: OperationStatistics
    yesterday: OperationStatistics
    this_month: OperationStatistics
    last_month: OperationStatistics
  }>('/api/v1/operation/statistics/dashboard')
}
