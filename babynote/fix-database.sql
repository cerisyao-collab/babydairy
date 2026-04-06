-- 快速修复脚本 - 添加 detail 字段
-- 在 Supabase SQL Editor 中运行此脚本

-- 1. 添加 detail 字段
ALTER TABLE records 
ADD COLUMN IF NOT EXISTS detail TEXT;

-- 2. 确认字段已添加成功
-- 运行后应该能看到 detail 字段
