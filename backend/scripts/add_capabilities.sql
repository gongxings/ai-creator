-- 为 ai_models 表添加 capabilities 字段
-- 该字段存储模型支持的能力列表，如 ["text", "image", "video", "audio"]

-- 添加 capabilities 字段（如果不存在）
ALTER TABLE ai_models 
ADD COLUMN IF NOT EXISTS capabilities JSON DEFAULT '["text"]' COMMENT '模型能力列表(text/image/video/audio)';

-- 更新现有记录，设置默认值为 ["text"]
UPDATE ai_models 
SET capabilities = '["text"]' 
WHERE capabilities IS NULL;

-- 验证更新结果
SELECT id, name, provider, model_name, capabilities FROM ai_models;
