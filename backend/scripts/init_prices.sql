-- 初始化积分价格和会员价格配置
-- 积分规则: 1元 = 100积分

-- 清空现有数据（如果需要）
-- TRUNCATE TABLE credit_prices;
-- TRUNCATE TABLE membership_prices;

-- 插入积分价格套餐
INSERT INTO credit_prices (name, amount, credits, bonus_credits, is_active, sort_order, description, created_at, updated_at)
VALUES 
    ('10元套餐', 10.00, 1000, 0, 1, 1, '1000积分，适合轻度使用', NOW(), NOW()),
    ('50元套餐', 50.00, 5000, 200, 1, 2, '5000积分+赠送200积分', NOW(), NOW()),
    ('100元套餐', 100.00, 10000, 500, 1, 3, '10000积分+赠送500积分，超值推荐', NOW(), NOW()),
    ('200元套餐', 200.00, 20000, 1500, 1, 4, '20000积分+赠送1500积分，性价比最高', NOW(), NOW())
ON DUPLICATE KEY UPDATE
    amount = VALUES(amount),
    credits = VALUES(credits),
    bonus_credits = VALUES(bonus_credits),
    description = VALUES(description),
    updated_at = NOW();

-- 插入会员价格套餐
INSERT INTO membership_prices (name, membership_type, amount, original_amount, duration_days, is_active, sort_order, description, features, created_at, updated_at)
VALUES 
    ('月度会员', 'monthly', 29.00, 39.00, 30, 1, 1, '适合尝试体验', 
     '["所有AI创作工具不限次数", "不消耗积分", "基础客服支持"]', NOW(), NOW()),
    ('季度会员', 'quarterly', 79.00, 117.00, 90, 1, 2, '省38元，性价比之选', 
     '["所有AI创作工具不限次数", "不消耗积分", "优先客服支持", "新功能优先体验"]', NOW(), NOW()),
    ('年度会员', 'yearly', 299.00, 468.00, 365, 1, 3, '省169元，长期用户首选', 
     '["所有AI创作工具不限次数", "不消耗积分", "专属客服经理", "新功能优先体验", "定制化服务支持"]', NOW(), NOW())
ON DUPLICATE KEY UPDATE
    amount = VALUES(amount),
    original_amount = VALUES(original_amount),
    duration_days = VALUES(duration_days),
    description = VALUES(description),
    features = VALUES(features),
    updated_at = NOW();

-- 查看插入结果
SELECT * FROM credit_prices;
SELECT * FROM membership_prices;
